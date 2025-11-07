Setting up HoneyHive in your Python Package Manager
====================================================

Learn how to properly include HoneyHive in your project's ``pyproject.toml`` file using optional dependency groups for clean, targeted installations.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

HoneyHive provides optional dependency groups that bundle the SDK with specific LLM provider instrumentors and SDKs. This approach offers:

- **🎯 Targeted Dependencies**: Only install what you need
- **📦 Automatic Resolution**: Correct versions guaranteed to work together  
- **🚀 Zero Configuration**: Everything ready after installation
- **🔄 Easy Switching**: Change providers by updating dependency group
- **📊 Clear Intent**: Your ``pyproject.toml`` shows exactly which providers you use

Single Provider Integration
---------------------------

**Most Common Pattern - Add one provider:**

.. code-block:: toml

   [project]
   name = "my-llm-app"
   version = "0.1.0"
   dependencies = [
       "honeyhive[openinference-openai]",  # OpenAI + instrumentor + SDK
       "fastapi>=0.100.0",
       "uvicorn>=0.20.0"
   ]

**Available Single Provider Options:**

.. code-block:: toml

   dependencies = [
       "honeyhive[openinference-openai]",        # OpenAI GPT models
       "honeyhive[openinference-anthropic]",     # Anthropic Claude models  
       "honeyhive[openinference-google-ai]",     # Google Gemini models
       "honeyhive[openinference-bedrock]",   # AWS Bedrock multi-model
       "honeyhive[openinference-azure-openai]",  # Azure-hosted OpenAI
   ]

Multiple Provider Integration  
-------------------------------

**Production Apps with Multiple Providers:**

.. code-block:: toml

   [project]
   name = "my-multi-provider-app"
   version = "1.0.0"
   dependencies = [
       "honeyhive[openinference-openai,openinference-anthropic,openinference-google-ai]",  # Multiple providers
       "fastapi>=0.100.0",
       "pydantic>=2.0.0"
   ]

**Popular Provider Combination:**

.. code-block:: toml

   dependencies = [
       "honeyhive[openinference-llm-providers]",  # OpenAI + Anthropic + Google (most popular)
   ]

Framework-Specific Integration
------------------------------

**LangChain Applications:**

.. code-block:: toml

   [project]
   name = "my-langchain-app"
   dependencies = [
       "honeyhive[openinference-langchain]",     # LangChain + instrumentor
       "honeyhive[openai]",        # Add your LLM provider  
       "chromadb>=0.4.0"
   ]

**LlamaIndex RAG Applications:**

.. code-block:: toml

   [project]
   name = "my-rag-app"  
   dependencies = [
       "honeyhive[llamaindex]",    # LlamaIndex + instrumentor
       "honeyhive[openai]",        # Add your LLM provider
       "pinecone-client>=2.0.0"
   ]

**DSPy Programming Framework:**

.. code-block:: toml

   [project]
   name = "my-dspy-app"
   dependencies = [
       "honeyhive[dspy]",          # DSPy + instrumentor  
       "honeyhive[openai]",        # Add your LLM provider
   ]

Optional Dependencies Pattern (Recommended)
-------------------------------------------

**Flexible User Choice - Let users pick providers:**

.. code-block:: toml

   [project]
   name = "my-flexible-library"
   version = "0.1.0"
   dependencies = [
       "honeyhive",  # Core SDK only - no provider lock-in
       "pydantic>=2.0.0",
       "httpx>=0.24.0"
   ]

   [project.optional-dependencies]
   # Let users choose their providers
   openai = ["honeyhive[openinference-openai]"]
   anthropic = ["honeyhive[anthropic]"]
   google = ["honeyhive[google-ai]"]
   aws = ["honeyhive[bedrock]"]
   azure = ["honeyhive[azure-openai]"]

   # Framework integrations
   langchain = ["honeyhive[openinference-langchain]"]
   llamaindex = ["honeyhive[llamaindex]"]

   # Convenience groups
   popular = ["honeyhive[llm-providers]"]        # OpenAI + Anthropic + Google
   all-providers = ["honeyhive[all-integrations]"]  # Everything

   # Development dependencies  
   dev = [
       "honeyhive[openai,anthropic]",  # Test with multiple providers
       "pytest>=7.0.0",
       "black>=23.0.0",
       "mypy>=1.0.0"
   ]

