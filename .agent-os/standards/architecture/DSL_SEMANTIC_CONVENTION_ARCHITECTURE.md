# DSL-Based Semantic Convention Translation Architecture

**Document Version**: 1.0  
**Date**: 2025-09-30  
**Status**: Authoritative Architecture Reference  

---

## 🎯 Executive Summary

HoneyHive's platform uses a **declarative, language-agnostic, centrally-managed DSL** to translate any OpenTelemetry semantic convention (GenAI, OpenInference, Traceloop, custom) into the unified `honeyhive_*` convention. This architecture enables:

1. **Backend Simplification**: Reduce backend processing from 1,120 lines of conditional logic to ~100 lines of attribute unwrapping
2. **True Neutrality**: Accept spans from ANY instrumentor (OpenLit, Traceloop, direct OTEL, custom)
3. **Multi-Language Consistency**: Same DSL works across Python SDK, TypeScript SDK, Go SDK, and backend
4. **Centralized Maintenance**: Update once in DSL repo → all consumers benefit
5. **100% Data Fidelity**: Ensure all provider response data is preserved through translation

---

## 📊 The Problem: Backend Processing Mess

### Current State (Before DSL Architecture)

**File**: `../hive-kube/kubernetes/ingestion_service/app/services/otel_processing_service.js`  
**Size**: 1,120 lines of hardcoded attribute processing

```javascript
// Lines 90-291: The Mess™
function parseTrace(trace) {
  for (let key in parsedAttributes) {
    let value = parsedAttributes[key];
    
    // Hardcoded rules for every semantic convention
    if (key === 'traceloop.association.properties.session_id') {
      session_id = value;
    } else if (key.startsWith('honeyhive_inputs')) {
      setNestedValue(inputs, key.split('.').slice(1), value);
    } else if (key.startsWith('honeyhive_outputs')) {
      setNestedValue(outputs, key.split('.').slice(1), value);
    } else if (key === 'gen_ai.system') {
      eventConfig['provider'] = value;
    } else if (key === 'gen_ai.request.model') {
      eventConfig['model'] = value;
    } else if (key === 'gen_ai.request.max_tokens') {
      eventConfig['max_completion_tokens'] = value;
    } else if (key === 'gen_ai.prompt') {
      if (llmRequestType === 'chat') {
        inputs['chat_history'] = value;
      } else if (llmRequestType === 'rerank') {
        inputs['nodes'] = value.map((prompt) => prompt.content);
      }
      // ... complex nested logic
    } else if (key === 'gen_ai.completion') { ... }
    else if (key === 'llm.usage.total_tokens') { ... }
    else if (key === 'llm.user') { ... }
    else if (key === 'llm.headers') { ... }
    else if (key.startsWith('ai.prompt.')) { ... }
    else if (key.startsWith('ai.response.')) { ... }
    else if (key.startsWith('gen_ai.request.')) { ... }
    // ... 100+ more else-if blocks
    else {
      eventMetadata[key] = value;
    }
  }
}
```

### Problems with Current Architecture

| Problem | Impact |
|---------|--------|
| **Backend owns semantic convention knowledge** | Every new instrumentor requires backend code changes |
| **Hardcoded attribute extraction** | Difficult to test, maintain, and extend |
| **Duplicate logic** | `parseTrace()`, `parseNextJSTrace()`, etc. duplicate rules |
| **No separation of concerns** | Backend mixes protocol handling + business logic |
| **Language lock-in** | JavaScript-only logic, can't reuse in Python/Go SDKs |
| **Deployment coupling** | Convention changes require backend deployment |
| **No fallback consistency** | Fallback path may diverge from SDK processing |

---

## ✅ The Solution: DSL-Based Translation Architecture

### Core Concept

**Declarative YAML configs** define how to translate any semantic convention into `honeyhive_*` attributes.

**Platform-wide application**: Same DSL used in Python SDK, TypeScript SDK, Go SDK, and backend fallback processor.

### Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                  DSL Configuration Repository                │
│                 (Future: honeyhiveai/semantic-conventions-dsl)│
│                                                               │
│  providers/                                                   │
│  ├── openai/                                                 │
│  │   ├── structure_patterns.yaml    # Response structure     │
│  │   ├── navigation_rules.yaml      # How to navigate attrs  │
│  │   ├── field_mappings.yaml        # Convention mappings    │
│  │   └── transforms.yaml             # Data transformations  │
│  ├── anthropic/                                              │
│  ├── gemini/                                                 │
│  └── ...                                                      │
│                                                               │
│  conventions/                                                 │
│  ├── gen_ai/         # GenAI semconv → honeyhive_*          │
│  ├── openinference/  # OpenInference → honeyhive_*          │
│  ├── traceloop/      # Traceloop → honeyhive_*              │
│  └── ...                                                      │
│                                                               │
│  transforms/                                                  │
│  ├── python/         # Python transform implementations       │
│  ├── javascript/     # JS transform implementations          │
│  └── go/             # Go transform implementations          │
└─────────────────────────────────────────────────────────────┘
                              ↓
            ┌─────────────────┴─────────────────┐
            ↓                                   ↓
┌───────────────────────┐           ┌───────────────────────┐
│    Python SDK         │           │   TypeScript SDK      │
│                       │           │                       │
│  Uses DSL to:         │           │  Uses DSL to:         │
│  - Detect convention  │           │  - Detect convention  │
│  - Translate to       │           │  - Translate to       │
│    honeyhive_*        │           │    honeyhive_*        │
│  - Export via OTLP    │           │  - Export via OTLP    │
└───────────────────────┘           └───────────────────────┘
            ↓                                   ↓
            └─────────────────┬─────────────────┘
                              ↓
                    ┌─────────────────────┐
                    │  OTLP (HoneyHive)   │
                    └─────────────────────┘
                              ↓
            ┌─────────────────────────────────────────┐
            │      Backend Ingestion Service          │
            │                                          │
            │  Primary Path: honeyhive_* attributes   │
            │  ├─ Simple unwrap & validate            │
            │  └─ Convert to HoneyHive events         │
            │                                          │
            │  Fallback Path: Other conventions       │
            │  ├─ Uses SAME DSL configs               │
            │  ├─ Translate to honeyhive_* (runtime)  │
            │  └─ Convert to HoneyHive events         │
            └─────────────────────────────────────────┘
```

---

## 🔄 Data Flow Scenarios

### Scenario 1: HoneyHive SDK User (Pre-processed Path) ✅ Preferred

```
1. Provider API (OpenAI, Anthropic, etc.)
   ↓ Returns: Complex JSON response
   
2. Instrumentor (OpenLit, Traceloop, Manual, etc.)
   ↓ Sets: gen_ai.*, llm.*, custom attributes on span
   
3. HoneyHive SDK Span Processor
   ↓ Detects: Semantic convention from span attributes
   ↓ Loads: DSL YAML configs for that convention
   ↓ Translates: gen_ai.* → honeyhive_* (using DSL rules)
   ↓ Adds: honeyhive_outputs.*, honeyhive_inputs.*, etc.
   
4. OTLP Export
   ↓ Span now has: Original attributes + honeyhive_* attributes
   
5. Backend Ingestion Service (PRIMARY PATH)
   ↓ Reads: honeyhive_outputs.*, honeyhive_inputs.*, etc.
   ↓ Validates: JSON structure, unwraps JSON strings
   ↓ Converts: honeyhive_* → HoneyHive event schema
   
6. HoneyHive Events (Database)
   ↓ Stored: Structured event data
   
7. HoneyHive UI
   ↓ Displays: Tool calls, messages, metrics, etc.
```

**Advantages**:
- ✅ Translation happens ONCE (in SDK, at span creation)
- ✅ Backend processing is fast (simple unwrap)
- ✅ Data is pre-validated (SDK ensures correctness)

### Scenario 2: Non-HoneyHive User (Fallback Path) 🔄 Compatibility

```
1. Provider API (OpenAI, Anthropic, etc.)
   ↓ Returns: Complex JSON response
   
