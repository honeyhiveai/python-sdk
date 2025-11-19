# Task 5: Validate Gate Consistency

**Objective:** Ensure generated gates match checkpoint requirements and are internally consistent.

---

## 🎯 Context

Gate-definition.yaml files must accurately reflect the checkpoint requirements defined in phase.md files. Inconsistencies between gates and checkpoints can lead to validation failures or missed requirements.

**Why This Matters:**
- Prevents validation bugs
- Ensures requirements match implementation
- Maintains consistency across workflow phases

---

## 📋 Prerequisites

🛑 EXECUTE-NOW: Task 4 must be completed (gates generated)

Required inputs:
- `workflow_name` from Task 1
- Generated gate-definition.yaml files from Task 4
- All phase.md files with checkpoint sections

---

## 🔧 Execution Steps

### Step 1: List All Generated Gates

📊 COUNT-AND-DOCUMENT: Number of gates to validate

🛑 EXECUTE-NOW: List gate files

```bash
# From project root
find .praxis-os/workflows/{workflow_name}/phases -name "gate-definition.yaml" -type f | sort
```

**Expected Output:**
```
.praxis-os/workflows/{workflow_name}/phases/0/gate-definition.yaml
.praxis-os/workflows/{workflow_name}/phases/1/gate-definition.yaml
.praxis-os/workflows/{workflow_name}/phases/2/gate-definition.yaml
...
```

---

### Step 2: Validate YAML Syntax

🛑 EXECUTE-NOW: Check all gates for valid YAML

```bash
# Validate each gate file
for gate in .praxis-os/workflows/{workflow_name}/phases/*/gate-definition.yaml; do
    echo "Validating: $gate"
    python -c "import yaml; yaml.safe_load(open('$gate'))" && echo "✅ Valid" || echo "❌ Invalid"
done
```

**Expected:** All gates show "✅ Valid"

📊 COUNT-AND-DOCUMENT: Validation results

---

### Step 3: Cross-Reference with Checkpoints

For each phase, manually verify gates match checkpoint requirements:

🔍 QUERY-AND-DECIDE: For each phase with a gate

**Verification Process:**

1. **Open phase.md file:**
   ```bash
   cat .praxis-os/workflows/{workflow_name}/phases/1/phase.md | grep -A 20 "Checkpoint\|Validation Gate"
   ```

2. **Open corresponding gate file:**
   ```bash
   cat .praxis-os/workflows/{workflow_name}/phases/1/gate-definition.yaml
   ```

3. **Compare fields:**
   - [ ] All checkpoint requirements have corresponding evidence_schema fields
   - [ ] No extra fields in gate that aren't in checkpoint
   - [ ] Field types make sense (boolean for yes/no, integer for counts)
   - [ ] Descriptions are clear and match checkpoint language

**If mismatch found:**
- Document the discrepancy
- Update either phase.md (if requirement changed) or gate-definition.yaml (if parsing error)
- Re-run gate generation for that phase if needed

---

### Step 4: Validate Gate Structure

🛑 EXECUTE-NOW: Check structural requirements

For each gate file, verify it has:

```python
# Python validation script
from pathlib import Path
import yaml

def validate_gate_structure(gate_path):
    """Validate gate-definition.yaml structure."""
    content = yaml.safe_load(gate_path.read_text())
    
    errors = []
    
    # Check required top-level keys
    if "checkpoint" not in content:
        errors.append("Missing 'checkpoint' section")
    if "evidence_schema" not in content:
        errors.append("Missing 'evidence_schema' section")
    if "validators" not in content:
        errors.append("Missing 'validators' section")
    
    # Check checkpoint section
    if "checkpoint" in content:
        checkpoint = content["checkpoint"]
        if "strict" not in checkpoint:
            errors.append("Missing 'checkpoint.strict' field")
        if "allow_override" not in checkpoint:
            errors.append("Missing 'checkpoint.allow_override' field")
    
    # Check evidence_schema fields
    if "evidence_schema" in content:
        for field_name, field_spec in content["evidence_schema"].items():
            if "type" not in field_spec:
                errors.append(f"Field '{field_name}' missing 'type'")
            if "required" not in field_spec:
                errors.append(f"Field '{field_name}' missing 'required'")
            if "description" not in field_spec:
                errors.append(f"Field '{field_name}' missing 'description'")
            
            # Check type is valid
            valid_types = ["boolean", "integer", "string", "list", "dict"]
            if field_spec.get("type") not in valid_types:
                errors.append(f"Field '{field_name}' has invalid type: {field_spec.get('type')}")
    
    return errors

# Run validation
workflow_name = "{workflow_name}"
phases_dir = Path(f".praxis-os/workflows/{workflow_name}/phases")

for gate_file in sorted(phases_dir.glob("*/gate-definition.yaml")):
    print(f"\nValidating: {gate_file}")
    errors = validate_gate_structure(gate_file)
    
    if errors:
        print(f"❌ Errors found:")
        for error in errors:
            print(f"   - {error}")
    else:
        print(f"✅ Structure valid")
```

