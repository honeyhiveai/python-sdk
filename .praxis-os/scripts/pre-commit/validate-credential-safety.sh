#!/usr/bin/env bash
# Validate credential file safety
# Ensures no modifications to credential files (.env, etc)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Validating credential file safety..."

# Credential file patterns (read-only files)
CREDENTIAL_PATTERNS=(
    "\.env$"
    "\.env\..*"
    "credentials\.json$"
    "\.credentials"
    "secrets\..*"
    "\.secrets"
    "api[-_]?keys\..*"
)

# Check staged files
staged_files=$(git diff --cached --name-only --diff-filter=AM 2>/dev/null || true)

if [[ -z "$staged_files" ]]; then
    echo -e "${GREEN}✅ No staged files to check${NC}"
    exit 0
fi

violations=()

for file in $staged_files; do
    for pattern in "${CREDENTIAL_PATTERNS[@]}"; do
        if echo "$file" | grep -qE "$pattern"; then
            violations+=("$file")
            break
        fi
    done
done

if [[ ${#violations[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ No credential files modified${NC}"
    exit 0
else
    echo -e "${RED}❌ CREDENTIAL FILE SAFETY VIOLATION${NC}"
    echo ""
    echo -e "${RED}Attempting to modify credential files:${NC}"
    for file in "${violations[@]}"; do
        echo -e "  ${RED}✗${NC} $file"
    done
    echo ""
    echo -e "${YELLOW}Credential files are READ-ONLY.${NC}"
    echo -e "${YELLOW}They contain irreplaceable secrets and must never be modified by AI.${NC}"
    echo -e "${YELLOW}To update credentials, edit manually and do NOT commit.${NC}"
    exit 1
fi