2. OpenLit/Traceloop Direct (no HoneyHive SDK)
   ↓ Sets: gen_ai.*, llm.* attributes on span
   
3. OTLP Export to HoneyHive
   ↓ Span has: Only gen_ai.*, llm.* (no honeyhive_*)
   
4. Backend Ingestion Service (FALLBACK PATH)
   ↓ Detects: No honeyhive_* attributes present
   ↓ Detects: Semantic convention from span attributes
   ↓ Loads: SAME DSL YAML configs as SDK
   ↓ Translates: gen_ai.* → honeyhive events (using DSL)
   
5. HoneyHive Events (Database)
   ↓ Stored: Structured event data
   
6. HoneyHive UI
   ↓ Displays: Tool calls, messages, metrics, etc.
```

**Advantages**:
- ✅ Works even without HoneyHive SDK
- ✅ Uses SAME DSL as SDK (consistency guaranteed)
- ✅ Enables gradual migration (legacy support)

---

## 🏗️ DSL Structure

### Provider-Specific Configs

**Location**: `config/dsl/providers/{provider_name}/`

#### 1. Structure Patterns (`structure_patterns.yaml`)
```yaml
# Defines the expected structure of provider responses
patterns:
  chat_completion:
    type: object
    nested_arrays:
      - choices
      - messages
      - tool_calls
```

#### 2. Navigation Rules (`navigation_rules.yaml`)
```yaml
# Defines how to navigate span attributes to extract data
rules:
  output_message:
    source: "gen_ai.completion.0.message"
    fallback: "llm.output.message"
```

#### 3. Field Mappings (`field_mappings.yaml`)
```yaml
# Maps convention attributes to honeyhive_* attributes
mappings:
  gen_ai.request.model:
    target: "honeyhive_config.model"
  gen_ai.response.finish_reasons:
    target: "honeyhive_outputs.finish_reason"
```

#### 4. Transforms (`transforms.yaml`)
```yaml
# Defines data transformations
transforms:
  tool_calls:
    implementation: "reconstruct_array_from_flattened"
    params:
      prefix: "gen_ai.completion.0.message.tool_calls"
```

### Transform Registry

**Location**: `src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py`

```python
TRANSFORM_REGISTRY = {
    "reconstruct_array_from_flattened": reconstruct_array_from_flattened,
    "extract_user_message_content": extract_user_message_content,
    "extract_tool_call_function_name": extract_tool_call_function_name,
    # ... 18+ transform functions
}
```

**Equivalent in other languages**:
- JavaScript: `transforms/javascript/registry.js`
- Go: `transforms/go/registry.go`

---

## 🌍 Multi-Language Support

### Current Implementation (Python)

**Location**: `config/dsl/` in Python SDK

**Usage**:
```python
from honeyhive.tracer.processing.semantic_conventions import apply_dsl

def on_end(span):
    convention = detect_convention(span.attributes)
    apply_dsl(span, convention)  # Uses YAML + transform_registry.py
    export_span(span)
```

### Future: TypeScript SDK

**Location**: `config/dsl/` (git submodule or npm package)

**Usage**:
```typescript
import { applyDSL, detectConvention } from '@honeyhive/semantic-conventions-dsl';

function onEnd(span: Span): void {
  const convention = detectConvention(span.attributes);
  applyDSL(span, convention);  // Uses YAML + transforms/javascript/registry.js
  exportSpan(span);
}
```

### Future: Go SDK

**Location**: `config/dsl/` (git submodule or Go module)

**Usage**:
```go
import "github.com/honeyhiveai/semantic-conventions-dsl/go"

func onEnd(span Span) {
    convention := dsl.DetectConvention(span.Attributes())
    dsl.ApplyDSL(&span, convention)  // Uses YAML + transforms/go/registry.go
    exportSpan(span)
}
```

### Backend JavaScript

**Location**: `dsl/` (git submodule or npm package in hive-kube)

**Usage**:
```javascript
const { applyDSL, detectConvention } = require('@honeyhive/semantic-conventions-dsl');

