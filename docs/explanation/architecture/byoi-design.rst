Bring Your Own Instrumentor (BYOI) Design
==========================================

.. note::
   This document explains why HoneyHive uses a "Bring Your Own Instrumentor" architecture and how it solves common problems in LLM observability.

The Problem: Dependency Hell
----------------------------

Traditional observability SDKs face a fundamental challenge in the rapidly evolving LLM ecosystem:

**Version Conflicts**

.. code-block:: text

   Your App → requires openai==1.8.0
   Your App → requires honeyhive-old==0.5.0
   honeyhive-old → requires openai==1.6.0
   
   ❌ Conflict! Cannot install both openai 1.8.0 and 1.6.0

**Forced Dependencies**

When an observability SDK ships with LLM library dependencies:

- You're **locked to specific versions** of LLM libraries
- You **must install libraries** you don't use (bloated dependencies)
- You **can't use newer LLM features** until the SDK updates
- You face **supply chain security** concerns from transitive dependencies

**Real-World Example**

.. code-block:: bash

   # What happens with traditional SDKs:
   pip install traditional-llm-sdk
   # Also installs: openai==1.5.0, anthropic==0.8.0, google-cloud-ai==2.1.0
   # Even if you only use OpenAI!
   
   pip install openai==1.8.0  # You want the latest features
   # ❌ ERROR: Incompatible requirements

The BYOI Solution
-----------------

HoneyHive's BYOI architecture separates concerns:

.. code-block:: text

   Your App → honeyhive (core observability)
   Your App → openai==1.8.0 (your choice)
   Your App → openinference-instrumentation-openai (your choice)

**Key Principles:**

1. **HoneyHive Core**: Minimal dependencies, provides tracing infrastructure
2. **Instrumentors**: Separate packages that understand specific LLM libraries
3. **Your Choice**: You decide which instrumentors to install and use

How It Works
------------

**1. Core SDK (honeyhive)**

The core SDK provides:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   # Just the tracing infrastructure
   tracer = HoneyHiveTracer.init(
       api_key="your-key"   )

**Dependencies**: Only OpenTelemetry and HTTP libraries

**2. Instrumentor Packages (your choice)**

You install only what you need:

.. code-block:: bash

   # Only if you use OpenAI
   pip install openinference-instrumentation-openai
   
   # Only if you use Anthropic  
   # Recommended: Install with Anthropic integration
   pip install honeyhive[openinference-anthropic]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-anthropic
   
   # Only if you use Google AI
   # Recommended: Install with Google AI integration
   pip install honeyhive[openinference-google-ai]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-google-generativeai

**3. Integration at Runtime**

Connect them when initializing:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   # Bring your own instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       # Simplified API - no project parameter needed
       instrumentors=[OpenAIInstrumentor()]  # Your choice!
   )

Benefits of BYOI
----------------

**Dependency Freedom**

.. code-block:: bash

   # You control LLM library versions
   pip install openai==1.8.0        # Latest features
   pip install anthropic==0.12.0    # Latest version
   pip install honeyhive            # No conflicts!

**Minimal Installation**

.. code-block:: bash

   # Only install what you use
   pip install honeyhive                              # Core (5 deps)
   pip install openinference-instrumentation-openai  # Only if needed

**Future-Proof Architecture**

.. code-block:: python

   # New LLM provider? Just add its instrumentor
   from new_llm_instrumentor import NewLLMInstrumentor
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[
           OpenAIInstrumentor(),     # Existing
           NewLLMInstrumentor()      # New provider
       ]
   )

**Supply Chain Security**

- **Fewer dependencies** = smaller attack surface
- **Explicit choices** = you audit what you install
- **Community instrumentors** = distributed maintenance

Supported Instrumentor Providers
---------------------------------

HoneyHive supports multiple instrumentor providers through its BYOI architecture:

**OpenInference Instrumentors**

- **Open source** and community-driven
- **OpenTelemetry native** for standardization
- **LLM-focused** with rich semantic conventions
- **Multi-provider** support from day one

**OpenLLMetry Instrumentors**

- **Comprehensive LLM coverage** across providers
- **Production-ready** instrumentation
- **Active development** and maintenance
- **Enterprise support** available

**Custom Instrumentors**

- **Build your own** for proprietary systems
- **OpenTelemetry standards** compliance
- **Full control** over instrumentation behavior

**Example Instrumentor Installation:**

