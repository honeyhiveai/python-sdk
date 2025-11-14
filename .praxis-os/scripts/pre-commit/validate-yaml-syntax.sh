#!/usr/bin/env bash
# Validate YAML file syntax using yamllint
# Ensures all YAML files are properly formatted

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Validating YAML syntax..."

# Check if yamllint is installed
if ! command -v yamllint &> /dev/null; then
    echo -e "${YELLOW}⚠️  yamllint not installed, skipping YAML validation${NC}"
    echo -e "${YELLOW}Install with: pip install yamllint${NC}"
    exit 0
fi

# Find all YAML files
yaml_files=$(find . -name "*.yaml" -o -name "*.yml" | grep -v ".tox" | grep -v "node_modules" | grep -v ".venv" || true)

if [[ -z "$yaml_files" ]]; then
    echo -e "${YELLOW}⚠️  No YAML files found${NC}"
    exit 0
fi

# Run yamllint on all files
if yamllint $yaml_files 2>&1; then
    echo -e "${GREEN}✅ All YAML files valid${NC}"
    exit 0
else
    echo -e "${RED}❌ YAML validation failed${NC}"
    echo ""
    echo -e "${YELLOW}Fix YAML errors above before committing.${NC}"
    exit 1
fi

