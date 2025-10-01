# Span Attribute Research System

Systematic capture and analysis of real span attributes from different instrumentors, LLM providers, and usage scenarios to inform transform development.

## 🎯 Purpose

This research system addresses a critical question for the Universal LLM Discovery Engine v4.0:

**What do real span attributes actually look like from different sources?**

Understanding the actual format of span attributes is essential because:

1. **BYOI Architecture**: HoneyHive supports "Bring Your Own Instrumentor" - we need to handle diverse formats
2. **Multiple Data Sources**: Instrumentors, manual tracing, non-instrumentor frameworks all produce different formats
3. **Transform Design**: Transforms must dynamically handle whatever formats they receive
4. **Evidence-Based Development**: Design based on real data, not assumptions

## 🏗️ Architecture

### **Components**

```
scripts/
├── research_span_attributes.py          # Main research runner
└── benchmark/
    └── monitoring/
        ├── attribute_capture.py         # Span capture system
        ├── span_interceptor.py          # Span interception
        └── ...
    └── providers/
        ├── openinference_openai_provider.py
        ├── openinference_anthropic_provider.py
        ├── traceloop_openai_provider.py
        ├── traceloop_anthropic_provider.py
        ├── openlit_openai_provider.py   # NEW
        └── ...
```

### **Research Matrix**

| Dimension | Values | Purpose |
|-----------|--------|---------|
| **Instrumentors** | OpenInference, Traceloop, OpenLit, Manual, Strands, Pydantic AI, Semantic Kernel | Different attribute naming conventions |
| **Providers** | OpenAI, Anthropic, Gemini, Bedrock, etc. | Provider-specific response structures |
| **Scenarios** | Basic chat, Tool calls, Multimodal, Streaming, Complex | Different response types and complexity |

## 🚀 Quick Start

### **Basic Usage**

```bash
# Quick test: OpenInference + OpenAI, basic scenarios
python scripts/research_span_attributes.py \
    --instrumentors openinference \
    --providers openai \
    --scenarios basic_chat

# Comprehensive: All instrumentors × All providers
python scripts/research_span_attributes.py \
    --instrumentors all \
    --providers all \
    --scenarios all \
    --operations 5
```

### **Environment Setup**

Required environment variables:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export HH_API_KEY="your-honeyhive-key"
export HH_PROJECT="span-research"
```

Optional configuration:

```bash
export OPENAI_MODEL="gpt-4o-mini"           # Default model
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
```

## 📊 Output Files

### **1. Main Capture File**

`span_attribute_captures/span_captures_YYYYMMDD_HHMMSS.json`

All captured spans in a single file:

```json
{
  "capture_session_id": "20250130_143022",
  "capture_count": 45,
  "captured_at": "2025-01-30T14:35:18",
  "spans": [
    {
      "span_name": "openai.chat.completions",
      "instrumentor": "openinference",
      "provider": "openai",
      "scenario": "basic_chat",
      "attributes": {
        "llm.system": "openai",
        "llm.request.model": "gpt-4o-mini",
        "llm.input_messages.0.role": "user",
        "llm.input_messages.0.content": "Hello!",
        ...
      },
      "capture_timestamp": "2025-01-30T14:30:22",
      "metadata": {}
    }
  ]
}
```

### **2. Category Files**

`span_attribute_captures/{instrumentor}_{provider}/...json`

Organized by instrumentor/provider combination for easier analysis.

### **3. Attribute Matrix**

`span_attribute_captures/attribute_matrix_YYYYMMDD_HHMMSS.json`

Shows which attributes appear in which contexts:

```json
{
  "openinference/openai": {
    "scenarios": ["basic_chat", "tool_calls"],
    "span_count": 15,
    "attributes": {
      "llm.system": {
        "count": 15,
        "example_values": ["openai"]
      },
      "llm.input_messages.0.role": {
        "count": 15,
        "example_values": ["user", "system", "assistant"]
      }
    }
  }
}
```

## 🔬 Research Scenarios

### **Available Scenarios**

| Scenario | Description | What It Tests |
|----------|-------------|---------------|
| `basic_chat` | Simple Q&A | Basic message handling |
| `tool_calls` | Function calling | Tool use attributes |
| `multimodal` | Images, audio, video | Multimodal content handling |
| `complex_chat` | Long, detailed responses | Large token counts, complex structures |
| `streaming` | Streaming responses | Streaming-specific attributes |

### **Custom Scenarios**

Add new scenarios by editing `_get_scenario_prompts()` in `research_span_attributes.py`.

## 📈 Analysis Workflow

### **Step 1: Capture Data**

```bash
# Start with known working combinations
python scripts/research_span_attributes.py \
    --instrumentors openinference,traceloop \
    --providers openai \
    --scenarios basic_chat,complex_chat \
    --operations 3
