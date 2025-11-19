# Software Requirements Document (SRD)

**Feature:** Span Attribute Limit Configuration & Core Attribute Preservation  
**Date:** 2025-11-18  
**Status:** ✅ Ready for Phase 1 Implementation  
**Author:** HoneyHive Engineering  
**Priority:** CRITICAL  
**Review Status:** Pessimistic Review Complete - All Critical Issues Resolved

---

## 1. Executive Summary

OpenTelemetry's default span attribute limit (128 attributes) causes silent data loss in observability traces when large API responses are flattened into span attributes. This is a cardinal sin for observability systems. 

A real-world bug reported by the CEO demonstrated that when SerpAPI returns 400+ attributes, OpenTelemetry silently evicts core HoneyHive attributes like `session_id`, causing spans to be dropped during export with no error message.

This specification defines a dual-guardrail approach: configurable count limits (default 1024) and total span size limits (default 10MB) that protect against both "many small attributes" and "few large attributes" scenarios common in LLM/agent tracing workloads.

### Pessimistic Review Results (2025-11-18)

**Verdict:** 🟢 LOW RISK - Ready for Phase 1 Implementation

**Issue Resolution:**
- **Critical Issues:** 5 → 0 ✅ (All resolved)
  - Multi-instance isolation verified
  - Backend capacity verified (1GB HTTP limit, 100x headroom)
  - max_span_size implementation approach defined
  - Observability addressed (detection-only logging + future custom eviction)
  - Responsibility boundaries documented
- **High Issues:** 8 → 0 blockers (N/A for pre-release or out of scope)
- **Medium Issues:** 6 → 0 blockers (Phase 2 quick wins or deferred)
- **Low Issues:** 4 (all nice-to-have enhancements)

**Architecture Validation:**
- Multi-instance isolation confirmed (each tracer has own TracerProvider)
- Backend capacity verified (1000MB HTTP limit vs. 10MB default span size)
- ReadableSpan immutability constraint addressed (drop in on_end, optional truncation in exporter)
- Configuration precedence clarified (explicit params > config > env vars > defaults)

**See:** `.praxis-os/specs/review/2025-11-18-span-attribute-limit-configuration/supporting-docs/2025-11-18-span-limits-pessimistic-review.md`

### Implementation Priority (Multi-Repo Code Intelligence Findings)

**Investigation Date:** 2025-11-18  
**Method:** Multi-repo code intelligence (python-sdk + hive-kube)

| Config Field | Priority | Default | Rationale |
|--------------|----------|---------|-----------|
| `max_attributes` | **CRITICAL** | 1024 | CEO bug: SerpAPI 400+ attributes caused silent data loss |
| `max_events` | **CRITICAL** | 1024 | AWS Strands uses events; backend flattens to pseudo-attributes |
| `max_span_size` | **CRITICAL** | 10MB | Total span size limit; multimodal data (images, audio) in LLM/agent space |
| `max_links` | LOW | 128 | Future-proofing for distributed tracing; no current usage |

**Key Finding:** The ingestion service (`hive-kube/kubernetes/ingestion_service/app/utils/event_flattener.js`) flattens span events into pseudo-attributes with the pattern `_event.i.*`. This means `max_events` must match `max_attributes` for symmetric protection, especially for AWS Strands instrumentor which stores conversation history as span events.

**Link Analysis:** Span links connect spans across different traces (NOT parent-child). While the SDK accepts links and ingestion service has full protobuf support, the frontend has no visualization capability yet. Therefore, `max_links=128` is conservative future-proofing only.

---

## 2. Business Goals

### BG-1: Prevent Silent Data Loss in Production Observability
**Priority:** CRITICAL  
**Business Impact:** HIGH  
**Owner:** Platform Engineering  

**Description:**  
Eliminate all scenarios where observability spans are silently dropped due to attribute limit eviction. Observability is the foundation of our product—silent data loss undermines customer trust and system reliability.

**Success Metrics:**
- Zero span drop rate due to attribute eviction
- 100% of spans with large payloads (>400 attributes) successfully exported
- No customer-reported incidents of missing trace data

**Rationale:**  
The CEO bug report demonstrated real data loss in production. This is unacceptable for an observability platform and must be addressed immediately.

---

### BG-2: Provide "Just Works" Defaults for 95% of Users
**Priority:** HIGH  
**Business Impact:** HIGH  
**Owner:** Product Management  

