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

### Step 1: Create Supporting Docs Directory

Create the directory structure:

```bash
mkdir -p .agent-os/specs/{SPEC_DIR}/supporting-docs/
```

📊 COUNT-AND-DOCUMENT: Directory created
- Path: `.agent-os/specs/{SPEC_DIR}/supporting-docs/`
- Status: [created/already exists]

### Step 2: Process Documents Based on Mode

#### If `embed_supporting_docs` is TRUE:

Copy documents to supporting-docs:

```bash
# For each document
cp {doc_path_1} .agent-os/specs/{SPEC_DIR}/supporting-docs/
cp {doc_path_2} .agent-os/specs/{SPEC_DIR}/supporting-docs/
```

#### If `embed_supporting_docs` is FALSE:

Create REFERENCES.md with links:

```bash
cat > .agent-os/specs/{SPEC_DIR}/supporting-docs/REFERENCES.md << 'EOF'
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

### Step 3: Verify Documents Accessible

Verify all documents are accessible:

```bash
# If embedded
ls -lh .agent-os/specs/{SPEC_DIR}/supporting-docs/

# If referenced
# Check each reference path exists
test -f {doc_path_1} && echo "✅ {doc_1_name}" || echo "❌ {doc_1_name} NOT FOUND"
test -f {doc_path_2} && echo "✅ {doc_2_name}" || echo "❌ {doc_2_name} NOT FOUND"
```

📊 COUNT-AND-DOCUMENT: Documents processed
- Total documents: [number]
- Mode: [embedded/referenced]
- All accessible: [yes/no]

### Step 4: Document Processing Method

Add a note to track which method was used:

```bash
cat > .agent-os/specs/{SPEC_DIR}/supporting-docs/.processing-mode << 'EOF'
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
