# Phase 0.2: Check Existing Schema

## 🎯 **Objective**

Determine if a schema already exists for this provider, and if so, whether this is an update or a fresh extraction.

---

## 📋 **Tasks**

### **Task 2.1: Search for Existing Schema**

**Action**: Check if `provider_response_schemas/{provider}/` directory exists.

**How**:
1. Navigate to `provider_response_schemas/` directory
2. List all subdirectories
3. Search for provider name (exact match and variations)
4. Check for versioned schema files

**Evidence Required**:
- Directory path (if exists)
- List of existing schema files
- Latest version number

**Example - Schema EXISTS**:
```markdown
Existing Schema: YES
Location: provider_response_schemas/openai/
Files Found:
- v2025-01-30.json
- examples/basic_chat.json
- examples/tool_calls.json
- CHANGELOG.md
Latest Version: v2025-01-30
```

**Example - Schema DOES NOT EXIST**:
```markdown
Existing Schema: NO
Provider directory does not exist
Action: Creating new schema (proceed with full framework)
```

---

### **Task 2.2: Determine Mode**

**Action**: Based on Task 2.1 results, determine the appropriate mode.

**Modes**:

1. **NEW SCHEMA** (directory does not exist):
   - Full extraction required
   - Create all artifacts from scratch
   - Follow all phases 0-7

2. **UPDATE SCHEMA** (directory exists, updating for API changes):
   - Re-verify SDK versions
   - Extract new/changed fields
   - Create new version file
   - Update CHANGELOG
   - Follow phases 1-7 (skip some Phase 0 tasks)

3. **AUDIT SCHEMA** (directory exists, verifying accuracy):
   - Verify existing sources still valid
   - Validate schema against current SDK
   - Check for missing fields
   - May not create new version
   - Follow phases 1, 5, 7

**Decision Tree**:
```
Does schema directory exist?
├── NO → Mode: NEW SCHEMA
│        → Continue with Phase 0
│
└── YES → Is API version changed?
          ├── YES → Mode: UPDATE SCHEMA
          │         → Jump to Phase 1
          │
          └── NO → Mode: AUDIT SCHEMA
                    → Jump to Phase 1
```

**Output**:
```markdown
Mode: {NEW SCHEMA | UPDATE SCHEMA | AUDIT SCHEMA}
Reason: {brief explanation}
```

---

### **Task 2.3: Load Existing Context (if applicable)**

**Action**: If schema exists, load and review existing artifacts.

**How**:
1. Read latest version schema file
2. Read CHANGELOG.md
3. Read SDK_SOURCES.md (if exists)
4. Note current version and extraction date

**Evidence Required**:
- Current schema version
- Last extraction date
- Known issues or gaps (from CHANGELOG)
- SDK versions used

**Example**:
```markdown
## Existing Schema Context

Current Version: v2025-01-30
Extraction Date: 2025-01-30
SDK Versions:
- Python: v1.54.3 (commit: a1b2c3d4)
- TypeScript: v4.68.4 (commit: e5f6g7h8)

Known Gaps (from CHANGELOG):
- GPT-5 models have incomplete pricing data
- Audio response format not fully documented

Last Update Reason: Added GPT-5 models
```

**⚠️ SKIP**: If mode is NEW SCHEMA, skip this task.

---

## ✅ **Quality Gate: Schema Status**

Before proceeding to Task 3, verify:

- ✅ Existing schema status determined (exists or not)
- ✅ Mode selected (NEW, UPDATE, or AUDIT)
- ✅ If exists: context loaded and understood
- ✅ Decision documented with reasoning

---

## 📊 **Output**

Update: `provider_response_schemas/{provider}/PROGRESS.md`

**Add**:
```markdown
## Mode Determination
- **Mode**: {NEW SCHEMA | UPDATE SCHEMA | AUDIT SCHEMA}
- **Reason**: {explanation}
- **Existing Version**: {version or N/A}
- **Last Extraction**: {date or N/A}

## Context Review
{Summary of existing schema if applicable}
```

---

## 🔀 **Navigation Based on Mode**

### **If Mode = NEW SCHEMA**:
```
🎯 NEXT-MANDATORY: task-3-create-directory-structure.md
```

### **If Mode = UPDATE SCHEMA**:
```
🎯 NEXT-MANDATORY: ../1/task-1-locate-official-sdks.md
(Skip to Phase 1 - re-verify SDKs and extract updates)
```

### **If Mode = AUDIT SCHEMA**:
```
🎯 NEXT-MANDATORY: ../1/task-1-locate-official-sdks.md
(Skip to Phase 1 - verify sources and validate)
```

---

**Phase**: 0  
**Task**: 2  
**Status**: Active
