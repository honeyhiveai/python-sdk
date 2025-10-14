# Date Usage Policy - Agent OS

**Category**: AI Safety  
**Priority**: Critical  
**Enforcement**: Mandatory for all AI-generated content

---

## Problem Statement

AI assistants (LLMs) consistently make date-related errors due to knowledge cutoff dates and lack of real-time awareness. This manifests as:

1. **Wrong Dates**: Using old dates from training data (e.g., "2025-01-30" when current is "2025-10-06")
2. **Inconsistent Formats**: Mixing date formats within same document
3. **Hardcoded Values**: Manually typing dates instead of querying system
4. **Context Confusion**: Uncertain about current date during generation

These errors create confusion, unprofessional appearance, and maintenance issues.

---

## Solution: current_date Tool

Agent OS provides a `current_date` MCP tool that AI assistants MUST use when dealing with dates.

### Tool Usage

```python
# Call the MCP tool
result = await current_date()

# Primary field for all uses:
date = result["iso_date"]  # "2025-10-06"

# Other available fields:
result["iso_datetime"]       # "2025-10-06T14:30:00.123456"
result["day_of_week"]        # "Monday"
result["month"]              # "October"
result["year"]               # 2025
result["formatted"]["header"]  # "**Date**: 2025-10-06"
```

---

## Mandatory Usage Patterns

### Pattern 1: Creating Specifications

**ALWAYS call `current_date` first:**

```markdown
# ✅ Correct
1. Call current_date tool → get "2025-10-06"
2. Create directory: .agent-os/specs/2025-10-06-feature-name/
3. Add header: **Date**: 2025-10-06

# ❌ Wrong
1. Assume date is 2025-01-30
2. Create directory with wrong date
3. User has to correct manually
```

### Pattern 2: Documentation Headers

```markdown
# ✅ Correct
**Date**: 2025-10-06
**Last Updated**: 2025-10-06
**Review Date**: 2025-11-06

# ❌ Wrong
**Date**: January 30, 2025  (wrong format)
**Last Updated**: 01/30/2025  (wrong format and date)
```

### Pattern 3: Directory Naming

```bash
# ✅ Correct
.agent-os/specs/2025-10-06-api-design/
.agent-os/specs/2025-10-06-testing-framework/

# ❌ Wrong
.agent-os/specs/2025-01-30-new-feature/  (wrong date)
.agent-os/specs/oct-6-2025-feature/  (wrong format)
```

---

## Standard Date Format

**Use ISO 8601 format exclusively:**
- **Format**: `YYYY-MM-DD`
- **Example**: `2025-10-06`
- **Rationale**: Sortable, unambiguous, internationally recognized

**Never use:**
- ❌ `MM/DD/YYYY` (US format, ambiguous)
- ❌ `DD-MM-YYYY` (European format, ambiguous)
- ❌ `Month Day, Year` (verbose, hard to parse)
- ❌ `YYYY/MM/DD` (uses slashes, harder to parse in filenames)

---

## Enforcement Rules

### Rule 1: No Hardcoded Dates
**NEVER** hardcode dates in generated content. Always query `current_date` tool.

```python
# ❌ FORBIDDEN
date = "2025-01-30"  # Hardcoded!

# ✅ REQUIRED
result = await current_date()
date = result["iso_date"]
```

### Rule 2: Consistent Format
All dates in a single generation session MUST use the same format.

### Rule 3: Validate Before Use
After calling `current_date`, verify the returned date makes sense:
- Is it Monday when expected to be Monday?
- Is it October when expected to be October?

If something seems wrong, alert the user.

---

## Common Scenarios

### Scenario 1: Creating New Spec Directory

```python
# Step 1: Get current date
result = await current_date()
date = result["iso_date"]  # "2025-10-06"

# Step 2: Create directory
spec_name = "authentication-redesign"
directory = f".agent-os/specs/{date}-{spec_name}"
os.makedirs(directory)

# Step 3: Create README with date header
readme_content = f"""# Specification: {spec_name}

{result['formatted']['header']}
**Status**: Draft
**Last Updated**: {date}

## Overview
...
"""
```

### Scenario 2: Updating Existing Documentation

```python
# Get current date for "Last Updated" field
result = await current_date()
last_updated = result["iso_date"]

# Update header
content = f"""
**Created**: 2025-09-15  (preserve original)
**Last Updated**: {last_updated}  (use current)
"""
```

### Scenario 3: Planning Future Dates

```python
# Get current date
result = await current_date()
today = result["iso_date"]

# For future dates, explain the calculation
# Don't just add days blindly - be explicit
review_date = "2025-11-06"  # 30 days from 2025-10-06

content = f"""
**Created**: {today}
**Review Date**: {review_date}  (30 days from creation)
"""
```

---

## Error Prevention

### Pre-Generation Checklist
Before generating any content with dates:
- [ ] Call `current_date` tool
- [ ] Store result in variable
- [ ] Verify date makes sense
- [ ] Use ISO 8601 format
- [ ] Apply consistently

### Post-Generation Validation
After generating content with dates:
- [ ] All dates use ISO 8601 format
- [ ] All dates are correct (not from training data)
- [ ] Directory names match file headers
- [ ] Future dates have explanation

---

## Impact

Following this policy:
- ✅ **Eliminates date errors**: No more wrong dates in specs
- ✅ **Professional appearance**: Consistent, correct formatting
- ✅ **Easy maintenance**: Clear audit trail of changes
- ✅ **Better organization**: Sortable, chronological structure

---

## Related Standards

- `.cursorrules` - AI assistant operational guidelines
- `credential-file-protection.md` - Other AI safety rules
- `production-code-checklist.md` - Quality enforcement

---

## Version History

- **2025-10-06**: Initial policy created with `current_date` tool