```

### **Step 2: Review Outputs**

Check the generated files:

```bash
ls -lh span_attribute_captures/
cat span_attribute_captures/attribute_matrix_*.json | jq .
```

### **Step 3: Analyze Patterns**

Key questions to answer:

- **Flattened vs. Nested**: Are arrays flattened (`llm.messages.0.role`) or nested?
- **JSON Strings**: Are complex objects JSON-serialized strings?
- **Attribute Names**: What naming conventions are used?
- **Message Formats**: How are messages structured?
- **Tool Calls**: How are tool calls represented?
- **Multimodal**: How is non-text content handled?

### **Step 4: Document Findings**

Update transform development based on real data:

```
Finding: OpenInference uses flattened attributes
Example: llm.input_messages.0.role = "user"
Impact: Transforms must reconstruct arrays from flattened format

Finding: Traceloop uses JSON strings for messages
Example: gen_ai.prompt = '[{"role": "user", "content": "Hi"}]'
Impact: Transforms must parse JSON strings
```

## 🎓 Research Questions

### **Primary Questions**

1. **What attribute naming conventions do instrumentors use?**
   - OpenInference: `llm.*`
   - Traceloop: `gen_ai.*`
   - OpenLit: `gen_ai.*` + provider-specific

2. **How are complex objects serialized?**
   - Flattened: `prefix.0.field`
   - JSON strings: `'[{...}]'`
   - Mix of both?

3. **What formats do manual/framework integrations produce?**
   - HoneyHive SDK auto-flattening
   - Strands format
   - Pydantic AI format
   - Semantic Kernel format

4. **How is multimodal content represented?**
   - Image URLs
   - Base64 data
   - File references
   - Content type indicators

### **Secondary Questions**

- Which attributes are provider-specific vs. universal?
- How are error conditions represented?
- What metadata is included by each instrumentor?
- Are there performance implications (attribute count)?

## 🔧 Adding New Research Targets

### **New Instrumentor**

1. Create provider class in `benchmark/providers/`
2. Implement `BaseProvider` interface
3. Add to `_get_provider_instance()` in research script
4. Test with `--instrumentors your_instrumentor`

### **New Provider**

1. Implement provider class for each instrumentor
2. Add API key env var handling
3. Add to provider mapping
4. Test with `--providers your_provider`

### **New Scenario**

Add to `_get_scenario_prompts()`:

```python
scenarios = {
    ...
    "your_scenario": [
        "Prompt 1 for your scenario",
        "Prompt 2 for your scenario",
        "Prompt 3 for your scenario"
    ]
}
```

## 📋 Best Practices

### **Research Execution**

1. **Start Small**: Test one combination first
2. **Verify API Keys**: Ensure all required keys are set
3. **Monitor Costs**: Use cheaper models for initial research
4. **Check Outputs**: Verify files are being created correctly

### **Data Collection**

1. **Multiple Operations**: Run 3-5 operations per scenario for variety
2. **Diverse Scenarios**: Cover different response types
3. **Error Cases**: Include scenarios that might fail
4. **Edge Cases**: Test unusual inputs

### **Analysis**

1. **Compare Side-by-Side**: Use diff tools on JSON outputs
2. **Look for Patterns**: Identify commonalities and differences
3. **Document Surprises**: Note unexpected formats
4. **Update Transforms**: Use findings to improve transform design

## 🐛 Troubleshooting

### **No Spans Captured**

```bash
# Enable verbose logging
python scripts/research_span_attributes.py \
    --instrumentors openinference \
    --providers openai \
    --scenarios basic_chat \
    # Check if spans are being created
```

Check:
- Is the instrumentor properly initialized?
- Are API calls succeeding?
- Is the span interceptor active?

### **Import Errors**

```bash
# Install missing dependencies
pip install openlit  # For OpenLit instrumentor
pip install openinference-instrumentation-anthropic  # For Anthropic
```

### **API Errors**

Check:
- API keys are valid
- Rate limits not exceeded
- Model names are correct

## 📚 Related Documentation

- [Universal LLM Discovery Engine v4.0](../universal_llm_discovery_engine_v4_final/README.md)
- [BYOI Architecture](../docs/explanation/architecture/byoi-design.rst)
- [Transform Registry](../src/honeyhive/tracer/processing/semantic_conventions/transform_registry.py)
- [Benchmark System](./benchmark/README.md)

## 🎯 Success Criteria

A successful research run produces:

- ✅ Captured spans from all tested combinations
- ✅ Attribute matrix showing patterns
- ✅ Clear documentation of attribute formats
- ✅ Evidence for transform design decisions
- ✅ Identified gaps or edge cases

## 🔄 Continuous Research

This is an **ongoing research system**. As new instrumentors, providers, or usage patterns emerge:

1. Add them to the research matrix
2. Capture their attribute formats
3. Update transforms accordingly
4. Document findings

The goal is **evidence-based** transform development, not assumption-based.
