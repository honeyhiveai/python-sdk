# Task 4: Generate Gate Definitions

**Objective:** Generate gate-definition.yaml files for each phase to enable checkpoint validation.

---

## 🎯 Context

Validation gates ensure systematic quality enforcement at phase boundaries. The workflow_engine.py uses CheckpointLoader to parse gate-definition.yaml files and validate evidence against requirements.

**Why This Matters:**
- Prevents advancement without proper evidence
- Enforces quality standards programmatically
- Provides structured error feedback to AI agents

---

## 📋 Prerequisites

🛑 EXECUTE-NOW: Tasks 1-3 must be completed

⚠️ MUST-READ: [../../core/validation-gates.md](../../core/validation-gates.md) for gate structure

Required inputs:
- `workflow_name` from Task 1
- `metadata.json` created in Task 3
- All phase.md files with checkpoint sections

---

## 🔧 Execution Steps

### Step 1: Run Gate Generation Script

📊 COUNT-AND-DOCUMENT: Number of gates to generate

🛑 EXECUTE-NOW: Generate gates for this workflow

```bash
# From project root
python scripts/generate-gate-definitions.py \
    --workflow {workflow_name} \
    --dry-run
```

**Expected Output:**
```
Processing workflow: {workflow_name}
[DRY-RUN] Would create: .praxis-os/workflows/{workflow_name}/phases/0/gate-definition.yaml
Fields: [field1, field2, ...]
[DRY-RUN] Would create: .praxis-os/workflows/{workflow_name}/phases/1/gate-definition.yaml
Fields: [field1, field2, ...]
...
```

---

### Step 2: Review Generated Gate Preview

🔍 QUERY-AND-DECIDE: Are the detected fields correct?

For each phase, verify:
- [ ] All required evidence fields detected
- [ ] Field types inferred correctly (boolean, integer, string, list)
- [ ] No extraneous fields included

**If fields incorrect:**
1. Update checkpoint section in phase.md with clearer formatting
2. Use pattern: `- [ ] field_name: description`
3. Re-run dry-run

**If fields correct:** Proceed to Step 3

---

### Step 3: Generate Gates

🛑 EXECUTE-NOW: Generate actual gate files

```bash
python scripts/generate-gate-definitions.py \
    --workflow {workflow_name}
```

**Expected Output:**
```
Generated: .praxis-os/workflows/{workflow_name}/phases/0/gate-definition.yaml (X fields)
Generated: .praxis-os/workflows/{workflow_name}/phases/1/gate-definition.yaml (X fields)
...
Migration completed successfully!
```

📊 COUNT-AND-DOCUMENT: Gates generated

Variables to capture:
- `gates_generated`: Number of gate files created
- `total_phases`: Number of phases in workflow
- `coverage`: Percentage of phases with gates

---

### Step 4: Verify Gate Structure

🛑 EXECUTE-NOW: Check gate file structure

```bash
# View one of the generated gates
cat .praxis-os/workflows/{workflow_name}/phases/1/gate-definition.yaml
```

**Expected Structure:**
```yaml
checkpoint:
  strict: false  # Phases 0-1 are lenient
  allow_override: true
evidence_schema:
  field_name:
    type: boolean  # or integer, string, list
    required: true
    description: "Field description"
    validator: validator_name  # optional
validators:
  positive: "lambda x: x > 0"  # if integer fields present
```

Verify:
- [ ] `checkpoint` section present with `strict` and `allow_override`
- [ ] `evidence_schema` has all required fields
- [ ] Each field has `type`, `required`, `description`
- [ ] `validators` section present (even if empty)

---

### Step 5: Test Gate Loading

🛑 EXECUTE-NOW: Verify gates can be loaded

```python
# Test gate loading (from Python REPL or test script)
from pathlib import Path
import yaml

gate_path = Path(".praxis-os/workflows/{workflow_name}/phases/1/gate-definition.yaml")
content = yaml.safe_load(gate_path.read_text())

# Verify structure
assert "checkpoint" in content
assert "evidence_schema" in content
assert "validators" in content

print(f"✅ Gate loads successfully")
print(f"Fields: {list(content['evidence_schema'].keys())}")
```

📊 COUNT-AND-DOCUMENT: Gate validation result

---

### Step 6: Update Strictness for Later Phases

⚠️ CONDITIONAL: If this is a production-ready workflow

For phases 2+ (after initial validation), consider enabling strict mode:

```bash
# Edit gate-definition.yaml for phases 2+
# Change:
checkpoint:
  strict: false  # Lenient

# To:
checkpoint:
  strict: true   # Strict (errors block advancement)
  allow_override: false
```

**Strict Mode Criteria:**
- Phase has clear, measurable requirements
- Evidence fields are well-defined
- Validators accurately enforce quality

**When to Keep Lenient:**
- Early phases (0-1) for gradual onboarding
- Phases with subjective requirements
- Workflows still under development

---

## ✅ Acceptance Criteria

Before proceeding:
- [ ] Gate generation script ran successfully (exit code 0)
- [ ] All phases have gate-definition.yaml files
- [ ] Gate files have valid YAML syntax
- [ ] Evidence schema matches checkpoint requirements
- [ ] Gates can be loaded by CheckpointLoader

---

## 📊 Evidence for Checkpoint

Collect this evidence for Phase 2 validation gate:

```yaml
evidence:
  gates_generated: {number}  # Number of gate files created
  gate_files_valid: true     # All gates have valid YAML
  coverage_percent: {percent}  # Percentage of phases with gates
  gate_validation_passed: true  # Gates load successfully
```

---

## 🚨 Common Issues

### Issue 1: No Fields Detected

**Symptom:** Gate generation says "No checkpoint fields found"

**Cause:** Checkpoint section not properly formatted in phase.md

**Solution:**
1. Check phase.md has section header: `## Validation Gate` or `## Checkpoint`
2. Use clear field patterns:
   ```markdown
   - [ ] field_name: description
   - [ ] `another_field`: description
   ```
3. Re-run generation

---

### Issue 2: Wrong Field Types

**Symptom:** Integer fields detected as string

**Cause:** Type inference based on field name patterns

**Solution:**
1. Use naming conventions:
   - Counts: `tests_passing`, `num_functions`, `total_lines`
   - Flags: `is_valid`, `has_tests`, `can_proceed`
   - Lists: `functions` (plural), `test_files_list`
2. Or manually edit gate-definition.yaml to fix types

---

### Issue 3: Missing Validators

**Symptom:** No validators in gate file

**Cause:** No integer fields detected (validators only added for integers)

**Solution:**
- This is normal for gates with only boolean/string fields
- Add custom validators manually if needed:
  ```yaml
  validators:
    non_empty: "lambda x: len(x) > 0"
  ```

---

## 🎯 Next Steps

After generating gates:
1. Proceed to Task 5: Validate Gate Consistency
2. Ensure gates match checkpoint requirements
3. Test workflow with actual validation

---

**Task Complete:** Gate-definition.yaml files generated and validated for all phases.