**Description:**  
Per CEO/CTO directive: "Customers have a hard time understanding the complexity of observability. They want simple solutions." The default configuration must handle typical LLM/agent workloads without any user configuration.

**Success Metrics:**
- 95% of users require zero configuration changes
- Default limits (1024 attributes, 10MB size) handle typical workloads
- No documentation required for basic usage

**Rationale:**  
Reducing cognitive load on customers increases adoption and reduces support burden. Sensible defaults are a product differentiator.

---

### BG-3: Enable Power Users to Handle Edge Cases
**Priority:** MEDIUM  
**Business Impact:** MEDIUM  
**Owner:** Platform Engineering  

**Description:**  
Provide simple configuration knobs (count + size) for the 5% of users with unusual requirements (e.g., multimodal data, extremely long conversations, memory-constrained environments).

**Success Metrics:**
- Power users can tune limits via 2 simple parameters
- Environment variable support for deployment flexibility
- Configuration documented with clear guidance

**Rationale:**  
Edge cases exist (very long conversations, image/audio data, constrained environments). Two simple knobs provide flexibility without overwhelming users.

---

### BG-4: Maintain Backward Compatibility
**Priority:** HIGH  
**Business Impact:** HIGH  
**Owner:** Platform Engineering  

**Description:**  
Existing code must work without changes. Users who don't know about this feature should see improved behavior without breaking changes.

**Success Metrics:**
- Zero breaking API changes
- Existing tracer initialization code works unchanged
- All existing tests pass

**Rationale:**  
Breaking changes slow adoption and create upgrade friction. Backward compatibility is essential for enterprise customers.

---

## 3. User Stories

### US-1: As an ML Engineer, I Want Traces to Always Capture My Data
**Priority:** CRITICAL  
**Persona:** ML Engineer building LLM applications  

**Story:**  
As an ML engineer using HoneyHive to trace my LLM application, I want every operation to be captured in traces, so that I can debug issues and optimize my application. When my application calls APIs that return large responses (like search results), I need the complete trace including all the result data and the session context.

**Acceptance Criteria:**
- [ ] Traces with large API responses (400+ attributes) are fully captured
- [ ] Session context (session_id, project) is never lost
- [ ] No silent data loss—if capture fails, I receive an error

**Current Pain:**  
CEO reported that SerpAPI calls with 50+ results cause session_id to be evicted, resulting in silently dropped spans.

---

### US-2: As a Platform Operator, I Want Simple Configuration
**Priority:** HIGH  
**Persona:** Platform operator deploying HoneyHive SDK  

**Story:**  
As a platform operator deploying the HoneyHive SDK across multiple services, I want default settings that "just work" for typical workloads, so that I don't need to tune every deployment. When I do need to adjust limits for edge cases, I want simple environment variables, not complex configuration files.

**Acceptance Criteria:**
- [ ] Default configuration handles 95% of workloads
- [ ] Can tune via 2 environment variables: HH_MAX_ATTRIBUTES, HH_MAX_ATTRIBUTE_LENGTH
- [ ] Clear documentation explains when tuning is needed

**Current Pain:**  
OpenTelemetry's 128-attribute default is too low for LLM workloads, requiring manual configuration.

---

### US-3: As a Developer, I Want Backward Compatibility
**Priority:** HIGH  
**Persona:** Developer maintaining existing HoneyHive integrations  

**Story:**  
As a developer with existing HoneyHive tracer code, I want new versions to improve behavior without breaking my code, so that I can upgrade without rewriting integrations. My initialization code should continue working exactly as before.

**Acceptance Criteria:**
- [ ] Existing `HoneyHiveTracer.init()` calls work unchanged
- [ ] All existing tests pass without modification
- [ ] Improved behavior is automatic (no code changes required)

**Current Pain:**  
Fear of breaking changes prevents timely SDK upgrades.

---

## 4. Functional Requirements

### FR-1: Configurable Span Attribute Limits
**Priority:** CRITICAL  
**Status:** Phase 1 - Implemented  

**Description:**  
Add configuration fields to `TracerConfig` that allow users to override OpenTelemetry's default span attribute limits.

