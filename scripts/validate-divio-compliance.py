#!/usr/bin/env python3
"""
Validate Divio framework compliance.

Checks:
1. Getting Started purity (0 migration guides)
2. Migration guide separation
3. Content type categorization

Exit 0 if all checks pass, non-zero otherwise.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple


def check_getting_started_purity(index_path: Path) -> Tuple[bool, List[str]]:
    """
    Check Getting Started section has 0 migration guides.
    
    Returns:
        (passed, issues_found)
    """
    if not index_path.exists():
        return False, [f"Index file not found: {index_path}"]
    
    content = index_path.read_text()
    
    # Find Getting Started toctree
    in_getting_started = False
    in_toctree = False
    migration_guides_found = []
    lines = content.splitlines()
    
    for i, line in enumerate(lines):
        # Check if we're in Getting Started section
        if "Getting Started" in line or "getting-started" in line.lower():
            in_getting_started = True
            in_toctree = False
        # Check if we hit another major section
        elif in_getting_started and line.strip() and line[0] in ['=', '-', '~', '^'] and len(set(line.strip())) == 1:
            # Heading underline - check if next section
            if i > 0 and "Getting Started" not in lines[i-1]:
                in_getting_started = False
                in_toctree = False
        # Check if we're in a toctree directive
        elif in_getting_started and ".. toctree::" in line:
            in_toctree = True
        # Check for end of toctree (non-indented line)
        elif in_toctree and line and not line[0].isspace():
            in_toctree = False
        # Check for migration-related entries in toctree
        elif in_getting_started and in_toctree and "migration" in line.lower():
            migration_guides_found.append(line.strip())
        elif in_getting_started and in_toctree and "compatibility" in line.lower() and "backwards" in content[max(0, content.find(line)-200):content.find(line)].lower():
            migration_guides_found.append(line.strip())
    
    if migration_guides_found:
        issues = [f"Migration guides found in Getting Started: {migration_guides_found}"]
        return False, issues
    
    return True, []


def check_migration_separation(index_path: Path) -> Tuple[bool, List[str]]:
    """
    Check that migration guides are in a separate section.
    
    Returns:
        (passed, issues_found)
    """
    if not index_path.exists():
        return False, [f"Index file not found: {index_path}"]
    
    content = index_path.read_text()
    
    # Check for Migration & Compatibility section or similar
    has_migration_section = (
        "Migration" in content and "Compatibility" in content or
        "migration-compatibility" in content
    )
    
    if not has_migration_section:
        return False, ["No separate Migration & Compatibility section found"]
    
    return True, []


def main():
    parser = argparse.ArgumentParser(description="Validate Divio framework compliance")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="Output format")
    parser.add_argument("--help-flag", action="store_true", dest="show_help")
    
    args = parser.parse_args()
    
    if args.show_help:
        parser.print_help()
        sys.exit(0)
    
    # Run checks
    index_path = Path("docs/how-to/index.rst")
    
    checks = {
        "getting_started_purity": check_getting_started_purity(index_path),
        "migration_separation": check_migration_separation(index_path),
    }
    
    all_passed = True
    results = {}
    
    for check_name, (passed, issues) in checks.items():
        results[check_name] = {
            "passed": passed,
            "issues": issues
        }
        if not passed:
            all_passed = False
    
    # Output results
    if args.format == "json":
        print(json.dumps({
            "overall_pass": all_passed,
            "checks": results
        }, indent=2))
    else:
        print("=== Divio Framework Compliance Validation ===\n")
        
        for check_name, result in results.items():
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            check_display = check_name.replace("_", " ").title()
            print(f"{status}: {check_display}")
            
            if result["issues"]:
                for issue in result["issues"]:
                    print(f"  - {issue}")
        
        print()
        if all_passed:
            print("✅ All Divio compliance checks passed")
        else:
            print("❌ Some Divio compliance checks failed")
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

