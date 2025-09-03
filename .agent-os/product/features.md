# HoneyHive Python SDK - Feature Catalog

## Core Tracing Features

### 🔍 Automatic Instrumentation

#### Universal @trace Decorator
```python
from honeyhive.models import EventType

# Works with both sync and async functions
@trace(event_type=EventType.model, event_name="chat_completion")
def sync_function(prompt: str) -> str:
    return llm.complete(prompt)

@trace(event_type=EventType.model)
async def async_function(prompt: str) -> str:
    return await llm.complete_async(prompt)
```

#### Class-Level Tracing
```python
@trace_class
class ChatService:
    def process_message(self, msg: str):
        # Automatically traced
        return self.llm.complete(msg)
```

#### Manual Span Management
```python
# Context manager for fine control
with tracer.start_span("custom_operation") as span:
    span.set_attribute("user_id", user_id)
    result = perform_operation()
    span.set_attribute("result_size", len(result))
```

### 📊 Session Management

#### Automatic Session Creation
```python
# Session automatically created on init
tracer = HoneyHiveTracer.init(
    api_key="hh_api_...",
    project="my_app",
    session_name="production_session"  # Optional, defaults to filename
)
```

#### Session Enrichment
```python
# Add metadata to sessions
tracer.enrich_session(
    metadata={"version": "1.0.0"},
    feedback={"rating": 5},
    metrics={"latency_ms": 150},
    user_properties={"tier": "premium"}
)
```

### 🧪 Evaluation Framework

#### Client-Side Evaluations
```python
from honeyhive import evaluate, evaluator

@evaluator
def accuracy_evaluator(output, expected):
    return {"accuracy": output == expected}

@evaluate(
    name="model_test",
    evaluators=[accuracy_evaluator]
)
def test_model(inputs):
    return model.predict(inputs)
```

#### Async Evaluations
```python
@aevaluator
async def async_evaluator(output, context):
    result = await validate_async(output)
    return {"valid": result}
```

#### Batch Evaluations with Threading
```python
from honeyhive import evaluate_batch

results = evaluate_batch(
    function=process_item,
    dataset=test_dataset,
    evaluators=[eval1, eval2],
    max_workers=10  # Parallel execution
)
```

### 🔌 Integration Features

#### Auto-Instrumentor Support
```python
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(
    api_key="...",
    instrumentors=[OpenAIInstrumentor()]  # BYOI: OpenInference, OpenLLMetry, or custom
)

# Now all OpenAI calls are automatically traced
response = openai.chat.completions.create(...)
```

#### HTTP Tracing Control
```python
# Disable HTTP tracing for performance
tracer = HoneyHiveTracer.init(
    api_key="...",
    disable_http_tracing=True  # Default
)

# Or enable for debugging
tracer = HoneyHiveTracer.init(
    api_key="...",
    disable_http_tracing=False
)
```

### 🎯 Span Enrichment

#### Enrich Current Span
```python
# Direct enrichment
tracer.enrich_span(
    metadata={"model": "gpt-4"},
    metrics={"tokens": 150},
    outputs={"response": "..."}
)

# Context manager pattern
with enrich_span(event_type=EventType.tool):
    process_data()
```

#### Comprehensive Attributes
```python
with tracer.start_span("operation") as span:
    # Set various attribute types
    span.set_attribute("string_attr", "value")
    span.set_attribute("int_attr", 42)
    span.set_attribute("float_attr", 3.14)
    span.set_attribute("bool_attr", True)
    span.set_attribute("list_attr", [1, 2, 3])
    span.set_attribute("dict_attr", {"key": "value"})
```

### 🔄 Multi-Instance Support

#### Run Multiple Tracers
```python
# Create independent tracer instances
tracer1 = HoneyHiveTracer.init(
    api_key="key1",
    project="project1"
)

tracer2 = HoneyHiveTracer.init(
    api_key="key2",
    project="project2"
)

# Each maintains its own state
with tracer1.start_span("op1"):
    # Traced to project1
    pass

with tracer2.start_span("op2"):
    # Traced to project2
    pass
```

### 📝 Configuration Management

