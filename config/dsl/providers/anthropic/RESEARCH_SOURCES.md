# Anthropic Provider Research Sources

**Provider**: Anthropic  
**Last Updated**: 2025-09-29  
**Version**: 1.0  

## 📋 **Research Sources Used**

### **Official Anthropic Documentation**
- **Anthropic API Documentation**: https://docs.anthropic.com/claude/reference/
- **Claude Models Overview**: https://docs.anthropic.com/claude/docs/models-overview
- **Anthropic Pricing**: https://www.anthropic.com/pricing
- **Claude API Reference**: https://docs.anthropic.com/claude/reference/messages

### **Semantic Convention Standards**
- **OpenInference Semantic Conventions**: https://github.com/Arize-ai/openinference
  - Version: 0.1.15+
  - Attributes: `llm.*` namespace
  - Key patterns: `llm.model_name`, `llm.input_messages`, `llm.invocation_parameters.top_k`
  
- **Traceloop OpenLLMetry**: https://github.com/traceloop/openllmetry
  - Version: 0.46.2+
  - Attributes: `gen_ai.*` namespace
  - Key patterns: `gen_ai.request.model`, `gen_ai.completion`, `gen_ai.system`

- **Direct Anthropic SDK Patterns**:
  - Based on Anthropic Python SDK v0.x
  - Custom attributes: `anthropic.*` namespace
  - Patterns derived from SDK response structure

- **LangChain Integration**:
  - LangChain Anthropic integration patterns
  - Attributes: `langchain.llm.*` namespace
  - Version compatibility: 0.1.0+

- **Haystack Integration**:
  - Haystack Anthropic component patterns
  - Attributes: `haystack.anthropic.*` namespace
  - Version compatibility: 2.0.0+

### **Model Information Sources**
- **Current Models (as of 2025-09-29)**:
  - Claude 3.5 Sonnet: `claude-3-5-sonnet-20241022`, `claude-3-5-sonnet-20240620`
  - Claude 3.5 Haiku: `claude-3-5-haiku-20241022`
  - Claude 3 Opus: `claude-3-opus-20240229`
  - Claude 3 Sonnet: `claude-3-sonnet-20240229`
  - Claude 3 Haiku: `claude-3-haiku-20240307`
  - Legacy: `claude-2.1`, `claude-2.0`, `claude-instant-1.2`

### **Pricing Information Sources**
- **Official Anthropic Pricing Page**: Verified 2025-09-29
- **Pricing per 1M tokens (USD)**:
  - Claude 3.5 Sonnet: $3.00 input / $15.00 output
  - Claude 3.5 Haiku: $0.80 input / $4.00 output
  - Claude 3 Opus: $15.00 input / $75.00 output
  - Claude 3 Sonnet: $3.00 input / $15.00 output
  - Claude 3 Haiku: $0.25 input / $1.25 output

### **Anthropic-Specific Features**
- **Top-k sampling**: Unique to Claude models
- **System messages**: Enhanced system instruction support
- **Safety settings**: Content filtering and safety controls
- **Tool use**: Function calling capabilities
- **Message format**: Role-based conversation structure

## 🔧 **Implementation Details**

### **Structure Patterns**
- **6 detection patterns** covering major instrumentors
- **Unique signature**: Uses `llm.invocation_parameters.top_k` for differentiation
- **Confidence weights**: 0.75-0.98 based on instrumentor type

### **Navigation Rules**
- **30+ extraction rules** for comprehensive data mapping
- **Multi-instrumentor support**: OpenInference, Traceloop, Direct, LangChain, Haystack
- **Claude-specific fields**: top_k, safety_settings, system instructions

### **Field Mappings**
- **HoneyHive 4-section schema**: inputs, outputs, config, metadata
- **Required fields**: model (config), provider (metadata)
- **Claude-specific config**: top_k, safety_settings

### **Transforms**
- **12 transformation functions** for data processing
- **Cost calculation**: Current pricing table with 15+ model variants
- **Finish reason mapping**: Claude-specific completion reasons

## 🔄 **Update Procedures**

### **When to Update**
1. **New Claude models released**
2. **Pricing changes announced**
3. **Semantic convention updates**
4. **SDK version changes**
5. **New integration frameworks**

### **Update Checklist**
- [ ] Check Anthropic model documentation for new models
- [ ] Verify current pricing on official pricing page
- [ ] Update `structure_patterns.yaml` with new model patterns
- [ ] Update `transforms.yaml` pricing table
- [ ] Check for new Claude-specific parameters
- [ ] Test compilation and validation
- [ ] Update this documentation with sources and dates

### **Key Files to Update**
1. `structure_patterns.yaml` - Add new model patterns and instrumentors
2. `navigation_rules.yaml` - Add new SDK attribute patterns
3. `field_mappings.yaml` - Adjust mappings for new features
4. `transforms.yaml` - Update pricing table and model list
5. `RESEARCH_SOURCES.md` - Update documentation

## 📚 **Additional References**

### **Community Resources**
- **Anthropic Discord**: Developer community discussions
- **Anthropic Support**: https://support.anthropic.com/
- **Claude API Cookbook**: https://github.com/anthropics/anthropic-cookbook

### **Integration Examples**
- **Anthropic Python SDK**: https://github.com/anthropics/anthropic-sdk-python
- **LangChain Anthropic**: https://python.langchain.com/docs/integrations/llms/anthropic
- **Haystack Anthropic**: https://haystack.deepset.ai/integrations/anthropic

### **Monitoring Sources**
- **Anthropic Status**: https://status.anthropic.com/
- **Anthropic Blog**: https://www.anthropic.com/news (for announcements)
- **Anthropic Twitter**: @AnthropicAI (for updates)

### **Research Papers**
- **Constitutional AI**: Anthropic's safety research
- **Claude model papers**: Technical specifications and capabilities
- **Safety and alignment research**: Anthropic's research publications

## 🎯 **Claude-Specific Considerations**

### **Unique Parameters**
- **top_k**: Sampling parameter unique to Claude
- **system**: Enhanced system message support
- **stop_sequences**: Custom stop sequence support
- **max_tokens_to_sample**: Claude-specific token limiting

### **Safety Features**
- **Content filtering**: Built-in safety mechanisms
- **Harm categories**: Specific safety classifications
- **Constitutional AI**: Self-correction capabilities

### **Message Format**
- **Role structure**: human, assistant, system roles
- **Content types**: Text and structured content support
- **Tool use**: Function calling with specific format

---

**📝 Notes for Future Updates**:
- Monitor Anthropic's research publications for new capabilities
- Check for updates to Constitutional AI features
- Verify compatibility with new integration frameworks
- Test safety feature changes that might affect attribute extraction
