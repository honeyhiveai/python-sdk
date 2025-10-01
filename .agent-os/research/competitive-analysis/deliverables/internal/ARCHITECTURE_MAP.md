# HoneyHive SDK Architecture Map

**Analysis Date**: 2025-09-30  
**Framework Version**: 1.0  
**Repository**: github.com/honeyhiveai/python-sdk  
**Branch**: complete-refactor

---

## Executive Summary

The HoneyHive SDK follows a **modular, extensible architecture** built on OpenTelemetry primitives with a sophisticated **DSL-based provider configuration system**. The architecture emphasizes:

- **Separation of Concerns**: 9 distinct modules with clear responsibilities
- **Extensibility**: Registry-based patterns for transforms and conventions
- **Configuration-Driven**: YAML DSL for provider-specific logic
- **OTel Native**: Full integration with OpenTelemetry SDK
- **Type Safety**: Pydantic models throughout

**Key Metrics**:
- 94 Python files, 35,586 lines of code
- 9 core modules + 3 sub-module hierarchies
- 43 YAML configuration files
- 20+ external dependencies
- 4 semantic convention definitions

---

## 1. High-Level Module Organization

### Core SDK Structure

```
honeyhive/
├── api/              API client integration
├── cli/              Command-line interface
├── config/           Configuration management
├── evaluation/       Evaluation capabilities
├── models/           Data models
├── tracer/           ⭐ Core tracing functionality (primary focus)
└── utils/            Utility functions
```

### Tracer Module Organization (9 Sub-Modules)

```
tracer/
├── core/                          (6 files)  Core primitives
├── infra/                         (3 files)  Infrastructure
├── instrumentation/               (4 files)  Instrumentation APIs
├── integration/                   (6 files)  Framework integration
├── lifecycle/                     (4 files)  Lifecycle management
├── processing/                    (7 files)  Span processing pipeline
│   └── semantic_conventions/      (5 files)  Processing utilities
├── semantic_conventions/          (13 files) Convention system
│   ├── definitions/               (5 files)  Convention definitions
│   └── mapping/                   (4 files)  Mapping engine
└── utils/                         (6 files)  Tracer utilities
```

**Total Tracer Files**: ~50 Python files

---

## 2. Module Responsibilities

### 2.1 Core Module (Foundation)

**Purpose**: Core tracing primitives and base classes

**Key Files**:
- `base.py` - `HoneyHiveTracerBase` - Foundation tracer class
- `tracer.py` - Main tracer implementation
- `config_interface.py` - `TracerConfigInterface` - Configuration contract
- `context.py` - Context management
- `operations.py` - Span operations
- `__init__.py` - Public API

**Pattern**: Base class architecture with interface segregation

### 2.2 Infrastructure Module

**Purpose**: Environment and resource management

**Key Files**:
- `environment.py` - Environment detection
- `resources.py` - Resource attributes (service name, version, etc.)

**Pattern**: Factory pattern for resource creation

### 2.3 Instrumentation Module

**Purpose**: Instrumentation APIs and decorators

**Key Files**:
- `decorators.py` - `@trace` and other decorators
- `enrichment.py` - Span enrichment utilities
- `initialization.py` - SDK initialization

**Pattern**: Decorator pattern for non-invasive instrumentation

### 2.4 Integration Module

**Purpose**: Framework and instrumentor compatibility

**Key Files**:
- `compatibility.py` - Compatibility layer for external instrumentors
- `detection.py` - Framework/instrumentor auto-detection
- `error_handling.py` - Error handling middleware
- `http.py` - HTTP integration
- `processor.py` - Integration span processor

**Pattern**: Adapter pattern for external framework integration

### 2.5 Lifecycle Module

**Purpose**: Tracer lifecycle management

**Key Files**:
- `core.py` - Core lifecycle logic
- `flush.py` - Flush operations
- `shutdown.py` - Graceful shutdown

**Pattern**: Lifecycle hooks pattern

### 2.6 Processing Module (Span Pipeline)

**Purpose**: Span processing and export

**Key Files**:
- `span_processor.py` - **`HoneyHiveSpanProcessor`** (OTel SpanProcessor)
- `otlp_exporter.py` - OTLP export logic
- `otlp_profiles.py` - OTLP configuration profiles
- `otlp_session.py` - Session management
- `provider_interception.py` - Provider-specific interception
- `context.py` - Processing context
- `semantic_conventions/` - Processing utilities

**Pattern**: Pipeline pattern with processor chain

### 2.7 Semantic Conventions Module (★ Core Innovation)

**Purpose**: Multi-convention support and mapping

