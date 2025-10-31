# Universal Instrumentor: Quick Reference

**Companion to**: [UNIVERSAL_INSTRUMENTOR_DESIGN.md](./UNIVERSAL_INSTRUMENTOR_DESIGN.md)

---

## TL;DR

Replace 50+ instrumentor packages with a single schema-driven universal instrumentor that:
- Ships as JSON bundle with SDK (lazy-loaded, 2ms startup, 3MB memory)
- AI maintains schemas (updates in hours, not weeks)
- Works across Python/TypeScript/Go (same schemas)
- Preserves BYOI compatibility (user choice, not lock-in)

---

## Architecture Diagram

```
USER CODE
    │
    ▼ Method call
┌───────────────────────────────────────┐
│  INSTRUMENTATION DSL (Frontend)        │
│  • Lazy-load library config            │
│  • Extract attributes (before/after)   │
│  • Create OTLP span                    │
└───────────┬───────────────────────────┘
            │ OTLP span
            ▼
┌───────────────────────────────────────┐
│  TRANSLATION DSL (Backend - Existing)  │
│  • Detect provider (O(1) signature)    │
│  • Lazy-load translation config        │
│  • Transform to canonical event        │
└───────────┬───────────────────────────┘
            │ Canonical event
            ▼
    HONEYHIVE BACKEND
```

---

## Usage Examples

### Default: Universal Instrumentor (Recommended)

```python
from honeyhive import HoneyHiveTracer
import openai

# That's it! Auto-instruments everything.
tracer = HoneyHiveTracer.init(project="my-project")

client = openai.OpenAI()
response = client.chat.completions.create(...)
# ↑ Automatically traced with zero config
```

### BYOI: Bring Your Own Instrumentor

```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

# Disable auto-instrumentation
tracer = HoneyHiveTracer.init(
    project="my-project",
    auto_instrument=False
)

# Use community instrumentor
OpenAIInstrumentor().instrument()
```

### Hybrid: Mix & Match

```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

# Universal instrumentor for most libraries, BYOI for openai
tracer = HoneyHiveTracer.init(
    project="my-project",
    exclude_libraries=["openai"]
)

# Custom instrumentor for openai
OpenAIInstrumentor().instrument()
```

---

## Schema Example (Minimal)

```yaml
# schemas/instrumentation/openai.yaml

library:
  name: "openai"
  import_path: "openai"

targets:
  - target_id: "chat_completions_create"
    location:
      module: "openai.resources.chat.completions"
      class: "Completions"
      method: "create"
    
    span_config:
      name: "openai.chat.completions.create"
      kind: "CLIENT"
    
    extract_before:
      - attribute: "gen_ai.system"
        value: "openai"
      - attribute: "gen_ai.request.model"
        path: "kwargs.model"
        type: "string"
    
    extract_after:
      - attribute: "gen_ai.response.message.content"
        path: "result.choices[0].message.content"
        type: "string"
```

---

## Performance at a Glance

| Metric | Traditional (50 packages) | Universal Instrumentor |
|--------|--------------------------|------------------------|
| **Startup** | 50-100ms | 2ms (50x faster) |
| **Memory** | 45MB | 3MB (15x less) |
| **Install steps** | 10+ commands | 1 command |
| **Config LOC** | 20-50 lines | 0 lines |
| **Time to add provider** | 2-4 weeks | 2 hours (40x faster) |

---

## File Structure

```
honeyhive-sdk/
├── src/honeyhive/
│   ├── instrumentation/           # NEW
│   │   ├── engine.py              # Runtime interpreter
│   │   ├── interceptor.py         # Monkey patching
│   │   └── extractor.py           # Attribute extraction
│   │
│   ├── translation/               # EXISTING
│   │   └── engine.py              # Translation DSL
│   │
│   └── tracer.py                  # Main entry point
│
├── bundles/
│   ├── instrumentation-bundle.json    # NEW
│   └── translation-bundle.json        # EXISTING
│
└── schemas/instrumentation/       # NEW (source)
    ├── openai.yaml
    ├── anthropic.yaml
    └── langchain.yaml
```

---

## Key Design Principles

