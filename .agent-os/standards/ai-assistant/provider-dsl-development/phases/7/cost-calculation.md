# Task 7.3: Cost Calculation Transform

**🎯 Define cost calculation using Phase 3 pricing data**

---

## 🚨 **ENTRY REQUIREMENTS**

🛑 VALIDATE-GATE: Prerequisites
- [ ] Task 7.2 complete (Finish reason normalization) ✅/❌
- [ ] transforms.yaml exists with 2 transforms ✅/❌
- [ ] Pricing data from Phase 3.2 available ✅/❌

---

## 🛑 **EXECUTION**

### **Step 1: Review Pricing Structure**

🛑 EXECUTE-NOW: Load pricing from Phase 3.2

From RESEARCH_SOURCES.md Phase 3.2:
- Currency: [USD/EUR/etc.]
- Pricing unit: [per 1M tokens / per request / etc.]
- Input vs Output pricing: [YES/NO]
- Models with pricing: [X/TOTAL]

📊 QUANTIFY-RESULTS: Pricing structure confirmed: YES/NO

### **Step 2: Extract Model Pricing Table**

🛑 EXECUTE-NOW: Create pricing lookup from Phase 3.2

From Phase 3.2 pricing table, extract:
```markdown
Model Pricing:
- model_1: input=$X.XX/1M, output=$Y.YY/1M
- model_2: input=$X.XX/1M, output=$Y.YY/1M
- ...
```

📊 COUNT-AND-DOCUMENT: Models with pricing: [NUMBER]

### **Step 3: Define Cost Calculation Transform**

🛑 EXECUTE-NOW: Add calculate_cost to transforms.yaml

```yaml
calculate_cost:
  type: "cost_calculation"
  description: "Calculate estimated API cost based on token usage"
  parameters:
    model_field: "model"  # Field containing model name
    prompt_tokens_field: "prompt_tokens"
    completion_tokens_field: "completion_tokens"
  pricing:
    currency: "USD"  # From Phase 3.2
    unit: "per_1m_tokens"  # From Phase 3.2
    models:
      # Pricing from Phase 3.2 - use EXACT model identifiers
      "{model-id-1}":
        input: 0.000XXX  # Price per token (converted to per-token if needed)
        output: 0.000YYY
      "{model-id-2}":
        input: 0.000XXX
        output: 0.000YYY
      # Add ALL models from Phase 3.2
      
  default_pricing:  # For unknown models
    input: 0.0  # Don't estimate if model unknown
    output: 0.0
  implementation: "python"
```

**⚠️ CRITICAL**: 
- Use EXACT model IDs from Phase 3.1
- Use CURRENT pricing from Phase 3.2 (2025-09-30+)
- Convert pricing to per-token if needed (divide by 1M if "per 1M tokens")

📊 COUNT-AND-DOCUMENT: Model pricing entries: [NUMBER]

### **Step 4: Verify Pricing Coverage**

🛑 EXECUTE-NOW: Ensure all current models have pricing

From Phase 3.1 model list:
- Total current models: [NUMBER]
- Models with pricing in transform: [NUMBER]
- Coverage: [PERCENTAGE]%

📊 QUANTIFY-RESULTS: Pricing coverage ≥ 90%: YES/NO

### **Step 5: Verify YAML Syntax**

🛑 EXECUTE-NOW: Test YAML compiles

```bash
python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/transforms.yaml'))"
```

🛑 PASTE-OUTPUT: Compilation result

📊 QUANTIFY-RESULTS: YAML compiles: YES/NO

### **Step 6: Document Cost Calculation**

🛑 EXECUTE-NOW: Update RESEARCH_SOURCES.md

```markdown
### **Transforms - Cost Calculation**

**Transform**: `calculate_cost`

**Pricing Configuration**:
- Currency: [USD/EUR]
- Unit: per 1M tokens / per request
- Models covered: [X/TOTAL] ([PERCENTAGE]%)

**Pricing Table**:
| Model | Input ($/1M) | Output ($/1M) |
|-------|--------------|---------------|
| {model} | $X.XX | $Y.YY |
| ... | ... | ... |

**Default**: $0.00 for unknown models (no estimation)

**Source**: Phase 3.2 pricing data (verified 2025-09-30)
```

📊 QUANTIFY-RESULTS: Cost calculation documented: YES/NO

---

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Cost Calculation Complete
- [ ] calculate_cost added to transforms.yaml ✅/❌
- [ ] Pricing for ALL current models from Phase 3 ✅/❌
- [ ] Pricing is current (2025-09-30+) ✅/❌
- [ ] Currency and unit specified ✅/❌
- [ ] YAML compiles ✅/❌
- [ ] Cost calculation documented ✅/❌

🚨 FRAMEWORK-VIOLATION: If using outdated pricing or missing models

---

## 🎯 **NAVIGATION**

🛑 UPDATE-TABLE: Phase 7.3 → Cost calculation defined for [X] models
🎯 NEXT-MANDATORY: [transform-validation.md](transform-validation.md)
