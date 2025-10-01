# HoneyHive Architecture Standards

**Last Updated**: 2025-09-30  
**Maintainer**: Platform Team  

---

## 📚 Architecture Documentation Index

This directory contains the authoritative architectural documentation for HoneyHive's platform, with a focus on the **DSL-based semantic convention translation layer** - our unique competitive advantage.

---

## 🚀 Getting Started

### ➡️ [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) 📋 **START HERE FOR OPENAI FIX**
**Size**: 5 min read  
**Purpose**: Executive summary of OpenAI DSL implementation

**Quick Overview**:
- The problem: 30% coverage, missing tool_calls/refusal/audio
- The fix: 6-phase plan, 2-3 days effort
- Critical notes: JSON strings, array reconstruction
- Next steps: Detailed implementation plan

**Read This First If**: You need to fix OpenAI DSL translation

---

## 🎯 Core Documents

### 1. [Quick Reference](./ARCHITECTURE_QUICK_REFERENCE.md) ⚡ **GENERAL START**
**Size**: ~5 min read  
**Purpose**: Quick overview and navigation guide

**Covers**:
- The big picture (data flow)
- Key concepts (DSL, two paths, target schema)
- Critical requirements (JSON strings, array reconstruction)
- Common tasks and debugging

**When to Use**: Need a quick refresher or starting point

---

### 2. [DSL Semantic Convention Architecture](./DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md) 📐
**Size**: ~20 min read  
**Purpose**: Complete technical architecture reference

**Covers**:
- The problem: Backend processing mess (1,120 lines analyzed)
- The solution: DSL-based translation architecture
- Two data flow paths (pre-processed + fallback)
- Multi-language support (Python, TypeScript, Go)
- Platform-wide DSL usage (SDK + Backend)
- Future centralized repo structure
- Implementation roadmap
- Testing strategy

**When to Use**: 
- Designing new DSL features
- Understanding the complete architecture
- Planning multi-language implementation
- Explaining the system to new team members

---

### 3. [HoneyHive Event Schema Reference](./HONEYHIVE_EVENT_SCHEMA_REFERENCE.md) 📋
**Size**: ~15 min read  
**Purpose**: Define what the DSL must produce

**Covers**:
- Complete HoneyHive event schema
- Model events (chat, completion, embeddings, rerank)
- Chain events (workflow steps)
- Tool events (function execution)
- Session events (root events)
- Critical data types (chat_history, tool_calls, etc.)
- JSON string vs object requirements
- Array reconstruction rules
- DSL translation requirements

**When to Use**:
- Building DSL mappings
- Understanding target schema
- Debugging translation issues
- Validating event structure

---

### 4. [Current vs Legacy Implementation](./CURRENT_VS_LEGACY_IMPLEMENTATION.md) ⚠️ **IMPORTANT**
**Size**: ~10 min read  
**Purpose**: Clarify what code is active vs legacy

**Covers**:
- Current system: Universal v4.0 with precompiled DSL ✅ (ACTIVE)
- Legacy system: Hardcoded transforms ❌ (INACTIVE)
- Why legacy files still exist
- Current execution path
- What might cause data loss (if any)
- How to audit DSL configs

**When to Use**:
- Understanding which code is actually running
- Debugging why certain code isn't being executed
- Planning cleanup of legacy files
- Investigating data loss issues

---

### 5. [OpenAI DSL Implementation Plan](./OPENAI_DSL_IMPLEMENTATION_PLAN.md) 🛠️ **ACTION PLAN**
**Size**: ~20 min read  
**Purpose**: Detailed roadmap to fix OpenAI DSL translation

