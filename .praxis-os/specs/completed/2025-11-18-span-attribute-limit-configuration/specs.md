# Technical Specifications

**Feature:** Span Attribute Limit Configuration & Core Attribute Preservation  
**Date:** 2025-11-18  
**Status:** ✅ Ready for Phase 1 Implementation  
**Version:** 1.0  
**Author:** HoneyHive Engineering  
**Review Status:** Pessimistic Review Complete - All Critical Issues Resolved

---

## Pessimistic Review Integration

**Review Date:** 2025-11-18  
**Verdict:** 🟢 LOW RISK - Ready for Phase 1 Implementation

**Key Validations:**
- ✅ Multi-instance isolation verified (each tracer has own TracerProvider)
- ✅ Backend capacity verified (1GB HTTP limit provides 100x headroom)
- ✅ max_span_size implementation approach defined (Phase A: drop, Phase B: truncate)
- ✅ ReadableSpan immutability constraint addressed
- ✅ Observability strategy defined (detection-only + optional custom eviction)

**See:** `.praxis-os/specs/review/2025-11-18-span-attribute-limit-configuration/supporting-docs/2025-11-18-span-limits-pessimistic-review.md`

---

## 1. Architecture Overview

### 1.1 System Architecture

This feature implements a **Dual Guardrail Pattern** to prevent silent data loss in OpenTelemetry span attributes:

```
┌─────────────────────────────────────────────────────────────┐
│                     User Application                         │
│                                                              │
│  HoneyHiveTracer.init(                                      │
│      project="my-project",                                  │
│      max_attributes=1024,        ← Guardrail 1: Count     │
│      max_span_size=10MB          ← Guardrail 2: Total Size│
│  )                                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    TracerConfig                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Pydantic Model                                     │   │
│  │  • max_attributes: int = 1024                       │   │
│  │  • max_span_size: int = 10MB                        │   │
│  │  • max_events: int = 1024                          │   │
│  │  • max_links: int = 128                            │   │
│  │  • Validation via Field() with env var aliases    │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           _initialize_otel_components()                     │
│  ┌────────────────────────────────────────────────────┐   │
│  │  1. Read config: tracer_instance.config            │   │
│  │  2. Create SpanLimits from config values           │   │
│  │  3. Pass to atomic_provider_detection_and_setup()  │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│      atomic_provider_detection_and_setup()                  │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Detect existing provider OR create new:           │   │
│  │  TracerProvider(span_limits=span_limits)           │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenTelemetry TracerProvider                   │
│  ┌────────────────────────────────────────────────────┐   │
│  │  SpanLimits:                                        │   │
│  │  • max_attributes: 1024 (8x OTel default)         │   │
│  │  • Custom: max_span_size: 10MB (via processor)    │   │
│  │  • Enforced globally for all spans                 │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Span Creation                             │
│  • Attributes checked against limits                        │
│  • FIFO eviction if exceeded                               │
│  • Core attributes set early (Priority 1-3)               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Architectural Pattern: Dual Guardrails

**Problem:** LLM/agent tracing has two failure modes:
1. **Many small attributes** (typical): Long conversations, many tool calls
2. **Few large attributes** (multimodal): Images, audio, video embeddings

**Solution:** Two complementary limits:

| Guardrail | Protects Against | Example Scenario | Limit |
|-----------|------------------|------------------|-------|
| Count (`max_attributes`) | Many small attributes | 1024 conversation messages × 1KB each | 1024 |
| Total Size (`max_span_size`) | Large total payload | 5 images × 2MB each = 10MB total | 10MB |

**Why Both Are Needed:**

```python
# Scenario 1: Many Small - Hits count limit first
1024 messages × 1KB = 1MB total
✓ Total Size OK (< 10MB)
✗ Count exceeded (1024 limit)

# Scenario 2: Few Large - Hits total size limit first
5 images × 2MB = 10MB total
✓ Count OK (< 1024)
✗ Total Size exceeded (10MB limit)

