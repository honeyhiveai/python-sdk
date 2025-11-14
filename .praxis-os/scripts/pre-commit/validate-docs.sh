#!/usr/bin/env bash
# Validates documentation quality before commit
# Runs Divio compliance and internal link checks on changed markdown files

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Validating documentation quality...${NC}"
echo ""

# Check if docs directory exists
if [[ ! -d "docs/content" ]]; then
    echo -e "${YELLOW}⚠️  No docs/content directory found, skipping doc validation${NC}"
    exit 0
fi

# Get list of changed markdown files in docs/
CHANGED_MD_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '^docs/.*\.md$' || true)

if [[ -z "$CHANGED_MD_FILES" ]]; then
    echo -e "${GREEN}✅ No documentation files changed, skipping validation${NC}"
    exit 0
fi

echo -e "${BLUE}📄 Changed documentation files:${NC}"
echo "$CHANGED_MD_FILES" | sed 's/^/  - /'
echo ""

VALIDATION_FAILED=0

# ============================================================================
# 1. Divio Compliance Check (Warning threshold: 80%)
# ============================================================================

echo -e "${BLUE}📋 Running Divio compliance check...${NC}"

if [[ ! -f "scripts/validate-divio-compliance.py" ]]; then
    echo -e "${YELLOW}⚠️  Divio validation script not found, skipping${NC}"
else
    # Run compliance check on docs/content
    if python scripts/validate-divio-compliance.py 2>&1 | grep -q "FAIL"; then
        echo -e "${RED}❌ Divio compliance check failed${NC}"
        echo -e "${YELLOW}💡 Fix: Review compliance violations above${NC}"
        echo -e "${YELLOW}   - Ensure 'doc_type' frontmatter is present${NC}"
        echo -e "${YELLOW}   - Check content matches declared type${NC}"
        echo -e "${YELLOW}   - Run: python scripts/validate-divio-compliance.py${NC}"
        VALIDATION_FAILED=1
    else
        echo -e "${GREEN}✅ Divio compliance check passed${NC}"
    fi
fi

echo ""

# ============================================================================
# 2. Internal Link Validation
# ============================================================================

echo -e "${BLUE}🔗 Running internal link validation...${NC}"

if [[ ! -f "scripts/validate-links.py" ]]; then
    echo -e "${YELLOW}⚠️  Link validation script not found, skipping${NC}"
else
    # CRITICAL: Validate staged files, not working directory
    # Stash any unstaged docs changes, validate staged files, then restore
    # This ensures we catch broken links in what's actually being committed
    UNSTAGED_DOCS=$(git diff --name-only | grep '^docs/.*\.md$' || true)
    
    if [[ -n "$UNSTAGED_DOCS" ]]; then
        echo -e "${YELLOW}⚠️  Unstaged docs changes detected - stashing to validate staged files only${NC}"
        git stash push -q -m "pre-commit-docs-validation-$$" -- docs/ 2>/dev/null || true
        STASHED=1
    else
        STASHED=0
    fi
    
    # Run link validation (skip external for speed)
    # This now validates the staged files (what's actually being committed)
    # Add timeout to prevent hanging (30 seconds should be enough)
    LINK_OUTPUT=$(timeout 30 python scripts/validate-links.py --skip-external 2>&1 || echo "TIMEOUT: Link validation took too long")
    LINK_EXIT_CODE=$?
    
    # If timeout occurred, treat as failure
    if echo "$LINK_OUTPUT" | grep -q "TIMEOUT"; then
        LINK_EXIT_CODE=1
    fi
    
    # Restore stashed changes if we stashed them
    if [[ $STASHED -eq 1 ]]; then
        git stash pop -q 2>/dev/null || true
    fi
    
    if [[ $LINK_EXIT_CODE -ne 0 ]]; then
        echo -e "${RED}❌ Link validation failed (broken internal links found)${NC}"
        echo ""
        # Show broken link details (extract the "Broken Links:" section)
        echo -e "${YELLOW}Broken links:${NC}"
        # Extract from "Broken Links:" section to "Status:" section
        echo "$LINK_OUTPUT" | sed -n '/Broken Links:/,/Status:/p' | head -50
        echo ""
        echo -e "${YELLOW}💡 Fix:${NC}"
        echo -e "${YELLOW}   - Review broken links above for file paths and line numbers${NC}"
        echo -e "${YELLOW}   - Update broken paths to match actual file locations${NC}"
        echo -e "${YELLOW}   - Verify target files exist${NC}"
        echo -e "${YELLOW}   - Run: python scripts/validate-links.py --skip-external${NC}"
        VALIDATION_FAILED=1
    else
        echo -e "${GREEN}✅ Link validation passed${NC}"
    fi
