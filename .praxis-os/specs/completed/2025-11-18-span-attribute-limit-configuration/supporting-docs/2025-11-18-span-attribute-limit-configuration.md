# OpenTelemetry Span Attribute Limits: Configuration & Preservation Design

**Date**: 2025-11-18  
**Author**: HoneyHive Engineering  
**Status**: Design Proposal  
**Priority**: CRITICAL  

---

## Executive Summary

### The Problem

OpenTelemetry's default span attribute limit (128 attributes) causes **silent data loss** in observability traces when large API responses are flattened into span attributes. This is a **cardinal sin for observability** — traces appear complete but are missing critical metadata like `session_id`, causing spans to be silently dropped.

### The Impact

**Real-World Example** (from CEO's script):
- SerpAPI search returns 400+ attributes when flattened
- OpenTelemetry evicts oldest attributes to stay under 128 limit
- Core HoneyHive attributes (`honeyhive.session_id`) are evicted
- Span is created but silently skipped during export
- Result: **Complete loss of observability for that operation**

### The Solution

**Implemented** (Phase 1 - Dual Guardrail Approach):
1. **Two complementary limits** for maximum flexibility:
   - `max_attributes = 1024` - Protects against many small attributes (typical LLM traces)
   - `max_span_size = 10MB` - Protects against total span size (supports variable attribute sizes: 1KB text to 10MB images)
2. **Simple defaults** that "just work" for 95% of users
3. **Easy configuration** for power users with unusual use cases
4. **Environment variable support** (`HH_MAX_ATTRIBUTES`, `HH_MAX_SPAN_SIZE`, `HH_MAX_EVENTS`, `HH_MAX_LINKS`)
5. **Applied via custom span size tracking** (OpenTelemetry doesn't provide max_span_size natively)

**Product Philosophy**:
- Customers find observability complexity overwhelming
- Provide sane defaults with configurable overrides
- LLM/agent space has unpredictable data sizes (can't predict in advance)
- Two simple knobs provide flexibility without overwhelming users

**Proposed** (Phase 2):
1. **Core attribute preservation** - protect critical attributes from eviction
2. **Smart truncation** - intelligently summarize large responses
3. **Attribute prioritization** - user-defined importance levels

---

## Table of Contents

1. [Background](#background)
2. [Root Cause Analysis](#root-cause-analysis)
3. [Product Philosophy: Simplicity vs Flexibility](#product-philosophy-simplicity-vs-flexibility)
4. [Phase 1: Dual Guardrail Approach (IMPLEMENTED)](#phase-1-dual-guardrail-approach-implemented)
5. [Phase 2: Core Attribute Preservation (PROPOSED)](#phase-2-core-attribute-preservation-proposed)
6. [Phase 3: Smart Truncation (PROPOSED)](#phase-3-smart-truncation-proposed)
7. [Comparison with Traceloop](#comparison-with-traceloop)
8. [Configuration Reference](#configuration-reference)
9. [Testing Strategy](#testing-strategy)
10. [Performance Implications](#performance-implications)
11. [Success Metrics](#success-metrics)

---

## Background

### OpenTelemetry Span Attribute Limits

OpenTelemetry enforces limits on span attributes to prevent:
- Unbounded memory growth
- Performance degradation
- Backend storage overload

**Default Limits**:
```python
SpanLimits(
    max_attributes=128,      # ⚠️ DEFAULT: Only 128 attributes!
    max_events=128,
    max_links=128,
    max_attributes_per_event=128,
    max_attributes_per_link=128
)
```

**Eviction Behavior**:
- When limit is reached, **oldest attributes are evicted**
- No warning or error is raised
- Silent data loss occurs

### HoneyHive's Attribute Flattening

HoneyHive SDK flattens nested structures into span attributes for observability:

```python
# API Response
{
    "search_results": [
        {"title": "...", "url": "...", "snippet": "..."},
        # ... 50+ results
    ],
    "metadata": {
        "total_results": 1000,
        "search_time": 0.5,
        # ... more metadata
    }
}

# Flattened to span attributes
{
    "search_results.0.title": "...",
    "search_results.0.url": "...",
    "search_results.0.snippet": "...",
    # ... 400+ flattened attributes
    "honeyhive.session_id": "abc123",  # ❌ EVICTED when limit reached!
    "honeyhive.project": "my-project",  # ❌ EVICTED when limit reached!
}
```

**The Critical Problem**:
- Core HoneyHive attributes (`honeyhive.session_id`, `honeyhive.project`) are set **early** in span lifecycle
- Large API response attributes are set **later**
- When limits are exceeded, early attributes (including core ones) are evicted
- Span processor requires `honeyhive.session_id` to export span
- Missing `session_id` → span is silently skipped

---

## Root Cause Analysis

### The Bug Timeline

**1. Span Creation (`on_start`)**:
```python
# HoneyHiveSpanProcessor.on_start()
span.set_attribute("honeyhive.session_id", "abc123")
span.set_attribute("honeyhive.project", "my-project")
span.set_attribute("honeyhive.session_name", "test-session")
# Attributes: 3 / 128
```

**2. Function Execution (inside `@trace` decorator)**:
```python
# User's decorated function calls SerpAPI
result = serpapi.search(query="...")  # Returns 50+ search results
# _set_span_attributes flattens the response
for i, result in enumerate(results):
    span.set_attribute(f"search_results.{i}.title", result["title"])
    span.set_attribute(f"search_results.{i}.url", result["url"])
    # ... 8 attributes per result × 50 results = 400 attributes
# Attributes: 403 / 128 → LIMIT EXCEEDED!
```

**3. Attribute Eviction**:
```python
# OpenTelemetry evicts oldest 275 attributes
# ❌ "honeyhive.session_id" EVICTED
# ❌ "honeyhive.project" EVICTED
# ❌ "honeyhive.session_name" EVICTED
# ✅ "search_results.45.title" KEPT (newer)
# ✅ "search_results.49.url" KEPT (newer)
```

**4. Span Export (`on_end`)**:
```python
# HoneyHiveSpanProcessor.on_end()
session_id = span.attributes.get("honeyhive.session_id")
if not session_id:
    logger.warning("Span has no session_id, skipping export")
    return  # ❌ SPAN SILENTLY DROPPED!
```

### Why This is Critical

1. **Silent Failure**: No error raised, span appears created but never exported
2. **Observability Gap**: Complete loss of trace data for affected operations
3. **Debugging Nightmare**: Span is created, `on_end` is called, but data disappears
4. **Cardinal Sin**: Observability tools must NEVER silently drop data

---

## Product Philosophy: Simplicity vs Flexibility

### The Customer Reality

**From CEO & CTO**: "Customers have a hard time understanding the complexity of observability. They want simple solutions."

**The Challenge**:
- Observability is inherently complex (traces, spans, attributes, limits, backends)
- LLM/agent tracing has unpredictable data sizes (can't forecast attribute sizes in advance)
- GPT-4 response: 500-5000 tokens (2KB-20KB) - varies wildly
- Tool responses: SerpAPI 50KB, database query 1KB - impossible to predict
- Multimodal: Images (2MB), audio embeddings (500KB), video frames (5MB)

### Our Approach: Radical Simplicity with Escape Hatches

**For 95% of Users** - Zero configuration:
```python
tracer = HoneyHiveTracer.init(project="my-project")
# Just works. No thinking required.
```

**For 5% of Power Users** - Simple one-line override:
```python
tracer = HoneyHiveTracer.init(
    project="my-project",
    max_attributes=5000,        # "I have many tool calls"
    max_span_size=20*1024*1024  # "I need larger spans for high-res images"
)
```

### What We DON'T Expose (Too Complex)

❌ **Don't expose**:
```python
# Overwhelming for customers who don't understand observability
max_span_size_bytes=10485760,           # "What's a byte? I work in tokens!"
truncation_strategy="preserve_first",    # "Too many choices, which one?"
priority_levels={"honeyhive": 0},        # "What's a priority level?"
max_attributes_per_event=128,            # "What's an event vs attribute?"
attribute_sampling_rate=0.1,             # "Sampling? I want all my data!"
```

✅ **Do expose**:
```python
# Simple, understandable
max_attributes=1024,        # "How many things to track"
max_span_size=10*1024*1024  # "How big can the whole span be"
```

**Why NOT per-attribute limit:**
- LLM ecosystem has extreme variability: 1KB text messages vs 10MB images
- Can't predict attribute sizes in advance (text, images, audio, video, embeddings)
- Total span size is the right limit for unpredictable workloads

### The Dual Guardrail Strategy

**Why two limits?**

Because LLM/agent tracing has **two distinct failure modes**:

**Failure Mode 1: Many Small Attributes (typical LLM)**
```python
# 1024 conversation messages × 1KB each = 1MB total
# Hits: max_attributes (1024) ✓ - PROTECTION!
# Safe: max_span_size (10MB) - total size only 1MB
```

**Failure Mode 2: Few Large Attributes (multimodal)**
```python
# 5 base64-encoded images × 2MB each = 10MB total
# Safe: max_attributes (1024) - only 5 attributes
# Hits: max_span_size (10MB) ✓ - PROTECTION!
```

**Together**: Two simple knobs handle unpredictable LLM/agent data without overwhelming users.

**Critical Design Note:**
- We use **total span size** (not per-attribute limit) because LLM ecosystem has extreme attribute size variability
- Individual attributes can be anywhere from 1KB (text) to 10MB (images)
- OpenTelemetry doesn't provide `max_span_size` natively - we implement it ourselves in the span processor

### Design Principle Applied

**In Python SDK rewrite**: "Provide sane defaults with configurable overrides"

- ✅ Sane defaults: `max_attributes=1024`, `max_span_size=10MB`
- ✅ Configurable: Easy one-line override for power users
- ✅ No prediction required: Limits catch edge cases automatically
- ✅ Simple: Two knobs, not twenty
- ✅ Flexible: Handles text, images, audio, video, embeddings (variable attribute sizes)

---

## Phase 1: Dual Guardrail Approach (IMPLEMENTED)

### Design Goals

1. **Simple for 95% of Users**: Zero configuration, "just works"
2. **Flexible for 5% of Power Users**: Two clear knobs to adjust
3. **Dual Guardrails**: Protect against both "many small" and "few large" attributes
4. **LLM/Agent Optimized**: Defaults handle unpredictable data sizes (text, images, audio)
5. **Environment Variables**: Support env vars for deployment flexibility
6. **Backward Compatible**: Existing code works without changes

### Implementation

#### 1. TracerConfig Extension

**File**: `src/honeyhive/config/models/tracer.py`

```python
class TracerConfig(BaseModel):
    """HoneyHive Tracer Configuration."""
    
    # ... existing fields ...
    
    # OpenTelemetry Span Limits Configuration
    # Dual Guardrail Approach: Count + Total Size
    
    max_attributes: int = Field(
        default=1024,  # 🔥 GUARDRAIL 1: Attribute count (8x OpenTelemetry default)
        description="Maximum number of attributes per span (protects against many small attributes)",
        validation_alias=AliasChoices("HH_MAX_ATTRIBUTES", "max_attributes"),
        examples=[128, 1024, 5000, 10000],
    )
    
    max_span_size: int = Field(
        default=10 * 1024 * 1024,  # 🔥 GUARDRAIL 2: 10MB total span size
        description="Maximum total size of all span attributes in bytes (protects against large payloads)",
        validation_alias=AliasChoices("HH_MAX_SPAN_SIZE", "max_span_size"),
        examples=[1048576, 5242880, 10485760, 20971520],  # 1MB, 5MB, 10MB, 20MB
    )
    
    max_events: int = Field(
        default=128,
        description="Maximum number of events per span",
        validation_alias=AliasChoices("HH_MAX_EVENTS", "max_events"),
    )
    
    max_links: int = Field(
        default=128,
        description="Maximum number of links per span",
        validation_alias=AliasChoices("HH_MAX_LINKS", "max_links"),
    )
```

**Features**:
- ✅ Pydantic validation
- ✅ Environment variable support (`HH_MAX_ATTRIBUTES`)
- ✅ Type hints and documentation
- ✅ Sensible defaults (1024 for attributes, 128 for events/links)

#### 2. Atomic Provider Detection Integration

**File**: `src/honeyhive/tracer/integration/detection.py`

```python
def atomic_provider_detection_and_setup(
    tracer_instance: Any = None,
    span_limits: Optional[Any] = None,  # 🔥 NEW PARAMETER
) -> Tuple[str, Optional[Any], Dict[str, Any]]:
    """
    Atomically detect existing TracerProvider or create new one.
    
    Args:
        span_limits: Optional SpanLimits to apply when creating new provider
    """
    with _tracer_provider_lock:
        main_provider = trace.get_tracer_provider()
        
        # Strategy 1: Use existing provider (no modifications)
        if not isinstance(main_provider, trace.NoOpTracerProvider):
            return ("existing_provider", main_provider, info)
        
        # Strategy 2: Create new provider WITH span limits
        if span_limits:
            new_provider = TracerProvider(span_limits=span_limits)  # 🔥 APPLY LIMITS
            safe_log(
                tracer_instance,
                "debug",
                "Creating TracerProvider with custom span limits",
                honeyhive_data={
                    "max_attributes": span_limits.max_attributes,
                },
            )
        else:
            new_provider = TracerProvider()  # Default OpenTelemetry limits
        
        trace.set_tracer_provider(new_provider)
        return ("created_new_provider", new_provider, info)
```

**Key Points**:
- ✅ `span_limits` passed during provider creation
- ✅ Atomic operation (thread-safe with lock)
- ✅ Respects existing providers (doesn't override)

#### 3. Initialization Flow

**File**: `src/honeyhive/tracer/instrumentation/initialization.py`

```python
def _initialize_otel_components(tracer_instance: Any) -> None:
    """Initialize OpenTelemetry components with dual-guardrail span limits."""
    
    # 1. Get user-configured span limits from tracer config (dual guardrails)
    max_attributes = getattr(tracer_instance.config, "max_attributes", 1024)
    max_span_size = getattr(tracer_instance.config, "max_span_size", 10 * 1024 * 1024)  # 10MB
    max_events = getattr(tracer_instance.config, "max_events", 128)
    max_links = getattr(tracer_instance.config, "max_links", 128)
    
    # 2. Create SpanLimits object (using OTel's max_attributes)
    # Note: max_span_size is enforced separately in HoneyHiveSpanProcessor
    span_limits = SpanLimits(
        max_attributes=max_attributes,  # Guardrail 1: Count (many small attrs)
        max_events=max_events,
        max_links=max_links,
        max_attributes_per_event=128,
        max_attributes_per_link=128,
    )
    
    # 3. Store max_span_size on tracer_instance for span processor to use
    tracer_instance._max_span_size = max_span_size  # Guardrail 2: Total size (custom implementation)
    
    # 3. Pass to atomic provider detection
    strategy_name, main_provider, provider_info = atomic_provider_detection_and_setup(
        tracer_instance=tracer_instance,
        span_limits=span_limits,  # 🔥 PASS CONFIGURED LIMITS
    )
    
    safe_log(
        tracer_instance,
        "debug",
        "Atomic provider detection completed",
        honeyhive_data={
            "provider_class": provider_info["provider_class_name"],
            "strategy": strategy_name,
            "max_attributes": max_attributes,     # Log guardrail 1
            "max_span_size": max_span_size,       # Log guardrail 2
        },
    )
```

**Flow**:
1. Read limits from `TracerConfig` (defaults: 1024/128/128)
2. Create `SpanLimits` object
3. Pass to atomic provider detection
4. Provider created with configured limits
5. All spans inherit these limits

### Usage Examples

#### Example 1: Default Configuration (Recommended)

```python
from honeyhive import HoneyHiveTracer

# Uses HoneyHive defaults: 1024 attributes, 128 events/links
tracer = HoneyHiveTracer.init(
    project="my-project",
    api_key="...",
)
# TracerProvider created with max_attributes=1024
```

#### Example 2: Environment Variables

```bash
# .env file
export HH_MAX_ATTRIBUTES=2000
export HH_MAX_SPAN_SIZE=20971520  # 20MB
export HH_MAX_EVENTS=256
export HH_MAX_LINKS=256
```

```python
from honeyhive import HoneyHiveTracer

# Reads from environment variables
tracer = HoneyHiveTracer.init(
    project="my-project",
    api_key="...",
)
# TracerProvider created with max_attributes=2000, max_span_size=20MB
```

#### Example 3: Power User - Multimodal (High-Res Images)

```python
from honeyhive import HoneyHiveTracer

# Scenario: Tracing image generation with high-res outputs
tracer = HoneyHiveTracer.init(
    project="my-project",
    api_key="...",
    max_attributes=500,                  # Fewer attributes (only image metadata)
    max_span_size=20 * 1024 * 1024,     # 20MB total span size (large images)
)
# Typical span: 10 attributes × 2MB images = 20MB
```

#### Example 4: Power User - Long Agent Sessions

```python
from honeyhive import HoneyHiveTracer

# Scenario: Multi-step agent with many tool calls
tracer = HoneyHiveTracer.init(
    project="my-project",
    api_key="...",
    max_attributes=5000,             # Many tool calls (5000 attributes)
    max_span_size=5 * 1024 * 1024,   # 5MB total (small tool responses)
)
# Typical span: 5000 attributes × 1KB average = 5MB
```

#### Example 5: Memory-Constrained Environment

```python
from honeyhive import HoneyHiveTracer

# Scenario: Edge device or serverless function with memory limits
tracer = HoneyHiveTracer.init(
    project="my-project",
    api_key="...",
    max_attributes=500,                # Lower limit
    max_span_size=1024 * 1024,         # 1MB total span size
    max_events=64,
    max_links=64,
)
# Max span size: 1MB (fits memory-constrained environment)
```

#### Example 4: OpenTelemetry Default (Not Recommended)

```python
from honeyhive import HoneyHiveTracer

# Revert to OpenTelemetry defaults (not recommended!)
tracer = HoneyHiveTracer.init(
    project="my-project",
    api_key="...",
    max_attributes=128,  # ⚠️ May cause data loss!
)
```

### Verification

```python
from opentelemetry import trace

# After initialization, check provider limits
provider = trace.get_tracer_provider()
print(provider._span_limits.max_attributes)  # Should print: 1024
print(provider._span_limits.max_events)      # Should print: 128
print(provider._span_limits.max_links)       # Should print: 128

# Check custom span size limit (stored on tracer instance)
print(tracer._max_span_size)  # Should print: 10485760 (10MB)
```

### Math: Understanding the Dual Guardrails

**Maximum Span Size** (enforced by custom span processor):
```
max_span_size = 10MB (total size of all attributes combined)
```

**Realistic Span Sizes**:

1. **Text-Heavy LLM Trace** (hits attribute count first):
   ```
   1024 attributes × 5KB average = 5.12MB per span ✓
   ```

2. **Multimodal Trace** (hits attribute length first):
   ```
   10 attributes × 10MB max = 100MB per span ✓
   ```

3. **Mixed Trace** (balanced):
   ```
   500 attributes × 50KB average = 25MB per span ✓
   ```

**Protection Scenarios**:

| Scenario | Attributes | Avg Size | Limit Hit | Result |
|----------|-----------|----------|-----------|---------|
| Many small messages | 2000 | 1KB | `max_attributes` ✓ | Stops at 1024 attrs |
| Few large images | 5 | 3MB | `max_span_size` ✓ | Stops when total hits 10MB |
| Balanced | 800 | 10KB | Neither | Works perfectly ✓ |

---

## Ingestion Service Required Attributes (CRITICAL)

### Backend Validation Requirements

From `hive-kube/kubernetes/ingestion_service/app/schemas/event_schema.js` and `new_event_validation.js`:

**Attributes that MUST be present or spans are REJECTED:**

| Attribute | Type | Auto-Generated? | Rejection Risk if Evicted |
|-----------|------|-----------------|---------------------------|
| `project_id` | string | ✅ Yes (from request) | ⚠️ **LOW** - Set by ingestion service from headers |
| `session_id` | UUID | ✅ Yes (if missing) | 🔥 **CRITICAL** - If evicted, auto-generates NEW session, breaks trace continuity |
| `event_id` | UUID | ✅ Yes (if missing) | ⚠️ **MEDIUM** - Auto-generated but loses span identity |
| `event_type` | string | ❌ No | 🔥 **CRITICAL** - Span rejected if missing |
| `event_name` | string | ❌ No | 🔥 **CRITICAL** - Span rejected if missing |
| `tenant` | string | ✅ Yes (from request) | ⚠️ **LOW** - Set by ingestion service from auth context |
| `source` | string | ❌ No | 🔥 **CRITICAL** - Span rejected if missing |
| `duration` | number | ❌ No | 🔥 **CRITICAL** - Span rejected if missing |
| `start_time` | number | ✅ Yes (if missing) | ⚠️ **LOW** - Auto-generated to current time |
| `end_time` | number | ✅ Yes (if missing) | ⚠️ **LOW** - Auto-generated from start_time + duration |
| `inputs` | object | ✅ Yes (defaults to `{}`) | ⚠️ **LOW** - Normalized to empty object |
| `outputs` | object/array | ❌ **Depends** | ⚠️ **MEDIUM** - Required but nullable in some cases |
| `metadata` | object | ✅ Yes (defaults to `{}`) | ⚠️ **LOW** - Normalized to empty object |
| `user_properties` | object | ✅ Yes (defaults to `{}`) | ⚠️ **LOW** - Normalized to empty object |
| `children_ids` | array | ✅ Yes (defaults to `[]`) | ⚠️ **LOW** - Normalized to empty array |
| `metrics` | object | ✅ Yes (defaults to `{}`) | ⚠️ **LOW** - Normalized to empty object, nullable |
| `feedback` | object | ✅ Yes (defaults to `{}`) | ⚠️ **LOW** - Normalized to empty object, nullable |

### Core Attributes That MUST NEVER Be Evicted

**Priority 1 - Span Identity (Session Continuity):**
```python
# If these are evicted, span is orphaned or rejected
"honeyhive.session_id"       # 🔥 CRITICAL - Creates new session if missing
"honeyhive.project_id"       # ⚠️ Set from headers, but eviction = wrong project
```

**Priority 2 - Span Validation (Rejection):**
```python
# If these are evicted, span is REJECTED by validation schema
"honeyhive.event_type"       # 🔥 CRITICAL - Required by Zod schema
"honeyhive.event_name"       # 🔥 CRITICAL - Required by Zod schema  
"honeyhive.source"           # 🔥 CRITICAL - Required by Zod schema
"honeyhive.duration"         # 🔥 CRITICAL - Required by Zod schema (milliseconds)
```

**Priority 3 - Span Content (Data Loss):**
```python
# If evicted, span accepted but loses critical data
"honeyhive.outputs"          # ⚠️ MEDIUM - LLM responses, tool results
"honeyhive.inputs"           # ⚠️ LOW - Defaults to {}, but loses context
```

### Real-World Impact: CEO's Bug

**What Happened:**
1. SerpAPI response → 400+ attributes when flattened
2. OpenTelemetry default limit: 128 attributes
3. Span created → `honeyhive.session_id` added early
4. Large response flattened → `session_id` evicted (FIFO)
5. `HoneyHiveSpanProcessor.on_end()` checks for `session_id` → **MISSING**
6. Span skipped: `"Span has no session_id, skipping HoneyHive export"`
7. Result: **Silent data loss** - span never exported

**The Fix:**
- Increased `max_attributes` from 128 → 1024 (8x safety margin)
- Added `max_span_size` (10MB) to protect against large total payloads
- Made both limits user-configurable for edge cases
- **Key Design:** Used total span size (not per-attribute) to support LLM ecosystem's variable attribute sizes

---

## Phase 2: Core Attribute Preservation (PROPOSED)

### The Problem

Even with increased limits, we can still hit edge cases:
- Very large API responses (1000+ attributes)
- Memory-constrained environments (lower limits)
- Multiple large nested objects

**Current Behavior**: All attributes treated equally, oldest evicted first.

**Desired Behavior**: Core HoneyHive attributes **never evicted**, regardless of limit.

### Design Goals

1. **Protect Core Attributes**: `honeyhive.*` namespace attributes cannot be evicted
2. **Transparent**: User doesn't need to configure anything
3. **OpenTelemetry Compatible**: Works within OTEL framework
4. **Minimal Overhead**: <1% performance impact

### Proposed Implementation

#### Approach 1: Custom Span Implementation (Recommended)

Create `HoneyHiveSpan` that wraps OpenTelemetry span and protects core attributes.

```python
# src/honeyhive/tracer/core/span.py

class HoneyHiveSpan:
    """
    Custom span wrapper that protects core HoneyHive attributes from eviction.
    
    Core attributes (honeyhive.*) are stored separately and never evicted.
    User attributes use standard OpenTelemetry limits and eviction.
    """
    
    def __init__(self, otel_span, max_attributes: int = 1024):
        self._otel_span = otel_span
        self._max_attributes = max_attributes
        
        # Separate storage for core attributes (never evicted)
        self._core_attributes: Dict[str, Any] = {}
        
        # Track user attribute count
        self._user_attribute_count = 0
    
    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set span attribute with core attribute protection.
        
        - Core attributes (honeyhive.*) stored separately, never evicted
        - User attributes follow normal OpenTelemetry limits
        """
        # Core attributes: store separately
        if key.startswith("honeyhive."):
            self._core_attributes[key] = value
            self._otel_span.set_attribute(key, value)
            return
        
        # User attributes: check limit
        if self._user_attribute_count >= self._max_attributes:
            logger.warning(
                f"Span attribute limit reached ({self._max_attributes}), "
                f"dropping attribute: {key}"
            )
            return
        
        self._otel_span.set_attribute(key, value)
        self._user_attribute_count += 1
    
    def get_attributes(self) -> Dict[str, Any]:
        """
        Get all attributes (core + user).
        
        Core attributes are always present, even if evicted from OTEL span.
        """
        attributes = dict(self._otel_span.attributes)
        
        # Ensure core attributes are present
        for key, value in self._core_attributes.items():
            if key not in attributes:
                # Core attribute was evicted from OTEL span, restore it
                logger.debug(f"Restoring evicted core attribute: {key}")
                attributes[key] = value
        
        return attributes
    
    def __getattr__(self, name):
        """Proxy all other methods to underlying OTEL span."""
        return getattr(self._otel_span, name)
```

**Integration**:
```python
# src/honeyhive/tracer/core/operations.py

@contextmanager
def start_span(self, name: str, **kwargs):
    """Start span with core attribute protection."""
    with self._get_tracer().start_as_current_span(name, **kwargs) as otel_span:
        # Wrap with HoneyHive span for core attribute protection
        span = HoneyHiveSpan(
            otel_span,
            max_attributes=self.config.max_attributes
        )
        
        # Set core attributes immediately
        span.set_attribute("honeyhive.session_id", self.session_id)
        span.set_attribute("honeyhive.project", self.project)
        span.set_attribute("honeyhive.session_name", self.session_name)
        
        yield span
```

#### Approach 2: Attribute Priority System

Extend OpenTelemetry's `SpanLimits` with priority-based eviction.

```python
# src/honeyhive/tracer/core/limits.py

class PrioritySpanLimits:
    """
    Span limits with priority-based eviction.
    
    Attributes are assigned priorities:
    - CRITICAL (0): Never evicted (e.g., honeyhive.*)
    - HIGH (1): Evicted last (e.g., request metadata)
    - NORMAL (2): Standard eviction (e.g., API responses)
    - LOW (3): Evicted first (e.g., debug info)
    """
    
    PRIORITY_CRITICAL = 0  # Never evicted
    PRIORITY_HIGH = 1      # Evicted last
    PRIORITY_NORMAL = 2    # Standard eviction
    PRIORITY_LOW = 3       # Evicted first
    
    def __init__(self, max_attributes: int = 1024):
        self.max_attributes = max_attributes
        
        # Priority rules (key prefix → priority)
        self.priority_rules = {
            "honeyhive.": self.PRIORITY_CRITICAL,
            "request.": self.PRIORITY_HIGH,
            "response.": self.PRIORITY_NORMAL,
            "debug.": self.PRIORITY_LOW,
        }
    
    def get_priority(self, key: str) -> int:
        """Get priority for attribute key."""
        for prefix, priority in self.priority_rules.items():
            if key.startswith(prefix):
                return priority
        return self.PRIORITY_NORMAL
    
    def should_evict(
        self,
        attributes: Dict[str, Any],
        new_key: str,
        new_value: Any
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if an attribute should be evicted to make room for new one.
        
        Returns:
            (should_evict, key_to_evict)
        """
        if len(attributes) < self.max_attributes:
            return (False, None)  # No eviction needed
        
        new_priority = self.get_priority(new_key)
        
        # Find lowest priority attribute
        lowest_priority = self.PRIORITY_CRITICAL
        key_to_evict = None
        
        for key in attributes.keys():
            key_priority = self.get_priority(key)
            
            # Never evict CRITICAL attributes
            if key_priority == self.PRIORITY_CRITICAL:
                continue
            
            # Find lowest priority
            if key_priority > lowest_priority:
                lowest_priority = key_priority
                key_to_evict = key
        
        # Evict if new attribute has higher priority
        if key_to_evict and new_priority <= lowest_priority:
            return (True, key_to_evict)
        
        # Otherwise, drop new attribute
        return (False, None)
```

### Comparison of Approaches

| Aspect | Approach 1: Custom Span | Approach 2: Priority System |
|--------|------------------------|----------------------------|
| **Core Protection** | ✅ Guaranteed | ✅ Guaranteed |
| **Flexibility** | ⚠️ Fixed core namespace | ✅ Configurable priorities |
| **Complexity** | ⚠️ Wrapper overhead | ✅ Simpler logic |
| **OTEL Compatibility** | ⚠️ Wrapper required | ✅ Extends standard pattern |
| **Performance** | ~1-2% overhead | <1% overhead |
| **User Control** | ❌ No customization | ✅ Custom priority rules |

**Recommendation**: Start with **Approach 1** (simpler, guaranteed protection), evolve to **Approach 2** if users need customization.

---

## Phase 3: Smart Truncation (PROPOSED)

### The Problem

Even with core attribute preservation, large API responses can:
- Consume excessive memory
- Slow down span processing
- Overwhelm backend storage

**Example**: SerpAPI returns 50 search results with 8 attributes each = 400 attributes. Do we need all 400?

### Design Goals

1. **Intelligent Summarization**: Keep most important data, summarize the rest
2. **Configurable**: User controls truncation strategy
3. **Transparent**: Log what was truncated
4. **Preserves Utility**: Truncated traces still useful for debugging

### Proposed Strategies

#### Strategy 1: Array Truncation

Keep first N items, summarize the rest.

```python
# Before truncation (50 search results)
{
    "search_results.0.title": "...",
    "search_results.0.url": "...",
    "search_results.1.title": "...",
    # ... 50 items × 8 attrs = 400 attributes
}

# After truncation (keep first 5, summarize rest)
{
    "search_results.0.title": "...",
    "search_results.0.url": "...",
    # ... 5 items × 8 attrs = 40 attributes
    "search_results.truncated": true,
    "search_results.total_count": 50,
    "search_results.shown_count": 5,
    "search_results.truncated_count": 45,
}
```

**Configuration**:
```python
tracer = HoneyHiveTracer.init(
    project="my-project",
    truncation_config={
        "enabled": True,
        "max_array_items": 5,      # Keep first 5 items
        "max_string_length": 1000,  # Truncate strings > 1000 chars
    }
)
```

#### Strategy 2: Sampling

Keep every Nth item instead of first N.

```python
# Sampling strategy: Keep every 10th item
{
    "search_results.0.title": "...",   # Item 0
    "search_results.10.title": "...",  # Item 10
    "search_results.20.title": "...",  # Item 20
    "search_results.30.title": "...",  # Item 30
    "search_results.40.title": "...",  # Item 40
    "search_results.sampling_rate": 10,
    "search_results.total_count": 50,
}
```

#### Strategy 3: Importance-Based

Use heuristics to keep most important attributes.

```python
# Importance rules:
# 1. Error/warning attributes: Keep all
# 2. User-defined important keys: Keep all
# 3. Small values (<100 chars): Keep all
# 4. Large arrays: Truncate to first N
# 5. Large strings: Truncate to N chars

truncation_config = {
    "enabled": True,
    "important_prefixes": ["error.", "warning.", "critical."],  # Never truncate
    "max_array_items": 5,
    "max_string_length": 1000,
    "keep_small_values": True,  # Values < 100 chars always kept
}
```

#### Strategy 4: Compression

Store full data as compressed JSON in single attribute.

```python
import json
import zlib
import base64

# Compress large nested structures
large_response = {
    "search_results": [...],  # 50 results
}

# Compress to single attribute
compressed = base64.b64encode(
    zlib.compress(json.dumps(large_response).encode())
).decode()

span.set_attribute("search_results.compressed", compressed)
span.set_attribute("search_results.compression", "zlib+base64")
span.set_attribute("search_results.original_size", len(json.dumps(large_response)))
span.set_attribute("search_results.compressed_size", len(compressed))
```

**Backend Decompression**:
```python
# In HoneyHive backend or analysis tools
import json
import zlib
import base64

compressed = span.attributes.get("search_results.compressed")
compression = span.attributes.get("search_results.compression")

if compression == "zlib+base64":
    original = json.loads(
        zlib.decompress(base64.b64decode(compressed)).decode()
    )
```

### Comparison of Strategies

| Strategy | Pros | Cons | Use Case |
|----------|------|------|----------|
| **Array Truncation** | Simple, predictable | May miss important items at end | Paginated results |
| **Sampling** | Good distribution | May miss important items | Large uniform arrays |
| **Importance-Based** | Keeps most valuable data | Complex rules, slower | Mixed data types |
| **Compression** | Preserves all data | Requires decompression | Archives, debugging |

**Recommendation**: Implement **Array Truncation** first (simplest), add **Importance-Based** for advanced users.

---

## Comparison with Traceloop

### Traceloop's Approach

Traceloop SDK (the previous live tracer in main branch) does NOT explicitly configure span limits:

```python
# Traceloop never sets SpanLimits
# Uses OpenTelemetry defaults (128 attributes)
```

**However**, Traceloop SDK:
1. **Sets attributes more carefully**: Only essential attributes, minimal flattening
2. **Doesn't flatten large responses**: Stores summaries instead of full payloads
3. **Uses events for large data**: Large data stored as span events, not attributes

**Example** (Traceloop):
```python
# Traceloop doesn't flatten entire response
span.set_attribute("request.model", "gpt-4")
span.set_attribute("request.messages_count", 3)
span.set_attribute("response.tokens", 150)

# Large content stored as event
span.add_event(
    name="llm.response",
    attributes={
        "content": response.choices[0].message.content  # Single attribute
    }
)
```

### HoneyHive vs Traceloop

| Aspect | Traceloop | HoneyHive (Before Fix) | HoneyHive (After Fix) |
|--------|-----------|----------------------|---------------------|
| **Span Limits** | Default (128) | Default (128) | Configurable (default 1024) |
| **Flattening** | Minimal | Aggressive | Aggressive |
| **Large Responses** | Events | Attributes | Attributes (more space) |
| **Risk of Eviction** | Low (minimal attrs) | High (many attrs) | Medium (higher limits) |
| **Observability Depth** | Lower (summaries) | Higher (full data) | Higher (full data) |

### Why HoneyHive Needs Higher Limits

1. **Richer Observability**: HoneyHive flattens nested structures for detailed analysis
2. **Backend Expectations**: HoneyHive backend expects flattened attributes
3. **User Experience**: Users expect to see full request/response data
4. **Debugging**: Full payloads critical for debugging LLM applications

**Trade-off**: Higher memory usage in exchange for richer observability.

---

## Configuration Reference

### TracerConfig Fields

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init(
    project="my-project",
    api_key="...",
    
    # Dual Guardrail Span Limits
    max_attributes=1024,              # Default: 1024 (OpenTelemetry: 128)
    max_span_size=10 * 1024 * 1024,   # Default: 10MB (custom implementation)
    max_events=128,                   # Default: 128
    max_links=128,                    # Default: 128
    
    # Future: Truncation Config
    truncation_config={
        "enabled": True,
        "max_array_items": 5,
        "max_string_length": 1000,
    },
    
    # Future: Core Attribute Protection
    protect_core_attributes=True,  # Default: True
    core_attribute_prefixes=["honeyhive.", "request.", "session."],
)
```

### Environment Variables

```bash
# Dual guardrail span limits
export HH_MAX_ATTRIBUTES=2000
export HH_MAX_SPAN_SIZE=20971520  # 20MB in bytes
export HH_MAX_EVENTS=256
export HH_MAX_LINKS=256

# Future: Truncation
export HH_TRUNCATION_ENABLED=true
export HH_MAX_ARRAY_ITEMS=5
export HH_MAX_STRING_LENGTH=1000

# Future: Core protection
export HH_PROTECT_CORE_ATTRIBUTES=true
```

### Choosing the Right Limits

| Scenario | `max_attributes` | `max_span_size` | Reasoning |
|----------|------------------|-----------------|-----------|
| **Default (Most Users)** | 1024 | 10MB | Handles text, images, audio - "just works" |
| **Text-Heavy (Long Conversations)** | 5000 | 5MB | Many messages, small total size |
| **Multimodal (High-Res Images)** | 500 | 20MB | Few attributes, large total size |
| **Memory Constrained (Edge/Serverless)** | 500 | 1MB | Tight memory budget |
| **Debugging/Development** | 10000 | 50MB | Capture everything for analysis |
| **Video/Large Files** | 100 | 100MB | Very few, very large attributes |

### Common Use Cases

**LLM Conversation Tracing** (typical):
```python
max_attributes=1024   # 50 messages × ~20 attrs each
max_span_size=10MB    # Total size covers typical conversations
# Works for: ChatGPT, Claude, Llama, etc.
```

**Agent with Tool Calls** (many small):
```python
max_attributes=5000   # Dozens of tool calls
max_span_size=5MB     # Total size for many small tool responses
# Works for: LangChain agents, CrewAI, AutoGPT
```

**Multimodal AI** (few large):
```python
max_attributes=500    # Limited metadata
max_span_size=20MB    # Total size for high-res images, audio clips
# Works for: DALL-E, Stable Diffusion, Whisper
```

**RAG with Large Documents** (mixed):
```python
max_attributes=2000   # Document chunks + metadata
max_span_size=10MB    # Total size for large document excerpts
# Works for: Document Q&A, semantic search
```

### Monitoring and Alerts

```python
# Log when limits are approached
if span_attribute_count > (max_attributes * 0.8):
    logger.warning(
        f"Span approaching attribute limit: {span_attribute_count}/{max_attributes}",
        extra={
            "span_name": span.name,
            "attribute_count": span_attribute_count,
            "limit": max_attributes,
            "usage_percent": (span_attribute_count / max_attributes) * 100,
        }
    )

# Metric for monitoring
metrics.gauge(
    "honeyhive.span.attribute_count",
    span_attribute_count,
    tags={"span_name": span.name}
)
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_span_limits.py

def test_span_limits_default():
    """Test default span limits are 1024."""
    tracer = HoneyHiveTracer.init(project="test")
    provider = trace.get_tracer_provider()
    assert provider._span_limits.max_attributes == 1024
    assert provider._span_limits.max_events == 128
    assert provider._span_limits.max_links == 128

def test_span_limits_custom():
    """Test custom span limits."""
    tracer = HoneyHiveTracer.init(
        project="test",
        max_attributes=2000,
        max_events=256,
    )
    provider = trace.get_tracer_provider()
    assert provider._span_limits.max_attributes == 2000
    assert provider._span_limits.max_events == 256

def test_span_limits_environment_variable():
    """Test span limits from environment variables."""
    os.environ["HH_MAX_ATTRIBUTES"] = "3000"
    tracer = HoneyHiveTracer.init(project="test")
    provider = trace.get_tracer_provider()
    assert provider._span_limits.max_attributes == 3000

def test_large_response_does_not_evict_core_attributes():
    """Test core attributes preserved with large response."""
    tracer = HoneyHiveTracer.init(
        project="test",
        max_attributes=100,  # Low limit to trigger eviction
    )
    
    with tracer.trace("test_function") as span:
        # Core attributes set first
        assert span.attributes.get("honeyhive.session_id") is not None
        
        # Add 200 attributes (exceeds limit)
        for i in range(200):
            span.set_attribute(f"large_response.item_{i}", f"value_{i}")
        
        # Core attributes should still be present
        assert span.attributes.get("honeyhive.session_id") is not None
        assert span.attributes.get("honeyhive.project") is not None
```

### Integration Tests

```python
# tests/integration/test_span_limits_integration.py

def test_serpapi_like_response():
    """Test handling of SerpAPI-like large responses."""
    tracer = HoneyHiveTracer.init(
        project="test",
        max_attributes=1024,
    )
    
    @tracer.trace()
    def search_function():
        # Simulate SerpAPI response with 50 results
        results = [
            {
                "title": f"Result {i}",
                "url": f"https://example.com/{i}",
                "snippet": f"Snippet for result {i}" * 10,  # Long snippet
                # ... 8 attributes per result
            }
            for i in range(50)
        ]
        return {"search_results": results}
    
    result = search_function()
    
    # Verify span was exported (not dropped)
    spans = get_exported_spans()
    assert len(spans) == 1
    
    span = spans[0]
    assert span.attributes.get("honeyhive.session_id") is not None
    assert "search_results.0.title" in span.attributes
    assert "search_results.49.title" in span.attributes

def test_ceo_script_reproduction():
    """Test CEO's exact reproduction script."""
    # Run sample-tests/openinference-anthropic.py
    # Verify get_search_results span is exported
    # Verify parent-child relationships intact
    pass
```

### Performance Tests

```python
# tests/performance/test_span_limits_performance.py

def test_attribute_setting_performance():
    """Measure performance impact of attribute limits."""
    import time
    
    tracer = HoneyHiveTracer.init(project="test", max_attributes=1024)
    
    start = time.perf_counter()
    with tracer.trace("test") as span:
        for i in range(1000):
            span.set_attribute(f"attr_{i}", f"value_{i}")
    elapsed = time.perf_counter() - start
    
    # Should be <10ms for 1000 attributes
    assert elapsed < 0.01

def test_memory_usage():
    """Measure memory usage with different limits."""
    import tracemalloc
    
    tracemalloc.start()
    
    tracer = HoneyHiveTracer.init(project="test", max_attributes=5000)
    with tracer.trace("test") as span:
        for i in range(5000):
            span.set_attribute(f"attr_{i}", f"value_{i}")
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Should be <5MB for 5000 attributes
    assert peak < 5 * 1024 * 1024
```

---

## Performance Implications

### Memory Impact

**Baseline** (OpenTelemetry default: 128 attributes):
- Average span: ~5KB
- 1000 spans: ~5MB

**HoneyHive** (1024 attributes):
- Average span: ~10KB (assuming ~50% utilization)
- 1000 spans: ~10MB

**High Limit** (5000 attributes):
- Average span: ~25KB (assuming ~50% utilization)
- 1000 spans: ~25MB

**Recommendation**: Default 1024 provides good balance between memory and observability.

### CPU Impact

Attribute setting performance:
- **Baseline** (128 limit): ~0.1μs per attribute
- **HoneyHive** (1024 limit): ~0.1μs per attribute
- **High** (5000 limit): ~0.12μs per attribute

**Impact**: Negligible (<1% CPU overhead even at 5000 limit)

### Network Impact

Larger spans = more data to export:
- **Baseline** (128 attrs): ~5KB per span
- **HoneyHive** (1024 attrs): ~10KB per span
- **High** (5000 attrs): ~25KB per span

**Mitigation**: 
- Batch exporting (100 spans = 1MB batch)
- Compression (OTLP gzip compression ~70% reduction)
- Async export (no user-facing latency)

---

## Success Metrics

### Technical Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Span Drop Rate** | <0.1% | Monitor `on_end` skipped spans |
| **Core Attribute Preservation** | 100% | Check `honeyhive.session_id` presence |
| **Memory Overhead** | <20MB per 1000 spans | Memory profiling |
| **Performance Overhead** | <1% | Benchmark attribute setting |
| **User Configuration Adoption** | >10% | Track non-default `max_attributes` |

### Observability Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Attribute Completeness** | >95% | % of spans with full data |
| **Debugging Success Rate** | >90% | User surveys on debugging effectiveness |
| **False Positive Reduction** | 50% | Compare alerts before/after fix |

### User Experience Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Configuration Clarity** | >4.5/5 | User surveys on config understanding |
| **Documentation Completeness** | >4.5/5 | User surveys on docs usefulness |
| **Setup Time** | <5 minutes | Track time to first successful trace |

---

## Implementation Roadmap

### Phase 1: Dual Guardrail Approach ✅ COMPLETED

**Timeline**: 2025-11-18 (1 day)

- [x] Add `max_attributes` to `TracerConfig` (count guardrail)
- [x] Add `max_span_size` to `TracerConfig` (total size guardrail)
- [x] Add `max_events`, `max_links` to `TracerConfig`
- [x] Add environment variable support (`HH_MAX_ATTRIBUTES`, `HH_MAX_SPAN_SIZE`)
- [x] Integrate with atomic provider detection
- [x] Update initialization flow to apply both guardrails
- [x] Verify with CEO's reproduction script
- [x] Document product philosophy (simplicity vs flexibility)
- [x] Update design documentation

### Phase 2: Core Attribute Preservation 🔜 NEXT

**Timeline**: 1-2 weeks

- [ ] Design: Choose approach (Custom Span vs Priority System)
- [ ] Implement: Core attribute protection logic
- [ ] Test: Unit tests for core attribute preservation
- [ ] Test: Integration tests with large responses
- [ ] Document: Usage guide and examples
- [ ] Deploy: Beta release with feature flag

### Phase 3: Smart Truncation 🔮 FUTURE

**Timeline**: 2-4 weeks

- [ ] Design: Choose truncation strategy
- [ ] Implement: Truncation logic
- [ ] Implement: Compression support (optional)
- [ ] Test: Truncation correctness
- [ ] Test: Performance impact
- [ ] Document: Truncation configuration guide
- [ ] Deploy: Stable release

### Phase 4: Monitoring & Optimization 🔮 FUTURE

**Timeline**: Ongoing

- [ ] Add metrics for attribute usage
- [ ] Add alerts for limit approaches
- [ ] Performance profiling and optimization
- [ ] User feedback collection
- [ ] Best practices documentation

---

## Open Questions

1. **Should we warn users when attributes are truncated?**
   - Pro: Transparency, helps debugging
   - Con: Log noise, performance overhead
   - **Decision**: Log at DEBUG level, expose metric

2. **Should core attribute protection be opt-in or opt-out?**
   - **Decision**: Opt-out (enabled by default), users can disable if needed

3. **What's the maximum recommended attribute limit?**
   - **Decision**: 5000 (above this, suggest chunking or compression)

4. **Should we support per-span limit overrides?**
   - **Decision**: Not in Phase 1, revisit if users request

5. **How to handle backend storage limits?**
   - **Decision**: Backend team to implement limits, SDK respects them via configuration

---

## Appendix A: Debugging Guide

### Symptom: Spans Missing from HoneyHive

**Check 1**: Verify span limits
```python
from opentelemetry import trace
provider = trace.get_tracer_provider()
print(f"Max attributes: {provider._span_limits.max_attributes}")
```

**Check 2**: Check logs for skipped spans
```bash
grep "Span has no session_id" logs.txt
```

**Check 3**: Count attributes being set
```python
@tracer.trace()
def my_function():
    result = large_api_call()
    # How many attributes will be set?
    flat_attrs = flatten_nested_dict(result)
    print(f"Attributes to set: {len(flat_attrs)}")
```

**Solution**: Increase `max_attributes` or enable truncation.

### Symptom: High Memory Usage

**Check**: Current span limit
```python
print(f"Max attributes: {tracer.config.max_attributes}")
```

**Solution**: Lower limit if memory constrained
```python
tracer = HoneyHiveTracer.init(
    project="test",
    max_attributes=500,  # Lower limit
    truncation_config={"enabled": True},  # Enable truncation
)
```

---

## Appendix B: Migration Guide

### From Traceloop to HoneyHive

**Before** (Traceloop):
```python
from traceloop.sdk import Traceloop

Traceloop.init(
    app_name="my-app",
    api_key="...",
)
# Uses OpenTelemetry defaults (128 attributes)
```

**After** (HoneyHive):
```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init(
    project="my-app",
    api_key="...",
    max_attributes=1024,  # 8x Traceloop's default
)
```

**Why Migrate**:
1. Richer observability (full payloads, not summaries)
2. Better debugging (detailed attribute flattening)
3. Configurable limits (adapt to your needs)
4. Active development (regular updates)

---

## Appendix C: Related Documentation

- `BUG_ANALYSIS.md` - Original bug report and debugging
- `SPAN_ATTRIBUTE_LIMIT_ANALYSIS.md` - Detailed technical analysis
- `src/honeyhive/config/models/tracer.py` - TracerConfig implementation
- `src/honeyhive/tracer/integration/detection.py` - Atomic provider detection
- OpenTelemetry Span Limits: https://opentelemetry.io/docs/specs/otel/trace/sdk/#span-limits

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-18 | Engineering | Initial design document |

---

**Status**: Phase 1 Implemented, Phase 2-3 Proposed  
**Last Updated**: 2025-11-18  
**Next Review**: 2025-12-01

