# Task 7.5.1: Pre-Compilation Validation

**🎯 Validate all DSL files against compiler schema before final compilation**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Phase 7 complete with all transforms ✅/❌
- [ ] All 4 YAML files exist ✅/❌
- [ ] structure_patterns.yaml created ✅/❌
- [ ] navigation_rules.yaml created ✅/❌
- [ ] field_mappings.yaml created ✅/❌
- [ ] transforms.yaml created ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Validate YAML Syntax**

🛑 EXECUTE-NOW: Test each YAML file parses correctly

```bash
cd config/dsl/providers/{provider}/

# Test structure patterns
python -c "import yaml; yaml.safe_load(open('structure_patterns.yaml')); print('✅ structure_patterns.yaml')"

# Test navigation rules
python -c "import yaml; yaml.safe_load(open('navigation_rules.yaml')); print('✅ navigation_rules.yaml')"

# Test field mappings
python -c "import yaml; yaml.safe_load(open('field_mappings.yaml')); print('✅ field_mappings.yaml')"

# Test transforms
python -c "import yaml; yaml.safe_load(open('transforms.yaml')); print('✅ transforms.yaml')"
```

🛑 PASTE-OUTPUT: Validation results

📊 QUANTIFY-RESULTS: All 4 files parse: YES/NO

🚨 FRAMEWORK-VIOLATION: If proceeding with YAML syntax errors

### **Step 2: Validate Field Names (CRITICAL)**

🛑 EXECUTE-NOW: Check for common field naming errors

```bash
# Check for INCORRECT "required_fields" usage (should be "signature_fields")
grep -n "required_fields:" config/dsl/providers/{provider}/structure_patterns.yaml
```

**Expected output**: (no matches)

**If matches found**: ❌ **CRITICAL ERROR**
- Field name must be `signature_fields:` not `required_fields:`
- Fix all occurrences before proceeding
- Re-run validation after fixing

```bash
# Check for INCORRECT "fields:" usage
grep -n "^  fields:" config/dsl/providers/{provider}/structure_patterns.yaml
```

**Expected output**: (no matches)

📊 QUANTIFY-RESULTS: Field names correct: YES/NO

🚨 FRAMEWORK-VIOLATION: If proceeding with incorrect field names

### **Step 3: Validate Pattern Structure**

🛑 EXECUTE-NOW: Verify all patterns have required fields

```bash
cd /Users/josh/src/github.com/honeyhiveai/python-sdk

python -c "
import yaml
with open('config/dsl/providers/{provider}/structure_patterns.yaml') as f:
    data = yaml.safe_load(f)
    patterns = data.get('patterns', {})
    
    errors = []
    for pattern_name, pattern in patterns.items():
        # Check required fields
        if 'signature_fields' not in pattern:
            errors.append(f'{pattern_name}: Missing signature_fields')
        elif not isinstance(pattern['signature_fields'], list):
            errors.append(f'{pattern_name}: signature_fields must be a list')
        elif len(pattern['signature_fields']) < 2:
            errors.append(f'{pattern_name}: Must have at least 2 signature_fields')
        
        if 'confidence_weight' not in pattern:
            errors.append(f'{pattern_name}: Missing confidence_weight')
        
        if 'instrumentor_framework' not in pattern:
            errors.append(f'{pattern_name}: Missing instrumentor_framework')
    
    if errors:
        print('❌ Validation errors found:')
        for error in errors:
            print(f'  - {error}')
        exit(1)
    else:
        print(f'✅ All {len(patterns)} patterns valid')
"
```

🛑 PASTE-OUTPUT: Validation result

📊 QUANTIFY-RESULTS: All patterns valid: YES/NO

🚨 FRAMEWORK-VIOLATION: If proceeding with invalid patterns

### **Step 4: Validate Navigation Rules Coverage**

🛑 EXECUTE-NOW: Verify minimum rules per instrumentor

```bash
python -c "
import yaml
with open('config/dsl/providers/{provider}/navigation_rules.yaml') as f:
    data = yaml.safe_load(f)
    rules = data.get('navigation_rules', {})
    
    traceloop_rules = [r for r in rules if r.startswith('traceloop_')]
    openinference_rules = [r for r in rules if r.startswith('openinference_')]
    openlit_rules = [r for r in rules if r.startswith('openlit_')]
    
    print(f'Traceloop rules: {len(traceloop_rules)}')
    print(f'OpenInference rules: {len(openinference_rules)}')
    print(f'OpenLit rules: {len(openlit_rules)}')
    print(f'Total rules: {len(rules)}')
    
    # Check minimum 7 rules per verified instrumentor
    if len(traceloop_rules) > 0 and len(traceloop_rules) < 7:
        print(f'⚠️  Traceloop has only {len(traceloop_rules)} rules (minimum 7 recommended)')
    if len(openinference_rules) > 0 and len(openinference_rules) < 7:
        print(f'⚠️  OpenInference has only {len(openinference_rules)} rules (minimum 7 recommended)')
    if len(openlit_rules) > 0 and len(openlit_rules) < 7:
        print(f'⚠️  OpenLit has only {len(openlit_rules)} rules (minimum 7 recommended)')
"
```