#### Environment Variable Support
```python
# Supports multiple env var patterns
# HH_* (HoneyHive specific)
export HH_API_KEY="..."
export HH_PROJECT="..."

# Standard patterns (compatibility)
export HTTP_PROXY="..."
export EXPERIMENT_ID="..."

# All automatically loaded
tracer = HoneyHiveTracer.init()  # Uses env vars
```

#### Experiment Harness
```python
# Set experiment context
export HH_EXPERIMENT_ID="exp_123"
export HH_EXPERIMENT_VARIANT="treatment"

# Automatically included in traces
tracer = HoneyHiveTracer.init()
# All spans include experiment metadata
```

### 🛡️ Reliability Features

#### Graceful Degradation
```python
# Never crashes your application
try:
    tracer = HoneyHiveTracer.init(api_key="invalid")
except Exception:
    # Falls back gracefully
    print("Tracing disabled, continuing...")

# Your app continues running
```

#### Force Flush
```python
# Ensure all spans are sent
success = tracer.force_flush(timeout_millis=5000)
if success:
    print("All telemetry data sent")
```

#### Proper Shutdown
```python
# Clean shutdown
try:
    # Your application code
    pass
finally:
    tracer.shutdown()  # Ensures cleanup
```

### 🔍 Observability Features

#### Baggage Propagation
```python
# Set baggage for context propagation
ctx = tracer.set_baggage("user_id", "12345")
value = tracer.get_baggage("user_id")  # "12345"

# Automatically propagated across services
```

#### Context Injection/Extraction
```python
# For distributed tracing
headers = {}
tracer.inject_context(headers)
# Send headers to downstream service

# In downstream service
ctx = tracer.extract_context(headers)
# Continues trace from upstream
```

### 📊 API Client Features

#### Comprehensive API Access
```python
from honeyhive import HoneyHive

client = HoneyHive(api_key="...")

# Events API
client.events.create_event(...)
client.events.update_event(...)

# Datasets API
client.datasets.create_dataset(...)
client.datasets.get_datasets(...)

# Configurations API
client.configurations.get_configurations(...)

# Evaluations API
client.evaluations.create_evaluation_run(...)

# Metrics API
client.metrics.create_metric(...)
```

### 🚀 Performance Features

#### Connection Pooling
```python
# Automatic connection reuse
# Configured via environment
export HH_MAX_CONNECTIONS=100
export HH_KEEPALIVE_EXPIRY=30
```

#### Rate Limiting
```python
# Built-in rate limiting
export HH_RATE_LIMIT_CALLS=1000
export HH_RATE_LIMIT_WINDOW=60
```

#### Retry Logic
```python
# Automatic retries with exponential backoff
export HH_MAX_RETRIES=3
# Handles transient failures automatically
```

### 📚 Documentation System - Divio Architecture

