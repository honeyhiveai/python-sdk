# SDK Analysis Methodology
## A Systematic Approach to Understanding Unknown SDKs for Instrumentation Support

**Date:** October 15, 2025  
**Purpose:** Create reusable methodology for analyzing any unknown SDK to determine instrumentation strategy

---

## Overview

When faced with an unknown SDK (or one without existing instrumentor support), we need a **systematic, comprehensive methodology** to understand:
1. How the SDK works internally
2. What LLM/API clients it uses
3. What observability it has built-in
4. Where we can hook instrumentation
5. How to integrate with HoneyHive's BYOI architecture

**Anti-Pattern:** Reading file snippets (head/tail), guessing, making assumptions  
**Correct Pattern:** Systematic discovery, complete file analysis, evidence-based conclusions

---

## Phase 1: Initial Discovery (15-30 minutes)

### 1.1 Repository Metadata Analysis

**Objective:** Understand the SDK's scope and dependencies

**Steps:**
1. Clone repository
2. Read complete `README.md` (not just head)
3. Read complete `pyproject.toml` or `setup.py` or `package.json`
4. Check for documentation links

**Commands:**
```bash
# Clone
git clone <repo-url>
cd <repo-name>

# Full README
cat README.md

# Full dependencies
cat pyproject.toml
# or
cat setup.py
# or (Node)
cat package.json

# Documentation structure
ls -la docs/
```

**Document:**
- [ ] SDK version
- [ ] Core dependencies (especially LLM client libraries)
- [ ] Optional dependencies
- [ ] Python/Node version requirements
- [ ] Key features listed

### 1.2 File Structure Mapping

**Objective:** Understand the codebase organization

**Commands:**
```bash
# Count files
find src -name "*.py" | wc -l
find src -name "*.ts" | wc -l

# List all directories
find src -type d | sort > structure_dirs.txt

# List all files
find src -type f -name "*.py" | sort > structure_files_py.txt
find src -type f -name "*.ts" | sort > structure_files_ts.txt

# Size analysis
find src -name "*.py" -exec wc -l {} + | sort -n | tail -20
```

**Document:**
- [ ] Total file count
- [ ] Total LOC
- [ ] Directory structure (modules)
- [ ] Largest files (likely core logic)
- [ ] Test file count

### 1.3 Entry Point Discovery

**Objective:** Find how users interact with the SDK

**Steps:**
1. Check `__init__.py` or main module exports
2. Read examples directory
3. Find `Runner`, `Client`, `Agent`, or similar main classes

**Commands:**
```bash
# Main exports
cat src/<package>/__init__.py

# Examples
ls -la examples/
cat examples/basic/* | head -100

# Find main classes
grep -r "class.*Runner" src/
grep -r "class.*Client" src/
grep -r "class.*Agent" src/
```

**Document:**
- [ ] Main user-facing classes
- [ ] Typical usage pattern from examples
- [ ] Configuration options

---

## Phase 1.5: Existing Instrumentor Discovery (15-30 minutes)

**⚠️ CRITICAL PHASE - DO NOT SKIP ⚠️**

**Objective:** Check if instrumentors already exist BEFORE designing custom solutions

**Why This Matters:** External instrumentors can save weeks of development effort. Even if the SDK doesn't use OpenTelemetry internally, third-party vendors (OpenInference, Traceloop, etc.) may have built instrumentors that hook into the SDK via callbacks or monkey-patching.

**Failure Mode:** LangChain analysis initially missed existing instrumentors, overestimating effort by 3 weeks. This phase prevents that mistake.

### 1.5.1 Check HoneyHive-Supported Instrumentor Providers

**HoneyHive's BYOI architecture supports three major instrumentor providers:**

