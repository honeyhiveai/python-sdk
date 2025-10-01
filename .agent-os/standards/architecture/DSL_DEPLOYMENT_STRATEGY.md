# DSL Deployment Strategy

**Date**: 2025-10-01  
**Status**: Strategic Plan  
**Priority**: Post SDK v0.1.0 Release

---

## 🎯 Strategic Overview

The DSL work is **deferred** to allow immediate release of the new SDK. The DSL will then be developed and deployed in a phased approach:

### Phase Sequence

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 0: SDK v0.1.0 Release (IMMEDIATE)                     │
│ - Release current SDK architecture                          │
│ - Keep existing honeyhive_* attribute pattern               │
│ - DSL work DEFERRED                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Standalone DSL Repository (Backend First)          │
│ - Create standalone DSL repository                          │
│ - Implement for ingestion service (backend)                 │
│ - DSL processes incoming OTLP spans                         │
│ - Outputs canonical HoneyHive schema                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: SDK Native Canonical Schema (SDK Refactor)         │
│ - Update Python SDK to use canonical schema natively        │
│ - REMOVE honeyhive_* intermediate layer                     │
│ - SDK works directly with 4-section schema                  │
│ - Integrate standalone DSL as dependency                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Phase 0: SDK v0.1.0 Release (IMMEDIATE)

### Goal
Release the new SDK architecture immediately without DSL dependency.

### Current State
- SDK uses `honeyhive_*` span attributes as intermediate layer
- Semantic convention processing exists but not using DSL
- Works but has redundant flatten/unflatten cycle

### Action Items
- ✅ No changes required for DSL
- ✅ Release SDK as-is
- ✅ Document current architecture
- ✅ Plan for Phase 1

### Timeline
**ASAP** - No blockers

---

## 📋 Phase 1: Standalone DSL Repository (Backend First)

### Goal
Build DSL as standalone, cross-language library. Deploy in ingestion service first.

### Repository Structure
```
honeyhive-dsl/
├── schemas/                    # Provider response schemas
│   ├── openai/
│   ├── anthropic/
│   └── ...
├── config/                     # DSL YAML configs
│   ├── providers/
│   │   ├── openai/
│   │   │   ├── structure_patterns.yaml
│   │   │   ├── navigation_rules.yaml
│   │   │   ├── field_mappings.yaml
│   │   │   └── transforms.yaml
│   │   └── ...
│   └── semantic_conventions/
│       ├── openinference/
│       ├── traceloop/
│       └── ...
├── compiler/                   # DSL compiler
│   └── build.py
├── bundles/                    # Compiled DSL bundles
│   ├── openai.json.gz
│   ├── anthropic.json.gz
│   └── universal.json.gz
├── runtime/                    # Runtime libraries
│   ├── python/
│   ├── typescript/
│   └── go/
└── docs/
```

### Implementation Focus

**Target**: Ingestion Service (Backend)

The DSL will process incoming OTLP spans in the backend:

```
[OTLP Span from ANY source]
    (OpenInference, Traceloop, Direct SDK, etc.)
           ↓
[Ingestion Service]
           ↓
[DSL Processing] ← STANDALONE LIBRARY
    - Detect source/provider
    - Extract data using navigation rules
    - Apply transforms
    - Map to canonical schema
           ↓
[Canonical HoneyHive Event]
    {
      "inputs": {...},
      "outputs": {...},
      "config": {...},
      "metadata": {...}
    }
           ↓
[Database Storage]
```

### Key Features

1. **Cross-Language Runtime**
   - Python runtime (for ingestion service)
   - TypeScript runtime (for future services)
   - Go runtime (for future services)

2. **O(1) Detection & Lookup**
   - Precompiled inverted indexes
   - Fast pattern matching
   - Efficient bundle loading

3. **100% Provider Coverage**
   - All major LLM providers
   - All semantic conventions
   - Framework patterns

### Success Criteria

- ✅ DSL successfully processes all trace sources
- ✅ 100% data fidelity (no loss from original spans)
- ✅ <50ms processing time per span
- ✅ Works in ingestion service (Python runtime)
- ✅ Validated against 385+ production events

### Timeline
**Post SDK Release** - 4-6 weeks

---

## 📋 Phase 2: SDK Native Canonical Schema (SDK Refactor)