**Structure**:
```
semantic_conventions/
├── definitions/           Convention definitions
│   ├── honeyhive_v1_0_0.py     Native HoneyHive
│   ├── openinference_v0_1_31.py  Arize/Phoenix
│   ├── openlit_v1_0_0.py       OpenLit
│   └── traceloop_v0_46_2.py    Traceloop/OpenLLMetry
├── mapping/               Mapping engine
│   ├── patterns.py            Pattern matching
│   ├── rule_applier.py        Rule application
│   ├── rule_engine.py         Rule evaluation
│   └── transforms.py          Convention transforms
├── central_mapper.py      Central coordinator
├── discovery.py           Auto-detection
└── schema.py              HoneyHive schema (Pydantic)
```

**Key Files**:
- `central_mapper.py` - Orchestrates convention mapping
- `discovery.py` - Auto-detects which convention is in use
- `schema.py` - Pydantic models: `HoneyHiveEventSchema`, `ChatMessage`, `LLMInputs`, `LLMOutputs`, `LLMConfig`, `LLMMetadata`
- `processing/semantic_conventions/` - Processing utilities: bundle_loader, provider_processor, transform_registry, universal_processor

**Pattern**: Strategy pattern + Registry pattern

### 2.8 Utils Module

**Purpose**: Utility functions

**Key Files**:
- `event_type.py` - Event type constants
- `session.py` - Session management
- `propagation.py` - Context propagation
- `git.py` - Git integration
- `general.py` - General utilities

**Pattern**: Utility/helper pattern

---

## 3. Core Architectural Patterns

### 3.1 Base Class Hierarchy

**Pattern**: Abstract base classes and interfaces

**Evidence**:
```python
# core/base.py
class HoneyHiveTracerBase:  # Foundation tracer

# core/config_interface.py
class TracerConfigInterface:  # Configuration contract

# semantic_conventions/schema.py
class HoneyHiveEventSchema(BaseModel):  # Pydantic validation
class ChatMessage(BaseModel)
class LLMInputs(BaseModel)
class LLMOutputs(BaseModel)
```

**Purpose**: 
- Type safety via Pydantic
- Clear contracts via interfaces
- Extensibility via base classes

### 3.2 Registry Pattern

**Pattern**: Dictionary-based registries for extensibility

**Evidence**:
```python
# processing/semantic_conventions/transform_registry.py
TRANSFORM_REGISTRY: Dict[str, Any] = {
    "extract_user_message_content": extract_user_message_content,
    "extract_assistant_message_content": extract_assistant_message_content,
    # ... 18 total transforms
}

# lifecycle/core.py
_TRACER_REGISTRY: WeakValueDictionary[str, HoneyHiveTracer]
```

**Purpose**:
- Plugin-like extension of transforms
- Central location for shared logic
- Weak references for tracer lifecycle

### 3.3 Strategy Pattern (Semantic Conventions)

**Pattern**: Interchangeable convention mapping strategies

**Evidence**:
- 4 convention definition files (honeyhive, openinference, openlit, traceloop)
- Auto-detection in `discovery.py`
- Dynamic loading in `central_mapper.py`

**Purpose**:
- Support multiple instrumentor formats
- Auto-detect convention from span attributes
- Map to unified HoneyHive schema

### 3.4 Pipeline Pattern (Span Processing)

**Pattern**: Multi-stage processing pipeline

**Evidence**:
```python
# processing/span_processor.py
class HoneyHiveSpanProcessor(SpanProcessor):
    def on_start(self, span):
        # Stage 1: Enrichment on start
        self._apply_semantic_conventions_on_start(span)
    
    def on_end(self, span):
        # Stage 2: Process conventions
        self._process_span_semantic_conventions(span)
        # Stage 3: Extract session/user
        session_id = self._extract_session_id(span)
        # Stage 4: Convert to event
        event = self._convert_span_to_event(span)
        # Stage 5: Export
        self._send_via_client(event) or self._send_via_otlp(span)
```

**Purpose**:
- Clear separation of processing stages
- Extensible via OTel SpanProcessor interface

### 3.5 Decorator Pattern (Instrumentation)

**Pattern**: Decorators for non-invasive tracing

**Evidence**:
- `instrumentation/decorators.py` - `@trace` decorator
- `instrumentation/enrichment.py` - Span enrichment

**Purpose**:
- Minimal code changes for tracing
- Declarative span creation

---

## 4. Data Flow Architecture

