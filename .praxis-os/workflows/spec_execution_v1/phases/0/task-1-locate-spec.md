# Task 1: Locate and Validate Spec

**Phase:** 0 (Spec Analysis & Planning)  
**Purpose:** Find specification directory, validate structure, check required files  
**Estimated Time:** 2 minutes

---

## 🎯 Objective

Locate the specification directory provided in workflow options, validate it contains all required files, and confirm the spec structure is complete and ready for execution.

---

## Prerequisites

🛑 EXECUTE-NOW: Verify workflow was started with spec_path option

```python
# Expected workflow invocation:
start_workflow(
    workflow_type="spec_execution_v1",
    target_file="spec-directory-path",
    options={"spec_path": ".praxis-os/specs/YYYY-MM-DD-name"}
)
```

---

## Steps

### Step 1: Locate Spec Directory

Check if the spec path exists and is accessible:

```bash
ls -la .praxis-os/specs/YYYY-MM-DD-name/
```

📊 COUNT-AND-DOCUMENT: Files found
- Total files: [number]
- File list: [list]

### Step 2: Validate Required Files

🛑 VALIDATE-GATE: Required Files Present

Check for all required spec files:
- [ ] `README.md` exists ✅/❌
- [ ] `srd.md` exists ✅/❌  
- [ ] `specs.md` exists ✅/❌
- [ ] `tasks.md` exists ✅/❌
- [ ] `implementation.md` exists ✅/❌

### Step 3: Validate File Content

Check that key files are not empty:

```bash
# Check tasks.md has content
wc -l .praxis-os/specs/YYYY-MM-DD-name/tasks.md

# Check specs.md has content  
wc -l .praxis-os/specs/YYYY-MM-DD-name/specs.md
```

📊 COUNT-AND-DOCUMENT: File sizes
- `tasks.md`: [number] lines
- `specs.md`: [number] lines
- `implementation.md`: [number] lines

### Step 4: Check for Supporting Docs (Optional)

If `supporting-docs/` directory exists, note it:

```bash
ls .praxis-os/specs/YYYY-MM-DD-name/supporting-docs/ 2>/dev/null || echo "No supporting docs"
```

---

## Completion Criteria

🛑 VALIDATE-GATE: Spec Location Validated

- [ ] Spec directory exists ✅/❌
- [ ] All 5 required files present ✅/❌
- [ ] `tasks.md` has content (>50 lines) ✅/❌
- [ ] `specs.md` has content (>100 lines) ✅/❌
- [ ] Spec structure is complete ✅/❌

🚨 FRAMEWORK-VIOLATION: Proceeding with missing files

If any required file is missing, **STOP HERE**. The spec must be complete before execution can begin. Missing files will cause execution failures.

---

## Evidence Collection

📊 COUNT-AND-DOCUMENT: Validation Results

**Spec Path:** `[actual path]`

**Required Files:**
- README.md: [✅/❌]
- srd.md: [✅/❌]
- specs.md: [✅/❌]
- tasks.md: [✅/❌]
- implementation.md: [✅/❌]

**File Sizes:**
- tasks.md: [number] lines
- specs.md: [number] lines

**Validation:** [PASS/FAIL]

---

## Next Step

🎯 NEXT-MANDATORY: [task-2-parse-tasks.md](task-2-parse-tasks.md)

Upon successful validation, proceed to parse the tasks.md file to extract phases, tasks, and dependencies.

