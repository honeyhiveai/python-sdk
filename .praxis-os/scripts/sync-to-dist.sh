#!/bin/bash
#
# sync-to-dist.sh: Sync local dev install to dist/ build artifacts
#
# Usage:
#   ./scripts/sync-to-dist.sh          # Dry-run (show what will be synced)
#   ./scripts/sync-to-dist.sh --sync   # Actually sync files
#
# What gets synced:
#   ✅ .praxis-os/ouroboros/ → dist/ouroboros/
#   ✅ .praxis-os/standards/universal/ → dist/universal/standards/
#   ✅ .praxis-os/workflows/ → dist/universal/workflows/
#   ❌ __pycache__, *.pyc (excluded)
#   ❌ state/, .cache/ (runtime files, excluded)
#
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

LOCAL_INSTALL="$PROJECT_ROOT/.praxis-os"
DIST_DIR="$PROJECT_ROOT/dist"

# Check mode
DRY_RUN_FLAG="-n"
if [[ "${1:-}" == "--sync" ]]; then
    DRY_RUN_FLAG=""
fi

# Common rsync options
RSYNC_OPTS=(
    -av
    --delete
    --exclude='__pycache__/'
    --exclude='*.pyc'
    --exclude='state/'
    --exclude='.cache/'
    --exclude='registry/'
)

# Header
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
if [[ -n "$DRY_RUN_FLAG" ]]; then
    echo -e "${BLUE}  Sync Preview (Dry-Run)${NC}"
else
    echo -e "${BLUE}  Syncing Local Install → dist/${NC}"
fi
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Validate paths
if [[ ! -d "$LOCAL_INSTALL" ]]; then
    echo -e "${RED}❌ Local install not found: $LOCAL_INSTALL${NC}"
    exit 1
fi

if [[ ! -d "$DIST_DIR" ]]; then
    echo -e "${RED}❌ Dist directory not found: $DIST_DIR${NC}"
    exit 1
fi

# 1. Sync Ouroboros Code
echo -e "${BLUE}━━━ 1. Ouroboros Code ━━━${NC}"
rsync "${RSYNC_OPTS[@]}" $DRY_RUN_FLAG "$LOCAL_INSTALL/ouroboros/" "$DIST_DIR/ouroboros/"
echo ""

# 2. Sync Universal Standards
echo -e "${BLUE}━━━ 2. Universal Standards ━━━${NC}"
rsync "${RSYNC_OPTS[@]}" $DRY_RUN_FLAG "$LOCAL_INSTALL/standards/universal/" "$DIST_DIR/universal/standards/"
echo ""

# 3. Sync Workflows
echo -e "${BLUE}━━━ 3. Workflows ━━━${NC}"
rsync "${RSYNC_OPTS[@]}" $DRY_RUN_FLAG "$LOCAL_INSTALL/workflows/" "$DIST_DIR/universal/workflows/"
echo ""

# Summary
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
if [[ -n "$DRY_RUN_FLAG" ]]; then
    echo -e "${YELLOW}📋 DRY-RUN COMPLETE${NC}"
    echo ""
    echo -e "  No files were modified. To actually sync, run:"
    echo -e "    ${GREEN}./scripts/sync-to-dist.sh --sync${NC}"
else
    echo -e "${GREEN}✅ SYNC COMPLETE${NC}"
    echo ""
    echo -e "  All files synced successfully!"
fi
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