function parseTrace(trace) {
  for (let span of spans) {
    // Primary path: honeyhive_* attributes (pre-processed by SDK)
    if (hasHoneyhiveAttributes(span)) {
      event = unwrapHoneyhiveAttributes(span);
    }
    // Fallback path: non-HoneyHive span (apply DSL)
    else {
      const convention = detectConvention(span.attributes);
      const honeyhiveAttrs = applyDSL(span.attributes, convention);
      event = convertToEvent(honeyhiveAttrs);
    }
    storeEvent(event);
  }
}
```

---

## 🎯 Architecture Benefits

### 1. Backend Simplification

**Before**: 1,120 lines of conditional logic  
**After**: ~100 lines of attribute unwrapping

```javascript
// BEFORE: Hardcoded rules (1,120 lines)
if (key === 'gen_ai.system') { ... }
else if (key === 'gen_ai.request.model') { ... }
// ... 100+ more else-if blocks

// AFTER: DSL-powered (~20 lines)
if (hasHoneyhiveAttributes(span)) {
  event = unwrapHoneyhiveAttributes(span);
} else {
  event = applyDSL(span.attributes, detectConvention(span));
}
```

### 2. Single Source of Truth

- **One DSL config** per provider/convention
- **Used everywhere**: Python SDK, TypeScript SDK, Go SDK, Backend
- **Update once**, propagates to all consumers

### 3. Language Agnostic

- **YAML configs** work in any language
- **Transform implementations** in each language (Python, JS, Go)
- **Same logic**, different runtime

### 4. Centralized Repository (Future)

```
honeyhiveai/semantic-conventions-dsl/
├── providers/          # Provider-specific DSL configs
├── conventions/        # Convention translation rules
├── transforms/         # Transform implementations per language
└── README.md

# Consumers reference it
python-sdk/config/dsl/ → git submodule
typescript-sdk/config/dsl/ → git submodule
hive-kube/ingestion_service/dsl/ → git submodule
```

### 5. Versioning & Rollout

- **DSL repo** versioned independently (semver)
- **SDKs** pin to specific DSL version
- **Backend** can use latest or pinned version
- **Gradual rollout** of new conventions

### 6. Testing Strategy

```python
# Test DSL configs (unit tests)
def test_openai_tool_calls_translation():
    span_attrs = {
        "gen_ai.completion.0.message.tool_calls.0.id": "call_abc",
        "gen_ai.completion.0.message.tool_calls.0.function.name": "get_weather",
    }
    result = apply_dsl(span_attrs, "gen_ai")
    assert result["honeyhive_outputs.tool_calls"][0]["id"] == "call_abc"

# Test backend fallback (integration tests)
def test_backend_fallback_gen_ai():
    span = create_gen_ai_span()
    event = backend_process_span(span)
    assert event["outputs"]["tool_calls"][0]["id"] == "call_abc"