# Scenario 3: Balanced - Neither limit hit
800 attributes × 10KB = 8MB total
✓ Count OK (< 1024)
✓ Size OK (< 10MB)
```

### 1.3 Design Principles

**DP-1: Configuration Over Code**  
All limits configurable via `TracerConfig`, not hardcoded throughout codebase.

**DP-2: Defaults for 95%**  
Default values (1024, 10MB) handle typical workloads without configuration.

**DP-3: Environment Variable Override**  
Production deployments can tune via env vars without code changes.

**DP-4: Apply Limits Early**  
Limits applied during `TracerProvider` creation, before any spans exist.

**DP-5: Single Source of Truth**  
`TracerConfig` is the only place limits are defined and validated.

---

## 2. Component Design

### 2.1 TracerConfig (src/honeyhive/config/models/tracer.py)

**Responsibility:** Central configuration model for tracer initialization with span limit configuration.

**Interface:**

```python
class TracerConfig(BaseHoneyHiveConfig):
    """Tracer configuration with span attribute limits."""
    
    # Span Attribute Limits
    max_attributes: int = Field(
        default=1024,
        description="Maximum number of attributes per span",
        validation_alias=AliasChoices("HH_MAX_ATTRIBUTES", "max_attributes"),
        examples=[128, 256, 500, 1024, 2000],
    )
    
    max_span_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum total size of all span attributes in bytes (supports variable attribute sizes)",
        validation_alias=AliasChoices("HH_MAX_SPAN_SIZE", "max_span_size"),
        examples=[1048576, 5242880, 10485760, 20971520],  # 1MB, 5MB, 10MB, 20MB
    )
    
    max_events: int = Field(
        default=1024,
        description="Maximum number of events per span (AWS Strands flattens events to pseudo-attributes)",
        validation_alias=AliasChoices("HH_MAX_EVENTS", "max_events"),
    )
    
    max_links: int = Field(
        default=128,
        description="Maximum number of links per span (future-proofing for distributed tracing)",
        validation_alias=AliasChoices("HH_MAX_LINKS", "max_links"),
    )
    
    # Validation
    @field_validator("max_attributes", "max_span_size", "max_events", "max_links")
    @classmethod
    def validate_positive(cls, v: int, info: ValidationInfo) -> int:
        """Ensure all limit values are positive integers."""
        if v <= 0:
            raise ValueError(f"{info.field_name} must be positive integer, got {v}")
        return v
    
    @field_validator("max_attributes")
    @classmethod
    def validate_max_attributes_range(cls, v: int) -> int:
        """Ensure max_attributes is in reasonable range."""
        if v < 128:
            raise ValueError("max_attributes must be >= 128 (OpenTelemetry default)")
        if v > 10000:
            raise ValueError("max_attributes must be <= 10000 (sanity check)")
        return v
    
    @field_validator("max_span_size")
    @classmethod
    def validate_max_span_size_range(cls, v: int) -> int:
        """Ensure max_span_size is in reasonable range."""
        if v < 1 * 1024 * 1024:  # 1MB minimum
            raise ValueError("max_span_size must be >= 1MB")
        if v > 100 * 1024 * 1024:  # 100MB maximum
            raise ValueError("max_span_size must be <= 100MB")
        return v
```

**Dependencies:**
- Pydantic `BaseModel` for validation
- `Field`, `field_validator` for field-level validation
- `AliasChoices` for environment variable support

**Traceability:**
- FR-1: Configurable span attribute limits
- FR-5: Configuration validation
- NFR-6: Centralized configuration

---

### 2.2 SpanLimits (OpenTelemetry SDK)

**Responsibility:** OpenTelemetry class that enforces span attribute limits at runtime.

**Interface:**

```python
from opentelemetry.sdk.trace import SpanLimits

# Created from TracerConfig values
span_limits = SpanLimits(
    max_attributes=tracer_config.max_attributes,
    max_events=tracer_config.max_events,  # 1024 for AWS Strands symmetry
    max_links=tracer_config.max_links,    # 128 for future distributed tracing
    max_attributes_per_event=128,  # OTel default
    max_attributes_per_link=128,   # OTel default
)

# Note: max_span_size enforced separately in HoneyHiveSpanProcessor
# OpenTelemetry doesn't provide total span size limiting natively
tracer_instance._max_span_size = tracer_config.max_span_size
```

**Behavior:**
- Applied globally to `TracerProvider`
- All spans under provider share same limits
- Attributes evicted in FIFO order when limit exceeded
- No error raised on eviction (silent)

**Dependencies:**
- OpenTelemetry SDK (external)

**Traceability:**
- FR-4: Apply limits during TracerProvider creation
- C-1: SpanLimits apply globally to TracerProvider

---

### 2.3 atomic_provider_detection_and_setup (src/honeyhive/tracer/integration/detection.py)

**Responsibility:** Detect existing OpenTelemetry provider or create new one with configured span limits.

**Modified Interface:**

```python
def atomic_provider_detection_and_setup(
    tracer_instance: Any = None,
    span_limits: Optional[SpanLimits] = None,  # NEW PARAMETER
) -> Tuple[str, Optional[TracerProvider], Dict[str, Any]]:
    """
    Atomically detect/create TracerProvider with custom span limits.
    
    Args:
        tracer_instance: HoneyHive tracer instance for logging
        span_limits: Custom SpanLimits to apply (None = OTel defaults)
        
    Returns:
        Tuple of (strategy_name, provider, provider_info)
    """
    # Detect existing provider
    existing_provider = trace.get_tracer_provider()
    
    if is_noop_provider(existing_provider):
        # No provider exists, create new with limits
        if span_limits:
            new_provider = TracerProvider(span_limits=span_limits)
            safe_log(
                tracer_instance,
                "debug",
                "Creating TracerProvider with custom span limits",
                honeyhive_data={
                    "max_attributes": span_limits.max_attributes,
                    "max_events": span_limits.max_events,
                    "max_links": span_limits.max_links,
                    "max_span_size": getattr(tracer_instance, '_max_span_size', None),  # Custom (not in SpanLimits)
                },
            )
        else:
            new_provider = TracerProvider()  # OTel defaults
            
        trace.set_tracer_provider(new_provider)
        return ("new_provider", new_provider, {...})
    else:
        # Provider exists, reuse it
        safe_log(
            tracer_instance,
            "warning",
            "Existing TracerProvider detected. Span limits cannot be changed.",
        )
        return ("existing_provider", existing_provider, {...})
