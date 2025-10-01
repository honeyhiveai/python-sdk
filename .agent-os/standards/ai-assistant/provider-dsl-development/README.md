# Provider DSL Development Framework v1.1

**Version**: 1.1  
**Date**: 2025-09-30  
**Status**: Active  
**Owner**: AI Assistant  
**Purpose**: Systematic framework for developing provider DSL files with verified accuracy

**Changelog**: v1.0 → v1.1
- ✅ Added compiler schema reference to Phase 4
- ✅ Added Phase 7.5 (Pre-Compilation Validation)
- ✅ Added intra-provider collision check to Phase 4.3
- ✅ Strengthened Phase 5 instrumentor isolation
- ✅ Created COMMON_PITFALLS.md document

---

## 🚨 **MANDATORY PREREQUISITE**

⚠️ **MUST-READ**: [`../.agent-os/standards/ai-assistant/command-language-glossary.md`](../command-language-glossary.md)

**Before executing this framework**, AI assistants MUST read the Command Language Glossary. This glossary defines binding commands used throughout this framework for:
- **Blocking checkpoints** (🛑 VALIDATE-GATE)
- **Evidence requirements** (📊 COUNT-AND-DOCUMENT)
- **Progress tracking** (🔄 UPDATE-TABLE)
- **Execution enforcement** (🛑 EXECUTE-NOW)

**🛑 BINDING**: All command language terms create non-negotiable obligations

---

## 🎯 **Framework Overview**

This framework provides a **systematic, evidence-based approach** for developing Universal LLM Discovery Engine provider DSL files. It prevents assumptions, ensures thorough research, and maintains quality through mandatory checkpoints.

**Inspired by**: V3 Test Generation Framework's phase-based approach with blocking checkpoints.

---

## 📋 **Framework Principles**

### **Core Principles**

1. **Evidence-Based**: Every field must be verified from primary sources
2. **No Assumptions**: If unverified, mark as "NEEDS VERIFICATION"
3. **Systematic Progress**: Complete each phase before advancing
4. **Blocking Checkpoints**: Cannot proceed without checkpoint validation
5. **Documentation-First**: Document sources before implementation
6. **Accuracy Over Speed**: Thoroughness is more important than fast completion

### **Quality Gates**

- ✅ **100% Source Verification**: All data traced to official sources
- ✅ **100% Instrumentor Validation**: Confirmed support, not assumed
- ✅ **100% Compilation**: DSL compiles without errors
- ✅ **100% Detection**: All instrumentors detect correctly
- ✅ **Current Data**: Pricing and models from 2025-09-30 or later

---

## 🔄 **Framework Phases**

### **Phase 0: Pre-Research Setup** (5-10 minutes)

**Objective**: Prepare for systematic research with clear documentation

**Tasks**:
1. Copy `RESEARCH_SOURCES_TEMPLATE.md` to provider directory
2. Fill in provider name and current date (YYYY-MM-DD)
3. Create evidence tracking table
4. Set up browser tabs for research

**Deliverables**:
- [ ] `RESEARCH_SOURCES.md` created in provider directory
- [ ] Date field set to current date
- [ ] Evidence table initialized

**Checkpoint**: Cannot proceed without RESEARCH_SOURCES.md file

---

### **Phase 1: Official Documentation Discovery** (15-30 minutes)

**Objective**: Locate and verify all official provider documentation

**🛑 BLOCKING CHECKPOINT**: Must find and verify ALL URLs before proceeding

#### **1.1: Find API Documentation**

**Search Patterns**:
- `{provider}.ai/docs`, `docs.{provider}.com`, `platform.{provider}.com/docs`
- `{provider}.com/documentation`, `api.{provider}.com/docs`
- GitHub: `github.com/{provider}` (look for docs links in README)

**Verification**:
- [ ] URL loads successfully
- [ ] Contains API reference/endpoints
- [ ] Dated 2024 or later (not outdated)
- [ ] Bookmark URL in browser

**Record in RESEARCH_SOURCES.md**:
```markdown
- **API Documentation**: {URL}
  - Last verified: {YYYY-MM-DD}
  - Notes: {What sections are available}
```

#### **1.2: Find Models Documentation**

**Search Patterns**:
- Look in API docs for "models", "capabilities", "available models"
- Check pricing page (often lists models)
- Try `{provider}/models`, `{provider}/docs/models`

**Verification**:
- [ ] Lists current model names
- [ ] Includes capabilities/descriptions
- [ ] Shows deprecation status
- [ ] Record ALL models (including legacy)

**Record in RESEARCH_SOURCES.md**:
```markdown
- **Models Overview**: {URL}
  - Last verified: {YYYY-MM-DD}
  - Model count: {number}
  - Legacy models included: {yes/no}
```

#### **1.3: Find Pricing Documentation**

**Search Patterns**:
- `{provider}.com/pricing`, `pricing.{provider}.com`
- API docs often have pricing section
- Blog posts announcing new models (often include pricing)

**Verification**:
- [ ] Shows per-token costs OR per-request costs
- [ ] Currency clearly stated (USD/EUR)
- [ ] Dated (if available)
- [ ] Includes ALL current models