**Specific Requirements:**
- Add `max_attributes` field (integer, default: 1024) - **CRITICAL PRIORITY**
- Add `max_span_size` field (integer, default: 10MB = 10,485,760 bytes) - **CRITICAL PRIORITY** (total span size, not per-attribute)
- Add `max_events` field (integer, default: 1024) - **CRITICAL PRIORITY** (AWS Strands uses events flattened to pseudo-attributes)
- Add `max_links` field (integer, default: 128) - LOW PRIORITY (future-proofing for distributed tracing)

**Design Rationale:**
- Use **total span size** (not per-attribute limit) because LLM ecosystem has extreme attribute size variability (1KB text vs 10MB images)
- OpenTelemetry doesn't provide `max_span_size` natively - requires custom implementation in span processor
- Support initialization via constructor parameters
- Support initialization via environment variables

**Acceptance Criteria:**
- [ ] TracerConfig accepts all four parameters
- [ ] Values are validated (positive integers)
- [ ] Default values applied if not specified
- [ ] Environment variables override defaults

**Test Cases:**
1. Initialize with defaults → verify 1024, 10MB, 128, 128
2. Initialize with custom values → verify custom values applied
3. Initialize with env vars → verify env vars take precedence
4. Initialize with invalid values → raise ValueError

---

### FR-2: Increased Default Limits
**Priority:** CRITICAL  
**Status:** Phase 1 - Implemented  

**Description:**  
Increase default `max_attributes` from OpenTelemetry's 128 to 1024 (8x safety margin) and add default `max_span_size` of 10MB.

**Rationale:**
- 128 attributes is too low for LLM workloads (CEO bug: 400+ attributes)
- 1024 provides 8x safety margin for typical workloads
- 10MB `max_span_size` handles large total span payloads (multimodal data: images, audio, long conversations)

**Acceptance Criteria:**
- [ ] Default `max_attributes` = 1024
- [ ] Default `max_span_size` = 10MB
- [ ] No user configuration required for typical workloads
- [ ] CEO's SerpAPI script (400+ attributes) works without configuration

**Test Cases:**
1. Create tracer with defaults → verify 1024 attribute limit
2. Create span with 1000 attributes → all attributes preserved
3. Create span with 1025 attributes → oldest evicted (expected behavior)

---

### FR-3: Environment Variable Support
**Priority:** HIGH  
**Status:** Phase 1 - Implemented  

**Description:**  
Support environment variables for deployment-time configuration without code changes.

**Environment Variables:**
- `HH_MAX_ATTRIBUTES` → maps to max_attributes
- `HH_MAX_SPAN_SIZE` → maps to max_span_size  
- `HH_MAX_EVENTS` → maps to max_events
- `HH_MAX_LINKS` → maps to max_links

**Acceptance Criteria:**
- [ ] All four environment variables recognized
- [ ] Environment variables override defaults
- [ ] Constructor parameters override environment variables
- [ ] Invalid env var values raise ValueError with clear message

**Test Cases:**
1. Set `HH_MAX_ATTRIBUTES=2000` → verify 2000 limit applied
2. Set env var + constructor param → constructor param wins
3. Set `HH_MAX_ATTRIBUTES=invalid` → ValueError raised

---

### FR-4: Apply Limits During TracerProvider Creation
**Priority:** CRITICAL  
**Status:** Phase 1 - Implemented  

**Description:**  
Apply configured limits when creating the OpenTelemetry TracerProvider via atomic provider detection.

**Implementation Details:**
- Retrieve limits from `tracer_instance.config`
- Create `SpanLimits` object from config values
- Pass `span_limits` to `atomic_provider_detection_and_setup()`
- Provider creation uses configured limits

**Acceptance Criteria:**
- [ ] Limits applied before any spans created
- [ ] Atomic provider detection respects custom limits
- [ ] Verification: check `provider._span_limits` reflects config

**Test Cases:**
1. Initialize tracer → verify TracerProvider has correct SpanLimits
2. Create multiple tracers → each has independent limits
3. Verify via `trace.get_tracer_provider()._span_limits`

---

### FR-5: Configuration Validation
**Priority:** HIGH  
**Status:** Phase 1 - Implemented  

**Description:**  
Validate configuration values to prevent invalid settings that could cause runtime errors.

**Validation Rules:**
- All limit values must be positive integers (> 0)
- `max_attributes` reasonable range: 128-10000
- `max_span_size` reasonable range: 1MB-100MB
- Invalid values raise `ValueError` with helpful message