fi

echo ""

# ============================================================================
# 3. MDX Compilation Check (Catches syntax errors before CI/CD)
# ============================================================================

echo -e "${BLUE}🔨 Running MDX compilation check...${NC}"

if [[ ! -d "docs" ]] || [[ ! -f "docs/package.json" ]]; then
    echo -e "${YELLOW}⚠️  Docusaurus project not found, skipping MDX check${NC}"
else
    cd docs
    
    # Check if node_modules exists, install if needed
    if [[ ! -d "node_modules" ]]; then
        echo -e "${YELLOW}⚠️  node_modules not found, installing dependencies...${NC}"
        npm ci > /dev/null 2>&1 || {
            echo -e "${RED}❌ Failed to install dependencies${NC}"
            cd ..
            VALIDATION_FAILED=1
            echo ""
        }
    fi
    
    if [[ $VALIDATION_FAILED -eq 0 ]]; then
        # Run build to catch MDX compilation errors
        # Capture both stdout and stderr to show errors
        # Note: Docusaurus build will fail fast on MDX errors
        BUILD_OUTPUT=$(npm run build 2>&1) || BUILD_FAILED=1
        
        if [[ "${BUILD_FAILED:-0}" == "1" ]]; then
            echo -e "${RED}❌ MDX compilation failed${NC}"
            echo ""
            echo -e "${YELLOW}Build errors:${NC}"
            # Extract and show relevant error lines (MDX errors, file paths, line numbers)
            echo "$BUILD_OUTPUT" | grep -E "(Error|ERROR|failed|Failed|MDX compilation)" | head -30
            echo ""
            echo -e "${YELLOW}💡 Common MDX issues:${NC}"
            echo -e "${YELLOW}   - '<1' interpreted as JSX tag → use 'Less than 1'${NC}"
            echo -e "${YELLOW}   - Unclosed JSX tags → check angle brackets${NC}"
            echo -e "${YELLOW}   - Invalid component names → must start with letter${NC}"
            echo ""
            echo -e "${YELLOW}💡 Fix:${NC}"
            echo -e "${YELLOW}   - Review errors above for file paths and line numbers${NC}"
            echo -e "${YELLOW}   - Run 'cd docs && npm run build' for full details${NC}"
            cd ..
            VALIDATION_FAILED=1
        else
            echo -e "${GREEN}✅ MDX compilation check passed${NC}"
            cd ..
        fi
    fi
    echo ""
fi

# ============================================================================
# 4. Optional: Full Docusaurus Build Check (for comprehensive validation)
# ============================================================================

if [[ "${DOCS_FULL_BUILD:-0}" == "1" ]]; then
    echo -e "${BLUE}🏗️  Running full Docusaurus build check...${NC}"
    
    if [[ ! -d "docs" ]] || [[ ! -f "docs/package.json" ]]; then
        echo -e "${YELLOW}⚠️  Docusaurus project not found, skipping build check${NC}"
    else
        cd docs
        if npm run build > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Full Docusaurus build passed${NC}"
            cd ..
        else
            echo -e "${RED}❌ Full Docusaurus build failed${NC}"
            echo -e "${YELLOW}💡 Fix: Run 'cd docs && npm run build' for details${NC}"
            cd ..
            VALIDATION_FAILED=1
        fi
    fi
    echo ""
fi

# ============================================================================
# Final Result
# ============================================================================

if [[ $VALIDATION_FAILED -eq 1 ]]; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Documentation validation failed${NC}"
    echo -e "${YELLOW}💡 Fix issues above or bypass with: git commit --no-verify${NC}"
    echo -e "${YELLOW}   (Not recommended - prefer fixing issues)${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
else
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ All documentation validation passed${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
fi

