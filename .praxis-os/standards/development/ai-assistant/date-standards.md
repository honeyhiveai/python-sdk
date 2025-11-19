# Date and Timestamp Standards - HoneyHive Python SDK

**🚨 CRITICAL ISSUE**: AI Assistants consistently make date errors that create confusion and misaligned documentation.

**🎯 MISSION: Eliminate date-related errors through mandatory validation protocols**

## The Date Error Problem

### Common AI Assistant Date Failures

**Pattern 1: Using Random Past Dates**
```bash
# ❌ WRONG: AI creates spec in September using January date
mkdir .agent-os/specs/2025-01-30-new-spec  # Created in September!

# ✅ CORRECT: Always use current system date
CURRENT_DATE=$(date +"%Y-%m-%d")
mkdir ".agent-os/specs/${CURRENT_DATE}-new-spec"
```

**Pattern 2: Hardcoded Dates in Content**
```markdown
❌ WRONG:
**Date**: 2025-01-30  <!-- Hardcoded wrong date -->

✅ CORRECT:
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "**Date**: $CURRENT_DATE" >> spec.md
```

**Pattern 3: Inconsistent Date Formats**
```bash
❌ WRONG:
- January 30, 2025
- 30-01-2025  
- 1/30/2025

✅ CORRECT:
- 2025-09-15 (always ISO 8601)
```

## Mandatory Date Usage Protocol

### ALWAYS Use System Date Command

**REQUIRED: Get current date before ANY date-related work:**

```bash
# MANDATORY: Execute this before creating dated content
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Today is: $CURRENT_DATE"

# Use this variable for all date references
echo "Creating spec for date: $CURRENT_DATE"
```

### Date Format Standards

**Standard Format**: `YYYY-MM-DD` (ISO 8601)
- ✅ **Correct**: `2025-09-15`
- ❌ **Wrong**: `2025-01-30` (when today is 2025-09-15)
- ❌ **Wrong**: `09/15/2025`, `Sep 15, 2025`, `15-9-2025`

### AI Assistant Date Requirements

#### For New Specifications
```bash
# 1. Get current date
CURRENT_DATE=$(date +"%Y-%m-%d")

# 2. Create directory with current date
mkdir -p ".agent-os/specs/${CURRENT_DATE}-spec-name"

# 3. Use date in file headers
echo "**Date**: $CURRENT_DATE" > spec-file.md
```

#### For File Naming
- **Directories**: `.agent-os/specs/YYYY-MM-DD-spec-name/`
- **Files**: `YYYY-MM-DD-feature-name.md`
- **Logs**: `build-YYYY-MM-DD.log`
- **Releases**: `v1.2.3-YYYY-MM-DD`

#### For Documentation Headers
```markdown
# Specification Title

**Date**: 2025-09-15
**Status**: Active
**Last Updated**: 2025-09-15
**Review Date**: 2025-10-15
```

## Automated Date Injection

### AI Assistant Template

```bash
#!/bin/bash
# Date-aware specification creation template

# Get current date
CURRENT_DATE=$(date +"%Y-%m-%d")
SPEC_NAME="$1"  # First argument is spec name

# Create directory
SPEC_DIR=".agent-os/specs/${CURRENT_DATE}-${SPEC_NAME}"
mkdir -p "$SPEC_DIR"

# Create README with correct date
cat > "$SPEC_DIR/README.md" << EOF
# Specification: $SPEC_NAME

**Date**: $CURRENT_DATE
**Status**: Draft
**Last Updated**: $CURRENT_DATE

## Overview
[Specification content here]
EOF

echo "Created specification: $SPEC_DIR"
echo "Date used: $CURRENT_DATE"
```

### Directory Naming Protocol

**For new specifications:**
```bash
# Template
.agent-os/specs/YYYY-MM-DD-specification-name/

# Example (if today is 2025-09-15)
.agent-os/specs/2025-09-15-new-feature-spec/
.agent-os/specs/2025-09-15-ai-quality-framework/
.agent-os/specs/2025-09-15-testing-standards/
```

**NEVER use old or random dates in new directories!**

## Date Validation Checklist

### Before Creating ANY Dated Content

1. **Get Current Date**: `date +"%Y-%m-%d"`
2. **Verify Output**: Confirm the date makes sense
3. **Use Variable**: Store in variable for consistency
4. **Validate Creation**: Check directory/file names match current date
5. **Review Headers**: Ensure all date headers use current date

### Validation Commands

```bash
# Verify current date before proceeding
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Working with date: $CURRENT_DATE"

# Validate new spec directories use current date
NEW_DIRS=$(find .agent-os/specs/ -name "*${CURRENT_DATE}*" -type d)
echo "Today's specs: $NEW_DIRS"

# Check for incorrectly dated directories
WRONG_DATES=$(find .agent-os/specs/ -name "2025-*" -type d | grep -v "$CURRENT_DATE")
if [ -n "$WRONG_DATES" ]; then
    echo "WARNING: Found specs with wrong dates: $WRONG_DATES"
fi
```

## Date Review and Maintenance

### Weekly Reviews
- **Audit existing specs**: Check for date inconsistencies
- **Update "Last Updated"**: Refresh modified specifications
- **Archive old specs**: Move outdated specs to archive directory

### Monthly Reviews
- **Validate date patterns**: Ensure consistency across all files
- **Update review dates**: Extend review cycles for stable specs
- **Clean up directories**: Remove any incorrectly dated directories

## Emergency Date Correction Protocol

### If Wrong Dates Are Discovered

