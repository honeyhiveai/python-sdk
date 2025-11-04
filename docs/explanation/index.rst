Explanation
===========

.. note::
   **Understanding-oriented documentation**
   
   This section explains the concepts, design decisions, and architecture behind the HoneyHive SDK. Read this to understand *why* things work the way they do, not just *how* to use them.

**Quick Navigation:**

.. contents::
   :local:
   :depth: 2

Overview
--------

Understanding HoneyHive requires grasping several key concepts:

- **Why observability matters** for LLM applications
- **How the BYOI architecture** solves dependency conflicts
- **Why multi-instance support** enables flexible workflows
- **How OpenTelemetry integration** provides industry standards

This section provides the conceptual foundation for effective use of HoneyHive.

Architecture & Design
---------------------

.. toctree::
   :maxdepth: 1

   architecture/overview
   architecture/byoi-design

Architecture Diagrams
---------------------

.. toctree::
   :maxdepth: 1

   architecture/diagrams

Fundamental Concepts
--------------------

.. toctree::
   :maxdepth: 1

   concepts/tracing-fundamentals
   concepts/llm-observability
   concepts/experiments-architecture

Compatibility Matrix
--------------------

This section provides comprehensive compatibility information for the HoneyHive Python SDK and various instrumentors across supported Python versions and providers.

**HoneyHive SDK Python Version Support**

The **HoneyHive Python SDK** officially supports the following Python versions:

- **Supported Versions**: Python 3.11, 3.12, 3.13
- **Minimum Version**: Python 3.11 (as defined in pyproject.toml)
- **Recommended Version**: Python 3.12 (optimal compatibility and performance)
- **Latest Tested**: Python 3.13 (cutting-edge features)

**HoneyHive SDK Compatibility**

.. list-table::
   :header-rows: 1
   :widths: 20 30 30 20

   * - Python Version
     - HoneyHive SDK Support
     - Notes
     - End of Life
   * - Python 3.11
     - ✅ Fully Supported
     - Minimum supported version
     - 2027-10
   * - Python 3.12
     - ✅ Fully Supported
     - Recommended version
     - 2028-10
   * - Python 3.13
     - ✅ Fully Supported
     - Latest supported version
     - 2029-10

.. note::
   HoneyHive SDK requires Python >=3.11 as specified in ``pyproject.toml``

**Instrumentor Compatibility**

All supported instrumentors are compatible with **Python 3.11, 3.12, and 3.13**.

**Status Legend:**

- **✅ Full Support**: Works out of the box
- **⚠️ Requires Workaround**: Works with documented workaround

**OpenInference Instrumentors**

All OpenInference instrumentors have **✅ Full Support** across all Python versions:

- ``openinference-instrumentation-openai``
- ``openinference-instrumentation-anthropic`` 
- ``openinference-instrumentation-bedrock``
- ``openinference-instrumentation-google-generativeai``
- ``openinference-instrumentation-google-adk``
- ``openinference-instrumentation-mcp``

**OpenTelemetry Instrumentors (Traceloop)**

Most OpenTelemetry instrumentors have **✅ Full Support**:

- ``opentelemetry-instrumentation-openai``
- ``opentelemetry-instrumentation-anthropic``
- ``opentelemetry-instrumentation-bedrock``
- ``opentelemetry-instrumentation-mcp``

**Special Case:**

- ``opentelemetry-instrumentation-google-generativeai`` - **⚠️ Requires Workaround** (see below)

**Instrumentors Requiring Workarounds**

Some instrumentors require workarounds due to upstream bugs or compatibility issues:

**OpenTelemetry Google AI** (``opentelemetry-instrumentation-google-generativeai``):

- **Issue**: Upstream bug with incorrect import path (``google.genai.types`` vs ``google.generativeai.types``)
- **Workaround**: See ``examples/traceloop_google_ai_example_with_workaround.py``
- **Status**: Fully functional with workaround applied

**Supported Providers**

The following providers are officially supported and production-ready:

**LLM Providers**

- **OpenAI** (GPT-4, GPT-3.5, embeddings)
- **Azure OpenAI** (Same models via Azure endpoints)
- **Anthropic** (Claude models)
- **Google Generative AI** (Gemini models)
- **AWS Bedrock** (Multi-model support)

**Specialized Providers**

- **Google Agent Development Kit** (Agent workflows)
- **Model Context Protocol** (MCP integration)

**Instrumentor Options**

For each provider, you can choose between:

1. **OpenInference** - Open source, community-driven
2. **OpenTelemetry (Traceloop)** - Enhanced features and metrics

Both options provide full compatibility with HoneyHive and work across all supported Python versions.

**Provider Onboarding Status**

**Currently Supported (11 instrumentors)**: All providers listed above have completed the HoneyHive onboarding process and are officially supported.

