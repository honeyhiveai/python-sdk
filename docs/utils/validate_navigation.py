#!/usr/bin/env python3
"""
Documentation Navigation Validation Script

Validates that all documentation navigation links are working correctly
after deployment. This script can be run locally or in CI/CD to ensure
documentation integrity.

Usage:
    python docs/utils/validate_navigation.py --base-url https://honeyhiveai.github.io/python-sdk/
    python docs/utils/validate_navigation.py --local  # For local builds
"""

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("❌ ERROR: Required dependencies not installed!")
    print("   Navigation validation requires: requests, beautifulsoup4")
    print("   Install with: pip install requests beautifulsoup4")
    print("   Or: pip install -r docs/utils/requirements.txt")
    print("")
    print("   Navigation validation CANNOT be skipped.")
    sys.exit(1)  # Fail the pre-commit hook!


class NavigationValidator:
    """Validates documentation navigation and links."""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "HoneyHive-Docs-Validator/1.0"})

        # Track validation results
        self.tested_urls: Set[str] = set()
        self.broken_links: List[Tuple[str, str, str]] = []  # (source_page, link, error)
        self.missing_pages: List[str] = []
        self.navigation_errors: List[str] = []

    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate a single URL and return (success, error_message)."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return True, ""
            else:
                return False, f"HTTP {response.status_code}"
        except requests.RequestException as e:
            return False, str(e)

    def extract_links_from_page(self, url: str) -> List[str]:
        """Extract all internal links from a documentation page."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.content, "html.parser")
            links = []

            # Extract links from navigation, content, and toctree
            for link_element in soup.find_all("a", href=True):
                href = link_element["href"]

                # Skip external links, anchors, and email links
                if (
                    href.startswith("http")
                    and not href.startswith(self.base_url)
                    or href.startswith("#")
                    or href.startswith("mailto:")
                ):
                    continue

                # Convert relative links to absolute
                if href.startswith("/"):
                    full_url = self.base_url + href
                elif href.startswith("./") or not href.startswith("http"):
                    full_url = urljoin(url, href)
                else:
                    full_url = href

                # Remove anchors for validation
                full_url = full_url.split("#")[0]

                if full_url and full_url not in links:
                    links.append(full_url)

            return links

        except Exception as e:
            print(f"⚠️  Error extracting links from {url}: {e}")
            return []

    def discover_documentation_pages(self) -> List[str]:
        """Dynamically discover all documentation pages from source files."""
        docs_dir = Path(__file__).parent.parent
        pages = []

        # Find all .rst files and convert to expected .html paths
        for rst_file in docs_dir.rglob("*.rst"):
            # Skip files that shouldn't be in the final build
            if any(
                skip in str(rst_file) for skip in ["_build", "_templates", "_static", "python-sdk", "site-packages", "venv"]
            ):
                continue

            # Convert .rst path to expected .html URL path
            relative_path = rst_file.relative_to(docs_dir)

            # Convert index.rst to index.html, others to .html
            if relative_path.name == "index.rst":
                if relative_path.parent == Path("."):
                    html_path = ""  # Root index
                else:
                    html_path = f"{relative_path.parent}/index.html"
            else:
                html_path = str(relative_path.with_suffix(".html"))

            # Normalize path separators for URLs
            html_path = html_path.replace("\\", "/")
            pages.append(html_path)

        return sorted(pages)

    def validate_critical_pages(self) -> bool:
        """Validate that all discovered documentation pages exist."""
        print("🔍 Discovering documentation pages from source files...")

        # Dynamically discover all pages
        discovered_pages = self.discover_documentation_pages()

        print(f"📄 Found {len(discovered_pages)} documentation pages to validate")

        # Always include these critical structural pages
        critical_structural_pages = [
            "",  # Root index
            "search.html",  # Search functionality
            "genindex.html",  # General index
        ]

        # Combine discovered pages with critical structural pages
        all_pages = discovered_pages + [
            p for p in critical_structural_pages if p not in discovered_pages
        ]

        print("🔍 Validating all documentation pages...")
        success = True

        for page_path in all_pages:
            url = f"{self.base_url}/{page_path}" if page_path else self.base_url
            is_valid, error = self.validate_url(url)

            if is_valid:
                print(f"✅ {page_path or 'index'}")
                self.tested_urls.add(url)
            else:
                print(f"❌ {page_path or 'index'} - {error}")
                self.missing_pages.append(f"{page_path or 'index'} - {error}")
                success = False

            # Small delay to be nice to the server
            time.sleep(0.1)

        return success

    def validate_navigation_structure(self) -> bool:
        """Validate the navigation structure and toctree integrity."""
        print("\n🧭 Validating navigation structure...")

        # Check main navigation from index page
        index_url = self.base_url
        is_valid, error = self.validate_url(index_url)

        if not is_valid:
            print(f"❌ Cannot access index page: {error}")
            return False

        # Extract and validate navigation links
        nav_links = self.extract_links_from_page(index_url)

        # Validate that main sections are linked
        required_sections = [
            "tutorials/",
            "how-to/",
            "reference/",
            "explanation/",
            "changelog",
        ]

        found_sections = set()
        for link in nav_links:
            for section in required_sections:
                if section in link:
                    found_sections.add(section)

        missing_sections = set(required_sections) - found_sections
        if missing_sections:
            for section in missing_sections:
                error_msg = f"Main navigation missing link to {section}"
                print(f"❌ {error_msg}")
                self.navigation_errors.append(error_msg)
            return False

        print("✅ Main navigation structure validated")
        return True

    def validate_toctree_links(self) -> bool:
        """Validate all toctree links are working."""
        print("\n📑 Validating toctree links...")

        # Pages with toctrees to validate
        toctree_pages = [
            ("", "Main toctree"),
            ("tutorials/index.html", "Tutorials toctree"),
            ("how-to/index.html", "How-to guides toctree"),
            ("how-to/integrations/index.html", "Integrations toctree"),
            ("reference/index.html", "Reference toctree"),
            ("explanation/index.html", "Explanation toctree"),
        ]

        success = True

        for page_path, description in toctree_pages:
            url = f"{self.base_url}/{page_path}" if page_path else self.base_url

            print(f"🔍 Checking {description}...")
            links = self.extract_links_from_page(url)

            # Validate each link in the toctree
            for link in links:
                if link in self.tested_urls:
                    continue

                is_valid, error = self.validate_url(link)
                if is_valid:
                    print(f"  ✅ {link.replace(self.base_url, '')}")
                    self.tested_urls.add(link)
                else:
                    print(f"  ❌ {link.replace(self.base_url, '')} - {error}")
                    self.broken_links.append((url, link, error))
                    success = False

                time.sleep(0.1)

        return success

    def validate_cross_references(self) -> bool:
        """Validate cross-references between documentation pages."""
        print("\n🔗 Validating cross-references...")

        # Sample pages to check cross-references
        pages_to_check = [
            "tutorials/03-llm-integration.html",
            "how-to/integrations/multi-provider.html",
            "how-to/integrations/google-adk.html",
            "reference/index.html",
        ]

        success = True

        for page_path in pages_to_check:
            url = f"{self.base_url}/{page_path}"
            print(f"🔍 Checking cross-references in {page_path}...")

            links = self.extract_links_from_page(url)
            internal_links = [link for link in links if link.startswith(self.base_url)]

            # Validate a sample of internal cross-references
            for link in internal_links[:5]:  # Check first 5 to avoid overloading
                if link in self.tested_urls:
                    continue

                is_valid, error = self.validate_url(link)
                if is_valid:
                    print(f"  ✅ {link.replace(self.base_url, '')}")
                    self.tested_urls.add(link)
                else:
                    print(f"  ❌ {link.replace(self.base_url, '')} - {error}")
                    self.broken_links.append((url, link, error))
                    success = False

                time.sleep(0.1)

        return success

    def validate_search_functionality(self) -> bool:
        """Validate that search functionality is available."""
        print("\n🔍 Validating search functionality...")

        # Check for search files
        search_files = ["search.html", "searchindex.js", "_static/searchtools.js"]

        success = True
        for file_path in search_files:
            url = f"{self.base_url}/{file_path}"
            is_valid, error = self.validate_url(url)

            if is_valid:
                print(f"✅ Search file: {file_path}")
            else:
                print(f"❌ Missing search file: {file_path} - {error}")
                success = False

        return success

    def generate_report(self) -> Dict:
        """Generate a comprehensive validation report."""
        return {
            "total_urls_tested": len(self.tested_urls),
            "missing_pages": self.missing_pages,
            "broken_links": self.broken_links,
            "navigation_errors": self.navigation_errors,
            "success": len(self.missing_pages) == 0
            and len(self.broken_links) == 0
            and len(self.navigation_errors) == 0,
        }

    def run_full_validation(self) -> bool:
        """Run complete navigation validation."""
        print(f"🚀 Starting documentation navigation validation for: {self.base_url}")
        print("=" * 70)

        # Run all validation steps
        results = []
        results.append(self.validate_critical_pages())
        results.append(self.validate_navigation_structure())
        results.append(self.validate_toctree_links())
        results.append(self.validate_cross_references())
        results.append(self.validate_search_functionality())

        # Generate final report
        report = self.generate_report()

        print("\n📊 Validation Summary")
        print("=" * 70)
        print(f"Total URLs tested: {report['total_urls_tested']}")
        print(f"Missing pages: {len(report['missing_pages'])}")
        print(f"Broken links: {len(report['broken_links'])}")
        print(f"Navigation errors: {len(report['navigation_errors'])}")

        if report["missing_pages"]:
            print("\n❌ Missing Pages:")
            for page in report["missing_pages"]:
                print(f"  • {page}")

        if report["broken_links"]:
            print("\n❌ Broken Links:")
            for source, link, error in report["broken_links"]:
                print(f"  • {link} (from {source}) - {error}")

        if report["navigation_errors"]:
            print("\n❌ Navigation Errors:")
            for error in report["navigation_errors"]:
                print(f"  • {error}")

        if report["success"]:
            print("\n🎉 All navigation validation checks passed!")
            return True
        else:
            print("\n💥 Navigation validation failed!")
            return False


def main():
    """Main function to run navigation validation."""
    parser = argparse.ArgumentParser(description="Validate documentation navigation")
    parser.add_argument(
        "--base-url",
        default="https://honeyhiveai.github.io/python-sdk",
        help="Base URL for documentation site",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Validate local build (uses localhost:8000)",
    )
    parser.add_argument(
        "--timeout", type=int, default=10, help="Request timeout in seconds"
    )

    args = parser.parse_args()

    if args.local:
        base_url = "http://localhost:8000"
    else:
        base_url = args.base_url

    validator = NavigationValidator(base_url, timeout=args.timeout)
    success = validator.run_full_validation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