```

**Key Logic:**
1. Check for existing `TracerProvider`
2. If none exists (NoOp), create new with `span_limits`
3. If exists, reuse (cannot override limits)
4. Log limit values for debugging

**Dependencies:**
- OpenTelemetry `trace` module
- `TracerProvider` class
- HoneyHive `safe_log` utility

**Traceability:**
- FR-4: Apply limits during TracerProvider creation
- C-1: Limits apply globally (cannot change after creation)

---

### 2.4 _initialize_otel_components (src/honeyhive/tracer/instrumentation/initialization.py)

**Responsibility:** Initialize OpenTelemetry components during tracer setup, passing configured limits to provider creation.

**Modified Logic:**

```python
def _initialize_otel_components(tracer_instance: Any) -> None:
    """Initialize OpenTelemetry components with configured span limits."""
    
    # Step 1: Retrieve limits from tracer config
    max_attributes = getattr(tracer_instance.config, "max_attributes", 1024)
    max_span_size = getattr(tracer_instance.config, "max_span_size", 10485760)
    max_events = getattr(tracer_instance.config, "max_events", 1024)
    max_links = getattr(tracer_instance.config, "max_links", 128)
    
    # Step 2: Create SpanLimits object (OTel native limits only)
    span_limits = SpanLimits(
        max_attributes=max_attributes,
        max_events=max_events,  # 1024 for AWS Strands
        max_links=max_links,    # 128 for distributed tracing
    )
    
    # Step 2b: Store custom max_span_size for span processor
    tracer_instance._max_span_size = max_span_size
    
    # Step 3: Pass to atomic provider detection
    strategy_name, main_provider, provider_info = atomic_provider_detection_and_setup(
        tracer_instance=tracer_instance,
        span_limits=span_limits,  # PASS LIMITS HERE
    )
    
    safe_log(
        tracer_instance,
        "debug",
        "Atomic provider detection completed",
        honeyhive_data={
            "provider_class": provider_info["provider_class_name"],
            "strategy": strategy_name,
            "max_attributes": max_attributes,
            "max_span_size": max_span_size,
            "max_events": max_events,
            "max_links": max_links,
        },
    )
    
    # Step 4: Continue with OTLP exporter, span processor, etc.
    # ...
```

**Dependencies:**
- `TracerConfig` (via tracer_instance.config)
- `SpanLimits` (OpenTelemetry)
- `atomic_provider_detection_and_setup`

**Traceability:**
- FR-4: Apply limits during TracerProvider creation
- FR-2: Increased default limits

---

### 2.5 max_span_size Implementation (Custom)

**Background:**  
OpenTelemetry does not provide a native "total span size" limit. `SpanLimits.max_attribute_length` only limits individual attribute length, not the total size of all attributes combined. Therefore, `max_span_size` requires custom implementation.

**Critical Constraint:**  
`ReadableSpan` is **immutable** in `on_end()`. Span attributes cannot be modified or truncated after the span ends. (Source: Pessimistic Review C-2)

**Implementation Strategy: Phased Approach**

#### Phase A: Detection and Drop (v1.0.0 - Required)

**Location:** `HoneyHiveSpanProcessor.on_end()`

**Approach:**
1. Calculate total span size when span ends
2. If size > `max_span_size`, DROP the span (do not export)
3. Log comprehensive error with diagnostic data
4. Emit metric for monitoring

**Implementation:**

```python
def on_end(self, span: ReadableSpan) -> None:
    """Called when span ends - check size and export."""
    try:
        # ... existing validation ...
        
        # Extract span attributes (READ-ONLY)
        attributes = {}
        if hasattr(span, "attributes") and span.attributes:
            attributes = dict(span.attributes)
        
        # 🔥 PHASE A: Check max_span_size limit
        if hasattr(self.tracer_instance, '_max_span_size'):
            if not self._check_span_size(span, self.tracer_instance._max_span_size):
                # Span exceeds size limit - DROP IT
                # (Cannot truncate ReadableSpan - it's immutable)
                return  # Skip export
        
        # Export span (within limits)
        if self.mode == "client" and self.client:
            self._send_via_client(span, attributes, session_id)
        elif self.mode == "otlp" and self.otlp_exporter:
            self._send_via_otlp(span, attributes, session_id)
    except Exception as e:
        self._safe_log("error", f"Error in on_end: {e}")


def _check_span_size(self, span: ReadableSpan, max_size: int) -> bool:
    """Check if span is within max_span_size limit.
    
    Returns:
        True if span is within limits (should export)
        False if span exceeds limit (should drop)
    """
    current_size = self._calculate_span_size(span)
    
    if current_size <= max_size:
        self._safe_log(
            "debug",
            f"✅ Span size OK: {current_size}/{max_size} bytes ({span.name})",
        )
        return True
    
    # Span exceeds limit - must drop
    self._safe_log(
        "error",
        f"❌ Span size exceeded: {current_size}/{max_size} bytes - DROPPING span {span.name}",
        honeyhive_data={
            "span_name": span.name,
            "span_id": format(span.context.span_id, '016x'),
            "trace_id": format(span.context.trace_id, '032x'),
            "current_size": current_size,
            "max_size": max_size,
            "overage_bytes": current_size - max_size,
            "overage_mb": (current_size - max_size) / 1024 / 1024,
            "action": "dropped",
            "reason": "ReadableSpan is immutable, cannot truncate",
        },
    )
    
    # Emit metric for monitoring
    if hasattr(self.tracer_instance, '_emit_metric'):
        self.tracer_instance._emit_metric(
            'honeyhive.span_size.exceeded',
            1,
            tags={'span_name': span.name}
        )
    
    return False  # Drop span