🛑 PASTE-OUTPUT: Coverage analysis

📊 QUANTIFY-RESULTS: All instrumentors have 7+ rules: YES/NO

### **Step 5: Validate Field Mappings Base Names**

🛑 EXECUTE-NOW: Verify field_mappings.yaml uses base names (no instrumentor prefixes)

```bash
python -c "
import yaml
with open('config/dsl/providers/{provider}/field_mappings.yaml') as f:
    data = yaml.safe_load(f)
    mappings = data.get('field_mappings', {})
    
    errors = []
    for section_name, section in mappings.items():
        for field_name, field_data in section.items():
            rule = field_data.get('source_rule', '')
            if rule.startswith('traceloop_') or rule.startswith('openinference_') or rule.startswith('openlit_'):
                errors.append(f'{section_name}.{field_name}: source_rule \"{rule}\" has instrumentor prefix (should use base name)')
    
    if errors:
        print('❌ Field mapping errors (instrumentor prefixes found):')
        for error in errors:
            print(f'  - {error}')
        print()
        print('ℹ️  Use base names (e.g., \"model_name\" not \"traceloop_model_name\")')
        print('ℹ️  Compiler handles dynamic routing to instrumentor-specific rules')
        exit(1)
    else:
        print('✅ All field mappings use base names (no instrumentor prefixes)')
"
```

🛑 PASTE-OUTPUT: Validation result

📊 QUANTIFY-RESULTS: All source_rule use base names: YES/NO

🚨 FRAMEWORK-VIOLATION: If proceeding with instrumentor-prefixed source_rule values

### **Step 6: Validate Transforms Pricing Currency**

🛑 EXECUTE-NOW: Verify pricing is current (2025-09-30+)

```bash
python -c "
import yaml
from datetime import datetime

with open('config/dsl/providers/{provider}/transforms.yaml') as f:
    data = yaml.safe_load(f)
    
    metadata = data.get('metadata', {})
    pricing_date = metadata.get('pricing_date', '')
    pricing_verified = metadata.get('pricing_verified', False)
    
    if not pricing_verified:
        print('⚠️  pricing_verified: false (should be true)')
    
    if pricing_date:
        date_obj = datetime.strptime(pricing_date, '%Y-%m-%d')
        min_date = datetime.strptime('2025-09-30', '%Y-%m-%d')
        if date_obj < min_date:
            print(f'❌ Pricing date {pricing_date} is before 2025-09-30 (outdated)')
            exit(1)
        else:
            print(f'✅ Pricing date {pricing_date} is current (>= 2025-09-30)')
    else:
        print('⚠️  No pricing_date in metadata')
    
    print(f'✅ Pricing verified: {pricing_verified}')
"
```

🛑 PASTE-OUTPUT: Pricing validation

📊 QUANTIFY-RESULTS: Pricing is current: YES/NO

### **Step 7: Summary Validation Report**

🛑 EXECUTE-NOW: Create validation summary

**Validation Checklist**:
- [ ] ✅ All 4 YAML files parse without errors
- [ ] ✅ structure_patterns.yaml uses `signature_fields:` (not `required_fields:`)
- [ ] ✅ All patterns have minimum 2 signature_fields
- [ ] ✅ All patterns have `instrumentor_framework` field
- [ ] ✅ Navigation rules meet minimum coverage (7+ per instrumentor)
- [ ] ✅ Field mappings use base names (no instrumentor prefixes)
- [ ] ✅ Transforms have current pricing (2025-09-30+)

📊 QUANTIFY-RESULTS: All validation checks passed: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Pre-Compilation Validation Complete
- [ ] All 4 YAML files parse successfully ✅/❌
- [ ] Field names match compiler expectations ✅/❌
- [ ] No `required_fields:` usage (must be `signature_fields:`) ✅/❌
- [ ] All patterns structurally valid ✅/❌
- [ ] Navigation rules meet coverage ✅/❌
- [ ] Field mappings use base names ✅/❌
- [ ] Pricing is current ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding with validation errors

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 7.5 → Pre-compilation validation complete
🎯 NEXT-MANDATORY: Phase 8 - Compilation (proceed to [../8/shared-analysis.md](../8/shared-analysis.md))

**✅ If all validation passed**: Proceed to Phase 8 with confidence
**❌ If validation failed**: Fix errors before attempting compilation
