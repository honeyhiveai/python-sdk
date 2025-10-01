Universal LLM Discovery Engine v4.0
====================================

.. note::
   **For HoneyHive SDK Developers**
   
   This guide covers the internal Universal LLM Discovery Engine architecture, DSL system, and provider development workflow. This is for SDK maintainers and contributors working on the semantic convention processing system.

Overview
--------

The Universal LLM Discovery Engine v4.0 is the core system that automatically detects and processes LLM provider spans from any instrumentor (Traceloop, OpenInference, OpenLit) with **O(1) performance** using a provider-isolated DSL architecture and build-time compilation.

**Key Features:**

- ✅ **O(1) Provider Detection**: Hash-based detection using frozenset signatures
- ✅ **Universal Instrumentor Support**: Works with Traceloop, OpenInference, OpenLit, and direct OTel
- ✅ **Two-Tier Architecture**: Separate instrumentor and provider detection
- ✅ **Build-Time Compilation**: YAML DSL compiled to optimized Python code
- ✅ **AI-Friendly Development**: Provider-isolated files for parallel development
- ✅ **Graceful Degradation**: Never crashes host application

**Performance Targets:**

- Provider Detection: <0.1ms (currently ~0.02ms ✅)
- Bundle Loading: <3ms (currently ~0.8ms ✅)  
- Span Processing: <0.1ms (currently ~0.02ms ✅)

Architecture
------------

Provider-Isolated DSL Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each provider gets its own directory with exactly 4 YAML files:

.. code-block:: text

   config/dsl/providers/{provider}/
   ├── structure_patterns.yaml    # Detection signatures (O(1) lookup)
   ├── navigation_rules.yaml       # Field extraction paths
   ├── field_mappings.yaml         # HoneyHive schema mapping
   └── transforms.yaml             # Data transformation functions

**Shared Configuration:**

.. code-block:: text

   config/dsl/shared/
   ├── core_schema.yaml            # HoneyHive 4-section schema
   ├── instrumentor_mappings.yaml  # Instrumentor patterns
   └── validation_rules.yaml       # Common validation rules

Two-Tier Detection System
~~~~~~~~~~~~~~~~~~~~~~~~~~

The engine uses a two-tier detection architecture:

**Tier 1: Instrumentor Detection**

Identifies the instrumentation framework based on attribute prefixes:

+----------------+------------------+--------------------------------+
| Instrumentor   | Prefix           | Example Attributes             |
+================+==================+================================+
| Traceloop      | ``gen_ai.*``     | ``gen_ai.system``              |
+----------------+------------------+--------------------------------+
| OpenInference  | ``llm.*``        | ``llm.provider``               |
+----------------+------------------+--------------------------------+
| OpenLit        | ``openlit.*``    | ``openlit.provider``           |
+----------------+------------------+--------------------------------+
| Direct OTel    | Custom           | Any custom attributes          |
+----------------+------------------+--------------------------------+

**Tier 2: Provider Detection**

Identifies the LLM provider using:

1. **Exact Signature Match** (O(1) using inverted index)
2. **Value-Based Detection** (explicit provider fields)
3. **Wildcard Pattern Match** (for flattened attributes)
4. **Subset Match** (O(log n) with size-based bucketing)

.. mermaid::

   flowchart TD
       A[Span Attributes] --> B[Tier 1: Detect Instrumentor]
       B -->|gen_ai.*| C[traceloop]
       B -->|llm.*| D[openinference]
       B -->|openlit.*| E[openlit]
       B -->|other| F[unknown/direct_otel]
       
       C --> G[Tier 2: Detect Provider]
       D --> G
       E --> G
       F --> G
       
       G -->|O1 Exact Match| H[openai/anthropic/gemini]
       G -->|Value-Based| H
       G -->|Wildcard Match| H
       G -->|Subset Match| H
       
       H --> I{Extract Data}
       I -->|Route by Instrumentor| J[Call instrumentor-specific rules]
       J --> K[Return HoneyHive Schema]