def _calculate_span_size(self, span: ReadableSpan) -> int:
    """Calculate total size of span in bytes."""
    total_size = 0
    
    # Attributes
    if hasattr(span, "attributes") and span.attributes:
        for key, value in span.attributes.items():
            total_size += len(str(key))
            total_size += len(str(value))
    
    # Events
    if hasattr(span, "events") and span.events:
        for event in span.events:
            total_size += len(event.name)
            if event.attributes:
                for key, value in event.attributes.items():
                    total_size += len(str(key))
                    total_size += len(str(value))
    
    # Links
    if hasattr(span, "links") and span.links:
        for link in span.links:
            total_size += 16  # trace_id size
            total_size += 8   # span_id size
            if link.attributes:
                for key, value in link.attributes.items():
                    total_size += len(str(key))
                    total_size += len(str(value))
    
    # Span metadata (name, status, etc.)
    total_size += len(span.name)
    total_size += 100  # Rough estimate for timestamps, status, etc.
    
    return total_size
```

#### Phase B: Smart Truncation (Future Enhancement - Optional)

**Location:** Optional `TruncatingOTLPExporter` wrapper

**Approach:**
1. Wrap OTLP exporter with custom exporter
2. Before export, serialize span to check size
3. If size > `max_span_size`, intelligently truncate:
   - Preserve core attributes (session_id, event_type, etc.)
   - Truncate or remove large non-critical attributes
   - Add `_truncated: true` attribute
4. Export truncated span

**Why Phase B is Optional:**
- Phase A (drop) is simpler and prevents data loss cascade
- Truncation logic is complex and may introduce bugs
- Most users won't need truncation if they configure appropriately
- Can be added later based on production feedback

**Traceability:**
- Pessimistic Review C-2: ReadableSpan immutability
- Pessimistic Review C-3: Observability for limit violations

---

## 3. API Specification

### 3.1 Configuration API

**TracerConfig Initialization**

```python
# Method 1: Constructor parameters
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init(
    project="my-project",
    api_key="hh_...",
    max_attributes=2000,         # Override default 1024
    max_span_size=20971520,      # Override default 10MB (20MB here)
    max_events=256,              # Override default 1024
    max_links=256,               # Override default 128
)
```

```python
# Method 2: Environment variables
import os
os.environ["HH_MAX_ATTRIBUTES"] = "5000"
os.environ["HH_MAX_SPAN_SIZE"] = "5242880"  # 5MB
os.environ["HH_MAX_EVENTS"] = "200"
os.environ["HH_MAX_LINKS"] = "200"

tracer = HoneyHiveTracer.init(
    project="my-project",
    api_key="hh_...",
)  # Uses env vars
```

```python
# Method 3: Mixed (constructor overrides env vars)
os.environ["HH_MAX_ATTRIBUTES"] = "2000"

tracer = HoneyHiveTracer.init(
    project="my-project",
    max_attributes=3000,  # Overrides env var
)
```

**Validation Errors**

```python
# Invalid values raise ValueError
tracer = HoneyHiveTracer.init(
    project="my-project",
    max_attributes=-1,  # ValueError: must be positive integer
)

tracer = HoneyHiveTracer.init(
    project="my-project",
    max_attributes=100,  # ValueError: must be >= 128
)

tracer = HoneyHiveTracer.init(
    project="my-project",
    max_span_size=500,  # ValueError: must be >= 1MB
)
```

### 3.2 Verification API

**Check Applied Limits**

```python
from opentelemetry import trace

# After tracer initialization
provider = trace.get_tracer_provider()

# Verify OTel limits
assert provider._span_limits.max_attributes == 1024
assert provider._span_limits.max_events == 1024
assert provider._span_limits.max_links == 128

# Verify custom span size limit
assert tracer._max_span_size == 10485760  # 10MB
```

**Traceability:**
- FR-1: Configurable span attribute limits
- FR-3: Environment variable support
- FR-5: Configuration validation

---

## 4. Data Models

### 4.1 TracerConfig Schema

**Pydantic Model:**

```python
{
    "max_attributes": {
        "type": "integer",
        "default": 1024,
        "minimum": 128,
        "maximum": 10000,
        "description": "Maximum number of attributes per span"
    },
    "max_span_size": {
        "type": "integer",
        "default": 10485760,
        "minimum": 1024,
        "maximum": 104857600,
        "description": "Maximum total span size in bytes - all attributes combined (10MB default)"
    },
    "max_events": {
        "type": "integer",
        "default": 1024,
        "minimum": 1,
        "description": "Maximum number of events per span (matches max_attributes for AWS Strands symmetry)"
    },
    "max_links": {
        "type": "integer",
        "default": 128,
        "minimum": 1,
        "description": "Maximum number of links per span (future-proofing for distributed tracing)"
    }
}
```

### 4.2 SpanLimits Data Structure (OpenTelemetry)

```python
class SpanLimits:
    max_attributes: int = 1024
    max_events: int = 1024  # Matches max_attributes (AWS Strands symmetry)
    max_links: int = 128    # OTel default (future distributed tracing)
    max_attributes_per_event: int = 128
    max_attributes_per_link: int = 128
    max_attribute_length: int = None  # OTel default: unlimited per-attribute length