1. **Stop all work**: Halt current development
2. **Identify scope**: Find all affected files/directories
3. **Create fix plan**: Plan correction strategy
4. **Execute corrections**: Rename directories, update headers
5. **Validate fixes**: Ensure all dates are now correct
6. **Document lessons**: Update this protocol if needed

### Correction Commands

```bash
# Find all incorrectly dated specs
CURRENT_DATE=$(date +"%Y-%m-%d")
find .agent-os/specs/ -name "2025-*" -type d | grep -v "$CURRENT_DATE"

# Rename incorrectly dated directory (example)
OLD_DIR=".agent-os/specs/2025-01-30-wrong-spec"
NEW_DIR=".agent-os/specs/${CURRENT_DATE}-corrected-spec"
if [ -d "$OLD_DIR" ]; then
    mv "$OLD_DIR" "$NEW_DIR"
    echo "Corrected: $OLD_DIR -> $NEW_DIR"
fi

# Update date headers in files
find .agent-os/specs/ -name "*.md" -exec sed -i "s/\*\*Date\*\*: 2025-01-30/**Date**: $CURRENT_DATE/g" {} \;
```

## Enforcement Mechanisms

### Pre-commit Hooks

```bash
# Add to pre-commit validation
check_dates() {
    # Validate new spec directories use current date
    CURRENT_DATE=$(date +"%Y-%m-%d")
    
    # Check for directories created today
    NEW_DIRS=$(git diff --cached --name-only | grep "\.agent-os/specs/" | head -1)
    if [[ $NEW_DIRS == *"specs/"* ]] && [[ $NEW_DIRS != *"$CURRENT_DATE"* ]]; then
        echo "ERROR: New spec directory must use current date: $CURRENT_DATE"
        echo "Found: $NEW_DIRS"
        exit 1
    fi
}
```

### CI/CD Validation

```yaml
# GitHub Actions date validation
- name: Validate Specification Dates
  run: |
    CURRENT_DATE=$(date +"%Y-%m-%d")
    # Check for any new specs with wrong dates
    NEW_SPECS=$(git diff --name-only HEAD~1 HEAD | grep "\.agent-os/specs/")
    for spec in $NEW_SPECS; do
        if [[ $spec == *"specs/"* ]] && [[ $spec != *"$CURRENT_DATE"* ]]; then
            echo "ERROR: Specification uses wrong date: $spec"
            echo "Expected date: $CURRENT_DATE"
            exit 1
        fi
    done
```

## Date Quality Metrics

### Track These Metrics to Prevent Date Errors

- **Specification Date Accuracy**: % of specs with correct creation dates
- **Directory Naming Consistency**: % of directories following date standards
- **Header Date Validity**: % of files with accurate date headers
- **Review Date Compliance**: % of specs with up-to-date review dates

### Monitoring Commands

```bash
# Check date consistency across specs
CURRENT_DATE=$(date +"%Y-%m-%d")

# Count specs created today
TODAY_SPECS=$(find .agent-os/specs/ -name "*${CURRENT_DATE}*" -type d | wc -l)
echo "Specs created today: $TODAY_SPECS"

# Count specs with wrong dates (created in last 7 days but not today)
WEEK_AGO=$(date -d '7 days ago' +"%Y-%m-%d")
RECENT_WRONG=$(find .agent-os/specs/ -name "2025-*" -type d -newer .agent-os/specs/ | grep -v "$CURRENT_DATE" | wc -l)
echo "Recent specs with wrong dates: $RECENT_WRONG"

# Accuracy percentage
TOTAL_RECENT=$(find .agent-os/specs/ -name "2025-*" -type d -newer .agent-os/specs/ | wc -l)
if [ $TOTAL_RECENT -gt 0 ]; then
    ACCURACY=$((($TODAY_SPECS * 100) / $TOTAL_RECENT))
    echo "Date accuracy: $ACCURACY%"
fi
```

## AI Assistant Validation Protocol

### Before ANY Date-Related Work

```bash
# MANDATORY: AI assistants must run this first
echo "=== DATE VALIDATION PROTOCOL ==="
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Current date: $CURRENT_DATE"
echo "Day of week: $(date +"%A")"
echo "Month: $(date +"%B %Y")"
echo "Timestamp: $(date)"
echo "================================"

# Validate date makes sense
if [[ $CURRENT_DATE =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "✅ Date format valid: $CURRENT_DATE"
else
    echo "❌ Date format invalid: $CURRENT_DATE"
    exit 1
fi
```

### During Specification Creation

```bash
# Use this template for all spec creation
create_spec() {
    local SPEC_NAME="$1"
    local CURRENT_DATE=$(date +"%Y-%m-%d")
    
    if [ -z "$SPEC_NAME" ]; then
        echo "ERROR: Spec name required"
        return 1
    fi
    
    local SPEC_DIR=".agent-os/specs/${CURRENT_DATE}-${SPEC_NAME}"
    
    echo "Creating spec: $SPEC_NAME"
    echo "Date: $CURRENT_DATE"
    echo "Directory: $SPEC_DIR"
    
    mkdir -p "$SPEC_DIR"
    
    # Create files with correct dates
    cat > "$SPEC_DIR/srd.md" << EOF
# $SPEC_NAME - Spec Requirements Document

**Date**: $CURRENT_DATE
**Status**: Draft
**Priority**: Medium
EOF
    
    echo "✅ Spec created successfully"
}
```

## References

- **[AI Assistant Quality Framework](quality-framework.md)** - Overall quality requirements
- **[Commit Protocols](commit-protocols.md)** - Date usage in commit messages
- **[Development Process](development-process.md)** - Date validation in development workflow

---

**📝 Next Steps**: Review [Commit Protocols](commit-protocols.md) for proper commit message formatting with dates.
