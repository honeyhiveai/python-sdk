# Task 1: Copy or Reference Documents

**Phase:** 0 (Supporting Documents Integration)  
**Purpose:** Make supporting documents accessible in spec directory  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Copy provided documents to `supporting-docs/` directory or create reference links, depending on embed mode. This ensures all supporting materials are accessible and version-controlled with the spec.

---

## Prerequisites

🛑 EXECUTE-NOW: Verify supporting docs provided

You provided these documents in workflow options:
- `supporting_docs`: [list of file paths]
- `embed_supporting_docs`: [true/false]

If `embed_supporting_docs` is `true`, documents will be copied into spec directory.  
If `false`, references will be created instead.

---

## Steps

### Step 1: Verify Spec Directory Exists

The spec directory was created in Task 0. Use the SPEC_DIR value from Task 0:

```bash
# SPEC_DIR was determined in Task 0 (e.g., review/2025-10-21-query-gamification-system)
# Verify it exists:
ls -ld .praxis-os/specs/${SPEC_DIR}
```

⚠️ **NOTE:** SPEC_DIR is available from Task 0 context or workflow artifacts. Do not use `.current-spec` file (deprecated ad-hoc workaround).

📊 COUNT-AND-DOCUMENT: Directory verified
- Path: `.praxis-os/specs/${SPEC_DIR}`
- Status: ✅ exists (created in Task 0)

### Step 2: Create Supporting Docs Subdirectory

```bash
mkdir -p .praxis-os/specs/${SPEC_DIR}/supporting-docs/
```

📊 COUNT-AND-DOCUMENT: Subdirectory created
- Path: `.praxis-os/specs/${SPEC_DIR}/supporting-docs/`
- Status: [created/already exists]

### Step 3: Process Documents Based on Mode

#### If `embed_supporting_docs` is TRUE:

Copy documents to supporting-docs:

```bash
# Use SPEC_DIR from Task 0 (e.g., review/2025-10-21-query-gamification-system)

# For each document
cp {doc_path_1} .praxis-os/specs/${SPEC_DIR}/supporting-docs/
cp {doc_path_2} .praxis-os/specs/${SPEC_DIR}/supporting-docs/
```

#### If `embed_supporting_docs` is FALSE:

Create REFERENCES.md with links:

```bash
# Use SPEC_DIR from Task 0
cat > .praxis-os/specs/${SPEC_DIR}/supporting-docs/REFERENCES.md << 'EOF'
# Document References

## Referenced Documents

### {DOCUMENT_1_NAME}
**Path:** `{absolute_or_relative_path_1}`  
**Purpose:** {brief_description}

### {DOCUMENT_2_NAME}
**Path:** `{absolute_or_relative_path_2}`  
**Purpose:** {brief_description}

---

**Note:** Ensure referenced files remain accessible.
EOF
```

### Step 4: Verify Documents Accessible

Verify all documents are accessible:

```bash
# Use SPEC_DIR from Task 0

# If embedded
ls -lh .praxis-os/specs/${SPEC_DIR}/supporting-docs/

# If referenced
# Check each reference path exists
test -f {doc_path_1} && echo "✅ {doc_1_name}" || echo "❌ {doc_1_name} NOT FOUND"
test -f {doc_path_2} && echo "✅ {doc_2_name}" || echo "❌ {doc_2_name} NOT FOUND"
```

📊 COUNT-AND-DOCUMENT: Documents processed
- Total documents: [number]
- Mode: [embedded/referenced]
- All accessible: [yes/no]

### Step 5: Document Processing Method

Add a note to track which method was used:

```bash
# Use SPEC_DIR from Task 0
cat > .praxis-os/specs/${SPEC_DIR}/supporting-docs/.processing-mode << 'EOF'
PROCESSING_MODE={embedded/referenced}
PROCESSED_DATE={current_date}
DOCUMENT_COUNT={number}
EOF
```

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] `supporting-docs/` directory created ✅/❌
- [ ] All documents accessible (copied or referenced) ✅/❌
- [ ] Files readable and valid (if embedded) ✅/❌
- [ ] REFERENCES.md created (if referenced) ✅/❌
- [ ] Processing mode documented ✅/❌

🚨 FRAMEWORK-VIOLATION: Broken document links

If using reference mode, ALL referenced documents MUST be accessible. Broken links will cause Phase 0 validation to fail. Consider embedding if document stability is uncertain.

---

## Evidence Collection

📊 COUNT-AND-DOCUMENT: Task Results

**Documents Processed:**
- Total count: [number]
- Processing mode: [embedded/referenced]
- Directory size: [size if embedded]

**Verification:**
- All documents accessible: [✅/❌]
- Format check passed: [✅/❌]

**Files Created:**
- `supporting-docs/` directory: ✅
- Embedded documents: [list if applicable]
- `REFERENCES.md`: [✅ if referenced mode]
- `.processing-mode`: ✅

---

## Next Task

🎯 NEXT-MANDATORY: [task-2-create-index.md](task-2-create-index.md)

Continue to Task 2 to create a comprehensive document index.
