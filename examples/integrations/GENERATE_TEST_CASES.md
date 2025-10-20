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

## Step 1: Run Integrations with Span Capture

Run each integration with the `CAPTURE_SPANS=true` environment variable:

```bash
cd examples/integrations

# Run Semantic Kernel
export CAPTURE_SPANS=true
python3 semantic_kernel_integration.py

# Run Google ADK
python3 openinference_google_adk_example.py

# Run AutoGen
python3 autogen_integration.py
```

This will create span dump files in `span_dumps/`:
- `semantic_kernel_YYYYMMDD_HHMMSS.json`
- `google_adk_YYYYMMDD_HHMMSS.json`
- `autogen_YYYYMMDD_HHMMSS.json`

## Step 2: Convert Spans to Test Cases

Run the conversion script to generate test case JSON files:

```bash
python3 convert_spans_to_test_cases.py
```

This will:
1. Read all span dumps from `span_dumps/`
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

## Files Modified

The following integration files have been updated with span capture:

1. **semantic_kernel_integration.py**:
   - Added `from capture_spans import setup_span_capture`
   - Added `span_processor = setup_span_capture("semantic_kernel", tracer)`
   - Added cleanup: `if span_processor: span_processor.force_flush()`

2. **openinference_google_adk_example.py**:
   - Added `from capture_spans import setup_span_capture`
   - Added `span_processor = setup_span_capture("google_adk", tracer)`
   - Added cleanup: `if span_processor: span_processor.force_flush()`

3. **autogen_integration.py**:
   - Added `from capture_spans import setup_span_capture`
   - Added `span_processor = setup_span_capture("autogen", tracer)`
   - Added cleanup: `if span_processor: span_processor.force_flush()`

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
- Basic agent with plugins
- Structured output
- Chat history
- Multi-turn with tools
- Multiple models
- Streaming
- Group chat orchestration

## Troubleshooting

**No span dumps created?**
- Ensure `CAPTURE_SPANS=true` is set
- Check that the integration runs successfully
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