Build-Time Compilation
~~~~~~~~~~~~~~~~~~~~~~~

The system compiles YAML DSL files to optimized Python structures:

.. code-block:: text

   Development:
   YAML Files → Compiler → Optimized Bundle → Runtime Loading
   (AI-friendly) (2-3s)   (Python pickle)    (<1ms)

**Compilation Process:**

1. **Load**: Read all provider YAML files
2. **Validate**: Schema validation and collision detection  
3. **Optimize**: Convert to frozensets and hash tables
4. **Generate**: Build-time Python code generation for transforms
5. **Serialize**: Save as compressed pickle bundle

**Development-Aware Loading:**

The bundle loader automatically detects the environment:

- **Development**: Auto-recompiles when YAML files change
- **Production**: Loads pre-compiled bundle directly

DSL File Specifications
------------------------

Structure Patterns (Provider Detection)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Define unique field combinations for O(1) provider detection.

**File**: ``structure_patterns.yaml``

.. code-block:: yaml

   version: "1.0"
   provider: "openai"
   dsl_type: "provider_structure_patterns"

   patterns:
     # Pattern naming: {instrumentor}_{provider}
     traceloop_openai:
       required_fields:
         - "gen_ai.system"
         - "gen_ai.request.model"
         - "gen_ai.usage.prompt_tokens"
       optional_fields:
         - "gen_ai.usage.completion_tokens"
         - "gen_ai.request.temperature"
       confidence_weight: 0.90
       description: "OpenAI via Traceloop instrumentation"
       instrumentor_framework: "traceloop"
     
     openinference_openai:
       required_fields:
         - "llm.provider"
         - "llm.model_name"
         - "llm.input_messages"
       confidence_weight: 0.95
       instrumentor_framework: "openinference"

**Key Concepts:**

- **required_fields**: MUST be present for detection (used in frozenset signature)
- **optional_fields**: MAY be present (boosts confidence if matched)
- **confidence_weight**: 0.0-1.0 (higher = more confident)
- **instrumentor_framework**: Which instrumentor this pattern detects

Navigation Rules (Field Extraction)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Define how to extract data from detected provider attributes.

**File**: ``navigation_rules.yaml``

.. code-block:: yaml

   version: "1.0"
   provider: "openai"
   dsl_type: "provider_navigation_rules"

   navigation_rules:
     # Rule naming: {instrumentor}_{field_name}
     traceloop_model_name:
       source_field: "gen_ai.request.model"
       extraction_method: "direct_copy"
       fallback_value: "unknown"
       validation: "non_empty_string"
       description: "Extract model from Traceloop"
     
     openinference_model_name:
       source_field: "llm.model_name"
       extraction_method: "direct_copy"
       fallback_value: "unknown"
       validation: "non_empty_string"
       description: "Extract model from OpenInference"
     
     openlit_model_name:
       source_field: "openlit.model"
       extraction_method: "direct_copy"
       fallback_value: "unknown"
       validation: "non_empty_string"
       description: "Extract model from OpenLit"

**Extraction Methods:**

- ``direct_copy``: Copy value as-is
- ``array_flatten``: Flatten nested arrays
- ``object_merge``: Merge multiple objects
- ``string_concat``: Concatenate strings
- ``numeric_sum``: Sum numeric values

**Critical**: Create rules for **ALL 3 instrumentors** (traceloop, openinference, openlit) for complete coverage.

Field Mappings (HoneyHive Schema)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Map extracted data to HoneyHive's 4-section schema.

**File**: ``field_mappings.yaml``

