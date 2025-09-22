#!/usr/bin/env python3
"""
README Hierarchy Validation Script

This script validates the Agent OS README hierarchy to detect drift and ensure
consistency across all levels.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple


def find_readme_files(base_path: str) -> List[Path]:
    """Find all README.md files in the Agent OS directory."""
    agent_os_path = Path(base_path) / ".agent-os"
    readme_files = []

    for readme_path in agent_os_path.rglob("README.md"):
        readme_files.append(readme_path)

    return sorted(readme_files)


def extract_internal_links(content: str) -> Set[str]:
    """Extract internal markdown links from README content."""
    # Pattern to match markdown links: [text](path)
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    links = set()

    for match in re.finditer(link_pattern, content):
        link_path = match.group(2)
        # Only include relative paths (internal links)
        if not link_path.startswith(("http://", "https://", "mailto:")):
            links.add(link_path)

    return links


def validate_links(readme_path: Path, content: str, base_path: str) -> List[str]:
    """Validate that internal links in README actually exist."""
    errors = []
    links = extract_internal_links(content)

    for link in links:
        # Skip pure anchor links (same page)
        if link.startswith("#"):
            continue

        # Handle links with anchors (file.md#anchor)
        if "#" in link:
            file_part = link.split("#")[0]
        else:
            file_part = link

        # Resolve relative path
        if file_part.startswith("./"):
            file_part = file_part[2:]

        # Build full path
        link_path = readme_path.parent / file_part

        # Check if file exists
        if not link_path.exists():
            errors.append(
                f"Broken link in {readme_path.relative_to(Path(base_path))}: {link}"
            )

    return errors


def extract_quality_targets(content: str) -> Dict[str, str]:
    """Extract quality targets using simple, reliable string operations."""
    targets = {}

    # Define the canonical quality targets we expect
    canonical_targets = {
        "pass_rate": "100",  # 100% pass rate
        "coverage": "90",  # 90%+ coverage for unit tests
        "pylint": "10.0",  # 10.0/10 Pylint score
        "mypy": "0",  # 0 MyPy errors
    }

    # Look for specific, well-defined quality target statements
    content_lower = content.lower()

    # Look for explicit quality target sections
    if "quality targets" in content_lower:
        # Find the quality targets section
        lines = content.split("\n")
        in_quality_section = False

        for line in lines:
            line_lower = line.lower().strip()

            # Start of quality targets section
            if "quality targets" in line_lower:
                in_quality_section = True
                continue

            # End of section (next major heading)
            if (
                in_quality_section
                and line.startswith("#")
                and "quality" not in line_lower
            ):
                break

            if in_quality_section:
                # Look for specific patterns in quality target sections
                if "100%" in line and "pass" in line_lower:
                    targets["pass_rate"] = "100"

                if (
                    "90%" in line
                    and "coverage" in line_lower
                    and "pass" not in line_lower
                ):
                    targets["coverage"] = "90"

                if "10.0/10" in line and "pylint" in line_lower:
                    targets["pylint"] = "10.0"

                if "0" in line and "mypy" in line_lower and "error" in line_lower:
                    targets["mypy"] = "0"

    # If no quality targets section found, return canonical targets
    # This avoids false positives from random mentions in text
    if not targets:
        return canonical_targets

    return targets


def check_quality_consistency(readme_files: List[Path], base_path: str) -> List[str]:
    """Check that quality targets are consistent across READMEs."""
    errors = []
    all_targets = {}

    for readme_path in readme_files:
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
                targets = extract_quality_targets(content)
                if targets:
                    all_targets[readme_path] = targets
        except Exception as e:
            errors.append(f"Error reading {readme_path}: {e}")

    # Check for inconsistencies
    if all_targets:
        # Get reference targets from the deepest level (most accurate)
        reference_targets = None
        deepest_path = None
        max_depth = 0

        for path, targets in all_targets.items():
            depth = len(path.parts)
            if depth > max_depth:
                max_depth = depth
                deepest_path = path
                reference_targets = targets

        # Compare all other targets to reference
        if reference_targets:
            for path, targets in all_targets.items():
                if path != deepest_path:
                    for target_type, value in reference_targets.items():
                        if target_type in targets and targets[target_type] != value:
                            rel_path = path.relative_to(Path(base_path))
                            errors.append(
                                f"Quality target inconsistency in {rel_path}: "
                                f"{target_type} is {targets[target_type]} but should be {value}"
                            )

    return errors


def check_framework_references(readme_files: List[Path], base_path: str) -> List[str]:
    """Check that framework references are consistent and point to existing files."""
    errors = []

    # Key frameworks that should be referenced
    key_frameworks = [
        "test generation framework",
        "production code framework",
        "test generation hub",
        "production code hub",
    ]

    for readme_path in readme_files:
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read().lower()

                # Check if this is a high-level README that should reference frameworks
                rel_path = readme_path.relative_to(Path(base_path))
                path_parts = len(rel_path.parts)

                # Top 3 levels should reference key frameworks
                if path_parts <= 3:
                    for framework in key_frameworks:
                        if framework in content:
                            # Found framework reference - this is good
                            break
                    else:
                        # No framework references found in high-level README
                        if (
                            "test" in content
                            or "code" in content
                            or "generation" in content
                        ):
                            errors.append(
                                f"High-level README {rel_path} mentions code/test generation "
                                f"but doesn't reference key frameworks"
                            )
        except Exception as e:
            errors.append(f"Error reading {readme_path}: {e}")

    return errors


def validate_cursorrules(base_path: str) -> List[str]:
    """Validate .cursorrules file for Agent OS integration and link consistency."""
    errors = []
    cursorrules_path = Path(base_path) / ".cursorrules"

    if not cursorrules_path.exists():
        errors.append("Missing .cursorrules file - required for Agent OS integration")
        return errors

    try:
        with open(cursorrules_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for required Agent OS references
        required_references = [
            "Agent OS",
            ".agent-os/standards/ai-assistant/compliance-checking.md",
            ".agent-os/standards/ai-assistant/code-generation/tests/README.md",
            ".agent-os/standards/ai-assistant/code-generation/production/README.md",
        ]

        for reference in required_references:
            if reference not in content:
                errors.append(f".cursorrules missing required reference: {reference}")

        # Validate internal links in .cursorrules
        links = extract_internal_links(content)
        for link in links:
            # Skip anchor links
            if link.startswith("#"):
                continue

            # Build full path (links in .cursorrules are relative to project root)
            if link.startswith("/"):
                link = link[1:]  # Remove leading slash
            elif link.startswith("./"):
                link = link[2:]  # Remove ./

            link_path = Path(base_path) / link

            # Check if file exists
            if not link_path.exists():
                errors.append(f"Broken link in .cursorrules: {link}")

        # Check for new modular framework reference
        if "v2/" not in content and "modular framework" not in content.lower():
            errors.append(
                ".cursorrules should reference new modular framework (v2/) for optimized AI consumption"
            )

    except Exception as e:
        errors.append(f"Error reading .cursorrules: {e}")

    return errors


def main():
    """Main validation function."""
    base_path = os.getcwd()

    print("🔍 Agent OS README Hierarchy Validation")
    print("=" * 50)

    # Find all README files
    readme_files = find_readme_files(base_path)
    print(f"📋 Found {len(readme_files)} README files")

    all_errors = []

    # Validate links
    print("\n🔗 Validating internal links...")
    for readme_path in readme_files:
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
                errors = validate_links(readme_path, content, base_path)
                all_errors.extend(errors)
        except Exception as e:
            all_errors.append(f"Error reading {readme_path}: {e}")

    # Check quality target consistency
    print("🎯 Checking quality target consistency...")
    quality_errors = check_quality_consistency(readme_files, base_path)
    all_errors.extend(quality_errors)

    # Check framework references
    print("📚 Checking framework references...")
    framework_errors = check_framework_references(readme_files, base_path)
    all_errors.extend(framework_errors)

    # Validate .cursorrules
    print("⚙️ Validating .cursorrules integration...")
    cursorrules_errors = validate_cursorrules(base_path)
    all_errors.extend(cursorrules_errors)

    # Report results
    print("\n" + "=" * 50)
    if all_errors:
        print(f"❌ Found {len(all_errors)} issues:")
        for error in all_errors:
            print(f"  • {error}")
        return 1
    else:
        print("✅ All validations passed! README hierarchy is consistent.")
        return 0


if __name__ == "__main__":
    exit(main())
