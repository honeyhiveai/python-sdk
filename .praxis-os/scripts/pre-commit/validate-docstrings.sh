#!/usr/bin/env bash
# Validate that new Python functions have docstrings
# Production code checklist requirement

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Validating docstring presence (production code requirement)..."

# Only check Python files in mcp_server/ and scripts/
staged_py_files=$(git diff --cached --name-only --diff-filter=AM | grep -E "^(mcp_server|scripts)/.*\.py$" || true)

if [[ -z "$staged_py_files" ]]; then
    echo -e "${GREEN}✅ No Python files to check${NC}"
    exit 0
fi

# This is a basic check - we look for new function definitions without docstrings
# Full validation is done by pylint
violations=()

for file in $staged_py_files; do
    # Get newly added/modified functions
    if git show ":$file" >/dev/null 2>&1; then
        # File exists in repo, check diff
        new_functions=$(git diff --cached -U0 "$file" | grep -E "^\+\s*def " | grep -v "^\+\s*#" || true)
        
        if [[ -n "$new_functions" ]]; then
            # Check if these functions have docstrings
            # This is a simple heuristic - full check is in pylint
            content=$(git show ":$file")
            while read -r func_line; do
                func_name=$(echo "$func_line" | sed -E 's/^\+\s*def\s+([a-zA-Z0-9_]+).*/\1/')
                if ! echo "$content" | grep -A3 "def $func_name" | grep -q '"""'; then
                    violations+=("$file: Function $func_name may be missing docstring")
                fi
            done <<< "$new_functions"
        fi
    fi
done

if [[ ${#violations[@]} -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  Possible missing docstrings (verify with pylint):${NC}"
    for violation in "${violations[@]}"; do
        echo -e "  ${YELLOW}!${NC} $violation"
    done
    echo ""
    echo -e "${YELLOW}Production code requires comprehensive docstrings.${NC}"
    echo -e "${YELLOW}Run: tox -e lint to verify compliance.${NC}"
    # Warning only - pylint will enforce
fi

echo -e "${GREEN}✅ Docstring validation complete (full check in pylint)${NC}"
exit 0

