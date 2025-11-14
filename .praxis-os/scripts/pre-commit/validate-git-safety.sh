#!/usr/bin/env bash
# Validate git safety rules
# Ensures no .git directory commits or destructive patterns

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Validating git safety rules..."

# Check for .git directory commits
git_dir_files=$(git diff --cached --name-only | grep "^\.git/" 2>/dev/null || true)

if [[ -n "$git_dir_files" ]]; then
    echo -e "${RED}❌ GIT SAFETY VIOLATION: Attempting to commit .git directory${NC}"
    echo ""
    echo "$git_dir_files"
    echo ""
    echo -e "${YELLOW}The .git directory should NEVER be committed.${NC}"
    echo -e "${YELLOW}This is a critical safety violation.${NC}"
    exit 1
fi

# Check for destructive git command patterns in code
staged_py_files=$(git diff --cached --name-only --diff-filter=AM | grep "\.py$" || true)

violations=()

if [[ -n "$staged_py_files" ]]; then
    for file in $staged_py_files; do
        # Check for dangerous git operations
        if git diff --cached "$file" | grep -qE "(git.*push.*--force|git.*reset.*--hard|git.*clean.*-fd)"; then
            violations+=("$file: Contains dangerous git operation")
        fi
    done
fi

if [[ ${#violations[@]} -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  Warning: Dangerous git patterns detected:${NC}"
    for violation in "${violations[@]}"; do
        echo -e "  ${YELLOW}!${NC} $violation"
    done
    echo ""
    echo -e "${YELLOW}Review these patterns carefully before committing.${NC}"
    # Warning only, don't fail
fi

echo -e "${GREEN}✅ Git safety checks passed${NC}"
exit 0