### Goal
Refactor Python SDK to work with canonical schema natively, eliminating the `honeyhive_*` intermediate layer.

### Current Architecture (Phase 0)

```python
# Step 1: Instrumentor sets attributes
span.set_attribute("gen_ai.completion.0.role", "assistant")

# Step 2: DSL processes to canonical schema
event_data = {
    "outputs": {"role": "assistant"}
}

# Step 3: FLATTEN to honeyhive_* attributes (REDUNDANT!)
span.set_attribute("honeyhive_outputs.role", "assistant")

# Step 4: UNFLATTEN back to canonical (REDUNDANT!)
event = {
    "outputs": {"role": "assistant"}
}

# Step 5: Send to API
client.create_event(event)
```

### Target Architecture (Phase 2)

```python
# Step 1: Instrumentor sets attributes
span.set_attribute("gen_ai.completion.0.role", "assistant")

# Step 2: DSL processes to canonical schema
event_data = {
    "outputs": {"role": "assistant"}
}

# Step 3: DIRECTLY store canonical schema in span context
# (using span context variables, NOT attributes)
span_context.set("honeyhive_event", event_data)

# Step 4: Send to API directly
client.create_event(event_data)
```

**OR** even better:

```python
# Step 1: Instrumentor sets attributes
span.set_attribute("gen_ai.completion.0.role", "assistant")

# Step 2: On span end, process ONCE and send DIRECTLY
def on_end(span):
    # Extract attributes
    attributes = span.attributes
    
    # Process with DSL (from standalone lib)
    event_data = dsl_processor.process(attributes)
    
    # Send directly to API (no intermediate storage on span)
    client.create_event(event_data)
```

### Key Changes

1. **Remove `honeyhive_*` Attributes**
   - No more `honeyhive_inputs.*`, `honeyhive_outputs.*`, etc.
   - No redundant flatten/unflatten cycle
   - Cleaner span attributes

2. **Native Schema Objects**
   - Work directly with canonical schema dicts
   - Type-safe using Pydantic models
   - No string serialization

3. **Integrate Standalone DSL**
   - Import from `honeyhive-dsl` package
   - Use precompiled bundles
   - Leverage cross-language work

4. **Simplified Span Processor**
   ```python
   class HoneyHiveSpanProcessor:
       def on_end(self, span):
           # Get raw attributes
           attributes = dict(span.attributes)
           
           # Process with DSL (standalone lib)
           from honeyhive_dsl import DSLProcessor
           event_data = DSLProcessor.process(attributes)
           
           # Add span metadata
           event_data.update({
               "event_id": str(span.context.span_id),
               "start_time": span.start_time,
               "end_time": span.end_time,
               "duration": span.end_time - span.start_time
           })
           
           # Send directly to API
           self.client.create_event(event_data)
   ```

### Migration Path

**For Direct SDK Users** (using `@trace` decorator):

```python
# Before (Phase 0/1)
@trace(
    event_type="model",
    outputs={"role": "assistant", "content": "..."}  # Sets honeyhive_outputs.*
)
def my_function():
    pass

# After (Phase 2)
@trace(
    event_type="model",
    outputs={"role": "assistant", "content": "..."}  # DIRECTLY as canonical schema
)
def my_function():
    pass
```

**API stays the same**, but internal handling changes to avoid flattening.

**For Instrumentor Users**:

No changes required - DSL handles the translation transparently.

### Success Criteria

- ✅ No `honeyhive_*` attributes on spans
- ✅ SDK works directly with canonical schema
- ✅ 100% backward compatibility for user-facing APIs
- ✅ Faster processing (no flatten/unflatten)
- ✅ Cleaner, more maintainable code

### Timeline
**After Phase 1** - 2-3 weeks

---

## 📊 Benefits of This Approach

### Phase 1 Benefits (Backend DSL)

1. **Validate DSL Before SDK Integration**
   - Test with real production traffic
   - Optimize performance in production environment
   - Fix bugs before SDK dependency

2. **Backend Can Handle Legacy SDKs**
   - Old SDKs keep sending `honeyhive_*` attributes
   - Backend DSL can still process other sources
   - Smooth migration path

3. **Cross-Language Foundation**
   - Build once, use everywhere
   - TypeScript/Go services can use same DSL
   - Centralized schema management

