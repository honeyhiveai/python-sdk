# Task 7: Validate Metadata.json

**Phase**: 2 - Workflow Scaffolding  
**Purpose**: Validate metadata.json compliance with standards  
**Depends On**: Task 6 (Generate Metadata JSON)  
**Feeds Into**: Task 8 (Verify Scaffolding)

---

## Objective

Run the official validation script to ensure metadata.json complies with workflow-metadata-standards.md. This is a quality gate that prevents non-compliant workflows from proceeding.

---

## Context

📊 **CONTEXT**: The `workflow-metadata-standards.md` document defines 7 required root fields and 6 required phase fields. All prAxIs OS workflows MUST comply with this standard for proper RAG indexing, AI planning, and workflow engine execution.

🔍 **MUST-SEARCH**: "workflow metadata standards validation"

🛑 **QUALITY GATE**: This is a mandatory validation checkpoint. The workflow CANNOT proceed if metadata.json is non-compliant.

---

## Instructions

### Step 1: Run Official Validator

Execute the validation script against the newly created metadata.json:

```bash
python scripts/validate_workflow_metadata.py {workflow_directory_path}
```

📖 **DISCOVER-TOOL**: Run terminal command

The validator automatically checks:

**Root Fields (7 required):**
- ✅ workflow_type
- ✅ version
- ✅ description
- ✅ total_phases
- ✅ estimated_duration
- ✅ primary_outputs
- ✅ phases

**Phase Fields (6 required per phase):**
- ✅ phase_number
- ✅ phase_name
- ✅ purpose
- ✅ estimated_effort
- ✅ key_deliverables
- ✅ validation_criteria

**Quality Checks:**
- ✅ Phase numbering sequential (0-based)
- ✅ total_phases matches phases.length
- ✅ Duration formats include units
- ✅ Deliverables are non-empty arrays
- ✅ Criteria are non-empty arrays
- ✅ Description is searchable (keywords, length)

### Step 2: Interpret Results

Expected output if compliant:
```
✅ VALID - All required fields present and properly structured

COMPLIANCE:
  ✅ Metadata follows workflow-metadata-standards.md
  ✅ Ready for workflow engine consumption
  ✅ Optimized for RAG semantic search
```

If validation fails, you'll see:
```
❌ INVALID - Validation errors found

ERRORS (N):
  ❌ Missing required root field: estimated_duration
  ❌ Phase 0 missing required field: purpose
  ...
```

### Step 3: Handle Validation Failures

🛑 **STOP-IF-INVALID**: If validation fails:

1. **Review error messages** - Each error specifies exactly what's missing
2. **Return to Task 6** - Fix metadata.json generation
3. **Re-generate metadata.json** - Apply fixes
4. **Re-run this validator** - Verify fixes worked
5. **Only proceed when validation passes**

⚠️ **CONSTRAINT**: Do NOT proceed to Task 8 until validator returns exit code 0 (success)

### Step 4: Capture Validation Evidence

Record validation results for checkpoint evidence:

**Variables to Capture**:
- `metadata_validation_passed`: Boolean (true if exit code 0)
- `metadata_validator_output`: String (full output from validator)
- `validation_timestamp`: String (when validation ran)
- `metadata_compliant`: Boolean (same as passed)

---

## Expected Output

**Success State**:
```
metadata_validation_passed: true
metadata_compliant: true
validator_exit_code: 0
```

**Failure State** (must fix before proceeding):
```
metadata_validation_passed: false
errors_found: [...list of errors...]
action_required: "Fix metadata.json and re-validate"
```

---

## Quality Checks

✅ Validation script executed successfully  
✅ Exit code captured (0 = success)  
✅ All error messages reviewed (if any)  
✅ Validation output saved for evidence  
✅ **Validation passed** (mandatory gate)  
✅ metadata.json confirmed compliant  
✅ Ready to proceed to scaffolding verification

---

## Troubleshooting

**Common Issues:**

1. **Missing primary_outputs**
   - Add array of deliverables to root level
   - Example: `["test files", "coverage report"]`

2. **Missing estimated_duration**
   - Add duration with units to root level
   - Example: `"2-3 hours"` or `"30-45 minutes"`

3. **Missing phase fields (purpose, effort, deliverables, criteria)**
   - Each phase must have all 6 required fields
   - Extract from phase.md files or definition

4. **Phase numbering wrong**
   - Phases must be sequential starting at 0
   - Fix phase_number fields in metadata

5. **total_phases mismatch**
   - Ensure total_phases equals phases.length
   - Or set to "dynamic" if dynamic workflow

---

## Navigation

🎯 **NEXT-MANDATORY**: task-8-verify-scaffolding.md (only if validation passed)

↩️ **RETURN-IF-FAILED**: task-6-generate-metadata-json.md (fix and regenerate)

↩️ **RETURN-TO**: phase.md (after task complete)

