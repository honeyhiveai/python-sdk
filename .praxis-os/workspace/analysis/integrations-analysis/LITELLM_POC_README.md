# LiteLLM → HoneyHive Integration POC

This directory contains proof-of-concept code demonstrating HoneyHive's integration with LiteLLM.

## Files

- `litellm_poc_custom_callback.py` - Core custom callback implementation
- `litellm_poc_router_example.py` - Router integration example
- `LITELLM_POC_README.md` - This file

## What This POC Demonstrates

### 1. Custom Callback Approach
- Captures **complete LiteLLM metadata** beyond what OTel instrumentors provide
- Works with Router, Proxy, and all 100+ providers
- Full control over captured data

### 2. Metadata Captured

**Standard LLM Data:**
- Model name and provider
- Input messages and parameters
- Output content and finish reasons
- Token usage (prompt, completion, total)
- Latency and timestamps

**LiteLLM-Specific:**
- Custom provider (openai, anthropic, bedrock, etc.)
- LiteLLM version
- User-provided metadata

**Router Data (when using Router):**
- Routing strategy (lowest-latency, least-busy, etc.)
- Selected deployment ID
- Model group
- Fallback information (in failure scenarios)

**Proxy Data (when using Proxy):**
- Virtual key hash
- Team ID
- User ID
- Request ID

## Running the POC

### Prerequisites
```bash
pip install litellm
```

### Basic Example
```bash
python litellm_poc_custom_callback.py
```

Expected output: Mock traces logged to console showing captured metadata structure.

### Router Example
```bash
python litellm_poc_router_example.py
```

Expected output: Demonstrates how Router-specific metadata is captured.

## Integration with Real HoneyHive

To integrate with actual HoneyHive backend:

1. **Replace MockHoneyHiveClient**
   ```python
   # In litellm_poc_custom_callback.py
   from honeyhive import HoneyHiveClient  # Real SDK
   
   self._client = HoneyHiveClient(
       api_key=api_key,
       base_url=api_url,
   )
   ```

2. **Adjust trace_data structure**
   - Modify `_build_trace_data()` to match HoneyHive's API schema
   - Add any additional fields HoneyHive requires

3. **Add error handling**
   - Retry logic for failed API calls
   - Batch processing for high volume
   - Circuit breaker for HoneyHive outages

4. **Add async support**
   - Implement `async_log_success_event()`
   - Use async HTTP client for HoneyHive API

5. **Package as pip-installable**
   - Create `pyproject.toml`
   - Publish to PyPI as `honeyhive-litellm`

## Comparison with Instrumentors

| Feature | OpenInference | OpenLIT | Custom Callback (This POC) |
|---------|--------------|---------|---------------------------|
| Automatic | Yes | Yes | No (explicit setup) |
| LiteLLM Router | Basic | Basic | **Complete** |
| Provider Details | Limited | Limited | **Complete** |
| Raw Requests | No | No | **Yes (optional)** |
| Custom Enrichment | Limited | Limited | **Full control** |
| Maintenance | Arize | OpenLIT | **HoneyHive** |

## Next Steps

1. ✅ POC demonstrates feasibility
2. ⏭️ HoneyHive team reviews trace data structure
3. ⏭️ Implement real HoneyHive client integration
4. ⏭️ Add comprehensive error handling
5. ⏭️ Add async support
6. ⏭️ Create pip package
7. ⏭️ Write user documentation
8. ⏭️ Test with real production workloads

## Questions for HoneyHive Team

1. **Trace Data Schema**: Does the `trace_data` structure in POC match HoneyHive's expected format?
2. **API Endpoints**: What's the actual endpoint for `log_trace()`?
3. **Authentication**: Any special auth requirements beyond API key?
4. **Batching**: Should traces be batched or sent individually?
5. **Rate Limits**: Any rate limits to be aware of?
6. **Error Handling**: How should failed trace uploads be handled? Retry? Drop?
7. **Async**: Is async/await required for production use?

## License

[Same as honeyhiveai/python-sdk]