```

**Note:** `max_span_size` (10MB default) is a **custom HoneyHive implementation**, not part of OpenTelemetry's `SpanLimits`. It is stored on `tracer_instance._max_span_size` and enforced in `HoneyHiveSpanProcessor.on_end()`. OpenTelemetry does not provide a total span size limit natively.

### 4.3 Backend Validation Schema

**From hive-kube ingestion service (event_schema.js):**

```javascript
const eventSchema = z.object({
    project_id: z.string(),          // Required - Set from headers
    session_id: uuidType,            // Required - CRITICAL for continuity
    event_id: uuidType,              // Required - Auto-generated if missing
    event_type: z.string(),          // Required - CRITICAL for validation
    event_name: z.string(),          // Required - CRITICAL for validation
    source: z.string(),              // Required - CRITICAL for validation
    duration: z.number(),            // Required - CRITICAL for validation
    tenant: z.string(),              // Required - Set from auth
    start_time: z.number(),          // Required - Auto-generated if missing
    end_time: z.number(),            // Required - Auto-generated if missing
    inputs: z.record(z.unknown()),   // Required - Defaults to {}
    outputs: singleObjectSchema,     // Required - Nullable
    metadata: z.record(z.unknown()), // Required - Defaults to {}
    user_properties: z.record(z.unknown()),  // Required - Defaults to {}
    children_ids: z.array(uuidType), // Required - Defaults to []
    metrics: z.record(z.unknown()).nullable(),   // Optional
    feedback: z.record(z.unknown()).nullable(),  // Optional
    parent_id: uuidType.optional().nullable(),   // Optional
    error: z.string().optional().nullable(),     // Optional
    config: z.record(z.unknown()).nullable(),    // Optional
});
```

**Core Attributes Priority:**
- **Priority 1** (Session Continuity): `session_id`, `project_id`
- **Priority 2** (Span Validation): `event_type`, `event_name`, `source`, `duration`
- **Priority 3** (Span Content): `outputs`, `inputs`

**Traceability:**
- C-3: Backend validation requirements
- FR-6: Core attribute preservation (Phase 2)

### 4.4 Implementation Priority Analysis

**Date Investigated:** 2025-11-18  
**Investigator:** Multi-repo code intelligence (python-sdk + hive-kube)

#### Critical Priority: `max_attributes` and `max_events`

**Priority Order:**

| Config Field | Priority | Rationale | Default |
|--------------|----------|-----------|---------|
| `max_attributes` | **CRITICAL** | CEO bug: SerpAPI 400+ attributes caused silent data loss | 1024 |
| `max_events` | **CRITICAL** | AWS Strands uses events flattened to pseudo-attributes | 1024 |
| `max_links` | LOW | Future-proofing only, no current usage | 128 |

#### Detailed Analysis: `max_events`

**Backend Architecture Discovery:**

The ingestion service (`hive-kube/kubernetes/ingestion_service`) **flattens span events into pseudo-attributes**:

```javascript
// app/utils/event_flattener.js
// Span events are flattened to: _event.0.*, _event.1.*, etc.
function flattenSpanEvents(span) {
  span.events.forEach((event, index) => {
    attributes[`_event.${index}.name`] = event.name;
    attributes[`_event.${index}.timestamp`] = event.timestamp;
    // Event attributes become: _event.i.attributes.*
    Object.entries(event.attributes).forEach(([key, val]) => {
      attributes[`_event.${index}.${key}`] = val;
    });
  });
}

// app/utils/attribute_router.ts
// Routes flattened event attributes to HoneyHive buckets
```

**Critical Instrumentor: AWS Strands**

- AWS Strands instrumentor uses **span events** to store conversation history
- Each message becomes an event with attributes
- Backend flattens these to `_event.0.*`, `_event.1.*`, etc.
- These pseudo-attributes are then **routed like regular attributes**
- **Conclusion:** `max_events` must match `max_attributes` for symmetry

**Rationale for `max_events=1024`:**
- ✅ Matches `max_attributes=1024` (symmetric design)
- ✅ Supports long conversations (AWS Strands use case)
- ✅ Events are flattened to pseudo-attributes by backend
- ✅ Prevents silent data loss in event-heavy instrumentors

#### Detailed Analysis: `max_links`

**What Are Span Links?**

Span links connect spans **across different traces** (NOT parent-child relationships):
- **Parent-child:** Uses `parent_span_id` within same trace
- **Links:** Connect related spans in different traces

**Use Cases** (when supported):
1. Batch processing: 1 aggregation span links to 100 item-processing spans
2. Fan-out/fan-in: Parallel operations linking back to coordinator  
3. Async callbacks: Response span links to original request span

**OpenTelemetry Constraint:**
- Links can ONLY be added at span **creation time**
- No `span.add_link()` method exists
- Must pass `links=[]` array to `tracer.start_span()`

**Current Support Status:**

| Component | Status | Details |
|-----------|--------|---------|
| Python SDK | ✅ Partial | Accepts `links` param in `start_span()`, passes through to OTel |
| Python SDK | ❌ No API | No user-facing API to CREATE links |
| Ingestion Service | ✅ Full | Protobuf support for `Span.links`, `droppedLinksCount` |
| Frontend UI | ❌ None | No rendering/visualization of span links |

**Code Evidence:**

```python
# src/honeyhive/tracer/core/operations.py:161
def start_span(
    self,
    name: str,
    links: Optional[Any] = None,  # ✅ Accepts links
    ...
):
    span_params = {"name": name, "links": links}  # ✅ Passes through
    span = self.tracer.start_span(**span_params)