.. code-block:: bash

   # OpenInference Providers
   pip install openinference-instrumentation-openai
   # Recommended: Install with Anthropic integration
   pip install honeyhive[openinference-anthropic]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-anthropic
   # Recommended: Install with Google AI integration
   pip install honeyhive[openinference-google-ai]
   
   # Alternative: Manual installation
   pip install honeyhive openinference-instrumentation-google-generativeai
   
   # OpenLLMetry Providers (alternative)
   pip install openllmetry[openai]
   pip install openllmetry[anthropic]
   pip install openllmetry[google]
   
   # Framework Support
   pip install openinference-instrumentation-llamaindex
   pip install openinference-instrumentation-langchain

.. note::
   **Compatibility Matrix Coming Soon**
   
   A comprehensive compatibility matrix with full testing and generation documentation for all supported instrumentor providers is in development. This will include detailed installation guides, testing results, and performance benchmarks for each provider.

**Custom Instrumentors:**

You can also build custom instrumentors for proprietary or new LLM providers:

.. code-block:: python

   from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
   
   class CustomLLMInstrumentor(BaseInstrumentor):
       def _instrument(self, **kwargs):
           # Your custom instrumentation logic
           pass
       
       def _uninstrument(self, **kwargs):
           # Cleanup logic
           pass

Implementation Details
----------------------

**Runtime Discovery**

The BYOI system works through runtime discovery:

.. code-block:: python

   # HoneyHiveTracer.init() process:
   
   1. Initialize core OpenTelemetry infrastructure
   2. For each instrumentor in the list:
      a. Call instrumentor.instrument()
      b. Register with tracer provider
   3. Set up HoneyHive-specific span processors
   4. Return configured tracer

**Instrumentor Lifecycle**

.. code-block:: python

   class ExampleInstrumentor(BaseInstrumentor):
       def _instrument(self, **kwargs):
           # Patch the target library
           # Add OpenTelemetry spans
           # Set LLM-specific attributes
           pass
       
       def _uninstrument(self, **kwargs):
           # Remove patches
           # Clean up resources
           pass

**No Monkey Patching by Default**

HoneyHive core doesn't monkey patch anything. Only instrumentors modify library behavior, and only when explicitly requested.

Migration Examples
------------------

**From All-in-One SDKs**

.. code-block:: python

   # Old way (hypothetical all-in-one SDK)
   from llm_observability import LLMTracer
   
   # Forces specific versions of openai, anthropic, etc.
   tracer = LLMTracer(api_key="key")

.. code-block:: python

   # New way (BYOI)
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   # You control openai version
   tracer = HoneyHiveTracer.init(
       api_key="key",
       instrumentors=[OpenAIInstrumentor()]
   )

**Adding New Providers**

.. code-block:: python

   # Before: Wait for SDK update to support new provider
   # After: Install community instrumentor or build your own
   
   pip install openinference-instrumentation-newprovider
   
   tracer = HoneyHiveTracer.init(
       instrumentors=[
           OpenAIInstrumentor(),
           NewProviderInstrumentor()  # Immediate support
       ]
   )

Best Practices
--------------

**Start Minimal**

.. code-block:: python

   # Begin with just what you need
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]  # Only OpenAI
   )

**Add Incrementally**

.. code-block:: python

   # Add providers as you adopt them
   tracer = HoneyHiveTracer.init(
       instrumentors=[
           OpenAIInstrumentor(),
           AnthropicInstrumentor(),    # Added Anthropic
           GoogleGenAIInstrumentor()   # Added Google AI
       ]
   )

**Version Pinning**

.. code-block:: bash

   # Pin versions for reproducible builds
   openai==1.8.0
   anthropic==0.12.0
   openinference-instrumentation-openai==0.1.2
   honeyhive>=0.1.0

**Testing Strategy**

.. code-block:: python

   # Test without instrumentors for unit tests
   tracer = HoneyHiveTracer.init(
       instrumentors=[]  # No automatic tracing
   )
   
   # Test with instrumentors for integration tests
   tracer = HoneyHiveTracer.init(
       instrumentors=[OpenAIInstrumentor()]
   )

Trade-offs and Limitations
--------------------------

**Trade-offs**

**Pros:**
- ✅ No dependency conflicts
- ✅ Minimal required dependencies
- ✅ Future-proof architecture
- ✅ Community-driven instrumentors
- ✅ Custom instrumentor support

**Cons:**
- ❌ Requires explicit instrumentor installation
- ❌ More setup steps than all-in-one SDKs
- ❌ Need to track instrumentor compatibility
- ❌ Potential for instrumentor version mismatches

**When BYOI Might Not Be Ideal**

