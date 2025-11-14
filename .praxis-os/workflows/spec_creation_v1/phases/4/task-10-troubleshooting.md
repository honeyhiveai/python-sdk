# Task 4: Provide Troubleshooting Guide

**Phase:** 4 (Implementation Guidance)  
**Purpose:** Common issues and debugging tips  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Document common issues developers may encounter during implementation and provide debugging guidance with solutions.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-3 must be completed

⚠️ MUST-READ: Reference template

See `core/implementation-template.md` for troubleshooting format.

---

## Steps

### Step 1: Add Troubleshooting Section

Append to implementation.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/implementation.md << 'EOF'

---

## 6. Troubleshooting

EOF
```

### Step 2: Add Common Issues

⚠️ MUST-READ: Use format from `core/implementation-template.md`

For project-specific issues, document:
- **Issue:** {Name}
- **Symptoms:** {What you see}
- **Cause:** {Why it happens}
- **Solution:** {Steps to fix}

### Step 3: Add Debugging Techniques

Include language-appropriate debugging commands (pdb, debugger, logging, health checks, DB inspection). See template for examples.

### Step 4: Add Performance Debugging

Document approaches for slow queries, high memory, etc.

### Step 5: Add Getting Help

List resources (docs, team chat, etc.) and what info to include when asking.

📊 COUNT-AND-DOCUMENT: Issues [number], debugging techniques [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] Common issues documented ✅/❌
- [ ] Solutions provided for each issue ✅/❌
- [ ] Debugging techniques listed ✅/❌
- [ ] Performance troubleshooting included ✅/❌
- [ ] Getting help section added ✅/❌

---

## Phase 4 Completion

🎯 PHASE-COMPLETE: Implementation guidance complete

This phase is complete when implementation.md contains:
- ✅ Code patterns documented with concrete examples
- ✅ Testing strategy defined (unit, integration, performance)
- ✅ Deployment procedures with step-by-step guidance
- ✅ Troubleshooting guide with common issues and solutions

Submit checkpoint evidence to advance to Phase 5 (Finalization) where you'll review and package all specification documents.
