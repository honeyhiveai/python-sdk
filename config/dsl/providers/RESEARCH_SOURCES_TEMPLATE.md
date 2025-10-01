# {Provider Name} Provider Research Sources

**Provider**: {Provider Name}  
**Last Updated**: {YYYY-MM-DD}  
**Version**: 1.0  
**Maintainer**: AI Assistant / {Your Name}

---

## 📋 **Research Sources Used**

### **Official Provider Documentation**

**⚠️ CRITICAL**: Always start here first!

- **API Documentation**: {URL to API reference}
  - Where to find: Official developer docs, usually `/docs/api` or `/api-reference`
  - What to look for: Endpoint structure, request/response formats, authentication
  - Last verified: {Date}

- **Models Overview**: {URL to models page}
  - Where to find: Usually `/docs/models`, `/models`, or pricing page
  - What to look for: Current model names, capabilities, context windows
  - Last verified: {Date}

- **Pricing**: {URL to pricing page}
  - Where to find: Usually `/pricing` or `/docs/pricing`
  - What to look for: Cost per token/request, different model tiers
  - Last verified: {Date}

- **Release Notes**: {URL to changelog/releases}
  - Where to find: `/changelog`, `/releases`, `/docs/updates`, GitHub releases
  - What to look for: New models, deprecated models, API changes
  - Last verified: {Date}

### **Semantic Convention Standards**

**Why this matters**: Each instrumentor uses different attribute names for the same data!

#### **OpenInference** (llm.* namespace)
- **GitHub**: https://github.com/Arize-ai/openinference
- **Semantic Conventions**: https://github.com/Arize-ai/openinference/tree/main/spec
- **Version Tested**: {Version number, e.g., 0.1.15+}
- **Key Attributes**:
  ```
  llm.provider           # Provider name (e.g., "openai", "anthropic")
  llm.model_name         # Model identifier
  llm.input_messages     # Input message array
  llm.output_messages    # Output message array
  llm.token_count.*      # Token usage
  llm.invocation_parameters.*  # Model parameters
  ```
- **Where to find examples**: Check `tests/` directory in openinference repo
- **Provider-specific quirks**: {Note any special handling}

#### **Traceloop** (gen_ai.* namespace)
- **GitHub**: https://github.com/traceloop/openllmetry
- **Semantic Conventions**: https://github.com/traceloop/openllmetry/tree/main/packages/opentelemetry-semantic-conventions-ai
- **Version Tested**: {Version number, e.g., 0.46.2+}
- **Key Attributes**:
  ```
  gen_ai.system          # Provider name (e.g., "openai")
  gen_ai.request.model   # Model identifier
  gen_ai.prompt          # Raw prompt (for completion models)
  gen_ai.completion      # Raw completion
  gen_ai.usage.*         # Token usage
  gen_ai.request.*       # Request parameters
  gen_ai.response.*      # Response metadata
  ```
- **Where to find examples**: Check instrumentor packages in repo
- **Provider-specific quirks**: {Note any special handling}

#### **OpenLit** (openlit.* namespace)
- **GitHub**: https://github.com/openlit/openlit
- **Instrumentation**: https://github.com/openlit/openlit/tree/main/sdk/python/src/openlit/instrumentation
- **Version Tested**: {Version number}
- **Key Attributes**:
  ```
  openlit.provider       # Provider name
  openlit.model          # Model identifier
  openlit.usage.*        # Token and cost metrics
  openlit.cost.*         # Cost breakdown
  openlit.request.*      # Request parameters
  openlit.response.*     # Response metadata
  ```
- **Where to find examples**: Check SDK instrumentation directory
- **Provider-specific quirks**: {Note any special handling, e.g., built-in cost calculation}

#### **Direct SDK Patterns** (provider.* or custom namespace)
- **SDK Repository**: {URL to official SDK}
- **Version Tested**: {Version number}
- **Namespace Pattern**: `{provider}.*` (e.g., `openai.*`, `anthropic.*`)
- **Key Attributes**: {List observed attributes from direct SDK usage}
- **Where to find examples**: SDK documentation, example code
- **Provider-specific quirks**: {Note any special handling}

### **Model Information Sources**

**Current Models (as of {Date})**:

Organize by family/tier:

**Flagship Models**:
- `{model-name}` - {Description, context window, capabilities}
- `{model-name-variant}` - {Variant description}

**Mid-Tier Models**:
- `{model-name}` - {Description}

**Budget Models**:
- `{model-name}` - {Description}