📊 COUNT-AND-DOCUMENT: Structural validation results

---

### Step 5: Check Validator References

🛑 EXECUTE-NOW: Verify validator references are valid

For gates with validator references in evidence_schema:

```python
# Validator reference checker
def check_validator_references(gate_path):
    """Verify all validator references exist."""
    content = yaml.safe_load(gate_path.read_text())
    
    validators_defined = set(content.get("validators", {}).keys())
    errors = []
    
    for field_name, field_spec in content.get("evidence_schema", {}).items():
        if "validator" in field_spec:
            validator_name = field_spec["validator"]
            if validator_name not in validators_defined:
                errors.append(
                    f"Field '{field_name}' references undefined validator: '{validator_name}'"
                )
    
    return errors

# Run check
for gate_file in sorted(phases_dir.glob("*/gate-definition.yaml")):
    errors = check_validator_references(gate_file)
    if errors:
        print(f"❌ {gate_file}:")
        for error in errors:
            print(f"   - {error}")
```

---

### Step 6: Test Gate Loading with CheckpointLoader

🛑 EXECUTE-NOW: Verify gates load correctly in the system

```python
# Test with actual CheckpointLoader
import sys
sys.path.insert(0, ".")

from mcp_server.workflow_engine import CheckpointLoader
from mcp_server.rag_engine import RAGEngine

# Initialize (requires RAG engine)
rag_engine = RAGEngine()
loader = CheckpointLoader(rag_engine)

# Test loading each gate
workflow_name = "{workflow_name}"
phases = [0, 1, 2, 3, 4, 5]  # Adjust based on workflow

for phase in phases:
    try:
        requirements = loader.load_checkpoint_requirements(workflow_name, phase)
        
        print(f"✅ Phase {phase}: Loaded successfully")
        print(f"   Source: {requirements.get('source', 'unknown')}")
        print(f"   Fields: {len(requirements.get('required_evidence', {}))}")
        
        if requirements.get("source") == "yaml":
            print(f"   ✓ Using YAML gate (first-tier)")
        elif requirements.get("source") == "permissive":
            print(f"   ⚠ Using permissive gate (no requirements found)")
            
    except Exception as e:
        print(f"❌ Phase {phase}: Load failed - {e}")
```

📊 COUNT-AND-DOCUMENT: Loading test results

---

## ✅ Acceptance Criteria

Before proceeding:
- [ ] All gates have valid YAML syntax
- [ ] All gates match checkpoint requirements
- [ ] Gate structures are complete (checkpoint, evidence_schema, validators)
- [ ] Validator references are valid
- [ ] Gates load successfully with CheckpointLoader
- [ ] No errors in validation tests

---

## 📊 Evidence for Checkpoint

Collect this evidence for Phase 2 validation gate:

```yaml
evidence:
  gates_validated: {number}  # Number of gates checked
  syntax_errors: 0          # Should be 0
  structure_errors: 0       # Should be 0
  consistency_verified: true  # Gates match checkpoints
  loading_successful: true    # CheckpointLoader works
```

---

## 🚨 Common Issues

### Issue 1: YAML Syntax Errors

**Symptom:** `yaml.safe_load()` raises exception

**Cause:** Invalid YAML formatting (indentation, special characters)

**Solution:**
1. Check indentation (use spaces, not tabs)
2. Quote strings with special characters
3. Validate with online YAML validator
4. Re-generate gate if needed

---

### Issue 2: Missing Fields

**Symptom:** Checkpoint has requirements not in gate

**Cause:** Parsing didn't detect all fields in phase.md

**Solution:**
1. Update phase.md to use clear patterns: `- [ ] field_name: description`
2. Re-run gate generation: `python scripts/generate-gate-definitions.py --workflow {workflow_name}`
3. Re-validate

---

### Issue 3: Type Mismatches

**Symptom:** Boolean field typed as string

**Cause:** Type inference based on naming patterns

**Solution:**
1. Use clear naming: `is_*`, `has_*` for booleans; `*_count`, `num_*` for integers
2. Or manually edit gate-definition.yaml to correct type
3. Validate type makes sense for requirement

---

### Issue 4: CheckpointLoader Fails

**Symptom:** Gate loads but returns permissive

**Cause:** File path incorrect or gate malformed

**Solution:**
1. Verify file path: `.praxis-os/workflows/{workflow_name}/phases/{phase}/gate-definition.yaml`
2. Check file permissions (readable)
3. Verify YAML structure matches expected format
4. Check logs for specific error

---

## 🎯 Next Steps

After validating consistency:
1. Proceed to Phase 3 tasks (if applicable)
2. Or finalize workflow documentation
3. Test workflow execution with actual validation

---

**Task Complete:** All gates validated for consistency and structural correctness.
