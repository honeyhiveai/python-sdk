# Task 3: Validate All Links

**Phase**: 4 - Semantic Validation  
**Purpose**: Validate all links (references resolve)  
**Depends On**: Task 2  
**Feeds Into**: Task 4

---

## Objective

Validate all links (references resolve)

---

## Context

📊 **CONTEXT**: Broken links degrade standard quality and agent trust. Link validation ensures all references are accessible.

---

## Instructions

### Step 1: Extract all markdown links

Extract all markdown links

### Step 2: For internal links

check file exists

### Step 3: For external URLs

perform DNS check

### Step 4: Skip anchor links in v1.0

Skip anchor links in v1.0

### Step 5: Document broken links

Document broken links

---

## Examples

### Example 1: Link validation passing

```
[Example content]
```

### Example 2: Link validation with broken links

```
[Example content]
```

---

## Expected Output

**Variables to Capture**:
- `validate_all_links_complete`: Boolean

---

## Quality Checks

✅ All links validated  
✅ Internal file links resolve  
✅ External URLs have valid DNS  
✅ No broken links found  

---

## Navigation

🎯 **NEXT-MANDATORY**: task-4-check-no-duplication.md

↩️ **RETURN-TO**: phase.md