**Specialty Models** (if applicable):
- `{model-name}` - {Description, e.g., code-specialized, multimodal}

**Legacy/Deprecated Models**:
- `{model-name}` - {Include for backward compatibility, note deprecation date}

**Where to find**:
- Primary source: {URL to models page}
- Secondary source: {API documentation endpoint that lists models}
- API endpoint: {If provider has /v1/models or similar}

### **Pricing Information Sources**

**Official Pricing Page**: {URL}  
**Last Verified**: {Date}  
**Currency**: USD

**Pricing Structure**:

Describe how this provider charges (important for cost calculation!):
- ☐ Per million tokens (most common)
- ☐ Per request + tokens
- ☐ Per minute/hour
- ☐ Tiered pricing
- ☐ Other: {Describe}

**Pricing Table (per 1M tokens in USD)**:

| Model | Input Cost | Output Cost | Notes |
|-------|------------|-------------|-------|
| `{model-1}` | ${X.XX} | ${X.XX} | {Any notes, e.g., "cached prompts discounted"} |
| `{model-2}` | ${X.XX} | ${X.XX} | |
| ... | ... | ... | |

**Special Pricing Cases**:
- Fine-tuned models: {How pricing works}
- Batch API: {If cheaper, note discount}
- Cached content: {If applicable}
- Rate limits: {If they affect cost}

**Where to verify pricing**:
- Primary: Official pricing page (link above)
- Secondary: API response headers (if provider includes cost info)
- Calculator: {Link if provider has pricing calculator}

### **Provider-Specific Features**

**⚠️ Document unique features that affect DSL design!**

**Unique Parameters**:
- `{parameter-name}`: {What it does, why it matters for our DSL}
  - Default value: {Value}
  - Where used: {Which models support it}
  - Example: {How it appears in traces}

**Response Format Quirks**:
- {Any non-standard response patterns}
- {How errors are formatted}
- {Streaming vs non-streaming differences}

**Authentication Methods**:
- Primary: {e.g., API key in header}
- Alternative: {e.g., OAuth, service accounts}
- Relevant for: {When this affects trace attributes}

**Rate Limiting**:
- Limits: {Requests per minute/day}
- Headers: {How limits are communicated}
- Relevant for: {If this appears in traces}

## 🔧 **Implementation Details**

### **Structure Patterns**
- **Number of patterns**: {Count} detection patterns
- **Instrumentors covered**: {List: OpenInference, Traceloop, OpenLit, etc.}
- **Unique signature fields**: {What makes this provider unique}
- **Confidence weights**: {Range, e.g., 0.85-0.98}
- **Collision risk**: {Any providers with similar signatures}

### **Navigation Rules**
- **Total rules**: {Count} extraction rules
- **Instrumentor coverage**: {Rules per instrumentor breakdown}
- **Provider-specific fields**: {Unique fields only this provider has}
- **Fallback strategy**: {How missing fields are handled}

### **Field Mappings**
- **HoneyHive schema**: All 4 sections (inputs, outputs, config, metadata)
- **Required fields**: {List fields marked required: true}
- **Optional fields**: {Count or list key optional fields}
- **Provider-specific mappings**: {Any unique mappings}

### **Transforms**
- **Total transforms**: {Count} transformation functions
- **Cost calculation**: ✅ Implemented with {Count} model variants
- **Message extraction**: ✅ User, assistant, system prompts
- **Finish reason normalization**: ✅ Provider-specific → standard mapping
- **Custom transforms**: {Any provider-specific transforms}

## 🔄 **Update Procedures**

### **When to Update**

**Monthly Checks** (first Monday of month):
- [ ] Check for new models on official models page
- [ ] Verify pricing hasn't changed
- [ ] Check release notes for API changes

**Quarterly Reviews** (every 3 months):
- [ ] Review instrumentor SDK updates
- [ ] Check for semantic convention changes
- [ ] Validate attribute patterns still match

**Immediate Updates** (when notified):
- [ ] New model releases
- [ ] Pricing changes
- [ ] API breaking changes
- [ ] Deprecation notices

### **Update Checklist**

When updating provider DSL:

1. **Research Phase**:
   - [ ] Check official documentation for changes
   - [ ] Review release notes since last update
   - [ ] Verify current pricing
   - [ ] Check instrumentor releases for pattern changes

2. **Update DSL Files**:
   - [ ] `structure_patterns.yaml` - Add new model patterns
   - [ ] `navigation_rules.yaml` - Update attribute paths if changed
   - [ ] `field_mappings.yaml` - Adjust mappings if schema changed
   - [ ] `transforms.yaml` - Update pricing table and model list