1. **Runtime Interpretation**: No code generation, JSON bundles interpreted at runtime
2. **Lazy Loading**: Load configs only when needed (fast startup, low memory)
3. **AI-Maintained**: Schemas updated by AI in hours, not weeks
4. **BYOI Compatible**: Users can opt-out and bring own instrumentor
5. **Multi-Language**: Same bundles work in Python, TypeScript, Go

---

## Lazy Loading Flow

```
Startup (1-2ms):
  └─ Load bundle index: {openai: metadata, anthropic: metadata, ...}

Auto-discover (5ms):
  ├─ openai installed? YES → Load openai config (0.5ms)
  ├─ anthropic installed? NO → Skip
  └─ langchain installed? YES → Load langchain config (0.5ms)

First span (0.5ms):
  └─ Lazy-load translation config for openai.gen_ai

Subsequent spans (0.05ms):
  └─ Use cached configs (no loading)

Result: 8ms total startup, 3MB memory for 2 libraries
```

---

## Schema Patterns Cheat Sheet

### Static Value
```yaml
- attribute: "gen_ai.system"
  value: "openai"
```

### Extract from Path
```yaml
- attribute: "gen_ai.request.model"
  path: "kwargs.model"
  type: "string"
```

### Nested Path
```yaml
- attribute: "gen_ai.response.message.content"
  path: "result.choices[0].message.content"
```

### Array Flattening
```yaml
- attribute: "gen_ai.request.messages"
  path: "kwargs.messages"
  type: "array"
  flatten_to:
    - attribute: "gen_ai.request.messages.{index}.role"
      path: "role"
    - attribute: "gen_ai.request.messages.{index}.content"
      path: "content"
```

### Conditional Extraction
```yaml
- attribute: "gen_ai.request.stream"
  path: "kwargs.stream"
  condition:
    path: "kwargs.stream"
    exists: true
```

### Truncation
```yaml
- attribute: "gen_ai.request.prompt"
  path: "kwargs.prompt"
  max_length: 10000
  truncate_indicator: "...[truncated]"
```

### Default Value
```yaml
- attribute: "gen_ai.request.temperature"
  path: "kwargs.temperature"
  type: "float"
  default: 1.0
```

---

## Implementation Phases

| Phase | Duration | Goal |
|-------|----------|------|
| **Phase 1: MVP** | 4 weeks | OpenAI + Anthropic, prove concept |
| **Phase 2: Expansion** | 6 weeks | 10+ providers, AI workflow |
| **Phase 3: TypeScript** | 8 weeks | Multi-language validation |
| **Phase 4: Go** | 8 weeks | Complete multi-language |
| **Phase 5: Advanced** | Ongoing | Streaming, hot-reload, A/B testing |

---

## FAQ

### Q: Why not just use community instrumentors?
A: We do! BYOI is fully supported. But universal instrumentor offers:
- Zero config (auto-discovers & instruments)
- Faster updates (AI maintains schemas in hours)
- Multi-language (same schemas work everywhere)
- Better UX (1 package vs 50+)

### Q: What if I prefer community instrumentors?
A: Use BYOI mode! Disable auto-instrumentation and use any OTLP-compatible instrumentor. Translation DSL still works.

### Q: Will this slow down my app?
A: No! Lazy loading means:
- 2ms startup (vs 50-100ms traditional)
- 3MB memory (vs 45MB traditional)
- 0.08ms per-call overhead (same as traditional)

### Q: How do you maintain 50+ providers?
A: AI (Agent OS Enhanced) maintains all schemas. AI can:
- Write schemas from API docs (2 hours vs 2 weeks)
- Update schemas when APIs change (auto-detect + update)
- Generate multi-language implementations (from single spec)

### Q: What if a provider API changes?
A: AI monitors provider APIs, detects changes, and updates schemas within hours. CI/CD validates and deploys automatically.

### Q: Can I add custom instrumentation?
A: Yes! Three options:
1. Contribute schema (PR to our repo)
2. Use BYOI for custom libraries
3. Use hybrid mode (universal + custom)

---

## Next Steps

1. **Read full design**: [UNIVERSAL_INSTRUMENTOR_DESIGN.md](./UNIVERSAL_INSTRUMENTOR_DESIGN.md)
2. **Review MVP scope**: Phase 1 (OpenAI + Anthropic)
3. **Provide feedback**: Technical review, user testing
4. **Plan migration**: BYOI → Universal (gradual, hybrid mode)

---

**Questions?** Open an issue or reach out to the team.