.. code-block:: yaml

   version: "1.0"
   provider: "openai"
   dsl_type: "provider_field_mappings"

   field_mappings:
     # inputs: User inputs, chat history, prompts, context
     inputs:
       chat_history:
         source_rule: "input_messages"      # Base name (no prefix!)
         required: false
         description: "User conversation history"
     
     # outputs: Model responses, completions, tool calls
     outputs:
       response:
         source_rule: "output_messages"
         required: false
         description: "Model response messages"
     
     # config: Model parameters, settings
     config:
       model:
         source_rule: "model_name"          # Base name enables routing
         required: true
         description: "Model identifier"
     
     # metadata: Usage metrics, provider info
     metadata:
       provider:
         source_rule: "static_openai"
         required: true
         description: "Provider identifier"
       
       instrumentor:
         source_rule: "detect_instrumentor"
         required: false
         description: "Instrumentor framework"

**Dynamic Routing Magic:**

Use **base rule names** (without instrumentor prefix) in field_mappings!

The compiler generates instrumentor-aware routing code:

.. code-block:: python

   # Generated code
   def extract_openai_data(attributes, instrumentor='unknown'):
       config = {}
       # Router automatically selects correct rule
       config['model'] = (
           attributes.get('gen_ai.request.model', 'unknown') if instrumentor == 'traceloop' else
           attributes.get('llm.model_name', 'unknown') if instrumentor == 'openinference' else
           attributes.get('openlit.model', 'unknown') if instrumentor == 'openlit' else
           None
       )
       return {"config": config, ...}

Transforms (Data Processing)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Define reusable transformation functions for data manipulation.

**File**: ``transforms.yaml``

.. code-block:: yaml

   version: "1.0"
   provider: "openai"
   dsl_type: "provider_transforms"

   transforms:
     extract_user_prompt:
       function_type: "extract_message_content_by_role"
       implementation: "python_code_generated_at_build_time"
       parameters:
         role: "user"
         messages_field: "chat_history"
         separator: "\n\n"
       description: "Extract user prompt from messages"
     
     calculate_openai_cost:
       function_type: "calculate_openai_cost"
       implementation: "python_code_generated_at_build_time"
       parameters:
         model_field: "model"
         prompt_tokens_field: "prompt_tokens"
         completion_tokens_field: "completion_tokens"
         pricing_table:
           "gpt-4o": {input: 0.0025, output: 0.01}
           "gpt-4o-mini": {input: 0.00015, output: 0.0006}
           # ... current pricing
       description: "Calculate cost using current OpenAI pricing"

**Transform Functions:**

Transform functions are **generated as Python code at build time** and inlined into extraction functions for zero runtime overhead.

Development Workflow
--------------------

Creating a New Provider
~~~~~~~~~~~~~~~~~~~~~~~

**Step 1: Generate Template** (30 seconds)

.. code-block:: bash

   cd /Users/josh/src/github.com/honeyhiveai/python-sdk
   python scripts/generate_provider_template.py {provider_name}

**Step 2: Research** (30-60 minutes)

**⚠️ CRITICAL**: Use the RESEARCH_SOURCES_TEMPLATE.md as your guide!

Every provider documents things differently. Here's where to look:

**Finding Official Documentation**:

+------------------+----------------------------------------+-------------------------------------+
| Provider Type    | Where to Find                          | What to Look For                    |
+==================+========================================+=====================================+
| **Big Tech**     | ``{provider}.ai/docs``,                | API reference, models list,         |
| (OpenAI,         | ``platform.{provider}.com/docs``       | pricing page, changelog             |
| Google, etc.)    |                                        |                                     |
+------------------+----------------------------------------+-------------------------------------+
| **Startups**     | ``docs.{provider}.com``,               | API docs (may be less               |
| (Anthropic,      | ``{provider}.ai/docs``                 | comprehensive), GitHub examples     |
| Cohere, etc.)    |                                        |                                     |
+------------------+----------------------------------------+-------------------------------------+
| **Enterprise**   | ``{provider}.com/docs/ai``,            | Enterprise docs (may require        |
| (AWS, Azure,     | ``cloud.{provider}.com/ai``            | login), service-specific pages      |
| IBM, etc.)       |                                        |                                     |
+------------------+----------------------------------------+-------------------------------------+
| **Open Source**  | GitHub README,                         | Model cards, usage examples,        |
| (Ollama, etc.)   | ``{provider}.ai/library``              | community docs                      |
+------------------+----------------------------------------+-------------------------------------+