### 4.1 Span Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        APPLICATION CODE                              │
│  (Direct SDK, Instrumentors, Frameworks)                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1: Span Creation (OTel SDK)                                  │
│  ├─ TracerProvider                                                  │
│  ├─ Tracer.start_span()                                            │
│  └─ Span created with attributes                                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 2: on_start() - HoneyHiveSpanProcessor                       │
│  └─ _apply_semantic_conventions_on_start()                          │
│     └─ Early enrichment (if needed)                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ... Application execution ...
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 3: on_end() - Semantic Convention Processing                 │
│  └─ _process_span_semantic_conventions()                            │
│     ├─ bundle_loader: Detect convention (HH/OpenInf/OpenLit/TL)    │
│     ├─ provider_processor: Detect provider (OpenAI/Anthropic/...)  │
│     ├─ transform_registry: Apply transforms (18 functions)          │
│     └─ universal_processor: Universal extraction logic              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 4: Event Conversion                                          │
│  ├─ _extract_session_id()                                           │
│  ├─ _extract_user_id()                                              │
│  ├─ _determine_event_type()                                         │
│  └─ _convert_span_to_event() → HoneyHiveEventSchema                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 5: Export                                                    │
│  ├─ _send_via_client() → HoneyHive API (if configured)             │
│  └─ _send_via_otlp() → OTLP HTTP Exporter (alternative)            │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Convention Detection Flow

```
Span Attributes →
    discovery.py (auto-detect convention) →
        Pattern matching on attribute prefixes →
            ├─ honeyhive_* → honeyhive_v1_0_0.py
            ├─ llm.* → openinference_v0_1_31.py  
            ├─ gen_ai.* + OpenLit patterns → openlit_v1_0_0.py
            └─ gen_ai.* + Traceloop patterns → traceloop_v0_46_2.py
```

### 4.3 Provider DSL Flow

```
Provider Detection (e.g., "openai") →
    Load YAML configs from config/dsl/providers/openai/ →
        ├─ structure_patterns.yaml
        ├─ navigation_rules.yaml
        ├─ field_mappings.yaml
        └─ transforms.yaml
    Compile DSL (compiler.py) →
        Generate Python extraction function →
            Execute against span attributes →
                Extract structured data →
                    Apply transforms →
                        Return HoneyHive schema
```

---

## 5. Configuration Architecture

### 5.1 DSL-Based Provider Configuration

**Location**: `config/dsl/`

**Structure**:
```
config/dsl/
├── compiler.py                (33,148 LOC) - DSL compiler
├── DSL_REFERENCE.md          (20,565 LOC) - Complete DSL docs
└── providers/                 (10 providers)
    ├── openai/
    │   ├── structure_patterns.yaml
    │   ├── navigation_rules.yaml
    │   ├── field_mappings.yaml
    │   └── transforms.yaml
    ├── anthropic/ (same 4 files)
    ├── aws_bedrock/
    ├── cohere/
    ├── gemini/
    ├── groq/
    ├── ibm/
    ├── mistral/
    ├── nvidia/
    └── ollama/
```

**Total Configuration Files**: 43 (40 provider YAMLs + 3 infrastructure files)

**DSL Capabilities**:
1. **Structure Patterns**: Define response object structures
2. **Navigation Rules**: Extract fields from nested attributes
3. **Field Mappings**: Map provider fields to HoneyHive schema
4. **Transforms**: Apply data transformations via registry

**Compiler Architecture**:
- Build-time compilation of YAML → Python functions
- Runtime execution for extraction
- Type-safe via Pydantic validation

### 5.2 Environment Configuration

**Method**: `pydantic-settings` + `python-dotenv`

**Key Files**:
- Uses `.env` for local development
- Environment variables for production
- Pydantic Settings for type-safe config

---

## 6. Dependency Architecture

### 6.1 Core Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **opentelemetry-api** | >=1.20.0 | OTel API primitives |
| **opentelemetry-sdk** | >=1.20.0 | OTel SDK implementation |
| **opentelemetry-exporter-otlp-proto-http** | >=1.20.0 | OTLP HTTP exporter |
| **httpx** | >=0.24.0 | HTTP client for API calls |
| **pydantic** | >=2.0.0 | Data validation & schemas |
| **pydantic-settings** | >=2.0.0 | Settings management |
| **wrapt** | >=1.14.0 | Decorator utilities |
| **pyyaml** | >=6.0 | YAML parsing (DSL) |
| **python-dotenv** | >=1.0.0 | .env file support |
| **click** | >=8.0.0 | CLI framework |

### 6.2 Development Dependencies

- **pytest** ecosystem (pytest, pytest-asyncio, pytest-cov, pytest-mock, pytest-xdist)
- **tox** - Test automation
- **black**, **isort** - Code formatting
- **flake8**, **mypy** - Linting & type checking

**Total Dependencies**: 20+

---

## 7. Extension Points & Extensibility