**Acceptance Criteria:**
- [ ] Negative values rejected
- [ ] Zero values rejected
- [ ] Non-integer values rejected
- [ ] Error messages explain valid ranges

**Test Cases:**
1. `max_attributes=-1` → ValueError
2. `max_attributes=0` → ValueError
3. `max_attributes="invalid"` → ValueError
4. `max_span_size=0` → ValueError

---

### FR-6: Core Attribute Preservation (Future)
**Priority:** HIGH  
**Status:** Phase 2 - Proposed  

**Description:**  
Implement mechanism to protect critical attributes from eviction even when limits are exceeded.

**Core Attributes to Preserve:**
- `honeyhive.session_id` (Priority 1)
- `honeyhive.project_id` (Priority 1)
- `honeyhive.event_type` (Priority 2)
- `honeyhive.event_name` (Priority 2)
- `honeyhive.source` (Priority 2)
- `honeyhive.duration` (Priority 2)

**Rationale:**  
These attributes are required by the backend ingestion service. Missing attributes cause span rejection or orphaned spans.

**Acceptance Criteria:**
- [ ] Core attributes never evicted regardless of span size
- [ ] Backend validation always passes for core attributes
- [ ] Zero span rejection due to missing core attributes

**Note:** Implementation details TBD in Phase 2 technical design.

---

### FR-7: Smart Truncation (Future)
**Priority:** MEDIUM  
**Status:** Phase 3 - Proposed  

**Description:**  
Intelligently summarize large attributes instead of evicting them entirely.

**Acceptance Criteria:**
- [ ] Large attributes (>100KB) are truncated with summary
- [ ] Truncation preserves semantic meaning
- [ ] Truncation marker indicates data was summarized

**Note:** Implementation details TBD in Phase 3 technical design.

---

## 5. Non-Functional Requirements

### NFR-1: Usability - Zero Configuration
**Priority:** HIGH  
**Target:** 95% of users require no configuration  

**Description:**  
Default settings must handle typical LLM/agent workloads without user intervention.

**Measurable Criteria:**
- 1024 attributes handles 95% of API responses
- 10MB handles typical multimodal data (images, audio)
- No documentation reading required for basic usage

**Test Strategy:**
- Survey typical customer workloads (message counts, response sizes)
- Validate defaults handle 95th percentile workloads

---

### NFR-2: Usability - Simple Configuration
**Priority:** HIGH  
**Target:** 2 configuration parameters maximum  

**Description:**  
Power users need only understand 2 knobs: count limit + size limit.

**Measurable Criteria:**
- Documentation explains purpose in <100 words
- Configuration examples fit on one screen
- No complex decision trees or tuning guides

---

### NFR-3: Backward Compatibility
**Priority:** CRITICAL  
**Target:** Zero breaking changes  

**Description:**  
All existing code must work without modification.

**Measurable Criteria:**
- All existing unit tests pass
- All existing integration tests pass
- Existing tracer initialization code unchanged

**Test Strategy:**
- Run full test suite against new implementation
- Manual testing of common initialization patterns

---

### NFR-4: Performance
**Priority:** MEDIUM  
**Target:** <1% overhead for limit checking  

**Description:**  
Attribute limit checking must have negligible performance impact.

**Measurable Criteria:**
- Per-span overhead <1ms
- Memory overhead <1KB per span
- No impact on throughput (<1% regression)

**Test Strategy:**
- Benchmark span creation with 100, 500, 1000 attributes
- Compare before/after performance

---

### NFR-5: Memory Safety
**Priority:** HIGH  
**Target:** Prevent unbounded growth  

**Description:**  
Limits must prevent unbounded memory growth from large attributes.

**Measurable Criteria:**
- Single span max memory = `max_span_size` (total size limit)
- Default: 10MB per span (enforced by `max_span_size`)
- `max_attributes` (1024) provides count protection against many small attributes
- Dual guardrail ensures memory is bounded regardless of attribute size distribution
- Typical span memory: <1MB for most LLM traces

**Note:** Customer is responsible for managing total memory across all concurrent spans (see C-8: Responsibility Boundary)

---

### NFR-6: Maintainability
**Priority:** MEDIUM  
**Target:** Configuration centralized in one location  

**Description:**  
All limit configuration lives in `TracerConfig` with clear documentation.

**Measurable Criteria:**
- Single source of truth for defaults
- No scattered configuration across codebase
- Pydantic validation enforces constraints

