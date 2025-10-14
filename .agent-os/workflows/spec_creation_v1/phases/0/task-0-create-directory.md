# Task 0: Create Spec Directory

**Phase:** 0 (Supporting Documents Integration)  
**Purpose:** Create properly-named spec directory following project convention  
**Estimated Time:** 1 minute

---

## 🎯 Objective

Create the spec directory with the correct naming convention: `YYYY-MM-DD-descriptive-name`. This ensures specs are chronologically sorted and discoverable.

---

## Directory Naming Convention

🚨 **MANDATORY FORMAT:** `YYYY-MM-DD-descriptive-name`

**Rules:**
- Date MUST be ISO 8601 format (YYYY-MM-DD) as PREFIX
- Date MUST be current date (use `current_date` tool if needed)
- Descriptive name MUST be kebab-case (lowercase, hyphen-separated)
- Descriptive name SHOULD be 2-5 words max
- Descriptive name MUST match the feature/project scope

**Examples:**
- ✅ `2025-10-13-thread-safety-fixes`
- ✅ `2025-10-07-dynamic-workflow-session-refactor`
- ✅ `2025-10-05-persona-system`
- ❌ `thread-safety-fixes-2025-10-13` (date as suffix)
- ❌ `thread_safety_fixes` (no date)
- ❌ `2025-10-13-ThreadSafetyFixes` (not kebab-case)

---

## Steps

### Step 1: Determine Spec Name

From the workflow options and project context, determine the descriptive name:

```bash
# Extract from target_file or description
# Examples:
# - "thread safety fixes" → "thread-safety-fixes"
# - "persona system" → "persona-system"
# - "RAG optimization" → "rag-optimization"
```

📊 **COUNT-AND-DOCUMENT:** Descriptive name determined
- **Descriptive Name:** {descriptive-name}
- **Rationale:** {why this name matches the scope}

### Step 2: Get Current Date

Use the `current_date` tool to ensure correct date:

```python
# AI should call: mcp_agent-os-rag_current_date()
# Returns: {"date": "YYYY-MM-DD", ...}
```

📊 **COUNT-AND-DOCUMENT:** Current date retrieved
- **Date:** {YYYY-MM-DD}

### Step 3: Construct SPEC_DIR

Combine date and descriptive name:

```bash
SPEC_DIR="{YYYY-MM-DD}-{descriptive-name}"
# Example: 2025-10-13-thread-safety-fixes
```

### Step 4: Validate Format

Before creating, validate the format:

```bash
# Check format: YYYY-MM-DD-kebab-case
if [[ $SPEC_DIR =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9-]+$ ]]; then
    echo "✅ Format valid: $SPEC_DIR"
else
    echo "❌ Format invalid: $SPEC_DIR"
    exit 1
fi
```

### Step 5: Create Directory

```bash
mkdir -p .agent-os/specs/${SPEC_DIR}
```

📊 **COUNT-AND-DOCUMENT:** Directory created
- **Directory:** `.agent-os/specs/${SPEC_DIR}`
- **Format:** YYYY-MM-DD-descriptive-name ✅
- **Date:** {current_date}
- **Descriptor:** {descriptive-name}

### Step 6: Store SPEC_DIR for Later Tasks

This SPEC_DIR value will be used in ALL subsequent tasks:

```bash
echo "SPEC_DIR=${SPEC_DIR}" > .agent-os/specs/.current-spec
echo "Created: $(date)" >> .agent-os/specs/.current-spec
```

📊 **COUNT-AND-DOCUMENT:** SPEC_DIR exported
- **Value:** `${SPEC_DIR}`
- **Stored:** `.agent-os/specs/.current-spec`

---

## Validation

🛑 VALIDATE: Directory naming

- [ ] Directory name starts with `YYYY-MM-DD-` format ✅/❌
- [ ] Date matches current date ✅/❌
- [ ] Descriptive name is kebab-case (lowercase, hyphens) ✅/❌
- [ ] Descriptive name is 2-5 words ✅/❌
- [ ] Directory exists at `.agent-os/specs/${SPEC_DIR}` ✅/❌
- [ ] SPEC_DIR exported to `.current-spec` ✅/❌

---

## Common Issues

### Issue 1: Date in Wrong Position

❌ **Wrong:** `thread-safety-fixes-2025-10-13`  
✅ **Correct:** `2025-10-13-thread-safety-fixes`

**Fix:** Date MUST be prefix, not suffix.

### Issue 2: Non-Kebab-Case

❌ **Wrong:** `2025-10-13-Thread_Safety_Fixes`  
✅ **Correct:** `2025-10-13-thread-safety-fixes`

**Fix:** Use lowercase and hyphens only.

### Issue 3: Wrong Date

❌ **Wrong:** Using date from supporting doc filename  
✅ **Correct:** Use current date from `current_date` tool

**Fix:** Always call `current_date` tool, don't infer from other sources.

---

## Next Step

🎯 **NEXT-MANDATORY:** [task-1-copy-documents.md](task-1-copy-documents.md)

The SPEC_DIR is now established and will be used consistently throughout all phases.

