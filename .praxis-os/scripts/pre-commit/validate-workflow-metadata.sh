#!/usr/bin/env bash
# Validate that all workflows have proper metadata.json files
# Ensures workflow metadata is complete and valid

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Validating workflow metadata..."

# Find all workflow directories
workflow_dirs=$(find universal/workflows -mindepth 1 -maxdepth 1 -type d 2>/dev/null || true)

if [[ -z "$workflow_dirs" ]]; then
    echo -e "${YELLOW}⚠️  No workflows found in universal/workflows/${NC}"
    exit 0
fi

missing_metadata=()
invalid_metadata=()

for workflow_dir in $workflow_dirs; do
    workflow_name=$(basename "$workflow_dir")
    metadata_file="$workflow_dir/metadata.json"
    
    # Check if metadata.json exists
    if [[ ! -f "$metadata_file" ]]; then
        missing_metadata+=("$workflow_name")
        continue
    fi
    
    # Validate JSON syntax
    if ! python3 -m json.tool "$metadata_file" > /dev/null 2>&1; then
        invalid_metadata+=("$workflow_name: Invalid JSON syntax")
        continue
    fi
    
    # Check required fields
    required_fields=("name" "version" "phases")
    for field in "${required_fields[@]}"; do
        if ! grep -q "\"$field\"" "$metadata_file"; then
            invalid_metadata+=("$workflow_name: Missing required field '$field'")
        fi
    done
done

# Report results
has_errors=0

if [[ ${#missing_metadata[@]} -gt 0 ]]; then
    echo -e "${RED}❌ Workflows missing metadata.json:${NC}"
    for workflow in "${missing_metadata[@]}"; do
        echo -e "  ${RED}✗${NC} $workflow"
    done
    has_errors=1
fi

if [[ ${#invalid_metadata[@]} -gt 0 ]]; then
    echo -e "${RED}❌ Workflows with invalid metadata:${NC}"
    for error in "${invalid_metadata[@]}"; do
        echo -e "  ${RED}✗${NC} $error"
    done
    has_errors=1
fi

if [[ $has_errors -eq 0 ]]; then
    echo -e "${GREEN}✅ All workflow metadata valid${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}All workflows must have valid metadata.json files.${NC}"
    echo -e "${YELLOW}See: mcp_server/WORKFLOW_METADATA_GUIDE.md${NC}"
    exit 1
fi

