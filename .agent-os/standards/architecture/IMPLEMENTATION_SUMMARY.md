# OpenAI DSL Implementation - Executive Summary

**Date**: 2025-09-30  
**Status**: Ready for Implementation  
**Estimated Effort**: 2-3 days

---

## 🎯 The Problem

The current OpenAI DSL configuration is **incomplete** (only ~30% coverage). Critical fields like `tool_calls`, `refusal`, and `audio` are either missing or not properly implemented. This causes data loss when translating LLM spans to HoneyHive events.

---

## ✅ What We Have

**Current DSL Configs** (`config/dsl/providers/openai/`):
- ✅ Basic field mappings (model, temperature, tokens, etc.)
- ✅ Provider detection patterns (OpenInference, Traceloop, OpenLit)
- ✅ Simple navigation rules
- ✅ Basic transforms using shared registry

**Transform Registry** (`transform_registry.py`):
- ✅ 18+ transform functions available
- ✅ Array reconstruction function exists
- ✅ Message extraction functions work

**Execution Path**:
- ✅ Universal v4.0 engine is ACTIVE
- ✅ Precompiled DSL bundles work
- ✅ Legacy hardcoded code is INACTIVE

---

## ❌ What's Missing

### Critical Gaps (Must Fix)

1. **Tool Calls** - Not properly extracted
   - Mapping exists but navigation rule missing
   - Array reconstruction not configured
   - JSON string preservation not enforced

2. **Flattened Array Reconstruction** - Not implemented
   - Can't rebuild tool_calls from `gen_ai.completion.0.message.tool_calls.0.id` pattern
   - Missing transform configuration

3. **JSON String Handling** - At risk
   - `arguments` might be parsed to object (wrong!)
   - Must preserve as JSON string for backend

### High Priority Gaps (Should Fix)

4. **Refusal Messages** - Missing
5. **Audio Responses** - Missing
6. **System Fingerprint** - Missing
7. **Annotations** - Missing

---

## 🏗️ The Fix (6 Phases)

### Phase 1: Navigation Rules (4 hours)
**Add to** `navigation_rules.yaml`:
- Tool calls extraction patterns (all 3 instrumentors)
- Advanced field extraction rules (refusal, audio, etc.)

### Phase 2: Transforms (3 hours)
**Add to** `transforms.yaml`:
- Tool calls reconstruction transform
- Advanced field extraction transforms
- JSON string preservation config

### Phase 3: Field Mappings (2 hours)
**Update** `field_mappings.yaml`:
- Fix tool_calls mapping (connect to new navigation rule)
- Add refusal, audio, annotations to outputs
- Add system_fingerprint to metadata

### Phase 4: Transform Registry (2 hours)
**Verify/Add** in `transform_registry.py`:
- `reconstruct_array_from_flattened` (should exist)
- `extract_nested_array` (may need to add)
- `extract_nested_object` (may need to add)
- JSON string preservation logic

### Phase 5: Recompile (1 hour)
- Run DSL compiler
- Generate new `compiled_providers.pkl`
- Verify bundle contents

### Phase 6: Testing (4 hours)
- Unit tests for each field type
- Integration tests with real spans
- End-to-end verification

---

## 📋 Quick Start

### Step 1: Read the Detailed Plan
```bash
# Full implementation details
cat .agent-os/standards/architecture/OPENAI_DSL_IMPLEMENTATION_PLAN.md
```

### Step 2: Check Current State
```bash
# What's in the DSL configs now?
ls config/dsl/providers/openai/

# Search for tool_calls references
grep -r "tool_calls" config/dsl/providers/openai/

# Check transform registry
grep "def reconstruct_array_from_flattened" src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py
```

### Step 3: Start with Phase 1
```bash
# Edit navigation rules
vim config/dsl/providers/openai/navigation_rules.yaml

# Add tool calls extraction patterns (see implementation plan for code)
```

---

## 🎯 Success Criteria

### Must Work

- ✅ Tool calls properly extracted from flattened attributes
- ✅ Arguments preserved as JSON strings (not objects)
- ✅ Works with OpenInference, Traceloop, OpenLit
- ✅ Bundle compiles without errors
- ✅ Integration tests pass

### Coverage Target

| Field Type | Before | After | Status |
|------------|--------|-------|--------|
| **Basic fields** | ✅ 100% | ✅ 100% | Done |
| **Tool calls** | ❌ 0% | ✅ 100% | **Needs Fix** |
| **Advanced fields** | ❌ 0% | ✅ 100% | **Needs Fix** |
| **Overall** | 30% | 100% | **+70%** |

---

## 📚 Documentation Index

### Core Docs (Read in Order)

1. **[Quick Reference](./ARCHITECTURE_QUICK_REFERENCE.md)** - 5 min overview
2. **[Current vs Legacy](./CURRENT_VS_LEGACY_IMPLEMENTATION.md)** - Understand what's active
3. **[Implementation Plan](./OPENAI_DSL_IMPLEMENTATION_PLAN.md)** - Detailed roadmap
4. **[Event Schema](./HONEYHIVE_EVENT_SCHEMA_REFERENCE.md)** - What DSL must produce
5. **[DSL Architecture](./DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md)** - Overall architecture

### Implementation Files

- **DSL Configs**: `config/dsl/providers/openai/*.yaml`
- **Transform Registry**: `src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py`
- **Compiled Bundle**: `src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl`
- **Provider Processor**: `src/honeyhive/tracer/processing/semantic_conventions/provider_processor.py`

---

## 🚀 Next Steps

### Immediate Actions

1. **Audit existing DSL configs** (30 min)
   ```bash
   grep -r "tool_calls\|refusal\|audio" config/dsl/providers/openai/
   ```

2. **Check transform registry** (30 min)
   ```bash
   grep "TRANSFORM_REGISTRY\[" src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py
   ```

3. **Start Phase 1** (4 hours)
   - Add missing navigation rules
   - See implementation plan for exact YAML to add

### Timeline

- **Day 1**: Phases 1-3 (DSL config updates)
- **Day 2**: Phase 4 (transform registry)
- **Day 3**: Phases 5-6 (compile & test)

---

## ⚠️ Critical Notes

### JSON String Preservation

**CRITICAL**: Tool call `arguments` MUST be a JSON string, NOT an object!

```python
# CORRECT ✅
"arguments": '{"location": "SF"}'  # String

# WRONG ❌
"arguments": {"location": "SF"}  # Object
```

**Why**: Backend expects to `JSON.parse()` the string.

### Array Reconstruction

**Pattern**: Flattened attributes like:
```
gen_ai.completion.0.message.tool_calls.0.id = "call_abc"
gen_ai.completion.0.message.tool_calls.0.function.name = "get_weather"
```

**Must become**:
```python
tool_calls = [
    {
        "id": "call_abc",
        "function": {"name": "get_weather", ...}
    }
]
```

### Bundle Recompilation

After ANY DSL config change:
```bash
# Force recompile
rm src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl

# Auto-recompile on next import (development mode)
python -c "from honeyhive.tracer.processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor"
```

---

## 🏆 Expected Impact

### Before

- ❌ Tool-using agents broken (no tool_calls)
- ❌ Safety incidents not tracked (no refusal)
- ❌ Multimodal apps incomplete (no audio)
- ❌ 70% data loss on advanced fields

### After

- ✅ Tool-using agents work perfectly
- ✅ Safety tracking complete
- ✅ Multimodal support full
- ✅ 100% data fidelity

---

**Ready to implement?** Start with the **[detailed plan](./OPENAI_DSL_IMPLEMENTATION_PLAN.md)**!

**Last Updated**: 2025-09-30

