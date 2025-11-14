#!/usr/bin/env python3
"""
Documentation Link Validator

Validates all links in documentation for correctness and accessibility.

Usage:
    python validate-links.py                    # Validate all links (including external)
    python validate-links.py --skip-external   # Skip external URL checks (faster)
    python validate-links.py --report           # Generate markdown report
    python validate-links.py --skip-external --report  # Both

Exit Codes:
    0: No broken links found
    1: Broken links detected

Validation:
    - Internal markdown links (relative paths)
    - Anchor links (section headers)
    - External URLs (HTTP 200 check with timeout)
    - Image paths
"""

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Warning: requests library not installed. External URL validation disabled.")
    print("Install with: pip install requests")
    requests = None


# ANSI color codes
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


@dataclass
class BrokenLink:
    """Represents a broken link"""

    source_file: str
    line_number: int
    link_text: str
    link_target: str
    issue: str
    link_type: str  # 'internal', 'anchor', 'external', 'image'


@dataclass
class LinkValidatorResult:
    """Results of link validation"""

    total_links: int = 0
    broken_links: List[BrokenLink] = field(default_factory=list)
    slow_links: List[tuple] = field(default_factory=list)  # (url, response_time)

    @property
    def has_broken_links(self) -> bool:
        return len(self.broken_links) > 0