**Record in RESEARCH_SOURCES.md**:
```markdown
- **Pricing**: {URL}
  - Last verified: {YYYY-MM-DD}
  - Currency: USD/EUR
  - Pricing structure: per-token / per-request / other
```

#### **1.4: Find Changelog/Release Notes**

**Search Patterns**:
- `{provider}/changelog`, `{provider}/docs/updates`, `{provider}/releases`
- GitHub releases: `github.com/{provider}/{repo}/releases`
- Blog: `{provider}.com/blog` (filter for model releases)

**Verification**:
- [ ] Recent updates (2024-2025)
- [ ] Model announcements
- [ ] API changes noted

**Record in RESEARCH_SOURCES.md**:
```markdown
- **Release Notes**: {URL}
  - Last verified: {YYYY-MM-DD}
  - Last update: {Date of most recent entry}
```

**📊 CHECKPOINT 1: Official Documentation Complete**

**Validation Criteria**:
- [ ] **MANDATORY**: API docs URL verified and working
- [ ] **MANDATORY**: Models list found (or noted as unavailable)
- [ ] **MANDATORY**: Pricing found (or noted as unavailable)
- [ ] Changelog found (or noted as unavailable)
- [ ] All URLs recorded in RESEARCH_SOURCES.md with verification dates
- [ ] **CHAT POST REQUIRED**: "✅ Phase 1 Complete: Official docs verified for {provider}"

**Cannot proceed to Phase 2 without completing this checkpoint!**

---

### **Phase 2: Instrumentor Support Verification** (30-45 minutes)

**Objective**: **VERIFY** (not assume!) which instrumentors support this provider

**🛑 BLOCKING CHECKPOINT**: Must verify actual code, not documentation claims

#### **2.1: Verify Traceloop/OpenLLMetry Support**

**Primary Check** (Most Reliable):
1. Navigate to: https://github.com/traceloop/openllmetry/tree/main/packages
2. **Look for**: `opentelemetry-instrumentation-{provider}` directory
3. If found → Open directory → Check `__init__.py` or instrumentor source
4. **Verify**: Actual attribute names used (e.g., `gen_ai.system = "provider"`)

**Secondary Check** (If not in packages):
1. Check: https://github.com/traceloop/openllmetry/blob/main/README.md
2. Look for provider in supported list
3. **Note**: Generic support (OpenAI-compatible) vs dedicated instrumentor

**Verification Evidence**:
```markdown
**Traceloop Support**: ✅ VERIFIED / ❌ NOT SUPPORTED / ⚠️ GENERIC

- **Package**: opentelemetry-instrumentation-{provider} (if exists)
- **Source**: {URL to actual code}
- **Attribute namespace**: gen_ai.* / other
- **Key attributes verified**:
  - gen_ai.system = "{value}"
  - gen_ai.request.model = "{field}"
  - {other key attributes from code}
- **Verification method**: Source code review
- **Last verified**: {YYYY-MM-DD}
```

#### **2.2: Verify OpenInference Support**

**Primary Check**:
1. Navigate to: https://github.com/Arize-ai/openinference/tree/main/python/instrumentation
2. **Look for**: Provider-specific directory OR generic LLM instrumentor
3. Check semantic conventions: https://github.com/Arize-ai/openinference/tree/main/spec

**Important Notes**:
- OpenInference often uses **generic LLM patterns** (`llm.*` namespace)
- May work with ANY provider via generic instrumentation
- Look for: `llm.provider` attribute with provider name as value

**Verification Evidence**:
```markdown
**OpenInference Support**: ✅ VERIFIED / ❌ NOT SUPPORTED / ⚠️ GENERIC

- **Type**: Provider-specific / Generic LLM
- **Source**: {URL to spec or instrumentor}
- **Attribute namespace**: llm.*
- **Key attributes verified**:
  - llm.provider = "{value}"
  - llm.model_name = "{field}"
  - {other key attributes from spec}
- **Verification method**: Spec review / Code review
- **Last verified**: {YYYY-MM-DD}
```

#### **2.3: Verify OpenLit Support**

**Primary Check**:
1. Navigate to: https://github.com/openlit/openlit/tree/main/sdk/python/src/openlit/instrumentation
2. **Look for**: Provider-specific directory (e.g., `mistralai/`, `cohere/`)
3. If found → Check `__init__.py` for attribute patterns

**Secondary Check**:
1. Check: https://docs.openlit.io/ for supported providers list
2. Look for: Provider in connections/integrations section

**Verification Evidence**:
```markdown
**OpenLit Support**: ✅ VERIFIED / ❌ NOT SUPPORTED / ⚠️ GENERIC

- **Directory**: {provider directory name} (if exists)
- **Source**: {URL to actual code}
- **Attribute namespace**: openlit.*
- **Key attributes verified**:
  - openlit.provider = "{value}"
  - openlit.model = "{field}"
  - {other key attributes from code}
- **Verification method**: Source code review
- **Last verified**: {YYYY-MM-DD}
```

#### **2.4: Document Direct SDK Patterns** (Optional)

**Check** (if provider has Python SDK):
1. Find: `github.com/{provider}/client-python` or similar
2. Look at: Response objects, trace examples
3. Note: Common attribute patterns for direct usage

