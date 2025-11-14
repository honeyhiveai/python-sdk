# Task 2: Create Document Index

**Phase:** 0 (Supporting Documents Integration)  
**Purpose:** Catalog all documents with structured metadata  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Create a comprehensive `INDEX.md` file that catalogs all supporting documents with metadata, purpose, and preliminary categorization. This index serves as a roadmap for extracting insights in Task 3.

---

## Prerequisites

🛑 EXECUTE-NOW: Task 1 must be completed

- All documents must be copied or referenced
- `supporting-docs/` directory must exist

---

## Steps

### Step 1: Gather Document Information

For each document, collect:
- **Filename** (or reference path)
- **Document type** (analysis, research, design, meeting notes, requirements draft, etc.)
- **Date created/modified** (if available)
- **Size** (if embedded)
- **Brief purpose** (why this document is relevant)

```bash
# If documents are embedded, get metadata
ls -lh .praxis-os/specs/{SPEC_DIR}/supporting-docs/*.md
ls -lh .praxis-os/specs/{SPEC_DIR}/supporting-docs/*.pdf
# etc.
```

### Step 2: Create INDEX.md Template

```bash
cat > .praxis-os/specs/{SPEC_DIR}/supporting-docs/INDEX.md << 'EOF'
# Supporting Documents Index

**Spec:** {FEATURE_NAME}  
**Created:** {CURRENT_DATE}  
**Total Documents:** {COUNT}

## Document Catalog

### 1. {DOCUMENT_1_NAME}

**File:** `{filename_or_path}`  
**Type:** {document_type}  
**Purpose:** {1-2 sentence description}

**Relevance:** Requirements [H/M/L], Design [H/M/L], Implementation [H/M/L]

**Key Topics:**
- {topic_1}
- {topic_2}

---

### 2. {DOCUMENT_2_NAME}

**File:** `{filename_or_path}`  
**Type:** {document_type}  
**Purpose:** {description}

**Relevance:** Requirements [H/M/L], Design [H/M/L], Implementation [H/M/L]

**Key Topics:**
- {topic_1}

---

## Cross-Document Analysis

**Common Themes:**
- {theme across multiple documents}

**Potential Conflicts:**
- {conflicting information - note sources}

**Coverage Gaps:**
- {areas not covered by supporting docs}

---

## Next Steps

This index will be used in Task 3 to systematically extract insights from each document. The extracted insights will be organized by:
- **Requirements Insights:** User needs, business goals, functional requirements
- **Design Insights:** Architecture patterns, technical approaches, component designs
- **Implementation Insights:** Code patterns, testing strategies, deployment guidance

EOF
```

### Step 3: Fill in Document Metadata

For each document:
1. Read/skim to understand purpose
2. Categorize relevance (Req/Design/Implementation as H/M/L)
3. List key topics
4. Note standout insights

### Step 4: Add Cross-Document Analysis

**Common Themes:** Topics appearing in multiple documents  
**Potential Conflicts:** Contradicting information or approaches  
**Coverage Gaps:** Areas not covered that need research

📊 COUNT-AND-DOCUMENT: Document analysis
- Documents indexed: [number]
- Common themes: [count]
- Conflicts: [count]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] INDEX.md created with all documents cataloged ✅/❌
- [ ] Purpose and relevance documented for each ✅/❌
- [ ] Key topics listed ✅/❌
- [ ] Cross-document analysis complete ✅/❌
- [ ] Themes, conflicts, gaps identified ✅/❌

🚨 FRAMEWORK-VIOLATION: Incomplete document analysis

The index must analyze each document's purpose, relevance, and key topics—not just list files

---

## Next Task

🎯 NEXT-MANDATORY: [task-3-extract-insights.md](task-3-extract-insights.md)

Continue to Task 3 to extract specific insights from each document based on the analysis completed in this index.