class LinkValidator:
    """Validates all links in markdown documentation"""

    def __init__(self, content_dir: str = "docs/content", skip_external: bool = False):
        self.content_dir = Path(content_dir)
        self.skip_external = skip_external
        self.result = LinkValidatorResult()

        # Track all valid internal files and their anchors
        self.valid_files: Set[Path] = set()
        self.file_anchors: Dict[Path, Set[str]] = {}

        # Session for external requests
        if requests and not skip_external:
            self.session = requests.Session()
            self.session.headers.update(
                {"User-Agent": "Mozilla/5.0 (Documentation Link Validator)"}
            )
        else:
            self.session = None

    def validate_all(self) -> LinkValidatorResult:
        """Validate all links in documentation"""
        if not self.content_dir.exists():
            print(
                f"{Colors.RED}Error: Content directory not found: {self.content_dir}{Colors.RESET}"
            )
            sys.exit(1)

        # First pass: collect all valid files and their anchors
        print(f"{Colors.BLUE}Scanning documentation structure...{Colors.RESET}")
        md_files = list(self.content_dir.rglob("*.md"))

        for md_file in md_files:
            self.valid_files.add(md_file)
            self.file_anchors[md_file] = self._extract_anchors(md_file)

        print(f"Found {len(md_files)} markdown files")

        # Second pass: validate all links
        print(f"{Colors.BLUE}Validating links...{Colors.RESET}")
        for md_file in md_files:
            self._validate_file(md_file)

        return self.result

    def _extract_anchors(self, file_path: Path) -> Set[str]:
        """Extract all anchor IDs from markdown headings"""
        anchors = set()

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract headings
        heading_pattern = r"^#{1,6}\s+(.+)$"
        for match in re.finditer(heading_pattern, content, re.MULTILINE):
            heading_text = match.group(1).strip()
            # Generate anchor ID (Docusaurus style: lowercase, hyphens, no special chars)
            anchor_id = re.sub(r"[^\w\s-]", "", heading_text.lower())
            anchor_id = re.sub(r"[-\s]+", "-", anchor_id).strip("-")
            anchors.add(anchor_id)

        return anchors

    def _validate_file(self, file_path: Path):
        """Validate all links in a single file"""
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, start=1):
            # Skip code blocks
            if line.strip().startswith("```"):
                continue

            # Find all markdown links: [text](url)
            link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
            for match in re.finditer(link_pattern, line):
                link_text = match.group(1)
                link_target = match.group(2)

                self.result.total_links += 1

                # Determine link type and validate
                if link_target.startswith("http://") or link_target.startswith(
                    "https://"
                ):
                    if not self.skip_external:
                        self._validate_external_link(
                            file_path, line_num, link_text, link_target
                        )
                elif link_target.startswith("#"):
                    self._validate_anchor_link(
                        file_path, line_num, link_text, link_target
                    )
                elif link_target.startswith("/"):
                    # Absolute path (Docusaurus route)
                    self._validate_docusaurus_route(
                        file_path, line_num, link_text, link_target
                    )
                else:
                    # Relative path
                    self._validate_internal_link(
                        file_path, line_num, link_text, link_target
                    )

            # Find image links: ![alt](path)
            image_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
            for match in re.finditer(image_pattern, line):
                alt_text = match.group(1)
                image_path = match.group(2)

                self.result.total_links += 1

                if not (
                    image_path.startswith("http://")
                    or image_path.startswith("https://")
                ):
                    self._validate_image_path(file_path, line_num, alt_text, image_path)

    def _validate_internal_link(
        self, source_file: Path, line_num: int, link_text: str, link_target: str
    ):
        """Validate internal markdown link (relative path)"""
        # Remove anchor if present
        target_path, _, anchor = link_target.partition("#")

        if not target_path:
            # Just an anchor, validate later
            return

        # Resolve relative path
        source_dir = source_file.parent
        target_file = (source_dir / target_path).resolve()

        # Check if link escapes docs/ directory (Docusaurus scope check)
        docs_root = (self.content_dir.parent).resolve()  # docs/ directory
        try:
            target_file.relative_to(docs_root)
        except ValueError:
            # Link escapes docs/ directory - will work locally but fail in Docusaurus build
            self.result.broken_links.append(
                BrokenLink(
                    source_file=str(source_file.relative_to(self.content_dir.parent)),
                    line_number=line_num,
                    link_text=link_text,
                    link_target=link_target,
                    issue=f"Link escapes docs/ directory (Docusaurus will fail to build). Use GitHub URL instead: https://github.com/honeyhiveai/praxis-os-enhanced/blob/main/{target_file.relative_to(docs_root.parent)}",
                    link_type="escape",
                )
            )
            return

        # Add .md extension if missing and it's not a directory
        if not target_file.suffix:
            # Could be Docusaurus route, check both .md and directory
            md_file = Path(str(target_file) + ".md")
            if md_file.exists() and md_file in self.valid_files:
                target_file = md_file
            elif not target_file.is_dir():
                target_file = md_file

        # Check if file exists
        if not target_file.exists():
            self.result.broken_links.append(
                BrokenLink(
                    source_file=str(source_file.relative_to(self.content_dir.parent)),
                    line_number=line_num,
                    link_text=link_text,
                    link_target=link_target,
                    issue=f"File not found: {target_file}",
                    link_type="internal",
                )
            )
            return

        # Validate anchor if present
        if anchor and target_file in self.file_anchors:
            if anchor not in self.file_anchors[target_file]:
                self.result.broken_links.append(
                    BrokenLink(
                        source_file=str(
                            source_file.relative_to(self.content_dir.parent)
                        ),
                        line_number=line_num,
                        link_text=link_text,
                        link_target=link_target,
                        issue=f"Anchor not found: #{anchor}",
                        link_type="anchor",
                    )
                )

    def _validate_anchor_link(
        self, source_file: Path, line_num: int, link_text: str, link_target: str
    ):
        """Validate anchor link within same file"""
        anchor = link_target[1:]  # Remove leading #

        if source_file in self.file_anchors:
            if anchor not in self.file_anchors[source_file]:
                self.result.broken_links.append(
                    BrokenLink(
                        source_file=str(
                            source_file.relative_to(self.content_dir.parent)
                        ),
                        line_number=line_num,
                        link_text=link_text,
                        link_target=link_target,
                        issue=f"Anchor not found in current file: #{anchor}",
                        link_type="anchor",
                    )
                )

    def _validate_docusaurus_route(
        self, source_file: Path, line_num: int, link_text: str, link_target: str
    ):
        """Validate Docusaurus route (absolute path starting with /)"""
        # Remove /docs/ or /docs prefix if present
        route = link_target
        if route.startswith("/docs/"):
            route = route[6:]
        elif route.startswith("/docs"):
            route = route[5:]

        # Remove anchor if present
        route_path, _, anchor = route.partition("#")

        if not route_path or route_path == "/":
            return  # Root or home page

        # Try to find corresponding file
        route_path = route_path.lstrip("/")
        possible_files = [
            self.content_dir / f"{route_path}.md",
            self.content_dir / route_path / "index.md",
            self.content_dir / f"{route_path}/index.md",
        ]

        found = False
        for possible_file in possible_files:
            if possible_file.exists() and possible_file in self.valid_files:
                found = True
                # Validate anchor if present
                if anchor and possible_file in self.file_anchors:
                    if anchor not in self.file_anchors[possible_file]:
                        self.result.broken_links.append(
                            BrokenLink(
                                source_file=str(
                                    source_file.relative_to(self.content_dir.parent)
                                ),
                                line_number=line_num,
                                link_text=link_text,
                                link_target=link_target,
                                issue=f"Anchor not found: #{anchor}",
                                link_type="anchor",
                            )
                        )
                break

        if not found:
            self.result.broken_links.append(
                BrokenLink(
                    source_file=str(source_file.relative_to(self.content_dir.parent)),
                    line_number=line_num,
                    link_text=link_text,
                    link_target=link_target,
                    issue=f"Docusaurus route not found: {link_target}",
                    link_type="internal",
                )
            )

    def _validate_external_link(
        self, source_file: Path, line_num: int, link_text: str, link_target: str
    ):
        """Validate external URL (HTTP/HTTPS)"""
        if not self.session:
            return  # requests not available

        try:
            start_time = time.time()
            response = self.session.head(link_target, timeout=5, allow_redirects=True)
            response_time = time.time() - start_time

            if response.status_code >= 400:
                self.result.broken_links.append(
                    BrokenLink(
                        source_file=str(
                            source_file.relative_to(self.content_dir.parent)
                        ),
                        line_number=line_num,
                        link_text=link_text,
                        link_target=link_target,
                        issue=f"HTTP {response.status_code}",
                        link_type="external",
                    )
                )
            elif response_time > 3.0:
                self.result.slow_links.append((link_target, response_time))

        except requests.exceptions.Timeout:
            self.result.broken_links.append(
                BrokenLink(
                    source_file=str(source_file.relative_to(self.content_dir.parent)),
                    line_number=line_num,
                    link_text=link_text,
                    link_target=link_target,
                    issue="Request timeout (>5s)",
                    link_type="external",
                )
            )
        except requests.exceptions.RequestException as e:
            self.result.broken_links.append(
                BrokenLink(
                    source_file=str(source_file.relative_to(self.content_dir.parent)),
                    line_number=line_num,
                    link_text=link_text,
                    link_target=link_target,
                    issue=f"Request failed: {str(e)[:100]}",
                    link_type="external",
                )
            )

    def _validate_image_path(
        self, source_file: Path, line_num: int, alt_text: str, image_path: str
    ):
        """Validate image path"""
        # Resolve relative path
        if image_path.startswith("/"):
            # Absolute path from docs root
            docs_root = self.content_dir.parent
            image_file = docs_root / image_path.lstrip("/")
        else:
            source_dir = source_file.parent
            image_file = (source_dir / image_path).resolve()

        if not image_file.exists():
            self.result.broken_links.append(
                BrokenLink(
                    source_file=str(source_file.relative_to(self.content_dir.parent)),
                    line_number=line_num,
                    link_text=alt_text or "(no alt text)",
                    link_target=image_path,
                    issue=f"Image not found: {image_file}",
                    link_type="image",
                )
            )

    def print_results(self):
        """Print validation results to console"""
        print(f"\n{Colors.BOLD}Link Validation Results{Colors.RESET}")
        print("=" * 80)

        print(f"\nTotal Links Checked: {self.result.total_links}")
        print(
            f"Broken Links: {Colors.RED if self.result.has_broken_links else Colors.GREEN}"
            f"{len(self.result.broken_links)}{Colors.RESET}"
        )

        if self.result.slow_links:
            print(
                f"{Colors.YELLOW}Slow Links (>3s): {len(self.result.slow_links)}{Colors.RESET}"
            )

        if self.result.broken_links:
            print(f"\n{Colors.BOLD}Broken Links:{Colors.RESET}\n")

            # Group by source file
            by_file: Dict[str, List[BrokenLink]] = {}
            for broken in self.result.broken_links:
                if broken.source_file not in by_file:
                    by_file[broken.source_file] = []
                by_file[broken.source_file].append(broken)

            for source_file in sorted(by_file.keys()):
                print(f"{Colors.BOLD}{source_file}{Colors.RESET}")
                for broken in by_file[source_file]:
                    print(
                        f"  Line {broken.line_number}: [{broken.link_text}]({broken.link_target})"
                    )
                    print(f"    {Colors.RED}✗{Colors.RESET} {broken.issue}")
                print()

        if self.result.slow_links:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}Slow External Links:{Colors.RESET}\n")
            for url, response_time in sorted(
                self.result.slow_links, key=lambda x: x[1], reverse=True
            )[:10]:
                print(f"  {response_time:.2f}s - {url}")

        # Final status
        print(f"\n{Colors.BOLD}Status:{Colors.RESET} ", end="")
        if self.result.has_broken_links:
            print(f"{Colors.RED}FAILED{Colors.RESET} - Broken links detected")
        else:
            print(f"{Colors.GREEN}PASSED{Colors.RESET} - All links valid")

    def generate_report(self, output_path: str = "link-validation-report.md"):
        """Generate markdown report"""
        with open(output_path, "w") as f:
            f.write("# Link Validation Report\n\n")
            f.write(f"**Generated:** {self._get_timestamp()}\n\n")

            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Links Checked:** {self.result.total_links}\n")
            f.write(f"- **Broken Links:** {len(self.result.broken_links)}\n")
            f.write(f"- **Slow Links (>3s):** {len(self.result.slow_links)}\n")
            f.write(
                f'- **Status:** {"❌ FAILED" if self.result.has_broken_links else "✅ PASSED"}\n\n'
            )

            # Broken links
            if self.result.broken_links:
                f.write("## Broken Links\n\n")

                by_file: Dict[str, List[BrokenLink]] = {}
                for broken in self.result.broken_links:
                    if broken.source_file not in by_file:
                        by_file[broken.source_file] = []
                    by_file[broken.source_file].append(broken)

                for source_file in sorted(by_file.keys()):
                    f.write(f"### {source_file}\n\n")
                    for broken in by_file[source_file]:
                        f.write(
                            f"- **Line {broken.line_number}:** `[{broken.link_text}]({broken.link_target})`\n"
                        )
                        f.write(f"  - ❌ {broken.issue}\n")
                    f.write("\n")

            # Slow links
            if self.result.slow_links:
                f.write("## Slow External Links\n\n")
                f.write("| Response Time | URL |\n")
                f.write("|---------------|-----|\n")
                for url, response_time in sorted(
                    self.result.slow_links, key=lambda x: x[1], reverse=True
                ):
                    f.write(f"| {response_time:.2f}s | {url} |\n")

        print(f"\n{Colors.GREEN}Report generated: {output_path}{Colors.RESET}")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    parser = argparse.ArgumentParser(
        description="Validate all links in documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--skip-external",
        action="store_true",
        help="Skip external URL validation (faster)",
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate markdown report"
    )
    parser.add_argument(
        "--content-dir",
        default="docs/content",
        help="Content directory to validate (default: docs/content)",
    )

    args = parser.parse_args()

    start_time = time.time()

    validator = LinkValidator(
        content_dir=args.content_dir, skip_external=args.skip_external
    )
    validator.validate_all()
    validator.print_results()

    if args.report:
        validator.generate_report()

    elapsed = time.time() - start_time
    print(f"\n{Colors.BLUE}Validation completed in {elapsed:.2f}s{Colors.RESET}")

    # Exit with appropriate code
    sys.exit(1 if validator.result.has_broken_links else 0)


if __name__ == "__main__":
    main()