### 7.1 Transform Registry

**Location**: `processing/semantic_conventions/transform_registry.py`

**Mechanism**: Dictionary-based registry

**Current Transforms**: 18 built-in functions

**How to Extend**:
```python
# Add custom transform to TRANSFORM_REGISTRY
TRANSFORM_REGISTRY["my_custom_transform"] = my_function

# Reference in provider YAML
transforms.yaml:
  custom_field:
    implementation: "my_custom_transform"
```

### 7.2 Semantic Convention Definitions

**Location**: `semantic_conventions/definitions/`

**Current Conventions**: 4 (honeyhive, openinference, openlit, traceloop)

**How to Extend**:
- Create new file `my_convention_v1_0_0.py`
- Define `CONVENTION_DEFINITION` dict with detection patterns
- Auto-discovered by `discovery.py`

### 7.3 Provider DSL Configurations

**Location**: `config/dsl/providers/`

**Current Providers**: 10

**How to Extend**:
- Create new directory `config/dsl/providers/my_provider/`
- Add 4 YAML files (structure, navigation, mappings, transforms)
- Automatically compiled on initialization

### 7.4 Custom Span Processors

**Mechanism**: OTel SpanProcessor interface

**How to Extend**:
```python
from opentelemetry.sdk.trace import SpanProcessor

class MyCustomProcessor(SpanProcessor):
    def on_start(self, span, parent_context):
        # Custom logic
    def on_end(self, span):
        # Custom logic

# Register with TracerProvider
tracer_provider.add_span_processor(MyCustomProcessor())
```

### 7.5 Decorator-Based Instrumentation

**Location**: `instrumentation/decorators.py`

**How to Use**:
```python
from honeyhive.tracer import trace

@trace(name="my_function")
def my_function():
    # Automatically traced
```

---

## 8. Architectural Strengths

### 8.1 Modularity
✅ Clear separation of concerns across 9 modules  
✅ Each module has focused responsibility  
✅ Low coupling between modules

### 8.2 Extensibility
✅ Registry patterns for transforms and conventions  
✅ DSL-based provider configuration (no code changes for new providers)  
✅ Plugin-like semantic convention definitions  
✅ OTel SpanProcessor interface for custom pipelines

### 8.3 Configuration-Driven
✅ YAML DSL for complex provider-specific logic  
✅ Build-time compilation for performance  
✅ 33K line compiler with comprehensive DSL reference

### 8.4 Type Safety
✅ Pydantic models throughout  
✅ Type hints everywhere  
✅ Mypy for static type checking

### 8.5 OTel Native
✅ Full OpenTelemetry SDK integration  
✅ Not a wrapper - uses OTel primitives directly  
✅ OTLP export support  
✅ W3C propagation standards

### 8.6 Multi-Convention Support
✅ Supports 4 different semantic conventions  
✅ Auto-detection of convention in use  
✅ Unified output schema regardless of input convention

---

## 9. Architectural Considerations

### 9.1 Complexity
⚠️ **33K line DSL compiler** - High complexity for provider configuration  
⚠️ **Multi-stage pipeline** - Many processing stages to understand  
⚠️ **4 conventions** - Complex detection and mapping logic

**Mitigation**: Excellent documentation (20K line DSL reference)

### 9.2 Configuration Proliferation
⚠️ **43 YAML files** - Large configuration surface area  
⚠️ **10 providers × 4 files** - Potential for inconsistency

**Mitigation**: DSL schema validation, compiler checks

### 9.3 Runtime Overhead
⚠️ **Multi-stage processing** - Potential performance impact  
⚠️ **Dynamic convention detection** - Runtime cost

**Note**: To be quantified in Task 1.3 (Performance Benchmarks)

### 9.4 Dependency on OTel Versions
⚠️ **OTel >=1.20.0** - Tied to specific OTel version range  

**Mitigation**: Well-defined version constraints

---

## Summary

The HoneyHive SDK architecture is characterized by:

1. **Modular Design**: 9 well-defined modules with clear responsibilities
2. **DSL-Driven Configuration**: Sophisticated YAML-based provider configuration system
3. **Multi-Convention Support**: Unique capability to handle 4 different semantic conventions
4. **OTel Native**: Full integration with OpenTelemetry SDK
5. **Extensible**: Registry patterns, plugin architectures, open interfaces

**Key Innovation**: The **DSL-based provider configuration system** with build-time compilation, allowing new providers to be added via YAML configuration without code changes.

**Architectural Maturity**: High - clear patterns, type safety, comprehensive testing infrastructure

---

**Analysis Complete**: Phase 1, Task 2  
**Next**: Performance Benchmarks (Task 1.3)