#### Four-Type Documentation Structure  
Following the [Divio Documentation System](https://docs.divio.com/documentation-system/) for optimal user experience:

#### Type Safety & Code Standards
**MANDATORY: Proper type usage in all documentation examples**

```python
# ✅ CORRECT: Type-safe enum usage
from honeyhive import HoneyHiveTracer, trace
from honeyhive.models import EventType

@trace(event_type=EventType.model)  # LLM operations
@trace(event_type=EventType.tool)   # Individual functions  
@trace(event_type=EventType.chain)  # Multi-step workflows
@trace(event_type=EventType.session) # User sessions

# ❌ INCORRECT: String literals (deprecated)
@trace(event_type="model")  # Breaks type safety
```

**Quality Requirements**:
- All code examples include proper imports
- Examples pass mypy type checking  
- Semantic EventType usage consistency
- AI assistant validation enforcement

```yaml
# TUTORIALS (Learning-oriented)
tutorials/:
  purpose: "Help newcomers get started and achieve early success"
  user_mindset: "I want to learn by doing"
  structure: "Objective → Prerequisites → Steps → Results → Next Steps"
  max_duration: "15-20 minutes per tutorial"
  testing: "Verified with 3+ new users monthly"

# HOW-TO GUIDES (Problem-oriented)  
how-to/:
  purpose: "Solve specific real-world problems"
  user_mindset: "I want to solve this specific problem"
  title_format: "How to [solve specific problem]"
  structure: "Problem → Solution → Implementation → Verification"
  content: "Minimal background, maximum solution focus"

# REFERENCE (Information-oriented)
reference/:
  purpose: "Provide comprehensive technical specifications"
  user_mindset: "I need to look up exact details"
  coverage: "100% API documentation with working examples"
  accuracy: "Automated testing of all code examples"
  cross_references: "Complete linking between related items"

# EXPLANATION (Understanding-oriented)
explanation/:
  purpose: "Provide context, background, and design decisions"
  user_mindset: "I want to understand how this works and why"
  content: "Design rationale, conceptual understanding, comparisons"
  depth: "Sufficient context for informed architectural decisions"
```

#### Content Quality Assurance
```python
# Automated Documentation Testing
docs/utils/
├── audit-content.py          # Broken link detection
├── test-examples.py          # Code example verification  
├── validate-structure.py     # Divio compliance checking
└── user-journey-test.py      # End-to-end tutorial testing
```

#### Documentation Deployment Features
```yaml
# Multi-Platform Publishing
github_pages:
  primary_hosting: "honeyhiveai.github.io/python-sdk"
  preview_builds: "Automatic PR previews via GitHub Actions"
  branch_deploys: "Feature branch documentation"

versioning:
  sphinx_versions: "Release-based versioning"
  backward_compatibility: "Previous version access"
  migration_guides: "Breaking change documentation"

accessibility:
  wcag_compliance: "WCAG 2.1 AA standard"
  screen_reader: "Full navigation support" 
  mobile_optimized: "Responsive design"
  offline_capable: "PDF generation"
```

#### Visual Documentation Standards
```yaml
# Diagram Standards
mermaid:
  architecture_diagrams: "System architecture visualization"
  flow_charts: "Process and decision flows"
  sequence_diagrams: "API interaction patterns"
  theme: "Base theme with consistent color palette"

screenshots:
  credential_sanitization: "All API keys and sensitive data redacted"
  consistent_styling: "Standardized UI capture settings"
  mobile_responsive: "Multi-device optimization"

code_highlighting:
  language_support: "Python, YAML, JSON, bash, docker"
  syntax_themes: "Light/dark mode compatibility"
  copy_to_clipboard: "One-click code copying"
```

### 🔧 CI/CD & DevOps Features

#### Multi-Tier Testing Strategy
```yaml
# Tier 1: Continuous Testing (Every PR/Push)
- Fast feedback (5-10 minutes)
- Core functionality validation
- Docker Lambda simulation
- Cross-Python version testing (3.11, 3.12, 3.13)
- Documentation build and link validation

# Tier 2: Daily Scheduled Testing (2 AM UTC) 
- Comprehensive validation (30-60 minutes)
- Real AWS Lambda environment testing
- Performance benchmarking with statistical significance
- Security and dependency vulnerability scans
- Documentation accessibility testing

# Tier 3: Release Candidate Testing (Manual)
- Complete validation (45-90 minutes)
- Package building and distribution testing
- Cross-platform testing (Ubuntu, Windows, macOS)
- Quality gates for production deployment
- Documentation versioning and deployment
```

#### GitHub Actions Workflow Optimization
```yaml
# Smart Job Organization
- Composite jobs reducing PR interface clutter
- Matrix strategy optimization for true parallelization
- Conditional execution based on branch and commit context

# Modern Infrastructure
- Latest stable action versions (v4/v5)
- Artifact management with configurable retention
- Duplicate execution prevention through trigger optimization
```

#### AWS Lambda Testing Framework
```python
# Docker Simulation Suite
- Complete Lambda runtime simulation using official AWS images
- Container validation with SDK import verification
- Memory configuration testing (128MB to 1024MB)
- Cold start and warm start performance analysis

# Real AWS Environment Testing
- Production Lambda deployment validation on main branch
- Stress testing with concurrent invocations
- Timeout handling and error resilience validation
```

#### Performance Analysis & Benchmarking
```python
# Scientific Measurement Methodology
- 99.8% variance reduction through statistical techniques
- Comparative baseline testing (SDK vs. no-SDK containers)
- Coefficient of Variation analysis achieving <10% CV
- Bulk operation testing for statistical significance

# CI-Compatible Thresholds
- Environment-aware performance limits
- Automated regression detection
- Performance monitoring with adaptive thresholds
```

#### YAML Configuration & Validation
```yaml
# yamllint Integration
- Custom configuration with 120-character line length
- Pre-commit YAML syntax validation
- Workflow self-validation and documentation generation

# Configuration Management
extends: default
rules:
  line-length:
    max: 120
  indentation:
    spaces: 2
```

## Feature Availability Matrix

| Feature | Status | Version |
|---------|--------|---------|
| @trace decorator | ✅ Stable | 0.1.0 |
| Async support | ✅ Stable | 0.1.0 |
| Multi-instance | ✅ Stable | 0.1.0 |
| Session management | ✅ Stable | 0.1.0 |
| HTTP tracing | ✅ Stable | 0.1.0 |
| Evaluations | ✅ Stable | 0.1.0 |
| Threading | ✅ Stable | 0.1.0 |
| BYOI Instrumentors | ✅ Stable | 0.1.0 |
| **Multi-tier CI/CD** | ✅ **Stable** | **0.1.0** |
| **Lambda testing** | ✅ **Stable** | **0.1.0** |
| **Performance benchmarks** | ✅ **Stable** | **0.1.0** |
| **GitHub Actions optimization** | ✅ **Stable** | **0.1.0** |
| **YAML validation** | ✅ **Stable** | **0.1.0** |
| **Divio documentation system** | ✅ **Stable** | **0.1.0** |
| **Automated content testing** | ✅ **Stable** | **0.1.0** |
| **GitHub Pages docs hosting** | ✅ **Stable** | **0.1.0** |
| **WCAG accessibility compliance** | ✅ **Stable** | **0.1.0** |
| **Documentation versioning** | ✅ **Stable** | **0.1.0** |
| Streaming | 🚧 Planned | 0.3.0 |
| Alerting | 🚧 Planned | 0.4.0 |
| Enterprise | 🚧 Planned | 1.0.0 |

## Configuration Options

### Initialization Parameters
```python
tracer = HoneyHiveTracer.init(
    api_key="...",              # Required (unless in env)
    project="...",              # Project name
    source="production",        # Environment
    session_name="...",         # Custom session name
    test_mode=False,            # Enable test mode
    disable_http_tracing=True,  # HTTP tracing control
    instrumentors=[],           # BYOI: OpenInference, OpenLLMetry, custom
    server_url="..."           # Custom server URL
)
```

### Environment Variables
```bash
# Core Configuration
HH_API_KEY="..."
HH_PROJECT="..."
HH_SOURCE="..."

# Feature Flags
HH_DISABLE_TRACING="false"
HH_DISABLE_HTTP_TRACING="true"
HH_TEST_MODE="false"
HH_DEBUG_MODE="false"

# Performance Tuning
HH_MAX_CONNECTIONS="100"
HH_RATE_LIMIT_CALLS="1000"
HH_TIMEOUT="30.0"

# Experiment Tracking
HH_EXPERIMENT_ID="..."
HH_EXPERIMENT_NAME="..."
HH_EXPERIMENT_VARIANT="..."
```

## Usage Examples

### Basic Tracing
```python
from honeyhive import HoneyHiveTracer, trace
from honeyhive.models import EventType

# Initialize
tracer = HoneyHiveTracer.init()

# Trace a function
@trace(event_type=EventType.tool)
def my_function():
    return "result"

result = my_function()
```

### Advanced Evaluation
```python
from honeyhive import evaluate, evaluator

@evaluator
def latency_check(output, context):
    return {"fast": context.duration < 100}

@evaluate(
    name="performance_test",
    evaluators=[latency_check]
)
def process_request(request):
    return handle(request)
```

### Production Deployment
```python
import os
from honeyhive import HoneyHiveTracer

# Production configuration
tracer = HoneyHiveTracer.init(
    api_key=os.getenv("HH_API_KEY"),
    project="production",
    source="api-server",
    disable_http_tracing=True
)

# Ensure clean shutdown
import atexit
atexit.register(lambda: tracer.force_flush() and tracer.shutdown())
```