**Users can then install with:**

.. code-block:: bash

   # Install your library with OpenAI support
   pip install my-flexible-library[openai]
   
   # Install with multiple providers
   pip install my-flexible-library[openai,anthropic]
   
   # Install with all providers for testing
   pip install my-flexible-library[all-providers]

All Integrations (Kitchen Sink)
-------------------------------

**Enterprise Apps with Comprehensive Provider Support:**

.. code-block:: toml

   [project]
   name = "enterprise-llm-platform"
   version = "2.0.0"
   dependencies = [
       "honeyhive[all-integrations]",  # All providers + frameworks
       "fastapi>=0.100.0",
       "sqlalchemy>=2.0.0",
       "redis>=4.0.0"
   ]

**Note**: Only use ``all-integrations`` if you actually need multiple providers. For most apps, specific provider groups are better.

Tool-Specific Examples
----------------------

**requirements.txt (pip)**

.. code-block:: text

   # Core app dependencies
   honeyhive[openinference-openai,openinference-anthropic]>=1.0.0
   fastapi>=0.100.0
   uvicorn>=0.20.0
   
   # Framework integration example
   # honeyhive[openinference-langchain]>=1.0.0
   
   # Multiple providers
   # honeyhive[openinference-llm-providers]>=1.0.0

.. code-block:: bash

   # Install from requirements.txt
   pip install -r requirements.txt
   
   # Or install directly
   pip install "honeyhive[openinference-openai,openinference-anthropic]>=1.0.0"

**uv**

.. code-block:: bash

   # Initialize new project with uv
   uv init my-llm-app
   cd my-llm-app
   
   # Add HoneyHive with providers
   uv add "honeyhive[openinference-openai]"
   uv add "honeyhive[openinference-anthropic]"
   
   # Or add multiple providers at once
   uv add "honeyhive[openinference-openai,openinference-anthropic]"
   
   # Add framework integration
   uv add "honeyhive[openinference-langchain]"
   
   # Run your application
   uv run python main.py

.. code-block:: toml

   # pyproject.toml (generated by uv)
   [project]
   name = "my-llm-app"
   version = "0.1.0"
   dependencies = [
       "honeyhive[openinference-openai,openinference-anthropic]>=1.0.0",
       "fastapi>=0.100.0",
   ]

**Poetry**

.. code-block:: toml

   [tool.poetry.dependencies]
   python = "^3.11"
   honeyhive = {extras = ["openinference-openai", "openinference-anthropic"], version = "^1.0.0"}
   fastapi = "^0.100.0"

**pip-tools (requirements.in)**

.. code-block:: text

   # Core app dependencies
   honeyhive[openinference-openai,openinference-anthropic]>=1.0.0
   fastapi>=0.100.0
   uvicorn>=0.20.0

.. code-block:: bash

   # Compile to requirements.txt
   pip-compile requirements.in
   
   # Install
   pip-sync requirements.txt

**Pipenv**

.. code-block:: toml

   [packages]
   honeyhive = {extras = ["openinference-openai"], version = "*"}
   fastapi = "*"

**Hatch**

.. code-block:: toml

   [project]
   dependencies = [
       "honeyhive[openinference-google-ai]",
   ]

   [project.optional-dependencies]
   dev = ["honeyhive[openinference-openai,openinference-anthropic]"]  # More providers for testing

Available Optional Dependencies
-------------------------------

**🤖 LLM Providers**

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Extra
     - What's Included
   * - ``openai``
     - OpenAI SDK + OpenInference OpenAI instrumentor
   * - ``anthropic``
     - Anthropic SDK + OpenInference Anthropic instrumentor
   * - ``google-ai``
     - Google Generative AI SDK + OpenInference Google instrumentor
   * - ``google-adk``
     - Google Agent Development Kit + OpenInference ADK instrumentor
   * - ``bedrock``
     - Boto3 + OpenInference Bedrock instrumentor
   * - ``azure-openai``
     - OpenAI SDK + Azure Identity + OpenInference OpenAI instrumentor
   * - ``mcp``
     - OpenInference MCP instrumentor for Model Context Protocol