```

---

## 🚀 Competitive Advantage

### What Competitors Do

**OpenLit, Traceloop, Arize, Langfuse**:
- ❌ Hardcode attribute extraction in their language (Python, JS, etc.)
- ❌ Different logic in different SDKs (Python ≠ JS ≠ Go)
- ❌ Backend duplicates extraction logic (or trusts SDK output blindly)
- ❌ No fallback for non-SDK usage
- ❌ No centralized semantic convention management

### What HoneyHive Does (Unique)

- ✅ **Declarative DSL** (YAML configs, language-agnostic)
- ✅ **Single source of truth** (one config, all consumers)
- ✅ **Platform-wide consistency** (SDK = Backend)
- ✅ **Fallback support** (works even without HoneyHive SDK)
- ✅ **Multi-language** (Python, JS, Go use same DSL)
- ✅ **Centralized updates** (update DSL → all consumers benefit)
- ✅ **True neutrality** (accept ANY instrumentor, translate via DSL)

---

## 📋 Implementation Roadmap

### Phase 1: Python SDK (Current) ✅
- [x] DSL configs embedded in `config/dsl/`
- [x] Transform registry in Python
- [x] Span processor applies DSL
- [x] 10 providers configured

### Phase 2: Backend Fallback 🔄 In Progress
- [ ] Integrate DSL into `otel_processing_service.js`
- [ ] Replace 1,120-line conditional logic with DSL
- [ ] Keep legacy code as fallback-of-fallback
- [ ] Test parity with current logic

### Phase 3: Centralized DSL Repo 📅 Planned
- [ ] Create `honeyhiveai/semantic-conventions-dsl` repo
- [ ] Move DSL configs from Python SDK
- [ ] Implement JavaScript transforms
- [ ] Version and publish (npm/pip/go mod)

### Phase 4: TypeScript SDK 📅 Planned
- [ ] Reference DSL repo (npm package or submodule)
- [ ] Implement span processor with DSL
- [ ] Test parity with Python SDK

### Phase 5: Go SDK 📅 Planned
- [ ] Reference DSL repo (Go module or submodule)
- [ ] Implement span processor with DSL
- [ ] Test parity with Python/TypeScript SDKs

### Phase 6: Provider Schema Coverage 📅 Ongoing
- [ ] Extract all OpenAI operation schemas (2/8 complete)
- [ ] Extract Anthropic schemas
- [ ] Extract Gemini schemas
- [ ] Extract Bedrock schemas
- [ ] Ensure `honeyhive_*` can represent 100% of provider data

---

## 🔍 Critical Questions

### 1. How much provider coverage does DSL need?

**Answer**: **100% of provider response schemas**

**Rationale**: 
- Neutrality approach means we accept ANY instrumentor
- Different instrumentors may expose different provider fields
- To avoid data loss, `honeyhive_*` must be able to represent everything

**Current State**: OpenAI 2/8 operations (25%)

### 2. How do we ensure DSL correctness?

**Answer**: **Multi-level validation**

1. **Schema Validation**: Provider response schemas → DSL configs cover all fields
2. **Unit Tests**: DSL configs → Transform functions produce correct output
3. **Integration Tests**: Real spans → SDK + Backend produce same events
4. **Regression Tests**: Version-to-version parity

### 3. How do we handle DSL updates?

**Answer**: **Versioned rollout with backward compatibility**

1. **DSL repo** uses semantic versioning (e.g., `v1.2.0`)
2. **SDKs** pin to specific DSL version in `requirements.txt`/`package.json`
3. **Backend** can use latest (for fallback) or pinned version
4. **Breaking changes** increment major version (e.g., `v1.x.x` → `v2.0.0`)
5. **Gradual migration** supported (old and new conventions coexist)

### 4. What if an instrumentor doesn't follow conventions?

**Answer**: **Custom DSL configs**

```yaml
# conventions/custom_instrumentor_v1/field_mappings.yaml
mappings:
  custom.attribute.path:
    target: "honeyhive_outputs.field"
```

The DSL is extensible to handle non-standard conventions.

---

## 📚 Related Documentation

- **DSL Reference**: `config/dsl/DSL_REFERENCE.md` - Complete DSL syntax guide
- **Transform Registry**: `src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py` - Available transforms
- **Provider Schemas**: `provider_response_schemas/` - Provider API response schemas
- **Competitive Analysis**: `.agent-os/research/competitive-analysis/` - How this compares to competitors

---

## 🔐 Maintenance Notes

### When to Update This Document

- ✏️ When adding support for a new language SDK
- ✏️ When moving DSL to centralized repo
- ✏️ When changing DSL structure or semantics
- ✏️ When adding new translation capabilities
- ✏️ When backend fallback implementation changes

### Document Owners

- **Architecture**: Platform Team
- **DSL Design**: SDK Team
- **Backend Integration**: Backend Team
- **Schema Coverage**: Product Team

---

**Last Updated**: 2025-09-30  
**Next Review**: When DSL is moved to centralized repo