### Phase 2 Benefits (SDK Refactor)

1. **Cleaner Architecture**
   - No redundant conversions
   - Direct schema manipulation
   - Less code complexity

2. **Better Performance**
   - Eliminate flatten/unflatten cycle
   - Fewer span attribute operations
   - Faster span processing

3. **Better Type Safety**
   - Work with typed Pydantic models
   - No string serialization/deserialization
   - IDE autocomplete for schema fields

4. **Easier Maintenance**
   - Canonical schema is single source of truth
   - Changes in one place
   - Clear data flow

---

## 🔗 Dependencies

### Phase 1 → Phase 2

Phase 2 **depends on** Phase 1 because:
- SDK will import standalone DSL library
- DSL must be battle-tested in production
- Cross-language runtime must be stable

### Critical Resources

1. **Canonical Schema Analysis** (✅ COMPLETE)
   - 385 production events analyzed
   - Schema patterns documented
   - Mapping rules defined
   - Files: `canonical_schema_analysis/`

2. **Provider Response Schemas** (🚧 IN PROGRESS)
   - OpenAI schema complete
   - Need: Anthropic, Google, etc.
   - Location: `provider_response_schemas/`

3. **Current DSL Config** (✅ EXISTS)
   - 10 providers configured
   - Location: `config/dsl/providers/`
   - Status: Needs update for 100% coverage

---

## 📅 Timeline Summary

| Phase | Timeline | Status | Blocker |
|-------|----------|--------|---------|
| Phase 0: SDK Release | **ASAP** | 🟢 Ready | None |
| Phase 1: Standalone DSL | 4-6 weeks | ⏸️ Deferred | SDK release |
| Phase 2: SDK Refactor | 2-3 weeks | ⏸️ Deferred | Phase 1 complete |

**Total Time**: 6-9 weeks after SDK release

---

## 🎓 Key Architectural Decisions

### Decision 1: Backend First, Then SDK

**Rationale**:
- Validates DSL in production before SDK dependency
- Allows legacy SDK versions to work during migration
- Reduces risk of SDK breaking changes

### Decision 2: Standalone Repository

**Rationale**:
- DSL is cross-language (Python, TypeScript, Go)
- Independent versioning
- Can be used by other services
- Clearer ownership

### Decision 3: Remove `honeyhive_*` Entirely

**Rationale**:
- Redundant flatten/unflatten cycle
- Performance overhead
- Complexity without benefit
- Canonical schema is the clean interface

### Decision 4: Canonical Schema is Source of Truth

**Rationale**:
- Production-validated (385 events)
- Simple, flat structure
- Clear contract for all systems
- Backend already uses this format

---

## 📋 Action Items

### Immediate (Pre-SDK Release)
- [x] Document current architecture
- [x] Analyze canonical schema (385 production events)
- [x] Define mapping rules
- [x] Document DSL deployment strategy

### Phase 1 (Standalone DSL)
- [ ] Create `honeyhive-dsl` repository
- [ ] Port DSL config from Python SDK
- [ ] Build Python runtime
- [ ] Integrate into ingestion service
- [ ] Validate with production traffic
- [ ] Build TypeScript/Go runtimes
- [ ] Achieve 100% provider coverage

### Phase 2 (SDK Refactor)
- [ ] Add `honeyhive-dsl` as SDK dependency
- [ ] Refactor span processor to use DSL directly
- [ ] Remove `honeyhive_*` attribute flattening
- [ ] Update `@trace` decorator to work with canonical schema
- [ ] Update all tests
- [ ] Migration guide for users
- [ ] Release SDK v0.2.0

---

## 🔍 Related Documentation

- [Canonical Schema Analysis](../../../canonical_schema_analysis/CANONICAL_SCHEMA_ANALYSIS.md) - Production event analysis
- [DSL Mapping Rules](../../../canonical_schema_analysis/DSL_MAPPING_RULES.md) - Implementation rules
- [DSL Flow](./DSL_TO_HONEYHIVE_SCHEMA_FLOW.md) - Current architecture
- [SDK Serialization](./HONEYHIVE_SDK_SERIALIZATION_PATTERN.md) - Current SDK patterns

---

**Last Updated**: 2025-10-01  
**Status**: Strategic Plan Approved  
**Next Review**: After SDK v0.1.0 Release