- **Prototype projects** where setup speed matters more than flexibility
- **Single LLM provider** applications that will never change
- **Teams unfamiliar** with dependency management concepts

**Mitigation Strategies: Ecosystem-Specific Package Groups**

HoneyHive provides industry-leading ecosystem-specific convenience groupings that simplify BYOI setup while maintaining maximum flexibility:

.. code-block:: bash

   # Ecosystem-specific integration groups (RECOMMENDED)
   pip install honeyhive[openinference-openai]      # OpenAI via OpenInference
   pip install honeyhive[openinference-langchain]   # LangChain via OpenInference
   pip install honeyhive[openinference-anthropic]   # Anthropic via OpenInference
   
   # Multi-ecosystem installation
   pip install honeyhive[openinference-openai,openinference-anthropic]
   
   # Convenience groups for common scenarios
   pip install honeyhive[all-openinference]            # All OpenInference integrations
   pip install honeyhive[openinference-llm-providers]  # Popular LLM providers only

**Key Benefits of Ecosystem-Specific Groups:**

- **🚀 Future-Proof**: Pattern ready for multiple instrumentor ecosystems
- **🎯 Clear Attribution**: Know exactly which instrumentor ecosystem you're using
- **📦 Optimal Dependencies**: Install only what you need for each ecosystem
- **🔧 Easy Debugging**: Clear package correlation for troubleshooting
- **⚡ Quick Setup**: One command installs instrumentor + provider SDK

**Practical BYOI Examples with Ecosystem Groups**

.. code-block:: python

   # Example 1: Quick OpenAI setup with ecosystem-specific group
   # pip install honeyhive[openinference-openai]
   
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       instrumentors=[OpenAIInstrumentor()]  # Auto-installed via group
   )

.. code-block:: python

   # Example 2: Multi-provider setup with convenience groups
   # pip install honeyhive[openinference-llm-providers]
   
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   
   tracer = HoneyHiveTracer.init(
       api_key="your-key",
       instrumentors=[
           OpenAIInstrumentor(),      # OpenAI via OpenInference
           AnthropicInstrumentor()    # Anthropic via OpenInference
       ]
   )

.. code-block:: bash

   # Example 3: Framework integration with ecosystem clarity
   pip install honeyhive[openinference-langchain]
   # Installs: openinference-instrumentation-langchain + langchain

This approach provides the best of both worlds: **BYOI flexibility** with **ecosystem-specific convenience**.

Future Evolution
----------------

**Multi-Ecosystem Support (Coming Soon)**

The ecosystem-specific package groups enable future support for multiple instrumentor ecosystems:

.. code-block:: bash

   # Current: OpenInference ecosystem
   pip install honeyhive[openinference-openai]
   pip install honeyhive[openinference-langchain]
   
   # Future: OpenLLMetry ecosystem
   pip install honeyhive[openllmetry-openai]
   pip install honeyhive[openllmetry-langchain]
   
   # Future: Custom enterprise ecosystems  
   pip install honeyhive[enterprise-openai]
   pip install honeyhive[acme-corp-langchain]

This pattern provides **unlimited scalability** for instrumentor ecosystem adoption while maintaining the core BYOI principles.

**Upcoming Features**

1. **Instrumentor Registry**: Discover available instrumentors across ecosystems
2. **Compatibility Matrix**: Track tested version combinations per ecosystem
3. **Auto-detection**: Suggest instrumentors based on installed packages
4. **Bundle Packages**: Pre-configured combinations for common use cases
5. **Ecosystem Marketplace**: Community hub for instrumentor ecosystem discovery

**Community Growth**

The BYOI model enables:

- **Community contributions** to instrumentor development
- **Faster adoption** of new LLM providers
- **Specialized instrumentors** for niche use cases
- **Corporate instrumentors** for proprietary systems

Conclusion
----------

The BYOI architecture represents a fundamental shift from monolithic observability SDKs to composable, dependency-free systems. While it requires slightly more setup, it provides:

- **Long-term maintainability** through dependency isolation
- **Flexibility** to adopt new LLM technologies quickly
- **Community-driven development** of instrumentors
- **Production-ready reliability** without version conflicts

This design philosophy aligns with modern software engineering practices of loose coupling, explicit dependencies, and composable architectures.

**Next Steps:**

- :doc:`../../tutorials/03-llm-integration` - Try BYOI integration
- :doc:`../../how-to/integrations/index` - Integration patterns
- :doc:`../concepts/llm-observability` - LLM observability concepts