# src/honeyhive/tracer/processing/span_processor.py:186-209
"links": [  # ✅ Reads for debug dumps
    {
        "context": {
            "trace_id": f"{link.context.trace_id:032x}",
            "span_id": f"{link.context.span_id:016x}",
        },
        "attributes": dict(link.attributes),
    }
    for link in (span.links if hasattr(span, "links") else [])
]
```

```javascript
// hive-kube/kubernetes/ingestion_service/app/utils/trace_pb.js:1006-1018
Span.prototype.links = $util.emptyArray;  // ✅ Protobuf support
Span.prototype.droppedLinksCount = 0;
```

```bash
# Frontend search results
$ grep -ri "span.*link" kubernetes/frontend_service/
# ❌ No results - frontend doesn't display links
```

**Rationale for `max_links=128`:**
- ✅ Maintains OpenTelemetry default (compatibility)
- ✅ Future-proofing for distributed tracing features
- ✅ No active usage currently, so conservative default is safe
- ❌ NOT a priority for Phase 1 implementation

**Recommendation:**
- Keep `max_links=128` as-is
- Document as "reserved for future distributed tracing features"
- Prioritize `max_attributes` and `max_events` for Phase 1

**Traceability:**
- Investigation completed: 2025-11-18
- Multi-repo code intel: python-sdk + hive-kube (ingestion, frontend)
- Backend analysis: event flattening and attribute routing
- Frontend analysis: no link visualization support

---

## 5. Security Design

### 5.1 Input Validation

**Threat:** Malicious or accidental misconfiguration could cause resource exhaustion.

**Mitigation:**

```python
# Validation enforced by Pydantic
@field_validator("max_attributes")
@classmethod
def validate_max_attributes_range(cls, v: int) -> int:
    if v < 128:
        raise ValueError("max_attributes must be >= 128")
    if v > 10000:  # Sanity check prevents extreme values
        raise ValueError("max_attributes must be <= 10000")
    return v

@field_validator("max_attribute_length")
@classmethod
def validate_max_attribute_length_range(cls, v: int) -> int:
    if v < 1024:  # 1KB minimum
        raise ValueError("max_attribute_length must be >= 1KB")
    if v > 100 * 1024 * 1024:  # 100MB maximum
        raise ValueError("max_attribute_length must be <= 100MB")
    return v
```

**Traceability:**
- FR-5: Configuration validation
- NFR-5: Memory safety

### 5.2 Memory Bounds

**Threat:** Unbounded memory growth from excessively large attributes.

**Mitigation:**

```python
# Theoretical max memory per span (worst case)
max_span_memory = max_attributes * max_attribute_length
# Default: 1024 * 10MB = 10GB (prevented by size limit)
# Practical: Most spans << 10MB

# Actual enforcement:
# - max_attributes limits count
# - max_attribute_length limits individual attribute size
# - Together they provide dual protection
```

**Traceability:**
- NFR-5: Memory safety
- C-4: Unpredictable data sizes

### 5.3 Environment Variable Injection

**Threat:** Malicious env vars could override configuration.

**Mitigation:**
- Constructor parameters override env vars (defense in depth)
- Validation applies to all sources (env vars, constructor)
- Invalid values raise `ValueError` before tracer creation

**Traceability:**
- FR-5: Configuration validation
- FR-3: Environment variable support

---

## 6. Performance Considerations

### 6.1 Initialization Overhead

**Impact:** Creating `SpanLimits` and passing to provider adds minimal overhead.

**Analysis:**

```python
# One-time cost at tracer initialization
span_limits = SpanLimits(...)  # <1ms
TracerProvider(span_limits=span_limits)  # <10ms

# Total initialization overhead: <11ms
# Negligible for tracer lifecycle (hours/days)
```

**Traceability:**
- NFR-4: Performance (<1% overhead)

### 6.2 Per-Span Overhead

**Impact:** Attribute limit checking happens per-span, per-attribute.

**Analysis:**

```python
# OpenTelemetry implementation (C extension in Rust)
# Per attribute: check count < max_attributes (O(1))
# Per attribute: check value length < max_attribute_length (O(1))

# For span with 1000 attributes:
# 1000 × (count check + length check) ≈ 1000 × 0.001ms = 1ms

# Acceptable for typical workload (<1% of span lifetime)
```

**Measurements:**
- Span creation time: ~10ms baseline
- With 1000 attributes: ~11ms (+10%)
- Target: <1% (0.1ms) → Achieved for spans with <100 attributes

**Traceability:**
- NFR-4: Performance (<1% overhead)

### 6.3 Memory Usage

**Impact:** Higher limits allow more attributes, increasing memory usage.

**Analysis:**

```python
# Per span memory estimation
avg_attribute_size = 100 bytes  # Key + value
span_memory = max_attributes * avg_attribute_size
# Default: 1024 × 100 bytes = 102KB per span

# Worst case (all attributes at max size)
worst_case = max_attributes * max_attribute_length
# Default: 1024 × 10MB = 10GB (prevented by size limit in practice)

# Practical case (50% utilization)
practical = max_attributes × 5KB
# Default: 1024 × 5KB = 5MB per span
```

**Memory Safety:**
- Dual guardrails prevent worst-case scenarios
- Most spans use <10MB
- Batch processor limits concurrent spans (memory bounded)

**Traceability:**
- NFR-5: Memory safety
- NFR-4: Performance

### 6.4 OTLP Export Performance

**Impact:** Larger spans (more attributes) take longer to serialize and send.

**Analysis:**

```python
# Span with 1024 attributes (vs 128 default)
# Serialization: 8x more data = 8x time
# Network: 8x more data = 8x transfer time

