# Task 4.2: Pattern Definitions

**🎯 Create YAML pattern definitions for ALL verified instrumentors**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 4.1 complete (Strategy designed) ✅/❌
- [ ] Signature fields identified for each instrumentor ✅/❌
- [ ] Confidence weights planned ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Create structure_patterns.yaml File**

🛑 EXECUTE-NOW: Open/create the YAML file

```bash
# File path
config/dsl/providers/{provider}/structure_patterns.yaml
```

📊 QUANTIFY-RESULTS: File opened/created: YES/NO

### **Step 2: Create Pattern for Each Verified Instrumentor**

🛑 EXECUTE-NOW: Write pattern definitions using Phase 4.1 strategy

⚠️ **CRITICAL**: Use EXACT field names expected by compiler (see schema below)

---

## 🚨 **COMPILER YAML SCHEMA REFERENCE**

**⚠️ MANDATORY**: Use these exact field names (compiler will reject incorrect names)

```yaml
{instrumentor}_{provider}:
  signature_fields:           # ⚠️ MUST use "signature_fields" (NOT "required_fields")
    - "{field.from.phase2}"   # From Phase 2 evidence
    - "{field.from.phase2}"   # Minimum 2 fields required
    - "{field.from.phase2}"   # Add more as needed
  optional_fields:            # Optional (can omit if no optional fields)
    - "{optional.field}"
  confidence_weight: 0.XX     # Float between 0.0 and 1.0
  description: "{text}"       # Human-readable description
  instrumentor_framework: "{traceloop/openinference/openlit}"  # Required
```

**❌ COMMON MISTAKES** (will cause compilation failure):

| ❌ INCORRECT | ✅ CORRECT | Issue |
|-------------|-----------|-------|
| `required_fields:` | `signature_fields:` | Wrong field name |
| `fields:` | `signature_fields:` | Wrong field name |
| `detection_fields:` | `signature_fields:` | Wrong field name |
| Missing `instrumentor_framework` | Add `instrumentor_framework: "traceloop"` | Required field |
| `confidence: 0.95` | `confidence_weight: 0.95` | Wrong field name |

**🛑 CRITICAL**: Always use `signature_fields:` (not `required_fields:`)

---

**Template for each verified instrumentor**:

```yaml
{instrumentor}_{provider}:
  signature_fields:  # ⚠️ Use "signature_fields" (compiler requirement)
    - "{field.from.phase2.verification}"  # From Phase 2 evidence
    - "{field.from.phase2.verification}"
    - "{field.from.phase2.verification}"
  optional_fields:
    - "{optional.field.if.available}"
  confidence_weight: 0.XX  # From Phase 4.1 uniqueness analysis
  description: "{Provider} via {Instrumentor} instrumentation"
  instrumentor_framework: "{traceloop/openinference/openlit}"
```

**Example - Traceloop (if verified)**:
```yaml
traceloop_{provider}:
  signature_fields:  # ✅ CORRECT: "signature_fields"
    - "gen_ai.system"
    - "gen_ai.request.model"
    - "gen_ai.response.model"
  optional_fields:
    - "gen_ai.usage.prompt_tokens"
  confidence_weight: 0.95  # Adjust based on uniqueness
  description: "{Provider} via Traceloop/OpenLLMetry instrumentation"
  instrumentor_framework: "traceloop"
```

📊 COUNT-AND-DOCUMENT: Patterns created: [NUMBER]

### **Step 3: Verify YAML Syntax**

🛑 EXECUTE-NOW: Test YAML file compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/structure_patterns.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: YAML compiles without errors: YES/NO

### **Step 4: Count and Validate Patterns**

🛑 EXECUTE-NOW: Verify pattern count matches verified instrumentors

From Phase 2:
- Verified instrumentors: [X/3]
- Patterns created: [X]
- Match: YES/NO

📊 QUANTIFY-RESULTS: All verified instrumentors have patterns: YES/NO

### **Step 5: Document in RESEARCH_SOURCES**

🛑 EXECUTE-NOW: Update implementation details

```markdown
## 5. **Implementation Details**

### **Structure Patterns**
- **File**: `config/dsl/providers/{provider}/structure_patterns.yaml`
- **Number of patterns**: [X]
- **Instrumentors covered**: [List: traceloop, openinference, openlit - only verified ones]
- **Confidence weights**: [Range: 0.XX - 0.YY]

**Pattern Summary**:
```yaml
# Pattern names created:
- traceloop_{provider}  # if verified
- openinference_{provider}  # if verified
- openlit_{provider}  # if verified
```

**Unique Signature Fields**:
- Traceloop: [fields used]
- OpenInference: [fields used]
- OpenLit: [fields used]

**Collision Risk**: [LOW/MEDIUM based on uniqueness]
```

📊 QUANTIFY-RESULTS: Implementation details documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Pattern Definitions Complete
- [ ] structure_patterns.yaml file created ✅/❌
- [ ] Pattern for EACH verified instrumentor ✅/❌
- [ ] All required_fields from Phase 2 verification ✅/❌
- [ ] Confidence weights from Phase 4.1 analysis ✅/❌
- [ ] YAML compiles without errors ✅/❌
- [ ] Implementation details documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding with compilation errors or missing patterns

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 4.2 → [X] patterns defined in structure_patterns.yaml
🎯 NEXT-MANDATORY: [uniqueness-validation.md](uniqueness-validation.md)