**Verification Evidence**:
```markdown
**Direct SDK Support**: ✅ DOCUMENTED / ⚠️ NEEDS INVESTIGATION

- **SDK Repository**: {URL}
- **Version checked**: {version}
- **Namespace pattern**: {provider}.* or custom
- **Last verified**: {YYYY-MM-DD}
```

**📊 CHECKPOINT 2: Instrumentor Support Verified**

**Validation Criteria**:
- [ ] **MANDATORY**: Traceloop support VERIFIED (code reviewed, not assumed)
- [ ] **MANDATORY**: OpenInference support VERIFIED (spec reviewed, not assumed)  
- [ ] **MANDATORY**: OpenLit support VERIFIED (code reviewed, not assumed)
- [ ] Direct SDK patterns documented (or marked as optional)
- [ ] Evidence recorded in RESEARCH_SOURCES.md with source URLs
- [ ] Attribute patterns captured from actual code
- [ ] **CHAT POST REQUIRED**: "✅ Phase 2 Complete: Instrumentor support verified - {count}/3 supported"

**❌ If provider not supported by any instrumentor**: Document why and mark provider as "future support only"

**Cannot proceed to Phase 3 without completing this checkpoint!**

---

### **Phase 3: Model & Pricing Data Collection** (20-30 minutes)

**Objective**: Collect verified, current model and pricing data

**🛑 BLOCKING CHECKPOINT**: Must have current data (2025-09-30 or later)

#### **3.1: Collect Model List**

**Data Collection**:
1. Open models documentation page from Phase 1
2. Create table of ALL models (including deprecated/legacy)
3. For each model, record:
   - Exact model identifier (e.g., `gpt-4o`, `claude-3-5-sonnet-20241022`)
   - Model family/tier (flagship, mid-tier, budget, specialty)
   - Capabilities (text, vision, code, embeddings, etc.)
   - Deprecation status
   - Context window (if available)

**Model Table Format**:
```markdown
### Current Models (as of {YYYY-MM-DD})

**Flagship Models**:
- `{model-id}` - {Description, capabilities, context window}
- `{model-id-variant}` - {Variant description}

**Mid-Tier Models**:
- `{model-id}` - {Description}

**Budget Models**:
- `{model-id}` - {Description}

**Specialty Models** (Code/Vision/Embeddings):
- `{model-id}` - {Description, specialty}

**Legacy/Deprecated Models** (for backward compatibility):
- `{model-id}` - {Description, deprecation date if known}

**Source**: {URL where this list was found}
**Verified**: {YYYY-MM-DD}
```

#### **3.2: Collect Pricing Data**

**Data Collection**:
1. Open pricing page from Phase 1
2. Record pricing structure (per-token, per-request, tiered, etc.)
3. For each model, record:
   - Input cost (per 1M tokens or per request)
   - Output cost (per 1M tokens or per request)
   - Currency (USD, EUR, etc.)
   - Special cases (batch discounts, caching, etc.)

**Pricing Table Format**:
```markdown
### Pricing Information (as of {YYYY-MM-DD})

**Pricing Structure**: ☑️ Per million tokens / Per request / Tiered / Other

**Currency**: USD / EUR

| Model | Input Cost | Output Cost | Unit | Notes |
|-------|------------|-------------|------|-------|
| `{model-1}` | ${X.XX} | ${Y.YY} | per 1M tokens | {special notes} |
| `{model-2}` | ${X.XX} | ${Y.YY} | per 1M tokens | |

**Special Pricing Cases**:
- Batch API: {Discount if applicable}
- Cached prompts: {Discount if applicable}
- Fine-tuned models: {Pricing structure}
- Enterprise tiers: {Different pricing if applicable}

**Source**: {URL where pricing was found}
**Verified**: {YYYY-MM-DD}
```

#### **3.3: Identify Provider-Specific Features**

**Research**:
1. Look for unique features in API docs
2. Compare to OpenAI (baseline) - what's different?
3. Note unique parameters or capabilities