---

## 6. Constraints

### C-1: OpenTelemetry Architecture
**Type:** Technical Constraint  

**Description:**  
OpenTelemetry `SpanLimits` apply globally to the `TracerProvider`, not per-span or per-operation.

**Implications:**
- Cannot have different limits for different operations
- All spans under one provider share the same limits
- Multi-tracer setups can have different limits per tracer

---

### C-2: FIFO Eviction Policy
**Type:** Technical Constraint  

**Description:**  
OpenTelemetry evicts oldest attributes first (FIFO). This behavior cannot be changed without forking OpenTelemetry.

**Implications:**
- Attributes set early (like `session_id`) are evicted first
- Cannot prioritize core attributes via OpenTelemetry API
- Phase 2 (core attribute preservation) requires custom solution

---

### C-3: Backend Validation Requirements
**Type:** Integration Constraint  

**Description:**  
HoneyHive ingestion service (hive-kube) validates 16+ required attributes per span. Missing attributes cause rejection or orphaned spans.

**Required Attributes:**
- session_id, event_id, event_type, event_name, source, duration, project_id, tenant, start_time, end_time, inputs, outputs, metadata, user_properties, metrics, feedback

**Implications:**
- These attributes must NEVER be evicted
- Phase 2 must guarantee their presence

---

### C-4: Unpredictable Data Sizes
**Type:** Domain Constraint  

**Description:**  
LLM/agent workloads have unpredictable attribute counts and sizes:
- GPT-4 responses: 500-5000 tokens (2KB-20KB)
- Tool responses: SerpAPI 50KB, database 1KB
- Multimodal: Images 2MB, audio 500KB, video 5MB

**Implications:**
- Cannot predict optimal limits in advance
- Must provide safety margins and configurability
- Dual guardrail (count + size) addresses both extremes

---

### C-5: ReadableSpan Immutability
**Type:** Technical Constraint  
**Source:** Pessimistic Review C-2

**Description:**  
OpenTelemetry's `ReadableSpan` is immutable in `on_end()`. Span attributes cannot be modified or truncated after the span ends.

**Implications:**
- Cannot truncate oversized spans in `HoneyHiveSpanProcessor.on_end()`
- Must DROP oversized spans (cannot smart-truncate in span processor)
- Smart truncation requires exporter-level implementation (Phase B - optional)
- Phase A: Detection and drop only
- Phase B: Optional exporter wrapper for truncation

**Mitigation:**
- Phase A: `_check_span_size()` drops oversized spans with comprehensive error logging
- Phase B: Optional `TruncatingOTLPExporter` wrapper for smart truncation (future enhancement)

---

### C-6: Backend Capacity Limits
**Type:** Infrastructure Constraint  
**Source:** Pessimistic Review C-1 (Backend Capacity)

**Description:**  
HoneyHive ingestion service has HTTP and buffer limits that constrain maximum span sizes:
- Express.js HTTP limit: 1000MB (1GB) per request
- Buffer manager chunks: 5MB per chunk

**Verified Headroom:**
- Default `max_span_size` (10MB) provides **100x headroom** vs. HTTP limit
- Maximum reasonable `max_span_size` (100MB) provides **10x headroom**

**Implications:**
- Current limits are well within backend capacity
- No backend changes required for Phase 1
- Load testing recommended (separate effort, Week 4+)

**Source:**
- `hive-kube/kubernetes/ingestion_service/app/express_worker.js:43-44`
- `hive-kube/kubernetes/ingestion_service/app/utils/buffer_worker.js:13`

---

### C-7: Pre-Release Validation Context
**Type:** Project Constraint  
**Source:** Pessimistic Review H-1

**Description:**  
This work is pre-release validation and fixes for v1.0.0, not a migration from an existing release.

**Implications:**
- No backwards compatibility concerns (establishing base behavior)
- No rollback/downgrade strategy needed
- All tests must be updated for new defaults
- No hardcoded limits allowed in codebase (all must come from config)

---

### C-8: Customer vs. SDK Responsibility Boundary
**Type:** Operational Constraint  
**Source:** Pessimistic Review C-4, H-3

**Description:**  
Clear division of responsibility between HoneyHive SDK and customers regarding resource management and code quality.