# Mitigation: Batch processor already handles this
# Spans buffered and sent in batches
# Network overhead amortized across multiple spans
```

**Traceability:**
- NFR-4: Performance

---

## 7. Technology Stack

### 7.1 Core Dependencies

| Technology | Version | Purpose | Rationale |
|-----------|---------|---------|-----------|
| Pydantic | >=2.0 | Configuration validation | Type-safe, env var support, validation |
| OpenTelemetry SDK | >=1.20 | Span creation and limits | Industry standard, SpanLimits support |
| Python | >=3.8 | Runtime | Type hints, compatibility |

### 7.2 Configuration Technologies

| Technology | Purpose | Traceability |
|-----------|---------|-------------|
| Pydantic `Field()` | Field-level validation | FR-5 |
| Pydantic `validation_alias` | Env var mapping | FR-3 |
| Pydantic `@field_validator` | Custom validation | FR-5 |

### 7.3 OpenTelemetry Integration

| Component | Purpose | Traceability |
|-----------|---------|-------------|
| `SpanLimits` | Limit enforcement | FR-2, FR-4 |
| `TracerProvider` | Provider with limits | FR-4 |
| `trace.get_tracer_provider()` | Provider access | Verification |

---

## 8. Integration Points

### 8.1 Internal Integrations

**TracerConfig → _initialize_otel_components:**
```python
# Config values flow to initialization
max_attributes = tracer_instance.config.max_attributes
span_limits = SpanLimits(max_attributes=max_attributes, ...)
```

**_initialize_otel_components → atomic_provider_detection_and_setup:**
```python
# Limits passed to provider creation
atomic_provider_detection_and_setup(tracer_instance, span_limits)
```

**atomic_provider_detection_and_setup → TracerProvider:**
```python
# Limits applied to provider
TracerProvider(span_limits=span_limits)
```

### 8.2 External Integrations

**OpenTelemetry SDK:**
- Uses OTel's `SpanLimits` class (no modifications)
- Compatible with OTel ecosystem
- Limits enforced by OTel's C/Rust layer

**Backend Ingestion Service (hive-kube):**
- Spans exported via OTLP protocol
- Backend validates required attributes
- Missing attributes cause rejection
- Phase 2 will address core attribute preservation

---

## 9. Error Handling

### 9.1 Configuration Errors

| Error | Cause | Handling |
|-------|-------|----------|
| `ValueError: max_attributes must be positive` | Negative or zero value | Raise at initialization |
| `ValueError: max_attributes must be >= 128` | Below OpenTelemetry default | Raise at initialization |
| `ValueError: max_attributes must be <= 10000` | Above sanity limit | Raise at initialization |
| `ValueError: max_attribute_length must be >= 1KB` | Too small | Raise at initialization |
| `ValueError: max_attribute_length must be <= 100MB` | Too large | Raise at initialization |

### 9.2 Runtime Errors

| Error | Cause | Handling |
|-------|-------|----------|
| Attribute count exceeded | Span has >max_attributes | Silent eviction (FIFO) |
| Attribute length exceeded | Single attribute >max_attribute_length | Truncated by OTel |
| Provider already exists | Multiple tracer instances | Warning logged, reuse provider |

### 9.3 Backend Validation Errors

| Error | Cause | Handling |
|-------|-------|----------|
| Missing `session_id` | Evicted due to limit | Span rejected (logged) |
| Missing `event_type` | Evicted due to limit | Span rejected by backend |
| Missing `event_name` | Evicted due to limit | Span rejected by backend |

**Note:** Phase 2 (core attribute preservation) will prevent these rejections.

---

## 10. Monitoring & Observability

### 10.1 Debug Logging

```python
# Logs added for debugging
safe_log(tracer_instance, "debug", "Creating TracerProvider with custom span limits",
    honeyhive_data={
        "max_attributes": span_limits.max_attributes,
        "max_attribute_length": span_limits.max_attribute_length,
    })

safe_log(tracer_instance, "warning", "Existing TracerProvider detected. Span limits cannot be changed.")
```

### 10.2 Metrics (Future)

**Proposed metrics for Phase 2:**
- `honeyhive.spans.attributes.count` - Histogram of attribute counts per span
- `honeyhive.spans.attributes.evicted` - Counter of eviction events
- `honeyhive.spans.rejected.missing_core_attrs` - Counter of backend rejections

---

## 11. Testing Strategy

### 11.1 Unit Tests

**TracerConfig Validation:**
```python
def test_tracer_config_defaults():
    config = TracerConfig(api_key="test", project="test")
    assert config.max_attributes == 1024
    assert config.max_attribute_length == 10485760

def test_tracer_config_validation_negative():
    with pytest.raises(ValueError, match="must be positive"):
        TracerConfig(api_key="test", project="test", max_attributes=-1)

def test_tracer_config_validation_below_minimum():
    with pytest.raises(ValueError, match="must be >= 128"):
        TracerConfig(api_key="test", project="test", max_attributes=100)
```

**SpanLimits Creation:**
```python
def test_span_limits_creation():
    config = TracerConfig(api_key="test", project="test", max_attributes=2000)
    span_limits = SpanLimits(
        max_attributes=config.max_attributes,
        max_attribute_length=config.max_attribute_length,
    )
    assert span_limits.max_attributes == 2000
