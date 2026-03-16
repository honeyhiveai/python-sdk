# Generate Test Cases for Missing Providers

This guide explains how to generate test cases for the 3 missing providers: **Google ADK**, **AutoGen**, and **Semantic Kernel**.

## Prerequisites

1. **Environment Setup**: Ensure you have a `.env` file in the repo root with:
   ```bash
   HH_API_KEY=your_honeyhive_api_key
   HH_PROJECT=your_project_name
   OPENAI_API_KEY=your_openai_key
   GOOGLE_API_KEY=your_google_key
   ```

2. **Install Dependencies**:
   ```bash
   # From repo root
   pip install -e .
   
   # For Semantic Kernel
   pip install semantic-kernel openinference-instrumentation-openai
   
   # For Google ADK
   pip install google-adk openinference-instrumentation-google-adk
   
   # For AutoGen
   pip install autogen-agentchat autogen-ext[openai] openinference-instrumentation-openai
   ```

## Step 1: Temporarily Add Span Capture

None of the public integration examples keep span-capture hooks committed. For each integration, temporarily add the capture hook locally, run the example once with `CAPTURE_SPANS=true`, save the dump under `.tmp/integration-example-dumps/<integration>/`, then remove the temporary capture code before committing.

Use this temporary local patch pattern:

```python
from capture_spans import setup_span_capture

async def main() -> None:
    tracer = HoneyHiveTracer.init(...)
    span_processor = setup_span_capture("<integration_name>", tracer)
    ...
    try:
        ...
    finally:
        if span_processor:
            span_processor.force_flush()
        ...
```

For synchronous examples, apply the same pattern around the main execution path:

```python
tracer = HoneyHiveTracer.init(...)
span_processor = setup_span_capture("<integration_name>", tracer)

try:
    ...
finally:
    if span_processor:
        span_processor.force_flush()
```

Then run each integration with `CAPTURE_SPANS=true`:

```bash
cd examples/integrations

export CAPTURE_SPANS=true

# Run Semantic Kernel
python3 semantic_kernel_integration.py

# Run Google ADK
python3 openinference_google_adk_example.py

# Run AutoGen
python3 autogen_integration.py
```

This will create span dump files under `.tmp/integration-example-dumps/`:
- `.tmp/integration-example-dumps/semantic_kernel/semantic_kernel_YYYYMMDD_HHMMSS.json`
- `.tmp/integration-example-dumps/google_adk/google_adk_YYYYMMDD_HHMMSS.json`
- `.tmp/integration-example-dumps/autogen/autogen_YYYYMMDD_HHMMSS.json`

## Step 2: Convert Spans to Test Cases

Run the conversion script to generate test case JSON files:

```bash
python3 convert_spans_to_test_cases.py
```

This will:
1. Read all span dumps from `.tmp/integration-example-dumps/`
2. Extract OpenTelemetry attributes
3. Map them to the expected HoneyHive event structure
4. Deduplicate by schema
5. Save unique test cases to `test_cases/`

## Output Format

Each test case follows this schema:

```json
{
  "name": "Instrumentor Provider Operation",
  "input": {
    "attributes": {
      "gen_ai.prompt": [...],
      "gen_ai.completion": [...],
      "gen_ai.system": "openai",
      "gen_ai.request.model": "gpt-4",
      "gen_ai.usage.prompt_tokens": 10,
      "gen_ai.usage.completion_tokens": 20
    },
    "scopeName": "openinference.instrumentation.openai",
    "eventType": "model"
  },
  "expected": {
    "inputs": {
      "chat_history": [...]
    },
    "outputs": {
      "message": "..."
    },
    "config": {
      "model": "gpt-4",
      "temperature": 0.7
    },
    "metrics": {
      "prompt_tokens": 10,
      "completion_tokens": 20,
      "total_tokens": 30
    },
    "metadata": {
      "system": "openai",
      "response_id": "..."
    },
    "session_id": "..."
  }
}
```

## Notes

- Add the span-capture hook locally for each integration, generate the dump, then remove the hook before committing.
- Keep generated dumps under `.tmp/integration-example-dumps/` rather than tracked paths.

## Expected Test Cases

After running all 3 integrations, you should have test cases covering:

### Google ADK
- Basic agent interactions
- Tool usage
- Sequential workflows
- Parallel workflows  
- Loop workflows

### AutoGen
- Basic assistant agent
- Custom system messages
- Agent-based tools
- Streaming responses
- Multi-turn conversations
- Multi-agent collaboration
- Agent handoffs
- Complex workflows

### Semantic Kernel
- Single agent with tool calls
- Multi-turn session continuity
- Multi-agent handoff orchestration
- Streaming

## Troubleshooting

**No span dumps created?**
- Ensure `CAPTURE_SPANS=true` is set
- Check that the integration runs successfully
- Confirm you temporarily added the local capture hook before running the example
- Look for error messages during execution

**Empty test cases?**
- The spans might not have LLM calls (only CHAIN/AGENT spans)
- Check the span dump JSON to see what attributes are available
- Adjust the `map_to_expected_structure` function if needed

**Duplicate test cases?**
- The script automatically deduplicates based on schema structure
- Only unique patterns are saved
- This is expected behavior

## Next Steps

Once test cases are generated:
1. Review them for completeness
2. Ensure they match the format of existing test cases
3. Validate that all provider/operation combinations are covered