**Features to Check**:
- [ ] Function calling / tool use (how it works)
- [ ] JSON mode / structured outputs
- [ ] Streaming (any unique aspects)
- [ ] Safety/moderation features
- [ ] Multimodal capabilities (vision, audio, etc.)
- [ ] Unique parameters (e.g., Anthropic's `top_k`)
- [ ] Regional/compliance features (EU data residency, etc.)

**Documentation Format**:
```markdown
### Provider-Specific Features

**Unique Parameters**:
- `{parameter-name}`: {Description, which models, example values}
  - Default: {value}
  - Appears in traces as: {attribute name}

**Unique Capabilities**:
- {Feature name}: {Description, how it differs from other providers}

**Compliance/Regional**:
- {Feature}: {Description if applicable}
```

**📊 CHECKPOINT 3: Data Collection Complete**

**Validation Criteria**:
- [ ] **MANDATORY**: Model list complete (10+ models typical, or ALL available)
- [ ] **MANDATORY**: Pricing table complete for ALL current models
- [ ] **MANDATORY**: Verification date is 2025-09-30 or later
- [ ] Currency clearly stated
- [ ] Source URLs documented
- [ ] Provider-specific features identified
- [ ] Legacy models included for backward compatibility
- [ ] **CHAT POST REQUIRED**: "✅ Phase 3 Complete: {count} models documented, pricing verified"

**Cannot proceed to Phase 4 without completing this checkpoint!**

---

### **Phase 4: Structure Patterns Development** (30-45 minutes)

**Objective**: Create detection patterns based on verified instrumentor data

**🛑 BLOCKING CHECKPOINT**: Must use ONLY verified attributes from Phase 2

#### **4.1: Design Detection Strategy**

**Analysis**:
1. Review verified instrumentor support from Phase 2
2. Identify unique signature fields (fields that ONLY this provider has)
3. Design 3-6 patterns covering supported instrumentors
4. Set confidence weights based on signature uniqueness

**Uniqueness Check**:
- Compare to existing providers (OpenAI, Anthropic, Gemini)
- Ensure required_fields are NOT shared with other providers
- Use provider-specific values (e.g., `llm.provider = "mistral"`)

#### **4.2: Create Pattern Definitions**

**For Each Instrumentor** (that has verified support):

```yaml
{instrumentor}_{provider}:
  required_fields:
    - "{field.from.verified.source}"  # Must be from Phase 2 evidence
    - "{field.from.verified.source}"
    - "{field.from.verified.source}"
  optional_fields:
    - "{field.from.verified.source}"
  confidence_weight: 0.XX  # Based on uniqueness
  description: "{Provider} via {Instrumentor} instrumentation"
  instrumentor_framework: "{instrumentor}"
```

**Confidence Weight Guidelines**:
- **0.95-0.98**: Highly unique signature with provider name in attributes
- **0.90-0.94**: Unique combination with clear provider indicators
- **0.85-0.89**: Less unique, relies on multiple fields
- **0.80-0.84**: Generic pattern, may overlap with others

#### **4.3: Validate Pattern Uniqueness**

**Check Against Existing Providers**:
```bash
# Search for potential collisions
grep -r "required_fields" config/dsl/providers/*/structure_patterns.yaml
```

**Validation**:
- [ ] No exact match with other providers
- [ ] required_fields are truly provider-specific
- [ ] Confidence weights appropriate for uniqueness
- [ ] All instrumentors from Phase 2 covered (or marked as unsupported)

**📊 CHECKPOINT 4: Structure Patterns Complete**

**Validation Criteria**:
- [ ] **MANDATORY**: 3-6 patterns created (one per verified instrumentor minimum)
- [ ] **MANDATORY**: All attributes verified from Phase 2 sources
- [ ] No assumptions - only verified fields used
- [ ] Confidence weights set and justified
- [ ] Pattern uniqueness validated
- [ ] File compiles: `python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/structure_patterns.yaml'))"`
- [ ] **CHAT POST REQUIRED**: "✅ Phase 4 Complete: {count} patterns created with verified attributes"

**Cannot proceed to Phase 5 without completing this checkpoint!**

---

### **Phase 5: Navigation Rules Development** (45-60 minutes)

**Objective**: Create extraction rules for ALL verified instrumentors

**🛑 BLOCKING CHECKPOINT**: Must create rules for EACH verified instrumentor

#### **5.1: Plan Navigation Rules**

**For Each Instrumentor** (with verified support):
1. List required fields for extraction (model, tokens, messages, etc.)
2. Map to verified attribute names from Phase 2
3. Determine extraction method (direct_copy, array_flatten, etc.)
4. Set fallback values (safe defaults)

**Rule Naming Convention**: `{instrumentor}_{field_name}`
- Traceloop: `traceloop_model_name`, `traceloop_prompt_tokens`
- OpenInference: `openinference_model_name`, `openinference_input_messages`
- OpenLit: `openlit_model_name`, `openlit_usage_prompt_tokens`

#### **5.2: Create Rules for Each Instrumentor**

**Minimum Required Rules** (per instrumentor):
- [ ] `{instrumentor}_model_name` - Model identifier
- [ ] `{instrumentor}_input_messages` OR `{instrumentor}_prompt` - Input
- [ ] `{instrumentor}_output_messages` OR `{instrumentor}_completion` - Output
- [ ] `{instrumentor}_prompt_tokens` - Input token count
- [ ] `{instrumentor}_completion_tokens` - Output token count
- [ ] `{instrumentor}_temperature` - Temperature parameter
- [ ] `{instrumentor}_max_tokens` - Max tokens parameter

**Additional Rules** (as applicable):
- [ ] `{instrumentor}_top_p` - Top-p sampling
- [ ] `{instrumentor}_finish_reason` - Completion reason
- [ ] `{instrumentor}_tool_calls` - Function calls (if supported)
- [ ] Provider-specific fields from Phase 3

**Format**:
```yaml
{instrumentor}_{field_name}:
  source_field: "{verified.attribute.path}"  # From Phase 2
  extraction_method: "direct_copy"  # or array_flatten, object_merge, etc.
  fallback_value: {safe default}
  validation: "non_empty_string"  # or positive_number, array_of_objects, etc.
  description: "Extract {field} from {Instrumentor}"
```

#### **5.3: Validate Coverage**

**Coverage Check**:
```bash
# Count rules per instrumentor
grep "traceloop_" config/dsl/providers/{provider}/navigation_rules.yaml | wc -l
grep "openinference_" config/dsl/providers/{provider}/navigation_rules.yaml | wc -l
grep "openlit_" config/dsl/providers/{provider}/navigation_rules.yaml | wc -l
```

**Expected**: 7-10 rules per instrumentor minimum

**📊 CHECKPOINT 5: Navigation Rules Complete**

**Validation Criteria**:
- [ ] **MANDATORY**: Rules created for ALL verified instrumentors from Phase 2
- [ ] **MANDATORY**: Minimum 7 rules per instrumentor (model, tokens, messages, params)
- [ ] All source_field paths verified from Phase 2 evidence
- [ ] Safe fallback values for all fields
- [ ] Appropriate validation rules
- [ ] Descriptive names and descriptions
- [ ] File compiles: `python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/navigation_rules.yaml'))"`
- [ ] **CHAT POST REQUIRED**: "✅ Phase 5 Complete: {count} navigation rules created across {count} instrumentors"

**Cannot proceed to Phase 6 without completing this checkpoint!**

---

### **Phase 6: Field Mappings Development** (30-45 minutes)

**Objective**: Map extracted data to HoneyHive 4-section schema

**🛑 BLOCKING CHECKPOINT**: Must use base rule names (no instrumentor prefixes!)

#### **6.1: Plan Field Mappings**

**HoneyHive Schema Sections**:
1. **inputs**: User inputs, prompts, chat history, context
2. **outputs**: Model responses, completions, tool calls, results
3. **config**: Model parameters, temperature, max_tokens, settings
4. **metadata**: Usage metrics, provider info, costs, timestamps

**Mapping Strategy**:
- Use **base rule names** (without instrumentor prefix) for automatic routing
- Example: `model_name` NOT `traceloop_model_name`
- Compiler will generate routing code: tries all instrumentor variants

#### **6.2: Create Field Mappings**

**Inputs Section**:
```yaml
inputs:
  chat_history:
    source_rule: "input_messages"  # Base name! Router handles instrumentor selection
    required: false
    description: "{Provider} input message array"
  
  prompt:
    source_rule: "user_prompt"  # Will map to transform function
    required: false
    description: "User prompt text"
  
  system_message:
    source_rule: "system_prompt"
    required: false
    description: "System message content"
```

**Outputs Section**:
```yaml
outputs:
  response:
    source_rule: "output_messages"  # Base name
    required: false
    description: "{Provider} response message array"
  
  completion:
    source_rule: "completion_text"  # Will map to transform
    required: false
    description: "Completion text content"
  
  tool_calls:
    source_rule: "tool_calls"
    required: false
    description: "Function/tool call results"
  
  finish_reason:
    source_rule: "finish_reason_normalized"  # Will map to transform
    required: false
    description: "Completion finish reason"
```

**Config Section**:
```yaml
config:
  model:
    source_rule: "model_name"  # Base name - REQUIRED!
    required: true
    description: "{Provider} model identifier"
  
  temperature:
    source_rule: "temperature"
    required: false
    description: "Model temperature setting"
  
  max_tokens:
    source_rule: "max_tokens"
    required: false
    description: "Maximum token limit"
  
  top_p:
    source_rule: "top_p"
    required: false
    description: "Top-p sampling parameter"
  
  # Add provider-specific config fields from Phase 3
```

**Metadata Section**:
```yaml
metadata:
  provider:
    source_rule: "static_{provider}"  # Static value
    required: true
    description: "Provider identifier"
  
  instrumentor:
    source_rule: "detect_instrumentor"  # Dynamic detection
    required: false
    description: "Instrumentor framework used"
  
  prompt_tokens:
    source_rule: "prompt_tokens"
    required: false
    description: "Input token count"
  
  completion_tokens:
    source_rule: "completion_tokens"
    required: false
    description: "Output token count"
  
  total_tokens:
    source_rule: "total_tokens"
    required: false
    description: "Total token usage"
  
  cost:
    source_rule: "calculate_{provider}_cost"  # Will map to transform
    required: false
    description: "Request cost in USD"
```

**📊 CHECKPOINT 6: Field Mappings Complete**

**Validation Criteria**:
- [ ] **MANDATORY**: All 4 sections populated (inputs, outputs, config, metadata)
- [ ] **MANDATORY**: `model` marked as `required: true`
- [ ] **MANDATORY**: `provider` marked as `required: true`
- [ ] **CRITICAL**: Base rule names used (NO instrumentor prefixes!)
- [ ] All source_rules map to navigation rules or transforms
- [ ] Descriptions provided for all fields
- [ ] Provider-specific fields from Phase 3 included
- [ ] File compiles: `python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/field_mappings.yaml'))"`
- [ ] **CHAT POST REQUIRED**: "✅ Phase 6 Complete: 4-section schema mapped with base rule names"

**Cannot proceed to Phase 7 without completing this checkpoint!**

---

### **Phase 7: Transforms Development** (45-60 minutes)

**Objective**: Create transformation functions with CURRENT pricing

**🛑 BLOCKING CHECKPOINT**: Pricing must be from 2025-09-30 or later

#### **7.1: Plan Transform Functions**

**Required Transforms**:
- [ ] `extract_user_prompt` - Extract user messages
- [ ] `extract_system_prompt` - Extract system messages
- [ ] `extract_completion_text` - Extract assistant messages
- [ ] `extract_finish_reason_normalized` - Normalize finish reason
- [ ] `calculate_{provider}_cost` - Calculate cost with CURRENT pricing
- [ ] `detect_instrumentor` - Detect which instrumentor (standard)

**Optional Transforms** (as needed):
- [ ] `extract_tool_calls` - Extract function calls
- [ ] `extract_request_identifier` - Extract request ID
- [ ] Custom transforms for provider-specific features

#### **7.2: Create Message Extraction Transforms**

**Standard Message Extractions**:
```yaml
extract_user_prompt:
  function_type: "extract_message_content_by_role"
  implementation: "python_code_generated_at_build_time"
  parameters:
    role: "user"
    messages_field: "chat_history"
    separator: "\n\n"
  description: "Extract user prompt from {provider} messages"

extract_system_prompt:
  function_type: "extract_message_content_by_role"
  implementation: "python_code_generated_at_build_time"
  parameters:
    role: "system"
    messages_field: "chat_history"
    separator: ""
  description: "Extract system message from {provider} messages"

extract_completion_text:
  function_type: "extract_message_content_by_role"
  implementation: "python_code_generated_at_build_time"
  parameters:
    role: "assistant"
    messages_field: "response"
    separator: "\n"
  description: "Extract completion text from {provider} response"
```

#### **7.3: Create Finish Reason Normalization**

**Provider-Specific Mapping** (verify from docs!):
```yaml
extract_finish_reason_normalized:
  function_type: "normalize_finish_reason"
  implementation: "python_code_generated_at_build_time"
  parameters:
    source_field: "finish_reason"
    mapping:
      "stop": "complete"
      "length": "max_tokens"
      "tool_calls": "function_call"
      "content_filter": "filtered"
      # Add provider-specific values from docs
  description: "Normalize {provider} finish reason to standard values"
```

**⚠️ CRITICAL**: Verify finish reason values from provider API docs!

#### **7.4: Create Cost Calculation**

**⚠️ MOST CRITICAL TRANSFORM**: Must use CURRENT pricing from Phase 3!

```yaml
calculate_{provider}_cost:
  function_type: "calculate_{provider}_cost"
  implementation: "python_code_generated_at_build_time"
  parameters:
    model_field: "model"
    prompt_tokens_field: "prompt_tokens"
    completion_tokens_field: "completion_tokens"
    pricing_table:
      # ⚠️ CRITICAL: Use EXACT pricing from Phase 3 (verified 2025-09-30)
      "{model-1}":
        input: 0.00XXX  # Per 1M tokens in USD
        output: 0.00YYY
      "{model-2}":
        input: 0.00XXX
        output: 0.00YYY
      # ... ALL models from Phase 3
  description: "Calculate request cost using current {provider} pricing (verified {YYYY-MM-DD})"
```

**Validation**:
- [ ] **MANDATORY**: Pricing matches Phase 3 data EXACTLY
- [ ] ALL current models included
- [ ] Legacy models included for backward compatibility
- [ ] Verification date in description
- [ ] Currency consistent (USD)

#### **7.5: Create Instrumentor Detection** (Standard)

```yaml
detect_instrumentor:
  function_type: "detect_instrumentor"
  implementation: "python_code_generated_at_build_time"
  parameters:
    attribute_patterns:
      "traceloop": ["gen_ai.system", "gen_ai.request.model"]
      "openinference": ["llm.provider", "llm.model_name"]
      "openlit": ["openlit.provider", "openlit.model"]
      # Only include verified instrumentors from Phase 2
  description: "Detect which instrumentor framework is being used"
```

**📊 CHECKPOINT 7: Transforms Complete**

**Validation Criteria**:
- [ ] **MANDATORY**: All required transforms created (message extraction, finish reason, cost, instrumentor)
- [ ] **MANDATORY**: Pricing table matches Phase 3 data EXACTLY
- [ ] **MANDATORY**: Pricing verification date in description
- [ ] ALL current models in pricing table
- [ ] Legacy models included
- [ ] Finish reason mapping verified from docs
- [ ] Only verified instrumentors in detect_instrumentor
- [ ] File compiles: `python -c "import yaml; yaml.safe_load(open('config/dsl/providers/{provider}/transforms.yaml'))"`
- [ ] **CHAT POST REQUIRED**: "✅ Phase 7 Complete: {count} transforms with verified pricing (as of {date})"

**Cannot proceed to Phase 8 without completing this checkpoint!**

---

### **Phase 8: Compilation & Validation** (15-30 minutes)

**Objective**: Compile DSL and validate all functionality

**🛑 BLOCKING CHECKPOINT**: Must achieve 100% compilation and detection success

#### **8.1: Compile Provider Bundle**

**Compilation**:
```bash
cd /Users/josh/src/github.com/honeyhiveai/python-sdk
python -m config.dsl.compiler
```

**Expected Output**:
```
✅ Successfully compiled provider bundle
📊 Providers: {count}
⚡ Patterns: {count}
```

**Validation**:
- [ ] Compilation succeeds without errors
- [ ] No YAML syntax errors
- [ ] No schema validation errors
- [ ] Bundle size reasonable (<30KB per provider)

#### **8.2: Test Provider Detection**

**For Each Verified Instrumentor**:

Create test data (minimal example):
```python
# Traceloop test data (if verified in Phase 2)
traceloop_attrs = {
    "gen_ai.system": "{provider_value}",
    "gen_ai.request.model": "{model_name}",
    "gen_ai.usage.prompt_tokens": 10,
}

# OpenInference test data (if verified in Phase 2)
openinference_attrs = {
    "llm.provider": "{provider_value}",
    "llm.model_name": "{model_name}",
    "llm.token_count.prompt": 10,
}

# OpenLit test data (if verified in Phase 2)
openlit_attrs = {
    "openlit.provider": "{provider_value}",
    "openlit.model": "{model_name}",
    "openlit.usage.prompt_tokens": 10,
}
```

**Run Detection Test**:
```bash
python -c "
from honeyhive.tracer.processing.semantic_conventions.provider_processor import UniversalProviderProcessor

processor = UniversalProviderProcessor(tracer_instance=None)

# Test each instrumentor
test_cases = {
    'Traceloop': {test_data},
    'OpenInference': {test_data},
    'OpenLit': {test_data},
}

for name, attrs in test_cases.items():
    instrumentor, provider = processor._detect_instrumentor_and_provider(attrs)
    print(f'{name}: [{instrumentor}, {provider}]')
"
```

**Expected Output**:
```
Traceloop: [traceloop, {provider}]
OpenInference: [openinference, {provider}]
OpenLit: [openlit, {provider}]
```

**Validation**:
- [ ] All verified instrumentors detect correctly
- [ ] Provider name matches expected
- [ ] No "unknown" for verified instrumentors

#### **8.3: Test Extraction**

**Add to test_two_tier_extraction.py**:
```python
# {Provider} + {Instrumentor} scenario
{instrumentor}_{provider}_attrs = {
    # Full attribute set with all fields
}
results.append(test_scenario(
    "{Instrumentor} + {Provider}",
    {instrumentor}_{provider}_attrs,
    "{instrumentor}",
    "{provider}"
))
```

**Run Extraction Test**:
```bash
python scripts/test_two_tier_extraction.py
```

**Validation**:
- [ ] All verified instrumentor scenarios PASS
- [ ] Fields populate correctly (not None/empty)
- [ ] Cost calculation returns reasonable value
- [ ] Model field populated
- [ ] Metadata instrumentor correct

#### **8.4: Performance Validation**

**Run Profiler**:
```bash
python scripts/profile_universal_engine.py
```

**Validation**:
- [ ] Provider detection < 0.1ms
- [ ] Span processing < 0.1ms
- [ ] Bundle size reasonable
- [ ] No performance regression

**📊 CHECKPOINT 8: Compilation & Validation Complete**

**Validation Criteria**:
- [ ] **MANDATORY**: Bundle compiles without errors
- [ ] **MANDATORY**: All verified instrumentors detect correctly (100% success rate)
- [ ] **MANDATORY**: Extraction returns populated fields (not None/empty)
- [ ] Cost calculation works (returns number > 0)
- [ ] Performance targets met (<0.1ms)
- [ ] No errors in compilation or testing
- [ ] **CHAT POST REQUIRED**: "✅ Phase 8 Complete: {provider} compiled and validated - {count}/{count} instrumentors passing"

**Cannot proceed to Phase 9 without completing this checkpoint!**

---

### **Phase 9: Documentation Finalization** (15-20 minutes)

**Objective**: Complete RESEARCH_SOURCES.md with all verification evidence

#### **9.1: Update Implementation Details**

**Fill in actual counts**:
```markdown
## 🔧 **Implementation Details**

### **Structure Patterns**
- **Number of patterns**: {actual count}
- **Instrumentors covered**: {list verified instrumentors}
- **Unique signature fields**: {list unique fields}
- **Confidence weights**: {range used}
- **Collision risk**: {assessment}

### **Navigation Rules**
- **Total rules**: {actual count}
- **Instrumentor coverage**: {breakdown per instrumentor}
- **Provider-specific fields**: {list unique fields}

### **Field Mappings**
- **HoneyHive schema**: ✅ All 4 sections
- **Required fields**: model, provider
- **Optional fields**: {count}

### **Transforms**
- **Total transforms**: {actual count}
- **Cost calculation**: ✅ Implemented with {count} model variants
- **Message extraction**: ✅ User, assistant, system
- **Finish reason normalization**: ✅ {count} mappings
```

#### **9.2: Mark Verification Complete**

**Update status fields**:
```markdown
**✅ Last Review**: 2025-09-30 by AI Assistant  
**⏭️ Next Review**: 2025-12-30 (3 months)  
**🚀 Status**: **COMPLETE - PRODUCTION READY**
```

**Remove all "NEEDS VERIFICATION" markers**:
- Replace with actual data
- Or mark as "Not Applicable" if truly unavailable

#### **9.3: Add Testing Notes**

**Document test results**:
```markdown
## ✅ **Validation Results**

**Compilation**: ✅ Success  
**Detection Tests**: ✅ {count}/{count} instrumentors passing  
**Extraction Tests**: ✅ All fields populating  
**Cost Calculation**: ✅ Verified accurate  
**Performance**: ✅ < 0.1ms processing  

**Test Date**: 2025-09-30  
**Tested By**: AI Assistant
```

**📊 CHECKPOINT 9: Documentation Complete**

**Validation Criteria**:
- [ ] **MANDATORY**: All "NEEDS VERIFICATION" removed or justified
- [ ] Implementation Details filled with actual counts
- [ ] Status updated to "COMPLETE"
- [ ] Validation results documented
- [ ] All URLs verified and dated
- [ ] No placeholders remaining
- [ ] **CHAT POST REQUIRED**: "✅ Phase 9 Complete: RESEARCH_SOURCES.md finalized"

---

## 📊 **Progress Tracking**

### **Evidence-Based Progress Table**

Update after each checkpoint:

| Phase | Status | Evidence | Verified | Notes |
|-------|--------|----------|----------|-------|
| 0: Setup | ⏳ / ✅ | RESEARCH_SOURCES.md exists | Y/N | |
| 1: Official Docs | ⏳ / ✅ | URLs verified | Y/N | {count} URLs |
| 2: Instrumentor Support | ⏳ / ✅ | Code reviewed | Y/N | {count}/3 verified |
| 3: Model/Pricing | ⏳ / ✅ | Data current | Y/N | {count} models |
| 4: Structure Patterns | ⏳ / ✅ | Patterns created | Y/N | {count} patterns |
| 5: Navigation Rules | ⏳ / ✅ | Rules created | Y/N | {count} rules |
| 6: Field Mappings | ⏳ / ✅ | Schema mapped | Y/N | 4 sections |
| 7: Transforms | ⏳ / ✅ | Pricing verified | Y/N | {count} transforms |
| 8: Validation | ⏳ / ✅ | Tests passing | Y/N | {count}/{count} pass |
| 9: Documentation | ⏳ / ✅ | Docs complete | Y/N | Status: COMPLETE |

**Legend**: ⏳ Pending | 🔄 In Progress | ✅ Complete

---

## ⚠️ **Common Mistakes to Avoid**

Based on lessons learned:

1. **❌ NEVER Assume Instrumentor Support**
   - ✅ ALWAYS verify in actual code repositories
   - ✅ Check source code, not just documentation

2. **❌ NEVER Use Placeholder Pricing**
   - ✅ ALWAYS verify current pricing from official sources
   - ✅ Include verification date

3. **❌ NEVER Skip Verification Steps**
   - ✅ Complete each checkpoint before advancing
   - ✅ Evidence-based progress only

4. **❌ NEVER Use Outdated Data**
   - ✅ Verify data is from 2025-09-30 or later
   - ✅ Check changelog for recent updates

5. **❌ NEVER Leave "NEEDS VERIFICATION"**
   - ✅ Either verify or mark as "Not Available"
   - ✅ No ambiguity in final docs

---

## 🎯 **Success Criteria**

**Provider DSL is COMPLETE when**:

- ✅ All 9 phases completed with checkpoint validation
- ✅ 100% source verification (no assumptions)
- ✅ 100% instrumentor verification (code reviewed)
- ✅ 100% compilation success
- ✅ 100% detection tests passing (all verified instrumentors)
- ✅ Extraction returns populated fields
- ✅ Current pricing (2025-09-30 or later)
- ✅ RESEARCH_SOURCES.md complete (no "NEEDS VERIFICATION")
- ✅ Performance targets met (<0.1ms)
- ✅ Documentation status: COMPLETE

---

## 📚 **ADDITIONAL RESOURCES**

### **Essential Documents**

- **[COMMON_PITFALLS.md](COMMON_PITFALLS.md)** - Common errors and how to avoid them
- **[RESEARCH_SOURCES_TEMPLATE.md](../../config/dsl/providers/RESEARCH_SOURCES_TEMPLATE.md)** - Template for provider research
- **[DSL_REFERENCE.md](../../config/dsl/DSL_REFERENCE.md)** - Complete DSL specification
- **[Command Language Glossary](../command-language-glossary.md)** - Framework command definitions

### **Retrospectives**

- **[Mistral AI Implementation](RETROSPECTIVE-MISTRAL-AI-2025-09-30.md)** - First execution learnings (v1.0 → v1.1)

### **Framework Design**

- **[LLM Workflow Engineering Methodology](../LLM-WORKFLOW-ENGINEERING-METHODOLOGY.md)** - Theoretical foundation
- **[Framework Design Guide](../framework-design-guide.md)** - How to build frameworks
- **[Framework Design Patterns](../framework-design-patterns.md)** - Reusable patterns

---

**🚀 This framework ensures systematic, verified, high-quality provider DSL development!**