**Covers**:
- Current DSL config analysis (what exists vs what's missing)
- Critical gaps: tool_calls, refusal, audio, array reconstruction
- 6-phase implementation plan with code examples
- Transform registry additions needed
- Bundle recompilation steps
- Integration testing strategy
- Success criteria and verification steps

**When to Use**:
- Implementing OpenAI DSL fixes
- Understanding what's broken and how to fix it
- Creating similar plans for other providers
- Debugging translation issues

---

## 🔗 Related Documentation

### Internal References

**Provider Schemas**:
- `../../../provider_response_schemas/` - Provider API response schemas
- OpenAI, Anthropic, Gemini, Bedrock schema definitions

**DSL Configurations**:
- `../../../config/dsl/` - Current DSL configs (Python SDK)
- Provider-specific mappings and transforms

**Schema Implementation**:
- `../../../src/honeyhive/tracer/semantic_conventions/schema.py` - Pydantic schema
- `../../../src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py` - Transform functions

**Backend Code**:
- `../../../../hive-kube/kubernetes/ingestion_service/app/services/otel_processing_service.js` - Current backend processing (the 1,120-line mess to be replaced)

### External References

**Competitive Analysis**:
- `../../research/competitive-analysis/ANALYSIS_COMPLETE.md` - Full analysis summary
- `../../research/competitive-analysis/deliverables/ARCHITECTURAL_ADVANTAGE.md` - Strategic positioning

**Universal LLM Discovery Engine**:
- `../../../universal_llm_discovery_engine_v4_final/` - V4.0 design docs (historical context)

---

## 🏗️ Architecture Evolution

### The Problem (Before DSL)

**Backend**: 1,120 lines of hardcoded conditional logic
```javascript
// otel_processing_service.js
for (let key in parsedAttributes) {
  if (key === 'gen_ai.system') { eventConfig['provider'] = value; }
  else if (key === 'gen_ai.request.model') { eventConfig['model'] = value; }
  else if (key === 'gen_ai.prompt') { ... }
  // ... 100+ more else-if blocks
}
```

**Problems**:
- ❌ Every new instrumentor = backend code change + deployment
- ❌ Divergence between SDK and backend logic
- ❌ Difficult to test (1,120 lines of conditionals)
- ❌ No reuse across languages (JavaScript only)

### The Solution (DSL Architecture)

**SDK + Backend**: Declarative YAML configs applied everywhere
```yaml
# config/dsl/conventions/gen_ai/field_mappings.yaml
mappings:
  gen_ai.request.model:
    target: "honeyhive_config.model"
  gen_ai.completion.0.message.content:
    target: "honeyhive_outputs.content"
```

**Backend** (after DSL integration): ~100 lines
```javascript
if (hasHoneyhiveAttributes(span)) {
  event = unwrapHoneyhiveAttributes(span);  // Primary path
} else {
  event = applyDSL(span.attributes, convention);  // Fallback path
}
```

**Benefits**:
- ✅ New instrumentor = DSL config update (no backend deployment)
- ✅ Perfect parity (SDK and backend use same DSL)
- ✅ Easy to test (DSL configs + transform functions)
- ✅ Reuse across Python, JS, Go, etc.

---

## 🎯 Key Innovations

### 1. Platform-Wide DSL
**What**: Same YAML configs used in Python SDK, TypeScript SDK, Go SDK, AND backend
**Why**: Perfect consistency, single source of truth
**Impact**: No divergence between SDK and backend processing

### 2. Two-Path Architecture
**What**: Pre-processed path (SDK) + Fallback path (backend)
**Why**: Works with or without HoneyHive SDK
**Impact**: True neutrality, gradual migration support

### 3. Centralized DSL Repository (Planned)
**What**: Standalone `honeyhiveai/semantic-conventions-dsl` repo
**Why**: Version independently, update once → all consumers benefit
**Impact**: First-mover advantage in declarative semantic convention management

### 4. 100% Data Fidelity Goal
**What**: DSL can represent all provider response fields
**Why**: Neutrality means accepting ANY data from ANY source
**Impact**: Zero data loss across all trace sources

---

## 📊 Current Status

### ✅ Completed

| Component | Status | Location |
|-----------|--------|----------|
| **Python SDK DSL** | ✅ Complete | `config/dsl/` |
| **Transform Registry** | ✅ Complete | `transform_registry.py` |
| **10 Providers** | ✅ Complete | OpenAI, Anthropic, Gemini, etc. |
| **Architecture Docs** | ✅ Complete | This directory |
| **Schema Definition** | ✅ Complete | `schema.py` |

### 🔄 In Progress

| Component | Status | Timeline |
|-----------|--------|----------|
| **Backend DSL Integration** | 🔄 In Progress | Q4 2025 |
| **Provider Schema Coverage** | 🔄 2/8 OpenAI ops | 6-8 weeks |
| **Centralized DSL Repo** | 📅 Planned | 4-6 weeks |

### 📅 Planned

| Component | Status | Timeline |
|-----------|--------|----------|
| **TypeScript SDK** | 📅 Planned | Q1 2026 |
| **Go SDK** | 📅 Planned | Q1 2026 |
| **Full Provider Coverage** | 📅 Planned | Q1 2026 |

---

## 🚀 Quick Start

### For New Team Members

1. **Read**: [Architecture Quick Reference](./ARCHITECTURE_QUICK_REFERENCE.md) (5 min)
2. **Understand**: [DSL Architecture](./DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md) (20 min)
3. **Reference**: [Event Schema](./HONEYHIVE_EVENT_SCHEMA_REFERENCE.md) (bookmark)

### For Developers

1. **Review**: Current DSL configs in `config/dsl/providers/`
2. **Study**: Transform registry in `transform_registry.py`
3. **Reference**: This architecture documentation

### For Product/PM

1. **Read**: [Architectural Advantage](../../research/competitive-analysis/deliverables/ARCHITECTURAL_ADVANTAGE.md)
2. **Review**: [Competitive Analysis](../../research/competitive-analysis/ANALYSIS_COMPLETE.md)
3. **Understand**: Why this is our unique value proposition

---

## 📋 Maintenance

### When to Update These Docs

- ✏️ DSL structure or semantics change
- ✏️ New language SDK added
- ✏️ Event schema changes
- ✏️ Backend processing logic changes
- ✏️ New providers or conventions added
- ✏️ Centralized repo created

### Document Owners

| Document | Owner | Review Cadence |
|----------|-------|----------------|
| DSL Architecture | Platform Team | Quarterly |
| Event Schema | Product Team | As needed |
| Quick Reference | SDK Team | Monthly |
| Competitive Analysis | Strategy Team | Quarterly |

---

## 🏆 Success Metrics

### Architecture Goals

- ✅ **Backend Simplification**: 1,120 → ~100 lines
- ✅ **Multi-Language Consistency**: Same DSL across Python, JS, Go
- ✅ **Zero Data Loss**: 100% provider field coverage
- ✅ **True Neutrality**: Accept ANY instrumentor
- ✅ **Rapid Iteration**: Config changes, not code changes

### Current Achievement

- ✅ Python SDK DSL architecture complete
- ✅ 10 providers configured
- ✅ Transform registry with 18+ functions
- 🔄 Backend integration in progress
- 📅 Centralized repo planned

---

## 🔍 Additional Resources

### Learning Path

**Beginner**:
1. [Quick Reference](./ARCHITECTURE_QUICK_REFERENCE.md)
2. [Event Schema](./HONEYHIVE_EVENT_SCHEMA_REFERENCE.md) - Focus on examples

**Intermediate**:
1. [DSL Architecture](./DSL_SEMANTIC_CONVENTION_ARCHITECTURE.md) - Full architecture
2. [Provider Schemas](../../../provider_response_schemas/) - Real provider data

**Advanced**:
1. [Competitive Analysis](../../research/competitive-analysis/) - Deep dive
2. [Universal LLM Discovery Engine](../../../universal_llm_discovery_engine_v4_final/) - Historical context

### External References

- OpenTelemetry Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/
- OpenInference Conventions: https://github.com/Arize-ai/openinference
- Traceloop Conventions: https://github.com/traceloop/openllmetry

---

## 📞 Contact

### Questions or Issues?

- **Architecture**: Platform Team
- **DSL Design**: SDK Team  
- **Backend Integration**: Backend Team
- **Schema**: Product Team
- **Competitive**: Strategy Team

---

**Remember**: This DSL-based architecture is HoneyHive's unique competitive advantage. It enables:

1. 🎯 **True Neutrality** - Accept ANY instrumentor
2. ⚡ **Backend Simplification** - Move complexity to SDK
3. 🌍 **Multi-Language Consistency** - Same logic everywhere
4. 🔄 **Rapid Iteration** - Config changes only
5. 🏆 **First-Mover Advantage** - No competitor has this

---

**Last Updated**: 2025-09-30  
**Next Review**: When centralized DSL repo is created