**🔧 Framework Integrations**

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Extra
     - What's Included
   * - ``langchain``
     - LangChain + OpenInference LangChain instrumentor
   * - ``llamaindex``
     - LlamaIndex + OpenInference LlamaIndex instrumentor
   * - ``dspy``
     - DSPy + OpenInference DSPy instrumentor

**🌟 Additional Providers**

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Extra
     - What's Included
   * - ``cohere``
     - Cohere SDK + OpenInference Cohere instrumentor
   * - ``huggingface``
     - Transformers + OpenInference HuggingFace instrumentor
   * - ``mistralai``
     - Mistral AI SDK + OpenInference Mistral instrumentor
   * - ``groq``
     - Groq SDK + OpenInference Groq instrumentor
   * - ``ollama``
     - Ollama SDK + OpenInference Ollama instrumentor
   * - ``litellm``
     - LiteLLM + OpenInference LiteLLM instrumentor

**📦 Convenience Groups**

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Extra
     - What's Included
   * - ``llm-providers``
     - OpenAI + Anthropic + Google AI (most popular providers)
   * - ``all-integrations``
     - All available instrumentors and SDKs

Best Practices
--------------

**✅ Do This**

.. code-block:: toml

   # Good: Specific providers you actually use
   dependencies = ["honeyhive[openai,anthropic]"]
   
   # Good: Let users choose in a library
   [project.optional-dependencies]
   openai = ["honeyhive[openinference-openai]"]

**❌ Avoid This**

.. code-block:: toml

   # Avoid: Installing everything when you only use OpenAI
   dependencies = ["honeyhive[all-integrations]"]
   
   # Avoid: Manual instrumentor management
   dependencies = [
       "honeyhive",
       "openinference-instrumentation-openai",  # Use honeyhive[openinference-openai] instead
       "openai"
   ]

**🎯 Choosing the Right Pattern**

- **Application**: Use specific provider extras like ``honeyhive[openinference-openai]``
- **Library**: Use optional dependencies to let users choose
- **Enterprise**: Consider ``honeyhive[llm-providers]`` for popular providers
- **Testing**: Use ``honeyhive[all-integrations]`` for comprehensive testing

Migration from Manual Installation
----------------------------------

**Before (Manual):**

.. code-block:: toml

   dependencies = [
       "honeyhive",
       "openinference-instrumentation-openai",
       "openinference-instrumentation-anthropic", 
       "openai",
       "anthropic"
   ]

**After (Optional Dependencies):**

.. code-block:: toml

   dependencies = [
       "honeyhive[openai,anthropic]"  # Much cleaner!
   ]

**Benefits of Migration:**

- **Fewer Dependencies**: One line instead of five
- **Version Compatibility**: Guaranteed to work together
- **Easier Maintenance**: Update one package instead of tracking multiple
- **Clearer Intent**: Obvious which providers you use

Troubleshooting
---------------

**Import Errors After Installation**

Make sure you installed the right extra:

.. code-block:: bash

   # If using OpenAI
   pip install honeyhive[openinference-openai]
   
   # If using multiple providers  
   pip install honeyhive[openinference-openai,openinference-anthropic]

**Version Conflicts**

The optional dependencies are curated to avoid conflicts. If you see version conflicts:

1. Use the optional dependency groups instead of manual installation
2. Update to the latest HoneyHive version
3. Check that you're not manually specifying conflicting versions

**Missing Provider Support**

If a provider isn't available as an optional dependency:

.. code-block:: bash

   # Fall back to manual installation
   pip install honeyhive
   pip install openinference-instrumentation-<provider>
   pip install <provider-sdk>

   # Then file an issue to request the provider be added!

Next Steps
----------

- **Quick Start**: :doc:`../index` - Choose your provider integration
- **Examples**: :doc:`../../tutorials/index` - See complete examples
- **Deployment**: :doc:`production` - Production deployment guides