3. **Testing**:
   - [ ] Recompile bundle: `python -m config.dsl.compiler`
   - [ ] Run extraction tests: `python scripts/test_two_tier_extraction.py`
   - [ ] Verify cost calculations with sample data
   - [ ] Test with real trace data if possible

4. **Documentation**:
   - [ ] Update this RESEARCH_SOURCES.md with new information
   - [ ] Update "Last Updated" date at top
   - [ ] Document what changed and why
   - [ ] Note any breaking changes

### **Key Files to Update**

| File | Update Frequency | When to Update |
|------|------------------|----------------|
| `structure_patterns.yaml` | Rare | New instrumentor patterns, new unique attributes |
| `navigation_rules.yaml` | Occasional | New SDK versions, attribute path changes |
| `field_mappings.yaml` | Rare | Schema changes, new required fields |
| `transforms.yaml` | **Frequent** | **New models, pricing changes** ⚠️ |
| `RESEARCH_SOURCES.md` | Every update | Document all changes |

## 📚 **Additional References**

### **Community Resources**

Where to find unofficial but helpful information:

- **Community Forum**: {URL if exists}
- **Discord/Slack**: {Invite link if exists}
- **Reddit**: {Subreddit if active}
- **Stack Overflow**: {Tag to follow}

### **Monitoring Sources**

Stay informed about changes:

- **Status Page**: {URL for service status}
- **Blog**: {Official blog URL}
- **Twitter/X**: {@handle for announcements}
- **GitHub**: {Watch repository for SDK updates}
- **RSS Feed**: {If available}

### **Integration Examples**

Real-world usage patterns:

- **Official Examples**: {Link to provider's examples}
- **HoneyHive Docs**: {Link to our integration guide}
- **OpenTelemetry Examples**: {If provider has OTel docs}
- **Community Examples**: {Gists, tutorials, etc.}

### **Debugging Resources**

When things go wrong:

- **API Playground**: {If provider has online tester}
- **Debug Mode**: {How to enable verbose logging}
- **Support Channels**: {Where to get help}
- **Known Issues**: {Link to known issues page}

## 🐛 **Known Quirks & Gotchas**

**⚠️ Document anything non-obvious!**

### **Provider Quirks**
- **{Quirk 1}**: {Description}
  - **Impact on DSL**: {How this affects our implementation}
  - **Workaround**: {How we handle it}

- **{Quirk 2}**: {Description}
  - **Impact on DSL**: {How this affects our implementation}
  - **Workaround**: {How we handle it}

### **Instrumentor Quirks**
- **OpenInference**: {Any special handling needed}
- **Traceloop**: {Any special handling needed}
- **OpenLit**: {Any special handling needed}

### **Common Issues**
- **Detection fails**: {Common reasons and solutions}
- **Extraction returns None**: {Common reasons and solutions}
- **Cost calculation wrong**: {Common reasons and solutions}

## 📊 **Testing Data**

**Sample Trace Data**:

Where to find real trace data for testing:

```yaml
# Location of test fixtures
test_data:
  openinference: tests/fixtures/{provider}_openinference_*.json
  traceloop: tests/fixtures/{provider}_traceloop_*.json
  openlit: tests/fixtures/{provider}_openlit_*.json
```

**Test Models to Validate**:
- Primary model: `{most common model}`
- Budget model: `{cheapest model}`
- Flagship model: `{most expensive/capable model}`
- Legacy model: `{for backward compatibility}`

**Manual Testing Checklist**:
- [ ] All 3 instrumentors detected correctly
- [ ] All fields extract properly
- [ ] Cost calculation accurate (verify against official calculator)
- [ ] Finish reasons normalized correctly
- [ ] Edge cases handled (empty messages, missing fields, etc.)

---

## 📝 **Notes for Future Maintainers**

**Key Decisions Made**:
- {Why certain patterns were chosen}
- {Why certain fields map certain ways}
- {Any trade-offs or compromises}

**Things to Watch Out For**:
- {Anything that might break in the future}
- {Dependencies on specific versions}
- {Assumptions that might become invalid}

**Improvement Opportunities**:
- {Things that could be better but aren't critical}
- {Features we're not capturing yet}
- {Potential optimizations}

---

**🔗 Quick Links**:
- Official Docs: {URL}
- Pricing: {URL}
- Models: {URL}
- Changelog: {URL}
- Support: {URL}

**✅ Last Review**: {Date} by {Maintainer}  
**⏭️ Next Review**: {Date (3 months from last review)}