**Not Yet Onboarded**: Other providers (Cohere, Vertex AI, LangChain, LlamaIndex, DSPy, Hugging Face, Mistral AI, Groq, Ollama, LiteLLM) have not completed the official onboarding process and are not included in compatibility testing.

**Installation Guide**

**Basic Installation**

Install the HoneyHive SDK:

.. code-block:: bash

   pip install honeyhive

**Choose Your Instrumentors**

**Option 1: OpenInference (Recommended for most users)**

.. code-block:: bash

   # Individual providers
   pip install openinference-instrumentation-openai
   pip install openinference-instrumentation-anthropic
   pip install openinference-instrumentation-bedrock
   
   # Or use HoneyHive convenience packages
   pip install honeyhive[openinference-openai]
   pip install honeyhive[openinference-anthropic]

**Option 2: OpenTelemetry (Traceloop)**

.. code-block:: bash

   # Individual providers
   pip install opentelemetry-instrumentation-openai
   pip install opentelemetry-instrumentation-anthropic
   pip install opentelemetry-instrumentation-bedrock

**Option 3: Install All OpenInference**

.. code-block:: bash

   pip install honeyhive[all-openinference]

**Known Issues**

**Google AI Instrumentor Workaround**

If using ``opentelemetry-instrumentation-google-generativeai``, you may need to apply a workaround for an upstream import bug.

**Symptoms**: Import errors mentioning ``google.genai.types``

**Solution**: See the complete working example at ``examples/traceloop_google_ai_example_with_workaround.py``

**Getting Help**

- **Integration Guides**: :doc:`../how-to/index`
- **Report Issues**: `GitHub Issues <https://github.com/honeyhiveai/python-sdk/issues>`_
- **Community Support**: `Discord <https://discord.gg/honeyhive>`_

**See Also**

- :doc:`../tutorials/02-add-llm-tracing-5min` - LLM integration tutorial
- :doc:`architecture/byoi-design` - BYOI architecture explanation
- :doc:`../how-to/index` - Integration guides and troubleshooting
- :doc:`../reference/configuration/environment-vars` - Environment variable reference

Understanding the Ecosystem
---------------------------

**LLM Observability Landscape:**

The LLM observability space is rapidly evolving. HoneyHive's approach focuses on:

1. **Standards Compliance**: Built on OpenTelemetry for interoperability
2. **Minimal Dependencies**: Avoid forcing specific LLM library versions
3. **Production Focus**: Designed for real-world deployment challenges
4. **Developer Experience**: Simple APIs with powerful capabilities

**When to Use HoneyHive:**

- You need production-grade LLM observability
- You have existing OpenTelemetry infrastructure
- You want to avoid dependency conflicts
- You need to trace across multiple LLM providers
- You require comprehensive evaluation capabilities

**When to Consider Alternatives:**

- You only need basic logging (use standard Python logging)
- You're only using one LLM provider with its own tracing
- You need real-time streaming observability
- You have very specific performance requirements

Common Questions
----------------

**Why Another Observability Tool?**

LLM applications have unique observability needs:

- **Token-level visibility** into costs and performance
- **Prompt and response tracking** for debugging and optimization
- **Multi-hop reasoning** tracing across agent workflows
- **Evaluation integration** to measure quality over time

Traditional APM tools weren't designed for these use cases.

**Why Not Just Use OpenTelemetry Directly?**

You can! HoneyHive is built on OpenTelemetry and doesn't replace it. We add:

- **LLM-specific attributes** and conventions
- **Evaluation frameworks** integrated with tracing
- **Dashboard optimized** for LLM workflows
- **SDKs designed** for common LLM patterns

**What's the "Bring Your Own Instrumentor" Philosophy?**

Instead of shipping with every possible LLM library, we let you choose:

- **Install only what you need** (openai, anthropic, etc.)
- **Avoid version conflicts** with your existing dependencies
- **Use community instrumentors** or build custom ones
- **Stay up-to-date** with the latest LLM libraries

Learning Path
-------------

**New to Observability?**

1. Start with :doc:`concepts/tracing-fundamentals`
2. Learn about :doc:`concepts/llm-observability`
3. Understand :doc:`architecture/overview`

**Coming from Other Tools?**

1. Read about observability patterns in general
2. Understand :doc:`architecture/byoi-design`
3. Review the dependency strategy in BYOI design

**Building Production Systems?**

1. Study :doc:`architecture/overview`
2. Understand :doc:`architecture/byoi-design`
3. Learn about the multi-instance patterns

Further Reading
---------------

**External Resources:**

- `OpenTelemetry Documentation <https://opentelemetry.io/docs/>`_
- `OpenInference Project <https://github.com/Arize-ai/openinference>`_
- `LLM Observability Best Practices <https://honeyhive.ai/blog/llm-observability>`_

**Related Documentation:**

- :doc:`../tutorials/index` - Learn by doing
- :doc:`../how-to/index` - Solve specific problems
- :doc:`../reference/index` - Look up technical details