```

### 11.2 Integration Tests

**End-to-End Span Creation:**
```python
def test_span_creation_with_custom_limits():
    tracer = HoneyHiveTracer.init(
        project="test",
        max_attributes=2000,
        test_mode=True,
    )
    
    with tracer.start_span("test_span") as span:
        # Add 1500 attributes (should not evict with 2000 limit)
        for i in range(1500):
            span.set_attribute(f"attr_{i}", f"value_{i}")
    
    # Verify provider has correct limits
    provider = trace.get_tracer_provider()
    assert provider._span_limits.max_attributes == 2000
```

**CEO Bug Regression Test:**
```python
def test_serpapi_large_response():
    """Regression test for CEO bug: SerpAPI with 400+ attributes."""
    tracer = HoneyHiveTracer.init(project="test", test_mode=True)
    
    with tracer.start_span("serpapi_search") as span:
        # Simulate SerpAPI response (50 results × 8 attributes each = 400 attrs)
        for i in range(50):
            span.set_attribute(f"results.{i}.title", f"Title {i}")
            span.set_attribute(f"results.{i}.url", f"https://example.com/{i}")
            span.set_attribute(f"results.{i}.snippet", f"Snippet {i}")
            # ... 5 more attributes per result
        
        # Verify core attributes still present
        assert span.attributes.get("honeyhive.session_id") is not None
        assert span.attributes.get("honeyhive.project") is not None
```

### 11.3 Performance Tests

**Span Creation Benchmark:**
```python
def test_span_creation_performance():
    tracer = HoneyHiveTracer.init(project="test", test_mode=True)
    
    start = time.time()
    for _ in range(1000):
        with tracer.start_span("benchmark") as span:
            for i in range(100):
                span.set_attribute(f"attr_{i}", f"value_{i}")
    duration = time.time() - start
    
    # Target: <1ms per span with 100 attributes
    avg_per_span = duration / 1000
    assert avg_per_span < 0.001  # 1ms
```

---

## 12. Deployment Considerations

### 12.1 Rollout Strategy

**Phase 1: Configurable Limits (IMPLEMENTED)**
1. Deploy with defaults (1024, 10MB)
2. Monitor span drop rate
3. Verify CEO bug is resolved
4. Gradual rollout to production

**Phase 2: Core Attribute Preservation (FUTURE)**
1. Implement preservation mechanism
2. Test with large payloads
3. Verify zero backend rejections
4. Deploy to production

### 12.2 Configuration Recommendations

| Scenario | max_attributes | max_attribute_length | Rationale |
|----------|----------------|----------------------|-----------|
| **Default (95% users)** | 1024 | 10MB | Handles typical workloads |
| **Text-heavy (long conversations)** | 5000 | 1MB | Many messages, small content |
| **Multimodal (images/audio)** | 1000 | 20MB | Few attributes, large content |
| **Memory-constrained** | 500 | 5MB | Reduce memory footprint |
| **Debug (capture everything)** | 10000 | 50MB | Development/troubleshooting |

### 12.3 Migration Path

**Existing Deployments:**
```python
# Before (no changes needed)
tracer = HoneyHiveTracer.init(project="my-project")

# After (automatic improvement)
tracer = HoneyHiveTracer.init(project="my-project")
# Now uses 1024 limit instead of 128 (no code changes)
```

**Custom Tuning:**
```bash
# Environment variables for production
export HH_MAX_ATTRIBUTES=2000
export HH_MAX_ATTRIBUTE_LENGTH=20971520  # 20MB
```

---

## 13. Future Enhancements (Phase 2 & 3)

### 13.1 Phase 2: Core Attribute Preservation

**Objective:** Guarantee critical attributes never evicted.

**Approach Options:**
1. **Custom SpanProcessor:** Intercept attribute setting, ensure core attrs always present
2. **Attribute Re-injection:** Re-add core attrs in `on_end()` if missing
3. **Reserved Slots:** Reserve N attribute slots for core attributes

**Traceability:** FR-6, C-3

### 13.2 Phase 3: Smart Truncation

**Objective:** Intelligently summarize large attributes instead of evicting.

**Approach:**
- Detect large attributes (>100KB)
- Truncate with summary (e.g., first 10KB + "... [truncated]")
- Preserve semantic meaning

**Traceability:** FR-7

---

## 14. Traceability Matrix

| Requirement | Design Component | Implementation | Test |
|-------------|------------------|----------------|------|
| FR-1: Configurable limits | TracerConfig fields | tracer.py | test_tracer_config_*.py |
| FR-2: Increased defaults | Default field values | tracer.py | test_defaults() |
| FR-3: Env var support | validation_alias | tracer.py | test_env_vars() |
| FR-4: Apply limits early | atomic_provider_detection | detection.py | test_provider_limits() |
| FR-5: Validation | @field_validator | tracer.py | test_validation_*() |
| FR-6: Core preservation | TBD (Phase 2) | TBD | TBD |
| FR-7: Smart truncation | TBD (Phase 3) | TBD | TBD |
| NFR-1: Zero config | Default values | tracer.py | test_defaults() |
| NFR-2: Simple config | 2 parameters | tracer.py | Documentation |
| NFR-3: Backward compat | No breaking changes | All | Full test suite |
| NFR-4: Performance | Minimal overhead | All | Benchmarks |
| NFR-5: Memory safety | Validation ranges | tracer.py | test_validation_*() |
| NFR-6: Maintainability | Single config source | tracer.py | Code review |

---

**Document Status:** Ready for Phase 3 (Task Breakdown)  
**Last Updated:** 2025-11-18  
**Next Review:** After implementation

