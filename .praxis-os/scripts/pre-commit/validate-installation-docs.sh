#!/usr/bin/env bash
# Validate that critical installation files exist
# Used by pre-commit hook to ensure installation integrity

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Validating installation documentation completeness..."

# Critical files that must exist
REQUIRED_FILES=(
    "installation/00-START.md"
    "installation/02-copy-files.md"
    # Note: build_rag_index.py removed - Ouroboros auto-builds indexes
    ".praxis-os/standards/development/code-quality.md"
)

missing_files=()

for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ All critical installation files present${NC}"
    exit 0
else
    echo -e "${RED}❌ Missing critical installation files:${NC}"
    for file in "${missing_files[@]}"; do
        echo -e "  ${RED}✗${NC} $file"
    done
    echo ""
    echo -e "${YELLOW}These files are required for proper prAxIs OS installation.${NC}"
    exit 1
fi

