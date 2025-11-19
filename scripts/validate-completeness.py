#!/usr/bin/env python3
"""
Validate all FR requirements are implemented.

Checks:
- FR-001: 4 Getting Started guides exist
- FR-002: All 7 integration guides have Compatibility sections
- FR-003: Span enrichment guide exists
- FR-007: LLM application patterns guide exists
- FR-008: Advanced production guide exists
- FR-009: Class decorators guide exists
- FR-010: SSL troubleshooting section exists
- FR-011: Testing applications guide exists
- FR-012: Advanced patterns guide exists

Exit 0 if all checks pass, non-zero otherwise.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple


# Define required files for each FR
REQUIRED_FILES = {
    "FR-001": [
        "docs/how-to/getting-started/setup-first-tracer.rst",
        "docs/how-to/getting-started/add-llm-tracing-5min.rst",
        "docs/how-to/getting-started/enable-span-enrichment.rst",
        "docs/how-to/getting-started/configure-multi-instance.rst",
    ],
    "FR-003": [
        "docs/how-to/advanced-tracing/span-enrichment.rst",
    ],
    "FR-007": [
        "docs/how-to/llm-application-patterns.rst",
    ],
    "FR-008": [
        "docs/how-to/deployment/advanced-production.rst",
    ],
    "FR-009": [
        "docs/how-to/advanced-tracing/class-decorators.rst",
    ],
    "FR-011": [
        "docs/how-to/testing-applications.rst",
    ],
    "FR-012": [
        "docs/how-to/advanced-tracing/advanced-patterns.rst",
    ],
}


def check_files_exist(check_frs: List[str] = None) -> Dict[str, Tuple[bool, List[str]]]:
    """
    Check all required files exist.
    
    Args:
        check_frs: List of specific FRs to check, or None for all
        
    Returns:
        Dict mapping FR to (passed, issues)
    """
    results = {}
    frs_to_check = check_frs if check_frs else REQUIRED_FILES.keys()
    
    for fr in frs_to_check:
        if fr not in REQUIRED_FILES:
            results[fr] = (False, [f"Unknown FR: {fr}"])
            continue
            
        files = REQUIRED_FILES[fr]
        issues = []
        all_exist = True
        
        for file_path_str in files:
            file_path = Path(file_path_str)
            if not file_path.exists():
                issues.append(f"Missing: {file_path}")
                all_exist = False
        
        results[fr] = (all_exist, issues)
    
    return results


def check_compatibility_sections() -> Tuple[bool, List[str]]:
    """
    Check FR-002: All 7 integration guides have Compatibility sections.
    
    Returns:
        (passed, issues)
    """
    providers = [
        "openai",
        "anthropic", 
        "google-ai",
        "google-adk",
        "bedrock",
        "azure-openai",
        "mcp"
    ]
    
    issues = []
    all_pass = True
    
    for provider in providers:
        guide_path = Path(f"docs/how-to/integrations/{provider}.rst")
        
        if not guide_path.exists():
            issues.append(f"Missing: {guide_path}")
            all_pass = False
            continue
        
        content = guide_path.read_text()
        
        # Check for Compatibility section
        has_compatibility = (
            "Compatibility" in content or
            "compatibility" in content.lower()
        )
        
        if not has_compatibility:
            issues.append(f"{provider}.rst missing Compatibility section")
            all_pass = False
    
    return all_pass, issues


def check_ssl_troubleshooting() -> Tuple[bool, List[str]]:
    """
    Check FR-010: SSL/TLS troubleshooting section exists.
    
    Returns:
        (passed, issues)
    """
    index_path = Path("docs/how-to/index.rst")
    
    if not index_path.exists():
        return False, ["docs/how-to/index.rst not found"]
    
    content = index_path.read_text()
    
    # Check for SSL/Network troubleshooting content
    has_ssl_section = (
        "SSL" in content or
        "Network" in content and "Issues" in content
    )
    
    if not has_ssl_section:
        return False, ["SSL/TLS troubleshooting section not found in how-to/index.rst"]
    
    return True, []


def main():
    parser = argparse.ArgumentParser(
        description="Validate completeness of all FR requirements"
    )
    parser.add_argument(
        "--check",
        nargs="+",
        help="Check specific FRs (e.g., FR-001 FR-003)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--help-flag",
        action="store_true",
        dest="show_help"
    )
    
    args = parser.parse_args()
    
    if args.show_help:
        parser.print_help()
        sys.exit(0)
    
    # Run checks
    results = {}
    
    # Check file existence for FRs
    file_results = check_files_exist(args.check)
    results.update(file_results)
    
    # Check FR-002 (compatibility sections) if not filtered
    if not args.check or "FR-002" in args.check:
        compat_passed, compat_issues = check_compatibility_sections()
        results["FR-002"] = (compat_passed, compat_issues)
    
    # Check FR-010 (SSL troubleshooting) if not filtered
    if not args.check or "FR-010" in args.check:
        ssl_passed, ssl_issues = check_ssl_troubleshooting()
        results["FR-010"] = (ssl_passed, ssl_issues)
    
    # Determine overall pass/fail
    all_passed = all(passed for passed, _ in results.values())
    
    # Output results
    if args.format == "json":
        json_results = {
            fr: {"passed": passed, "issues": issues}
            for fr, (passed, issues) in results.items()
        }
        print(json.dumps({
            "overall_pass": all_passed,
            "checks": json_results
        }, indent=2))
    else:
        print("=== Completeness Validation ===\n")
        
        for fr in sorted(results.keys()):
            passed, issues = results[fr]
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {fr}")
            
            if issues:
                for issue in issues:
                    print(f"  - {issue}")
        
        print()
        if all_passed:
            print(f"✅ All completeness checks passed ({len(results)} FRs verified)")
        else:
            failed_count = sum(1 for passed, _ in results.values() if not passed)
            print(f"❌ {failed_count}/{len(results)} completeness checks failed")
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