**HoneyHive SDK Responsibility:**
- Provide sensible defaults (1024 attrs, 10MB spans)
- Optimize tracer implementation
- Document resource implications
- Provide configuration flexibility
- Prevent common footguns

**Customer Responsibility:**
- Write bug-free code (no infinite loops, runaway attributes)
- Configure for their specific workload
- Monitor resource usage
- Manage concurrent span counts
- Test configurations in staging
- Manage infrastructure capacity

**Implications:**
- SDK will NOT implement circuit breakers for customer bugs (e.g., infinite attribute loops)
- SDK will NOT prevent memory explosion from poor customer code
- SDK WILL provide clear documentation and reasonable defaults
- SDK WILL provide observability (logging, metrics) for debugging

**Philosophy:**
Same as other observability tools (Datadog, New Relic): provide tools and defaults, customer manages usage.

---

### C-9: Configuration Precedence
**Type:** Technical Constraint  
**Source:** Pessimistic Review H-4

**Description:**  
TracerConfig field resolution follows a strict precedence order.

**Precedence Order (Highest to Lowest):**
1. Explicit constructor parameters (e.g., `HoneyHiveTracer.init(max_attributes=5000)`)
2. Resolved config object (from file or environment)
3. Environment variables (e.g., `HH_MAX_ATTRIBUTES`)
4. Final default values (e.g., 1024)

**Implications:**
- Follows industry standard: Code > Environment > Config > Defaults
- Pydantic `AliasChoices` handles this naturally
- Explicit always wins (allows per-instance overrides)
- Environment variables allow deployment-time tuning

**Rationale:**
Aligns with standard configuration patterns (e.g., Click, Django, Kubernetes)

---

## 7. Out of Scope

The following items are explicitly **NOT** included in this specification:

### OS-1: Per-Span Custom Limits
**Rationale:** OpenTelemetry architecture doesn't support this. Would require significant architectural changes.

### OS-2: Attribute Compression
**Rationale:** Adds complexity without addressing root cause. Focus on appropriate limits first.

### OS-3: Attribute Deduplication
**Rationale:** Edge case with minimal benefit. Adds complexity to span processing.

### OS-4: Alternative Serialization Formats
**Rationale:** Would break OpenTelemetry compatibility. Not worth the trade-off.

### OS-5: Streaming Large Attributes Separately
**Rationale:** Architectural change requiring backend modifications. Future consideration.

### OS-6: Dynamic Limit Adjustment
**Rationale:** Adds complexity. Static limits with configuration are sufficient.

### OS-7: Attribute Priority Levels (User-Configurable)
**Rationale:** Too complex for users. Phase 2 protects core attributes automatically.

---

## 8. Success Metrics

### Primary Metrics

**M-1: Span Drop Rate Due to Attribute Eviction**
- **Baseline:** Unknown (bug recently discovered)
- **Target:** 0%
- **Measurement:** Monitor `HoneyHiveSpanProcessor.on_end()` skip count

**M-2: User Configuration Rate**
- **Target:** <5% of users need to configure limits
- **Measurement:** Track env var usage in production deployments

**M-3: Backward Compatibility**
- **Target:** 100% of existing tests pass
- **Measurement:** CI/CD test suite results

### Secondary Metrics

**M-4: Performance Overhead**
- **Target:** <1% span creation time increase
- **Measurement:** Benchmark span creation with 1000 attributes

**M-5: Memory Usage**
- **Target:** <10MB per typical span
- **Measurement:** Monitor span memory usage in production

**M-6: Support Tickets**
- **Target:** Zero tickets related to missing trace data
- **Measurement:** Support ticket categorization

---

## 9. References

### Supporting Documentation
- [Design Document](supporting-docs/2025-11-18-span-attribute-limit-configuration.md) - Comprehensive technical design
- [Supporting Docs Index](supporting-docs/INDEX.md) - Extracted insights and analysis

### Related Issues
- CEO Bug Report: SerpAPI spans silently dropped (session_id evicted)
- Backend Validation: hive-kube ingestion service requirements

### Standards
- OpenTelemetry SpanLimits: https://opentelemetry.io/docs/specs/otel/trace/sdk/#span-limits
- HoneyHive Backend Schema: `hive-kube/kubernetes/ingestion_service/app/schemas/event_schema.js`

---

**Document Status:** Ready for Phase 2 (Technical Design)  
**Last Updated:** 2025-11-18  
**Next Review:** After Phase 2 completion