**Finding Instrumentor Patterns**:

+------------------+--------------------------------------------------+---------------------------------+
| Instrumentor     | Where to Find Patterns                           | Key Files to Check              |
+==================+==================================================+=================================+
| **OpenInference**| https://github.com/Arize-ai/openinference         | ``spec/semantic_conventions/`` |
|                  | Look in: ``spec/`` and ``python/`` directories   | ``python/instrumentation/``    |
+------------------+--------------------------------------------------+---------------------------------+
| **Traceloop**    | https://github.com/traceloop/openllmetry          | ``packages/*/instrumentation/``|
|                  | Look in: Provider-specific packages              | Check tests for examples       |
+------------------+--------------------------------------------------+---------------------------------+
| **OpenLit**      | https://github.com/openlit/openlit                | ``sdk/python/src/openlit/``    |
|                  | Look in: ``sdk/python/src/openlit/instrumentation``| Provider-specific folders    |
+------------------+--------------------------------------------------+---------------------------------+

**Finding Pricing Information**:

1. **Official Pricing Page**: Usually ``{provider}.com/pricing`` or ``pricing.{provider}.com``
2. **API Documentation**: Sometimes includes pricing in headers or responses
3. **Calculator Tools**: Many providers have pricing calculators
4. **Release Announcements**: Blog posts often announce pricing for new models

**Research Checklist**:

- [ ] Find and bookmark official API documentation
- [ ] Find models page and list all current models (including legacy!)
- [ ] Find pricing page and record costs per million tokens
- [ ] Check instrumentor repos for this provider's patterns
- [ ] Look for example code/traces showing attribute structure
- [ ] Create comprehensive ``RESEARCH_SOURCES.md`` using template
- [ ] Document any provider-specific quirks or unique features

**Step 3: Populate DSL Files** (1-2 hours)

1. **structure_patterns.yaml**: 3-6 patterns covering main instrumentors
2. **navigation_rules.yaml**: All extraction rules × 3 instrumentors
3. **field_mappings.yaml**: Complete HoneyHive schema mapping
4. **transforms.yaml**: Cost calculation + data transformations

**Step 4: Compile & Validate** (1 minute)

.. code-block:: bash

   # Compile the bundle
   python -m config.dsl.compiler
   
   # Output should show:
   # ✅ Successfully compiled provider bundle
   # 📁 Bundle location: .../compiled_providers.pkl
   # 📊 Providers: N
   # ⚡ Patterns: M
   # 🔧 Functions: N

**Step 5: Test** (15-30 minutes)

.. code-block:: bash

   # Test two-tier detection and extraction
   python scripts/test_two_tier_extraction.py
   
   # Test performance
   python scripts/profile_universal_engine.py

Updating an Existing Provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Check Research Sources**: Verify pricing and models are current
2. **Update Files**: Modify relevant YAML files
3. **Recompile**: ``python -m config.dsl.compiler``
4. **Test**: Run extraction and performance tests
5. **Document**: Update ``RESEARCH_SOURCES.md`` with changes

Quality Checklist
~~~~~~~~~~~~~~~~~

Before considering a provider "complete":

**Structure Patterns**:

- ☐ 3-6 patterns covering major instrumentors
- ☐ Unique required_fields (not duplicated with other providers)
- ☐ Appropriate confidence_weight (0.85-0.95)
- ☐ Clear descriptions

**Navigation Rules**:

- ☐ Rules for ALL 3 instrumentors (traceloop_*, openinference_*, openlit_*)
- ☐ Safe fallback values for all fields
- ☐ Appropriate validation rules
- ☐ Descriptive names and descriptions

**Field Mappings**:

- ☐ All 4 sections populated (inputs, outputs, config, metadata)
- ☐ ``model`` marked as required: true
- ☐ ``provider`` marked as required: true
- ☐ Base rule names (no instrumentor prefixes!)
- ☐ Descriptions for all fields

**Transforms**:

- ☐ Cost calculation with current pricing (dated)
- ☐ Message extraction transforms (user, assistant, system)
- ☐ Finish reason normalization
- ☐ All transforms referenced in field_mappings

**General**:

- ☐ Compiles without errors
- ☐ Passes bundle validation
- ☐ RESEARCH_SOURCES.md created
- ☐ Tested with real span data
- ☐ Performance meets targets

Testing the Engine
------------------

Unit Tests
~~~~~~~~~~

Unit tests cover individual components:

.. code-block:: bash

   # Test provider processor
   tox -e unit -- tests/unit/tracer/processing/semantic_conventions/test_provider_processor*.py
   
   # Test bundle loader
   tox -e unit -- tests/unit/tracer/processing/semantic_conventions/test_bundle_loader.py
   
   # Test compiler
   tox -e unit -- tests/unit/config/dsl/test_compiler.py

Integration Tests
~~~~~~~~~~~~~~~~~

Integration tests validate end-to-end extraction:

.. code-block:: bash

   # Run two-tier extraction tests
   python scripts/test_two_tier_extraction.py
   
   # Expected output:
   # 🎯 TWO-TIER DETECTION VALIDATION
   # Testing all 3 instrumentors with OpenAI provider:
   #   Traceloop       → [traceloop   , openai    ] ✅
   #   OpenInference   → [openinference, openai    ] ✅
   #   OpenLit         → [openlit     , openai    ] ✅

Performance Testing
~~~~~~~~~~~~~~~~~~~

Profile the engine to ensure O(1) performance:

.. code-block:: bash

   # Run performance profiler
   python scripts/profile_universal_engine.py
   
   # Expected output:
   # Provider Detection       : 0.02ms average  (target: <0.1ms ✅)
   # Span Processing          : 0.02ms average  (target: <0.1ms ✅)
   # Bundle Loading           : 0.8ms average   (target: <3ms ✅)

Common Issues
~~~~~~~~~~~~~

**Issue: "No provider detected"**

- Check ``structure_patterns.yaml`` has patterns for all instrumentors
- Verify ``required_fields`` match actual span attributes
- Ensure patterns have unique signatures (not shared with other providers)

**Issue: "Extraction returns None/empty values"**

- Check ``navigation_rules.yaml`` has rules for detected instrumentor
- Verify ``source_field`` paths match actual attribute keys
- Use base rule names in ``field_mappings.yaml`` (no instrumentor prefix!)

**Issue: "Compilation fails"**

- Run yamllint on YAML files: ``yamllint config/dsl/providers/{provider}/``
- Check for syntax errors (indentation, quotes, etc.)
- Verify all required fields are present in each file

**Issue: "Performance degradation"**

- Profile the system: ``python scripts/profile_universal_engine.py``
- Check for O(n) operations in detection logic
- Ensure frozensets are used for signature matching

Architecture Decisions
----------------------

Why Provider-Isolated DSL?
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: V3.0 had monolithic YAML files mixing all providers, making AI assistant development difficult with large context windows.

**Solution**: V4.0 uses provider-isolated files (~7KB per provider) for:

- ✅ **Parallel Development**: Multiple AI assistants can work on different providers simultaneously
- ✅ **Zero Contamination**: Changes to one provider don't affect others
- ✅ **Fast Context**: Small files load quickly into AI context windows
- ✅ **Clear Ownership**: Each provider is self-contained

Why Build-Time Compilation?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Runtime YAML parsing adds overhead to customer applications.

**Solution**: Build-time compilation provides:

- ✅ **Zero Runtime Overhead**: YAML parsed once at build time
- ✅ **O(1) Lookups**: Frozensets and hash tables for fast detection
- ✅ **Type Safety**: Pydantic validation at compile time
- ✅ **AI-Friendly**: Humans/AI edit YAML, customers get optimized Python

Why Two-Tier Detection?
~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Provider detection was unreliable when instrumentors use different attribute names for the same provider.

**Solution**: Two-tier system separates concerns:

- **Tier 1 (Instrumentor)**: Identifies how data is instrumented (Traceloop vs OpenInference)
- **Tier 2 (Provider)**: Identifies which LLM provider (OpenAI vs Anthropic)

This enables:

- ✅ **Correct Routing**: Extract data using instrumentor-specific rules
- ✅ **Better Accuracy**: Explicit detection of both layers
- ✅ **Extensibility**: Easy to add new instrumentors or providers

Reference Documentation
-----------------------

**Internal References:**

- ``config/dsl/DSL_REFERENCE.md`` - Complete DSL reference guide
- ``universal_llm_discovery_engine_v4_final/`` - v4.0 design documents
  
  - ``ARCHITECTURE_FOUNDATION.md`` - Architecture overview
  - ``PROVIDER_SPECIFICATION.md`` - Complete DSL specification
  - ``IMPLEMENTATION_PLAN.md`` - Build system details
  - ``RESEARCH_REFERENCES.md`` - Instrumentor patterns

**Example Implementations:**

- ``config/dsl/providers/openai/`` - Complete OpenAI implementation
- ``config/dsl/providers/anthropic/`` - Complete Anthropic implementation
- ``config/dsl/providers/gemini/`` - Complete Gemini implementation

**Tools:**

- ``scripts/generate_provider_template.py`` - Provider template generator
- ``config/dsl/compiler.py`` - DSL compiler
- ``scripts/test_two_tier_extraction.py`` - Extraction tester
- ``scripts/profile_universal_engine.py`` - Performance profiler

**Shared Configuration:**

- ``config/dsl/shared/core_schema.yaml`` - HoneyHive schema definition
- ``config/dsl/shared/instrumentor_mappings.yaml`` - Instrumentor patterns
- ``config/dsl/shared/validation_rules.yaml`` - Common validation

Quick Tips for SDK Developers
------------------------------

**Golden Rules:**

1. **Always use base rule names** in field_mappings.yaml (no instrumentor prefix)
2. **Create rules for all 3 instrumentors** in navigation_rules.yaml (traceloop, openinference, openlit)
3. **Keep pricing current** - always check official docs for latest pricing
4. **Test after every change** - compile and run extraction tests
5. **Document everything** - RESEARCH_SOURCES.md is your maintenance guide

**Common Mistakes:**

- ❌ Hardcoding instrumentor-specific rules in field_mappings (breaks routing)
- ❌ Forgetting to create rules for all instrumentors (partial coverage)
- ❌ Using outdated pricing (incorrect cost calculations)
- ❌ Skipping RESEARCH_SOURCES.md (no update trail)
- ❌ Not testing with real span data (catches issues early)

**Performance Tips:**

- Use ``frozenset`` for signature matching (O(1) lookup)
- Avoid loops in detection logic (breaks O(1) guarantee)
- Generate transforms at build time (zero runtime overhead)
- Cache logger instances (per-tracer-instance isolation)

Contributing
------------

**Adding New Providers:**

1. Use template generator to scaffold files
2. Research official docs thoroughly
3. Create comprehensive RESEARCH_SOURCES.md
4. Test with all 3 instrumentors
5. Submit PR with tests and documentation

**Improving Existing Providers:**

1. Check RESEARCH_SOURCES.md for update procedures
2. Verify current pricing on official pages
3. Update model lists with new releases
4. Recompile and test
5. Update RESEARCH_SOURCES.md with changes

**See Also:**

- :doc:`testing/unit-testing` - Testing guidelines
- :doc:`workflow-optimization` - Development optimization
- :doc:`../explanation/architecture/overview` - SDK architecture