| Provider | GitHub Location | Package Naming | Status |
|----------|----------------|----------------|---------|
| **OpenInference (Arize)** | [python/instrumentation](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation) | `openinference-instrumentation-<sdk>` | 657+ ⭐ |
| **Traceloop (OpenLLMetry)** | [packages](https://github.com/traceloop/openllmetry/tree/main/packages) | `opentelemetry-instrumentation-<sdk>` | 6.5k+ ⭐ |
| **OpenLIT** | [sdk/python/src/openlit/instrumentation](https://github.com/openlit/openlit/tree/main/sdk/python/src/openlit/instrumentation) | `openlit` (single package) | 2k+ ⭐ |

**Quick Links:**
- **OpenInference:** https://github.com/Arize-ai/openinference/tree/main/python/instrumentation
- **Traceloop:** https://github.com/traceloop/openllmetry/tree/main/packages
- **OpenLIT:** https://github.com/openlit/openlit/tree/main/sdk/python/src/openlit/instrumentation

**Commands to check each provider:**
```bash
# 1. Check OpenInference (Arize)
# Browse: https://github.com/Arize-ai/openinference/tree/main/python/instrumentation
# Look for: openinference-instrumentation-<sdk-name>
curl -s "https://api.github.com/repos/Arize-ai/openinference/git/trees/main?recursive=1" | \
  grep "path.*instrumentation.*<sdk-name>"

# Example output if found: "path": "python/instrumentation/openinference-instrumentation-langchain"

# 2. Check Traceloop (OpenLLMetry)
# Browse: https://github.com/traceloop/openllmetry/tree/main/packages
# Look for: opentelemetry-instrumentation-<sdk-name>
curl -s "https://api.github.com/repos/traceloop/openllmetry/git/trees/main?recursive=1" | \
  grep "path.*instrumentation.*<sdk-name>"

# Example output if found: "path": "packages/opentelemetry-instrumentation-langchain"

# 3. Check OpenLIT
# Browse: https://github.com/openlit/openlit/tree/main/sdk/python/src/openlit/instrumentation
# Look for: <sdk-name> subdirectory
curl -s "https://api.github.com/repos/openlit/openlit/git/trees/main?recursive=1" | \
  grep "path.*instrumentation.*<sdk-name>"

# Example output if found: "path": "sdk/python/src/openlit/instrumentation/langchain"
```

**Manual browsing (recommended for accuracy):**
```bash
# Clone repositories for local inspection
cd /tmp

# OpenInference
git clone --depth 1 https://github.com/Arize-ai/openinference.git
ls openinference/python/instrumentation/ | grep <sdk-name>

# Traceloop
git clone --depth 1 https://github.com/traceloop/openllmetry.git
ls openllmetry/packages/ | grep <sdk-name>

# OpenLIT
git clone --depth 1 https://github.com/openlit/openlit.git
ls openlit/sdk/python/src/openlit/instrumentation/ | grep <sdk-name>
```

**Package naming conventions:**
- **OpenInference:** `openinference-instrumentation-<sdk-name>`
- **Traceloop:** `opentelemetry-instrumentation-<sdk-name>`
- **OpenLIT:** `openlit` (single package with multiple instrumentors)

### 1.5.2 Search PyPI

**Commands:**
```bash
# Search for instrumentation packages (all three providers)
pip search openinference-instrumentation-<sdk-name> 2>/dev/null || echo "Check PyPI manually"
pip search opentelemetry-instrumentation-<sdk-name> 2>/dev/null || echo "Check PyPI manually"
pip search openlit 2>/dev/null || echo "Check PyPI manually"

# Or search PyPI website:
# OpenInference: https://pypi.org/search/?q=openinference-instrumentation-<sdk-name>
# Traceloop: https://pypi.org/search/?q=opentelemetry-instrumentation-<sdk-name>
# OpenLIT: https://pypi.org/project/openlit/ (check docs for supported frameworks)
```

**Direct PyPI package checks:**
```bash
# Check if packages exist
pip index versions openinference-instrumentation-<sdk-name> 2>/dev/null
pip index versions opentelemetry-instrumentation-<sdk-name> 2>/dev/null
pip index versions openlit 2>/dev/null
```

### 1.5.3 Web Search

**Search queries to try (all three providers):**
```
"openinference-instrumentation-<sdk-name>"
"opentelemetry-instrumentation-<sdk-name>"
"openlit <sdk-name> instrumentation"
"<sdk-name> instrumentor opentelemetry"
"<sdk-name> instrumentation traceloop"
"<sdk-name> instrumentation arize"
"<sdk-name> instrumentation openlit"
"<sdk-name>Instrumentor" (exact class name)
"honeyhive byoi <sdk-name>" (check if already documented)
```

**Provider-specific documentation:**
- **OpenInference:** https://docs.arize.com/phoenix
- **Traceloop:** https://www.traceloop.com/docs/openllmetry/getting-started
- **OpenLIT:** https://docs.openlit.io/

### 1.5.4 Check SDK Documentation

**Look for:**
- Observability integrations page
- OpenTelemetry integration docs
- Third-party integrations section
- Monitoring/tracing documentation

**Commands:**
```bash
# Search SDK docs for instrumentor references
grep -ri "instrumentor\|opentelemetry\|traceloop\|openinference" docs/ README.md
```

### 1.5.5 Community Search

**Check:**
- SDK's GitHub Discussions
- SDK's Issue tracker (search "opentelemetry", "instrumentation", "tracing")
- Community forums/Discord/Slack
- Stack Overflow

**Example searches:**
```
site:github.com <sdk-name> opentelemetry instrumentation
site:stackoverflow.com <sdk-name> opentelemetry
```

### Decision Point: Instrumentor Found?

**✅ IF INSTRUMENTOR EXISTS:**
1. Clone the instrumentor repository
2. **CONTINUE WITH MODIFIED ANALYSIS APPROACH:**
   - Phase 2: Understand SDK architecture (how instrumentor hooks in)
   - Phase 3: Analyze instrumentor implementation (what it captures)
   - Phase 4: Identify gaps (what instrumentor misses)
   - Phase 5: Test BYOI compatibility + document gaps
   - Phase 6: Create integration guide with all options

**Why continue analyzing even with instrumentors?**
- Need to understand WHAT the instrumentor captures vs SDK capabilities
- Need to identify gaps (e.g., missing agent context, custom metadata)
- Need to test compatibility with HoneyHive BYOI architecture
- Need to document trade-offs between providers (OpenInference vs Traceloop vs OpenLIT)
- May need custom enrichment on top of base instrumentor
- Need complete picture for informed recommendations

**❌ IF NO INSTRUMENTOR EXISTS:**
1. Document the search (what was checked)
2. Continue to Phase 2 (LLM Client Discovery)
3. Plan custom integration approach

**Document:**
- [ ] Checked OpenInference GitHub: YES / NO
- [ ] Checked Traceloop GitHub: YES / NO
- [ ] Checked OpenLIT GitHub: YES / NO
- [ ] Searched PyPI: YES / NO
- [ ] Searched web: YES / NO (queries used)
- [ ] Checked SDK docs: YES / NO
- [ ] **Result:** Instrumentor(s) found: YES / NO
- [ ] If found: Package names, versions, repository URLs (all providers found)
- [ ] If found: Instrumentation method (monkey-patching, callbacks, etc.)
- [ ] If found: What they capture (attributes, events, metrics)
- [ ] If found: What they DON'T capture (gaps to document)
- [ ] If found: Initial compatibility assessment with BYOI architecture

### Example: LangChain Discovery

**What should have been found (all three HoneyHive-supported providers):**

```bash
# 1. OpenInference (Arize)
Package: openinference-instrumentation-langchain
GitHub: https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-langchain
PyPI: https://pypi.org/project/openinference-instrumentation-langchain/
Status: Production/Stable (Development Status :: 5)
Dependencies: opentelemetry-api, openinference-semantic-conventions
Usage:
  from openinference.instrumentation.langchain import LangChainInstrumentor
  LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

# 2. Traceloop (OpenLLMetry)
Package: opentelemetry-instrumentation-langchain
GitHub: https://github.com/traceloop/openllmetry/tree/main/packages/opentelemetry-instrumentation-langchain
PyPI: https://pypi.org/project/opentelemetry-instrumentation-langchain/
Version: 0.47.3+
Dependencies: opentelemetry-api, opentelemetry-semantic-conventions-ai
Usage:
  from opentelemetry.instrumentation.langchain import LangchainInstrumentor
  LangchainInstrumentor().instrument()

# 3. OpenLIT
Package: openlit
GitHub: https://github.com/openlit/openlit/tree/main/sdk/python/src/openlit/instrumentation/langchain
PyPI: https://pypi.org/project/openlit/
Version: Check latest
Dependencies: opentelemetry-api (bundled in openlit package)
Usage:
  import openlit
  openlit.init()  # Auto-detects and instruments LangChain
```

**How to verify compatibility with HoneyHive BYOI:**
```python
# Test with HoneyHive tracer
from honeyhive import HoneyHiveTracer

# OpenInference
from openinference.instrumentation.langchain import LangChainInstrumentor
tracer = HoneyHiveTracer.init(project="test")
LangChainInstrumentor().instrument(tracer_provider=tracer.provider)

# Traceloop
from opentelemetry.instrumentation.langchain import LangchainInstrumentor
tracer = HoneyHiveTracer.init(project="test")
LangchainInstrumentor().instrument()  # Uses global provider

# OpenLIT
import openlit
openlit.init(otlp_endpoint="http://honeyhive.endpoint")
```

**Why it was missed:** Phase 1.5 didn't exist in v1.1, so instrumentor check was skipped.

**Impact:** Analysis overestimated effort by 3 weeks (assumed custom development needed).

**What should happen after finding instrumentors:**
1. ✅ Clone all three instrumentor repos
2. ✅ Continue to Phase 2: Understand LangChain architecture (chains, agents, tools, callbacks)
3. ✅ Continue to Phase 3: Analyze each instrumentor's implementation
   - What callbacks do they use?
   - What span attributes do they set?
   - What do they capture from chain/agent metadata?
4. ✅ Continue to Phase 4: Identify gaps
   - Do they capture custom chain metadata?
   - Do they capture agent handoffs?
   - Do they support all LangChain modules (LCEL, LangGraph, etc.)?
5. ✅ Continue to Phase 5: Test with HoneyHive BYOI
   - Test integration with each provider
   - Document which provider works best
   - Identify if custom enrichment needed
6. ✅ Phase 6: Create comprehensive integration guide

---

## Phase 2: LLM Client Discovery (30-60 minutes)

**Note:** Even if instrumentors exist (Phase 1.5), continue this phase to understand:
- How the SDK works (so you understand what instrumentors can/can't capture)
- SDK architecture (to identify potential gaps in instrumentation)
- Where custom enrichment might be needed

**If instrumentors exist:** Focus on understanding how they hook into the SDK and what they might miss.

**If no instrumentors:** This is critical for designing custom integration.

### 2.1 Dependency Analysis

**Objective:** Identify which LLM clients are used (or if this SDK IS the LLM client)

**Commands:**
```bash
# Check dependencies
grep -i "openai\|anthropic\|google\|bedrock\|azure" pyproject.toml
grep -i "openai\|anthropic\|google\|bedrock\|azure" setup.py

# Import analysis
grep -r "^import openai" src/
grep -r "^from openai" src/
grep -r "^import anthropic" src/
grep -r "^from anthropic" src/
```

**Document:**
- [ ] Which LLM client libraries are dependencies
- [ ] Which are required vs optional
- [ ] Version constraints

### 2.2 Client Instantiation Points

**Objective:** Find WHERE the SDK creates LLM clients

**Commands:**
```bash
# OpenAI client creation
grep -rn "OpenAI(" src/
grep -rn "AsyncOpenAI(" src/
grep -rn "AzureOpenAI(" src/

# Anthropic client creation  
grep -rn "Anthropic(" src/
grep -rn "AsyncAnthropic(" src/

# Generic client patterns
grep -rn "client = " src/ | grep -i "openai\|anthropic"
```

**Document:**
- [ ] All files that instantiate LLM clients
- [ ] Whether clients are passed in or created internally
- [ ] Client configuration points

### 2.3 API Call Points

**Objective:** Find WHERE the SDK actually calls LLM APIs

**Commands:**
```bash
# OpenAI API calls
grep -rn "chat.completions.create" src/
grep -rn "completions.create" src/
grep -rn "embeddings.create" src/

# Anthropic API calls
grep -rn "messages.create" src/

# Count occurrences
grep -r "chat.completions.create" src/ | wc -l
```

**Document:**
- [ ] All files that make API calls
- [ ] API call patterns (sync vs async)
- [ ] Which APIs are used (chat, embeddings, etc.)

---

## Phase 3: Observability System Analysis (1-2 hours)

**Note:** This phase is critical whether or not instrumentors exist:

**If instrumentors exist:** 
- Analyze instrumentor implementation files (how they wrap SDK calls)
- Understand what attributes/events they capture
- Check semantic conventions they use
- Identify what SDK features they DON'T instrument

**If no instrumentors:**
- Check if SDK has built-in tracing (can we leverage it?)
- Understand observability hooks available

### 3.1 Built-in Tracing Detection

**Objective:** Determine if SDK has observability built-in (and if instrumentors leverage it)

**Commands:**
```bash
# OpenTelemetry detection
grep -r "opentelemetry" src/
grep -r "from opentelemetry" src/
grep -r "import opentelemetry" src/

# Custom tracing
grep -r "tracing" src/ | head -20
find src -path "*tracing*" -name "*.py"
ls -la src/*/tracing/

# Span/trace patterns
grep -r "class.*Span" src/
grep -r "class.*Trace" src/
grep -r "create_span\|start_span" src/
```

**Decision Tree:**
- **If OpenTelemetry found:** Existing instrumentors MAY work
- **If custom tracing found:** Need to analyze custom system
- **If no tracing found:** Need to instrument from scratch

**Document:**
- [ ] Uses OpenTelemetry: YES / NO
- [ ] Has custom tracing: YES / NO
- [ ] Tracing module location
- [ ] Span/Trace data structures

### 3.2 OpenTelemetry Usage Deep Dive

**Objective:** If OpenTelemetry is found, understand HOW they use it

**CRITICAL:** This analysis determines if standard OTel integration will work.

#### 3.2.1 TracerProvider Integration Pattern

**Objective:** Determine if SDK respects global TracerProvider

**Commands:**
```bash
# MOST IMPORTANT: Check if they respect global provider
grep -rn "get_tracer_provider()" src/
grep -rn "trace_api.get_tracer_provider()" src/
grep -rn "set_tracer_provider" src/

# Check if they create their own provider
grep -rn "TracerProvider()" src/
grep -rn "trace.TracerProvider" src/
```

**Critical Decision:**
- ✅ **If uses `get_tracer_provider()`:** Standard integration works! We can provide our own TracerProvider
- ❌ **If creates own `TracerProvider()`:** Need custom integration or wrapper

**Document:**
- [ ] Uses `get_tracer_provider()`: YES / NO (file:line)
- [ ] Creates own TracerProvider: YES / NO (file:line)
- [ ] Sets global provider: YES / NO (file:line)
- [ ] Allows custom provider injection: YES / NO (how?)

#### 3.2.2 Span Attributes Analysis

**Objective:** Understand what metadata they capture via span attributes

**Commands:**
```bash
# Count span.set_attribute usage
grep -rn "span.set_attribute\|set_attribute" src/ | wc -l

# Find all attribute names (look for quoted strings)
grep -o '"[a-z_][a-z0-9_.]*"' src/telemetry/*.py | sort -u > span_attributes.txt
grep -o '"gen_ai\.[^"]*"' src/ | sort -u
grep -o '"llm\.[^"]*"' src/ | sort -u

# Check semantic conventions
grep -rn "gen_ai\.\|llm\.\|db\.\|http\." src/
```

**Semantic Convention Patterns to Look For:**
- `gen_ai.*` - GenAI semantic conventions (https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- `llm.*` - LLM-specific attributes
- `db.*` - Database operations
- `http.*` - HTTP calls
- Custom attributes

**Document:**
- [ ] Total span.set_attribute calls: [count]
- [ ] Uses GenAI conventions: YES / NO
- [ ] GenAI attributes found: [list unique ones]
- [ ] Uses custom attributes: [list patterns]
- [ ] Captures token usage: YES / NO
- [ ] Captures model name: YES / NO
- [ ] Captures latency metrics: YES / NO

#### 3.2.3 Span Events Analysis

**Objective:** Understand if they use span.add_event() for LLM interactions

**Commands:**
```bash
# Count span.add_event usage
grep -rn "span.add_event\|add_event" src/ | wc -l

# Find event names
grep -B2 -A5 "\.add_event(" src/telemetry/*.py | head -50

# Check for message content in events
grep -rn "gen_ai\..*\.message\|llm\..*\.message" src/
```

**Event Pattern Analysis:**
```bash
# Common GenAI event patterns
grep -rn "gen_ai.user.message" src/
grep -rn "gen_ai.choice" src/
grep -rn "gen_ai.tool.message" src/
grep -rn "gen_ai.client.inference" src/
```

**Document:**
- [ ] Total span.add_event calls: [count]
- [ ] Uses events for messages: YES / NO
- [ ] Event types found: [list unique event names]
- [ ] Captures full message content: YES / NO
- [ ] Captures tool calls via events: YES / NO
- [ ] Event naming convention: [describe pattern]

#### 3.2.4 Span Hierarchy and SpanKind

**Objective:** Understand span structure and SpanKind usage

**Commands:**
```bash
# Find SpanKind usage
grep -rn "SpanKind\." src/
grep -rn "span_kind=" src/

# Find span creation with hierarchy
grep -A10 "start_span\|create_span" src/telemetry/*.py | head -50

# Check for parent span handling
grep -rn "parent.*span\|parent_context" src/
```

**SpanKind Values:**
- `INTERNAL` - Internal operations
- `CLIENT` - Client calls (e.g., LLM API calls)
- `SERVER` - Server operations
- `PRODUCER` - Async message production
- `CONSUMER` - Async message consumption

**Document:**
- [ ] Uses SpanKind: YES / NO
- [ ] SpanKind patterns: CLIENT for [what], INTERNAL for [what]
- [ ] Creates span hierarchy: YES / NO
- [ ] Parent span propagation: [how it works]
- [ ] Root span name: [what it's called]

#### 3.2.5 Semantic Convention Versioning

**Objective:** Check if SDK supports multiple semantic convention versions

**Commands:**
```bash
# Check for convention version handling
grep -rn "OTEL_SEMCONV\|semconv\|semantic.*convention" src/
grep -rn "stability.*opt.*in\|opt.*in" src/

# Check for old vs new convention support
grep -rn "gen_ai.system\|gen_ai.provider.name" src/
```

**Document:**
- [ ] Supports convention versioning: YES / NO
- [ ] Environment variable used: [name]
- [ ] Old convention attributes: [which ones]
- [ ] New convention attributes: [which ones]
- [ ] Default convention: [old/new]

#### 3.2.6 Resource Attributes

**Objective:** Understand service identification via resource attributes

**Commands:**
```bash
# Find Resource configuration
grep -rn "Resource.create\|Resource(" src/
grep -rn "service.name\|service.version" src/

# Check resource attributes
grep -A10 "Resource.create\|Resource(" src/telemetry/*.py
```

**Document:**
- [ ] Sets resource attributes: YES / NO
- [ ] Service name: [what value]
- [ ] Service version: [static/dynamic]
- [ ] Custom resource attributes: [list them]

#### 3.2.7 Propagators Configuration

**Objective:** Check context propagation setup

**Commands:**
```bash
# Find propagator configuration
grep -rn "propagate\|Propagator" src/
grep -rn "W3C\|TraceContext\|Baggage" src/

# Check global propagator setup
grep -rn "set_global_textmap" src/
```

**Document:**
- [ ] Configures propagators: YES / NO
- [ ] W3C TraceContext: YES / NO
- [ ] W3C Baggage: YES / NO
- [ ] Custom propagators: [list them]

#### 3.2.8 Exporter Configuration

**Objective:** Understand how traces are exported

**Commands:**
```bash
# Find exporters
grep -rn "Exporter\|OTLP\|Console.*Export" src/
grep -rn "BatchSpanProcessor\|SimpleSpanProcessor" src/

# Check environment variables
grep -rn "OTEL_EXPORTER\|OTLP_ENDPOINT" src/
```

**Document:**
- [ ] Supported exporters: [Console, OTLP, Custom, etc.]
- [ ] Uses BatchSpanProcessor: YES / NO
- [ ] Environment variables: [list them]
- [ ] Export endpoint configuration: [how it's set]

### 3.3 Custom Tracing Deep Dive

**Objective:** If custom (non-OTel) tracing exists, understand it completely

**Steps:**
1. Read ALL files in tracing module (not just head)
2. Identify trace/span data model
3. Find how spans are created/closed
4. Understand span processors/exporters

**Commands:**
```bash
# List all tracing files
find src -path "*tracing*" -name "*.py"

# Read each file COMPLETELY
for file in $(find src -path "*tracing*" -name "*.py"); do
    echo "=== $file ==="
    cat "$file"
    echo ""
done > tracing_full_code.txt

# Find span creation patterns
grep -rn "def.*span\|class.*Span" src/*/tracing/
```

**Files to read COMPLETELY:**
- [ ] `tracing/__init__.py` - Exports and API
- [ ] `tracing/spans.py` - Span implementation
- [ ] `tracing/traces.py` - Trace implementation  
- [ ] `tracing/processor*.py` - Span processors
- [ ] `tracing/provider*.py` - Trace providers
- [ ] `tracing/create.py` - Span creation APIs

**Document:**
- [ ] Span data model (what fields?)
- [ ] How to create custom spans
- [ ] Processor interface (can we inject?)
- [ ] Export mechanism (where does data go?)

### 3.4 Instrumentor Implementation Analysis (IF INSTRUMENTORS EXIST)

**Objective:** Understand how existing instrumentors work and what they capture

**For each instrumentor found (OpenInference, Traceloop, OpenLIT):**

**Steps:**
1. Read complete instrumentor implementation files
2. Identify instrumentation technique (monkey-patching, callbacks, etc.)
3. Document what methods they wrap
4. Analyze what attributes they set
5. Check what events they emit
6. Identify gaps (what they DON'T capture)

**Commands:**
```bash
# OpenInference
cd /tmp/sdk-analysis/openinference/python/instrumentation/openinference-instrumentation-<sdk>/src
find . -name "*.py" -exec wc -l {} + | sort -n
cat openinference/instrumentation/<sdk>/__init__.py
cat openinference/instrumentation/<sdk>/_wrappers.py

# Traceloop
cd /tmp/sdk-analysis/openllmetry/packages/opentelemetry-instrumentation-<sdk>
cat opentelemetry/instrumentation/<sdk>/__init__.py

# OpenLIT
cd /tmp/sdk-analysis/openlit/sdk/python/src/openlit/instrumentation/<sdk>
cat __init__.py
cat <sdk>.py
cat async_<sdk>.py
```

**Document for EACH instrumentor:**
- [ ] Instrumentation method: monkey-patching / callbacks / other
- [ ] Methods wrapped: [list all wrapped methods]
- [ ] Span attributes set: [list key attributes]
- [ ] Span events emitted: [list event types]
- [ ] Supports streaming: YES / NO
- [ ] Supports async: YES / NO
- [ ] Semantic conventions: GenAI / Custom / Mixed
- [ ] What's captured: [prompts, completions, tokens, model, etc.]
- [ ] What's NOT captured: [custom metadata, agent context, etc.]
- [ ] Dependencies: [opentelemetry versions, etc.]

**Comparison Matrix:**
Create a table comparing all three instrumentors:

| Feature | OpenInference | Traceloop | OpenLIT |
|---------|---------------|-----------|---------|
| Instrumentation method | | | |
| Methods wrapped | | | |
| Attributes captured | | | |
| Events support | | | |
| Streaming support | | | |
| Semantic conventions | | | |
| Ease of use | | | |
| Maintenance status | | | |

### 3.5 Integration Points Discovery

**Objective:** Find where we can hook into the system (for custom enrichment if needed)

**Questions to answer:**
1. Can we inject a custom span processor?
2. Can we wrap the LLM client?
3. Are there lifecycle hooks?
4. Can we monkey-patch critical functions?

**Commands:**
```bash
# Processor registration
grep -rn "register.*processor\|add.*processor" src/
grep -rn "set.*processors" src/

# Hook points
grep -rn "hook\|callback" src/

# Configuration extension
grep -rn "config\|Config" src/ | grep "class"
```

**Document:**
- [ ] Can inject custom processor: YES / NO
- [ ] Processor registration API
- [ ] Available lifecycle hooks
- [ ] Configuration extension points

---

## Phase 4: Architecture Deep Dive (2-3 hours)

### 4.1 Core Flow Analysis

**Objective:** Understand the complete execution flow

**Steps:**
1. Find the main entry point (e.g., `Runner.run()`)
2. Read the COMPLETE implementation file
3. Trace the execution path
4. Document all LLM calls in the path

**Commands:**
```bash
# Find main runner/executor
grep -rn "class Runner" src/
grep -rn "def run\|async def run" src/ | grep -v "test"

# Read complete main file
cat src/agents/run.py
cat src/agents/_run_impl.py

# Find all called functions
grep -n "def \|async def " src/agents/run.py
```

**Document:**
- [ ] Entry point: function/class
- [ ] Execution flow diagram
- [ ] Where LLM calls happen in flow
- [ ] Where agent-specific logic happens

### 4.2 Agent/Handoff Analysis

**Objective:** Understand agent-specific concepts

**Files to read COMPLETELY:**
- [ ] `agent.py` - Agent class
- [ ] `handoffs.py` - Handoff mechanism
- [ ] `guardrail.py` - Guardrail system
- [ ] `tool.py` - Tool system

**Commands:**
```bash
cat src/agents/agent.py
cat src/agents/handoffs.py
cat src/agents/guardrail.py
cat src/agents/tool.py
```

**Document:**
- [ ] How agents are defined
- [ ] How handoffs work
- [ ] How guardrails are implemented
- [ ] Tool calling mechanism

### 4.3 Model Provider Abstraction

**Objective:** Understand multi-provider support

**Commands:**
```bash
# Find model abstraction
ls -la src/agents/models/
find src/agents/models -name "*.py"

# Read all model files
for file in src/agents/models/*.py; do
    echo "=== $file ==="
    cat "$file"
done
```

**Document:**
- [ ] Is there a model interface/ABC?
- [ ] Which providers are supported?
- [ ] How is provider selected?
- [ ] Does each provider have its own file?

---

## Phase 5: Instrumentation Strategy & Testing (2-3 hours)

### 5.1 Decision Matrix

Based on findings, choose approach(es) to test and document:

| Finding | Approach | Effort | Pros | Cons |
|---------|----------|--------|------|------|
| **Uses OpenAI client + no custom tracing** | Use existing OpenAI instrumentors | Low | Works immediately | Missing agent-specific context |
| **Uses OpenAI client + custom tracing** | Inject custom processor | Medium | Captures agent metadata | Requires understanding custom system |
| **Custom LLM calls + custom tracing** | Build custom instrumentor | High | Full control | High maintenance |
| **OpenTelemetry based** | Standard OTel integration | Low-Medium | Standard approach | May need configuration |

### 5.2 Integration Pattern Design

**Option A: Passthrough (Existing Instrumentors)**
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

# Existing instrumentor will catch LLM calls
tracer = HoneyHiveTracer.init(project="agents-demo")
openai_instrumentor = OpenAIInstrumentor()
openai_instrumentor.instrument(tracer_provider=tracer.provider)

# Use SDK normally
from agents import Agent, Runner
result = Runner.run_sync(agent, "task")
# LLM calls are traced, but agent context missing
```

**Option B: Custom Processor Injection**
```python
from honeyhive import HoneyHiveTracer
from agents.tracing import add_trace_processor, TracingProcessor

class HoneyHiveAgentsProcessor(TracingProcessor):
    def __init__(self, tracer):
        self.tracer = tracer
    
    def on_span_start(self, span):
        # Convert agents span to HoneyHive span
        pass
    
    def on_span_end(self, span):
        # Send to HoneyHive
        pass

tracer = HoneyHiveTracer.init(project="agents-demo")
add_trace_processor(HoneyHiveAgentsProcessor(tracer))

# Use SDK normally - agent context captured!
result = Runner.run_sync(agent, "task")
```

**Option C: Manual Enrichment**
```python
from honeyhive import HoneyHiveTracer
from agents import Agent, Runner

tracer = HoneyHiveTracer.init(project="agents-demo")

agent = Agent(name="ResearchAgent", instructions="...")

# Manual context enrichment
with tracer.enrich_span(metadata={"agent.name": agent.name}):
    result = Runner.run_sync(agent, "task")
```

### 5.3 Testing Instrumentors with HoneyHive BYOI (IF INSTRUMENTORS EXIST)

**Objective:** Test compatibility of all found instrumentors with HoneyHive architecture

**For each instrumentor, create test script:**

**Test Script Template:**
```python
# test_<instrumentor>_<sdk>_integration.py
"""Test <instrumentor> integration with HoneyHive BYOI."""

import os
from honeyhive import HoneyHiveTracer

# Test specific instrumentor
def test_<instrumentor>_integration():
    # Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        project="<sdk>-test",
        api_key=os.getenv("HH_API_KEY"),
        source="<instrumentor>-test"
    )
    
    # Instrument with provider
    # [Provider-specific instrumentation code]
    
    # Make SDK calls
    # [SDK usage code]
    
    # Verify spans in HoneyHive dashboard
    print("✓ Test completed - check HoneyHive dashboard")
    print(f"Project: <sdk>-test")
    print(f"Source: <instrumentor>-test")

if __name__ == "__main__":
    test_<instrumentor>_integration()
```

**Test all three providers:**

**OpenInference Test:**
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.<sdk> import <SDK>Instrumentor

tracer = HoneyHiveTracer.init(project="<sdk>-openinference")
instrumentor = <SDK>Instrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)

# Test SDK calls
# Verify what appears in HoneyHive
```

**Traceloop Test:**
```python
from honeyhive import HoneyHiveTracer
from opentelemetry.instrumentation.<sdk> import <SDK>Instrumentor

tracer = HoneyHiveTracer.init(project="<sdk>-traceloop")
<SDK>Instrumentor().instrument()  # Uses global provider

# Test SDK calls
# Verify what appears in HoneyHive
```

**OpenLIT Test:**
```python
from honeyhive import HoneyHiveTracer
from openlit.instrumentation.<sdk> import <SDK>Instrumentor

tracer = HoneyHiveTracer.init(project="<sdk>-openlit")
<SDK>Instrumentor().instrument(
    tracer=tracer,
    capture_message_content=True
)

# Test SDK calls
# Verify what appears in HoneyHive
```

**Document test results:**
- [ ] OpenInference compatibility: WORKS / ISSUES / FAILS
- [ ] OpenInference issues found: [list any issues]
- [ ] Traceloop compatibility: WORKS / ISSUES / FAILS
- [ ] Traceloop issues found: [list any issues]
- [ ] OpenLIT compatibility: WORKS / ISSUES / FAILS
- [ ] OpenLIT issues found: [list any issues]
- [ ] Recommended provider: [based on testing]
- [ ] Recommendation rationale: [why this provider?]

### 5.4 Proof of Concept (IF NO INSTRUMENTORS OR CUSTOM ENRICHMENT NEEDED)

**Create test script:**
```python
# test_agents_integration.py
"""Test integration approach for OpenAI Agents SDK with HoneyHive."""

import os
from honeyhive import HoneyHiveTracer
from agents import Agent, Runner

# Test Option A: Existing instrumentor
def test_existing_instrumentor():
    from openinference.instrumentation.openai import OpenAIInstrumentor
    
    tracer = HoneyHiveTracer.init(
        project="agents-test",
        api_key=os.getenv("HH_API_KEY")
    )
    
    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer.provider)
    
    agent = Agent(name="TestAgent", instructions="You are helpful")
    result = Runner.run_sync(agent, "Say hello")
    
    print("✓ Test completed")
    print(f"Result: {result.final_output}")
    
    # Check HoneyHive dashboard for traces

if __name__ == "__main__":
    test_existing_instrumentor()
```

---

## Phase 6: Documentation & Delivery (1-2 hours)

### 6.1 Create Analysis Report

Document findings in structured format:

**SDK Analysis Report Template:**
```markdown
# [SDK Name] Analysis Report

**Date:** [YYYY-MM-DD]  
**Analyst:** [Name]  
**Analysis Version:** [Based on SDK_ANALYSIS_METHODOLOGY.md v1.3]

## Executive Summary
- **SDK Purpose:** [what it does]
- **SDK Version Analyzed:** [version]
- **LLM Client:** [which client(s) OR "This SDK IS the LLM client"]
- **Observability:** [OTel / Custom / None]
- **Existing Instrumentors:** [✅ YES - 3 found / ⚠️ YES - partial / ❌ NO]
- **HoneyHive BYOI Compatible:** [✅ YES / ⚠️ WITH MODIFICATIONS / ❌ NO]
- **Recommended Approach:** [instrumentor name OR custom]

## Phase 1.5: Instrumentor Discovery Results

### Instrumentors Found

| Provider | Package | Version | Status | PyPI |
|----------|---------|---------|--------|------|
| **OpenInference** | openinference-instrumentation-[sdk] | [version] | [✅/⚠️/❌] | [link] |
| **Traceloop** | opentelemetry-instrumentation-[sdk] | [version] | [✅/⚠️/❌] | [link] |
| **OpenLIT** | openlit | [version] | [✅/⚠️/❌] | [link] |

### Instrumentor Comparison

| Feature | OpenInference | Traceloop | OpenLIT |
|---------|---------------|-----------|---------|
| **Instrumentation Method** | [monkey-patch/callbacks] | | |
| **Methods Wrapped** | [list] | | |
| **Span Attributes** | [count/list key ones] | | |
| **Span Events** | [YES/NO + types] | | |
| **Streaming Support** | [✅/❌] | | |
| **Async Support** | [✅/❌] | | |
| **Semantic Conventions** | [GenAI/Custom] | | |
| **Message Content** | [Captured/Optional/Not captured] | | |
| **Token Usage** | [✅/❌] | | |
| **HoneyHive BYOI Test** | [✅ PASS/⚠️ ISSUES/❌ FAIL] | | |
| **Ease of Use** | [1-5 rating] | | |
| **Maintenance** | [Active/Stale] | | |
| **Last Updated** | [date] | | |

### Gaps Identified

**What instrumentors DON'T capture:**
- [ ] Custom metadata
- [ ] Agent-specific context
- [ ] Tool/function call details
- [ ] Guardrail information
- [ ] Cost tracking beyond tokens
- [ ] [Other gaps...]

**SDK features not instrumented:**
- [ ] [Feature 1]
- [ ] [Feature 2]

## Architecture Overview
[Diagram or description of SDK architecture]

**Key Components:**
- Entry points: [list main classes/functions]
- Core execution flow: [describe]
- Extension points: [where custom logic can hook in]

## Key Findings

### SDK Architecture
- **SDK Type:** [Framework / Client Library / Both]
- **Primary API:** [messages.create / chat.completions / etc.]
- **Client Library:** [anthropic / openai / self / etc.]
- **Version Requirements:** [Python >=X.Y]
- **Key Dependencies:** [list important ones]

### LLM Client Usage (if SDK uses other clients)
- Client Library: [name] >= X.Y.Z
- Instantiation: [where/how]
- API Calls: [which APIs]
- Call Sites: [list all files]

### Observability System
- **Built-in Tracing:** [✅ YES / ❌ NO]
- **Type:** [OpenTelemetry / Custom / None]
- **Components:** [list modules if custom]
- **Span Model:** [describe if custom]
- **Export:** [where data goes if built-in]

### Integration Points
- **Existing Instrumentors:** ✅ YES ([providers])
- **Instrumentation Method:** [how they work]
- **Custom Enrichment Needed:** [YES/NO + what]
- **Processor Injection:** [✅/❌ + how]
- **Client Wrapping:** [✅/❌ + details]
- **Lifecycle Hooks:** [✅/⚠️/❌ + which ones]

## Integration Approach

### Recommended: [Instrumentor Name / Custom]

**Recommendation:** Use [OpenInference / Traceloop / OpenLIT / Custom] for HoneyHive integration

**Rationale:**
- [Why this approach over others]
- [Key advantages]
- [Trade-offs accepted]

**Implementation:**
```python
[Complete code example]
```

**What's Captured:**
- ✅ [Feature 1]
- ✅ [Feature 2]
- ⚠️ [Feature 3 - partial]

**What's NOT Captured (Gaps):**
- ❌ [Gap 1]
- ❌ [Gap 2]

**Custom Enrichment Needed:**
- [ ] [Enrichment 1]
- [ ] [Enrichment 2]

**Pros:**
- [benefit 1]
- [benefit 2]
- [benefit 3]

**Cons:**
- [limitation 1]
- [limitation 2]

### Alternative Approaches

#### Option 2: [Other instrumentor / Custom approach]
[Brief description, when to use, code snippet]

#### Option 3: [Another option if applicable]
[Brief description, when to use, code snippet]

## Testing Results

### HoneyHive BYOI Compatibility Tests

**OpenInference:**
- Status: [✅ PASS / ⚠️ ISSUES / ❌ FAIL]
- Issues: [list any issues encountered]
- Workarounds: [if needed]

**Traceloop:**
- Status: [✅ PASS / ⚠️ ISSUES / ❌ FAIL]
- Issues: [list any issues encountered]
- Workarounds: [if needed]

**OpenLIT:**
- Status: [✅ PASS / ⚠️ ISSUES / ❌ FAIL]
- Issues: [list any issues encountered]
- Workarounds: [if needed]

### Test Cases Executed

1. [✅/❌] Basic message creation
2. [✅/❌] Streaming responses
3. [✅/❌] Async operations
4. [✅/❌] Tool/function calling
5. [✅/❌] Error handling
6. [✅/❌] Token usage tracking
7. [✅/❌] Custom metadata

## Implementation Guide

**Quick Start:**
```bash
pip install honeyhive [instrumentor-package]
```

```python
[Minimal working example]
```

**Advanced Usage:**
```python
[Example with custom enrichment if needed]
```

**Configuration Options:**
- [Option 1]: [description]
- [Option 2]: [description]

**Troubleshooting:**
- **Issue:** [common issue 1]
  **Solution:** [how to fix]

## Next Steps

### Immediate Actions
1. [ ] Test recommended instrumentor with production workload
2. [ ] Validate custom enrichment (if needed)
3. [ ] Create integration documentation
4. [ ] Add to HoneyHive compatibility matrix

### Future Enhancements
1. [ ] Monitor instrumentor updates
2. [ ] Contribute gaps back to instrumentor project
3. [ ] Create custom enrichment utilities if patterns emerge

## Appendix

### Files Analyzed
- [List key files reviewed]

### Commands Used
- [List key discovery commands]

### References
- SDK Documentation: [link]
- OpenInference Repo: [link if used]
- Traceloop Repo: [link if used]
- OpenLIT Repo: [link if used]
- HoneyHive BYOI Docs: [link]
```

### 6.2 Create Integration Guide

**File:** `docs/how-to/integrations/[sdk-name].rst`

Include:
- Installation instructions
- Basic setup example
- Advanced usage
- Troubleshooting
- What's captured vs what's not

---

## Cleanup After Analysis

Once analysis is complete and deliverables are saved:

```bash
# Save final reports to project (if not already saved)
cp /tmp/sdk-analysis/reports/* ~/path/to/project/docs/

# Remove temporary analysis directory
rm -rf /tmp/sdk-analysis/

# Verify cleanup
ls /tmp/sdk-analysis/  # Should show "No such file or directory"
```

**Note:** Make sure all findings and reports are saved to your project before cleanup!

---

## Checklist: Comprehensive Analysis Complete

### Discovery Phase
- [ ] Read complete README
- [ ] Read complete pyproject.toml/setup.py
- [ ] Mapped ALL directories
- [ ] Listed ALL Python files
- [ ] Found ALL examples

### LLM Client Phase
- [ ] Identified which LLM client library
- [ ] Found ALL client instantiation points
- [ ] Found ALL API call sites
- [ ] Counted occurrences

### Instrumentor Discovery Phase (CRITICAL)
- [ ] Checked OpenInference GitHub
- [ ] Checked Traceloop GitHub
- [ ] Checked OpenLIT GitHub
- [ ] Searched PyPI for all three providers
- [ ] Cloned instrumentor repositories (if found)
- [ ] **Decision:** Found instrumentors: YES / NO

### Observability Phase
- [ ] Searched for OpenTelemetry in SDK
- [ ] If instrumentors exist: Analyzed each instrumentor implementation
- [ ] If instrumentors exist: Created comparison matrix
- [ ] If instrumentors exist: Documented what they capture
- [ ] If instrumentors exist: Identified gaps (what they DON'T capture)
- [ ] If OTel: Analyzed TracerProvider integration pattern
- [ ] If OTel: Analyzed span attributes and semantic conventions
- [ ] If OTel: Analyzed span events usage
- [ ] If OTel: Checked SpanKind and span hierarchy
- [ ] If OTel: Documented resource attributes and propagators
- [ ] If Custom: Found custom tracing system
- [ ] If Custom: Read ALL tracing module files (COMPLETE, not head)
- [ ] If Custom: Understood span/trace data model
- [ ] If Custom: Found processor interface

### Architecture Phase
- [ ] Read COMPLETE main execution file
- [ ] Read COMPLETE agent.py
- [ ] Read COMPLETE run.py or _run_impl.py
- [ ] Documented execution flow
- [ ] Understood agent concepts

### Integration Phase
- [ ] Decided on approach (instrumentor or custom)
- [ ] If instrumentors: Tested ALL three providers with HoneyHive BYOI
- [ ] If instrumentors: Documented compatibility for each
- [ ] If instrumentors: Identified recommended provider
- [ ] If instrumentors: Documented gaps and custom enrichment needs
- [ ] Created POC test scripts for chosen approach(es)
- [ ] Tested manually with real SDK calls
- [ ] Documented findings comprehensively

### Delivery Phase
- [ ] Created analysis report
- [ ] Created integration guide (if applicable)
- [ ] Updated compatibility matrix
- [ ] Submitted for review

---

## Anti-Patterns to Avoid

❌ **Reading file snippets (head/tail)**
- Problem: Miss critical details
- Solution: Read COMPLETE files for core modules

❌ **Guessing based on names**
- Problem: Wrong assumptions
- Solution: Verify with grep/actual code

❌ **Single-file analysis**
- Problem: Missing the bigger picture
- Solution: Trace execution across files

❌ **Assuming "it's like X"**
- Problem: Different SDKs have different patterns
- Solution: Evidence-based analysis

❌ **Skipping tests**
- Problem: Don't know if approach works
- Solution: Always create POC test

---

## Tools & Commands Reference

### Setup & Navigation
```bash
# Clone SDK to /tmp for analysis
cd /tmp
git clone <repo-url>
cd <repo-name>

# All analysis commands run from /tmp/<repo-name>
pwd  # Should show /tmp/<repo-name>
```

### Search & Discovery
```bash
# Find all occurrences (from /tmp/<repo-name>)
grep -rn "pattern" src/

# Count occurrences
grep -r "pattern" src/ | wc -l

# Find files by name
find src -name "*tracing*"

# List with details
ls -lah src/module/

# Read complete file
cat src/module/file.py

# Multiple files
for f in src/module/*.py; do cat "$f"; done
```

### Analysis
```bash
# Count LOC
wc -l src/**/*.py

# Largest files
find src -name "*.py" -exec wc -l {} + | sort -n | tail -20

# Function counts
grep -c "^def \|^async def " src/module/file.py

# Class hierarchy
grep "class.*(" src/**/*.py
```

### Documentation
```bash
# Export structure
find src -type f > structure.txt

# Export grep results
grep -rn "pattern" src/ > findings.txt

# Create report
cat analysis_template.md > SDK_ANALYSIS.md
```

---

**Version:** 1.3  
**Last Updated:** 2025-10-15  
**Applies To:** Any unknown SDK requiring instrumentation analysis

**Changelog:**
- **v1.3 (2025-10-15):** **CRITICAL CLARIFICATION** - Finding instrumentors does NOT mean stopping analysis
  - **Updated Phase 1.5 Decision Point:** Continue with all phases even when instrumentors exist
  - **Added rationale:** Need to understand gaps, test compatibility, document all options
  - **Updated Phase 2+:** Added notes that analysis continues regardless of instrumentor presence
  - **New Phase 3.4:** Instrumentor Implementation Analysis section
  - **New Phase 5.3:** Testing Instrumentors with HoneyHive BYOI section
  - **Enhanced Phase 6:** Comprehensive report template with instrumentor comparison matrix
  - **Key principle:** Complete analysis ensures informed recommendations and gap identification
- **v1.2 (2025-10-15):** **CRITICAL UPDATE** - Added Phase 1.5: Existing Instrumentor Discovery
  - New mandatory phase to check for existing instrumentors BEFORE custom development
  - Prevents overestimating effort (LangChain case: saved 3 weeks)
  - **Documents all three HoneyHive-supported providers:**
    - OpenInference (Arize) - 657+ ⭐
    - Traceloop (OpenLLMetry) - 6.5k+ ⭐
    - OpenLIT - 2k+ ⭐
  - Includes specific GitHub locations and package naming conventions
  - Provides commands to check each provider systematically
  - Includes decision tree for when instrumentor is found
  - Documents the LangChain miss as a cautionary example
- **v1.1 (2025-10-15):** Added comprehensive OpenTelemetry usage analysis (Phase 3.2) including:
  - TracerProvider integration pattern detection
  - Span attributes and semantic conventions analysis
  - Span events analysis
  - SpanKind and hierarchy analysis
  - Resource attributes and propagators
  - Exporter configuration patterns
- **v1.0 (2025-10-15):** Initial version

