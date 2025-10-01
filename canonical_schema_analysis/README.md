# Canonical Schema Analysis - Summary

**Date**: 2025-10-01  
**Analysis Complete**: ✅  
**Data Source**: Deep Research Prod - Financial Research Agent Eval  
**Sample Size**: 385 production events

---

## 📁 Files in This Directory

### 📊 Analysis Documents

1. **[CANONICAL_SCHEMA_ANALYSIS.md](./CANONICAL_SCHEMA_ANALYSIS.md)** (7.5KB)
   - Comprehensive deep-dive analysis
   - Event type breakdowns (MODEL, CHAIN, TOOL, SESSION)
   - Field frequency analysis
   - Cross-type patterns
   - Critical insights for DSL development

2. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** (5.2KB)
   - Quick lookup guide
   - Schema structure at a glance
   - Key insights (flat structure, dot notation, JSON strings)
   - Common field patterns
   - Production examples

3. **[DSL_MAPPING_RULES.md](./DSL_MAPPING_RULES.md)** (12KB)
   - **Actionable mapping rules** for DSL implementation
   - Rule-by-rule mapping from all trace sources
   - Flattening algorithms (Python code)
   - Edge cases and special handling
   - Implementation checklist

### 📦 Raw Data Files

4. **model_events.json** (949KB) - 100 MODEL events
5. **chain_events.json** (891KB) - 100 CHAIN events
6. **tool_events.json** (177KB) - 100 TOOL events
7. **session_events.json** (473KB) - 85 SESSION events

---

## 🎯 Key Findings

### 1. **The Canonical Schema is FLAT**

The HoneyHive canonical schema does **NOT** mirror raw provider API responses. Instead, it uses a flat, dot-notation structure:

```json
{
  "outputs": {
    "role": "assistant",
    "content": "text",
    "tool_calls.0.id": "call_abc",
    "tool_calls.0.name": "search",
    "tool_calls.0.arguments": "{\"json\":\"string\"}"
  }
}
```

NOT:
```json
{
  "outputs": {
    "tool_calls": [
      {
        "id": "call_abc",
        "name": "search",
        "arguments": {"json": "object"}
      }
    ]
  }
}
```

### 2. **4-Section Universal Contract**

Every event follows this structure:

- **`inputs`**: Dict[str, Any] - Event inputs/parameters
- **`outputs`**: Dict[str, Any] - Event results/responses  
- **`config`**: Dict[str, Any] - Event configuration
- **`metadata`**: Dict[str, Any] - Observability/tracking

### 3. **JSON Strings Stay as Strings**

Critical fields like `tool_calls.*.arguments` **must remain JSON strings**, NOT parsed objects.

### 4. **Chat History is an Array**

The `inputs.chat_history` field contains an **array of message objects**, reconstructed from flattened span attributes.

---

## 🚀 Next Steps

### Immediate Actions (Priority 1)

1. **Update DSL field_mappings.yaml**
   - Ensure all mappings target flat canonical structure
   - Use rules from `DSL_MAPPING_RULES.md`

2. **Add HoneyHive Direct SDK support**
   - Add navigation rules for `honeyhive_*` attributes
   - Test with direct SDK spans

3. **Validate Flattening Logic**
   - Ensure transforms correctly flatten nested structures
   - Verify dot notation (`.0`, `.1`, not `[0]`, `[1]`)

### Testing & Validation (Priority 2)

4. **Run DSL on Production Events**
   - Use these 385 events as test set
   - Compare DSL output to actual canonical schema
   - Calculate field-by-field accuracy

5. **Create Validation Suite**
   - Unit tests for each mapping rule
   - Integration tests with real events
   - Regression tests for edge cases

### Documentation (Priority 3)

6. **Update Architecture Docs**
   - Integrate findings into `DSL_TO_HONEYHIVE_SCHEMA_FLOW.md`
   - Update DSL compiler documentation
   - Create developer guide for DSL mapping

---

## 📊 Analysis Statistics

| Metric | Value |
|--------|-------|
| **Total Events Analyzed** | 385 |
| **MODEL Events** | 100 (26%) |
| **CHAIN Events** | 100 (26%) |
| **TOOL Events** | 100 (26%) |
| **SESSION Events** | 85 (22%) |
| **Unique Fields Identified** | 50+ |
| **Mapping Rules Defined** | 11 core + 5 special cases |
| **Data Quality** | Production-validated ✅ |

---

## 🔍 How to Use This Analysis

### For DSL Developers

1. **Start with** [DSL_MAPPING_RULES.md](./DSL_MAPPING_RULES.md)
   - Follow the rule-by-rule mapping guide
   - Implement flattening algorithms
   - Handle edge cases

2. **Reference** [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
   - Quick schema structure lookup
   - Common field patterns
   - Production examples

3. **Deep dive** [CANONICAL_SCHEMA_ANALYSIS.md](./CANONICAL_SCHEMA_ANALYSIS.md)
   - Understand event type variations
   - See full field frequency analysis
   - Understand design rationale

### For Testing

1. **Use raw data files** (`*_events.json`)
   - 385 production events as test fixtures
   - Validate DSL output against these
   - Ensure 100% accuracy

2. **Follow validation checklist** in DSL_MAPPING_RULES.md
   - Structural checks
   - Data integrity checks
   - Type checks

---

## 🎓 Key Takeaways

1. ✅ **Canonical schema is flat** - No nested objects in inputs/outputs/config/metadata
2. ✅ **Dot notation for arrays** - Use `.0`, `.1`, not `[0]`, `[1]`
3. ✅ **JSON strings preserved** - Don't parse `tool_calls.*.arguments`
4. ✅ **Chat history is array** - Reconstruct from flattened attributes
5. ✅ **DSL is translation layer** - From diverse sources → canonical schema
6. ✅ **4-section contract universal** - All events follow same structure
7. ✅ **Production-validated** - 385 real events confirm patterns

---

## 📞 Questions?

For questions about this analysis:
- See [CANONICAL_SCHEMA_ANALYSIS.md](./CANONICAL_SCHEMA_ANALYSIS.md) for detailed explanations
- See [DSL_MAPPING_RULES.md](./DSL_MAPPING_RULES.md) for implementation guidance
- Reference raw event files for specific examples

---

**Analysis Completed**: 2025-10-01  
**Validated Against**: 385 production events  
**Status**: ✅ Ready for DSL implementation

