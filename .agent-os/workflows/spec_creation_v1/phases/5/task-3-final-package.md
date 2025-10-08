# Task 3: Generate Final Package

**Phase:** 5 (Finalization)  
**Purpose:** Create final deliverable summary  
**Estimated Time:** 5-10 minutes

---

## 🎯 Objective

Create a final summary document (README.md) that provides an overview of all specification documents and serves as the entry point for implementation teams.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-2 must be completed

- All documents complete and consistent

---

## Steps

### Step 1: Create README.md from Template

⚠️ MUST-READ: Use template from `core/readme-template.md`

Create README.md with full template structure (document index, quick start by role, metrics, next steps). Customize with project-specific details from specs.md, srd.md, and tasks.md.

```bash
# Copy template and customize
cat core/readme-template.md > .agent-os/specs/{SPEC_DIR}/README.md
# Then edit with project specifics
```

### Step 2: Validate Package Completeness

Check all documents present:
- [ ] srd.md (requirements)
- [ ] specs.md (technical design)
- [ ] tasks.md (implementation plan)
- [ ] implementation.md (code guidance)
- [ ] README.md (package overview)

📊 COUNT-AND-DOCUMENT: Package metrics from each document

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] README.md created ✅/❌
- [ ] Document index complete ✅/❌
- [ ] Quick start guide included ✅/❌
- [ ] Key metrics documented ✅/❌
- [ ] Next steps clear ✅/❌

---

## Phase 5 Completion

🎯 PHASE-COMPLETE: Specifications finalized

Specification package is complete and includes:
- ✅ srd.md (requirements)
- ✅ specs.md (technical design)
- ✅ tasks.md (implementation plan)
- ✅ implementation.md (code guidance)
- ✅ README.md (package overview)

All documents are complete, consistent, and ready for implementation teams.

Submit final checkpoint evidence:

```python
complete_phase(
    session_id=session_id,
    phase=5,
    evidence={
        "all_documents_complete": True,
        "all_documents_consistent": True,
        "readme_created": True,
        "package_ready": True
    }
)
```

🎉 **Workflow Complete!** Specifications are ready for implementation.
