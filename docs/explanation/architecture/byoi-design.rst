Bring Your Own Instrumentor (BYOI) Design
=========================================

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
       api_key="your-key",      # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )

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
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-key",      # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()  # Your choice!
   instrumentor.instrument(tracer_provider=tracer.provider)

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
   
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",  # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentors separately with tracer_provider
   openai_instrumentor = OpenAIInstrumentor()     # Existing
   openai_instrumentor.instrument(tracer_provider=tracer.provider)
   
   new_llm_instrumentor = NewLLMInstrumentor()    # New provider
   new_llm_instrumentor.instrument(tracer_provider=tracer.provider)

**Supply Chain Security**

- **Fewer dependencies** = smaller attack surface
- **Explicit choices** = you audit what you install
- **Community instrumentors** = distributed maintenance

Supported Instrumentor Providers
--------------------------------

HoneyHive supports multiple instrumentor providers through its BYOI architecture:

**OpenInference Instrumentors**

- **Open source** and community-driven
- **OpenTelemetry native** for standardization
- **LLM-focused** with rich semantic conventions
- **Multi-provider** support from day one

**Traceloop Instrumentors**

- **Enhanced metrics and monitoring** capabilities
- **Production-ready** instrumentation with detailed cost tracking
- **OpenTelemetry-based** for standardization
- **Extended provider support** with performance analytics

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
   
   # Traceloop Providers (alternative - enhanced metrics)
   pip install opentelemetry-instrumentation-openai
   pip install opentelemetry-instrumentation-anthropic
   pip install opentelemetry-instrumentation-bedrock

.. note::
   **Compatibility Matrix Available**
   
   A comprehensive compatibility matrix with full testing documentation for all supported instrumentor providers is available in the :doc:`../index` section. This includes:
   
   - Detailed installation guides
   - Testing results and compatibility status
   - Python version support matrix

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
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",  # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

**Adding New Providers**

.. code-block:: python

   # Before: Wait for SDK update to support new provider
   # After: Install community instrumentor or build your own
   
   pip install openinference-instrumentation-newprovider
   
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",  # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = 
           OpenAIInstrumentor(),
           NewProviderInstrumentor()  # Immediate support
       
   instrumentor.instrument(tracer_provider=tracer.provider)

Best Practices
--------------

**Start Minimal**

.. code-block:: python

   # Begin with just what you need
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",  # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   openai_instrumentor = OpenAIInstrumentor()  # Only OpenAI
   openai_instrumentor.instrument(tracer_provider=tracer.provider)

**Add Incrementally**

.. code-block:: python

   # Add providers as you adopt them
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",  # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = 
           OpenAIInstrumentor(),
           AnthropicInstrumentor(),    # Added Anthropic
           GoogleGenAIInstrumentor()   # Added Google AI
       
   instrumentor.instrument(tracer_provider=tracer.provider)

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
       project="test-project",  # Or set HH_PROJECT environment variable
       test_mode=True           # No automatic tracing (or set HH_TEST_MODE=true)
   )
   
   # Test with instrumentors for integration tests
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",  # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

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
   pip install honeyhive[openinference-anthropic]   # Anthropic via OpenInference
   pip install honeyhive[openinference-bedrock]     # AWS Bedrock via OpenInference
   pip install honeyhive[openinference-google-ai]   # Google AI via OpenInference
   
   # Multi-ecosystem installation
   pip install honeyhive[openinference-openai,openinference-anthropic]
   
   # Convenience groups for common scenarios
   pip install honeyhive[all-openinference]         # All OpenInference integrations

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
   
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-key",      # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   openai_instrumentor = OpenAIInstrumentor()  # Auto-installed via group
   openai_instrumentor.instrument(tracer_provider=tracer.provider)

.. code-block:: python

   # Example 2: Multi-provider setup with convenience groups
   # pip install honeyhive[all-openinference]
   
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   
   # Step 1: Initialize HoneyHive tracer first (without instrumentors)
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",  # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor separately with tracer_provider
   instrumentor = 
           OpenAIInstrumentor(),      # OpenAI via OpenInference
           AnthropicInstrumentor()    # Anthropic via OpenInference
       
   instrumentor.instrument(tracer_provider=tracer.provider)

.. code-block:: bash

   # Example 3: Specialized provider integration
   pip install honeyhive[openinference-google-adk]
   # Installs: openinference-instrumentation-google-adk + dependencies

This approach provides the best of both worlds: **BYOI flexibility** with **ecosystem-specific convenience**.

Future Evolution
----------------

**Multi-Ecosystem Support**

The ecosystem-specific package groups support multiple instrumentor ecosystems:

.. code-block:: bash

   # OpenInference ecosystem (community-driven)
   pip install honeyhive[openinference-openai]
   pip install honeyhive[openinference-anthropic]
   pip install honeyhive[openinference-bedrock]
   
   # Traceloop ecosystem (enhanced metrics)
   pip install honeyhive[traceloop-openai]
   pip install honeyhive[traceloop-anthropic]
   pip install honeyhive[traceloop-bedrock]

This pattern provides **unlimited scalability** for instrumentor ecosystem adoption while maintaining the core BYOI principles.

**Available Features**

1. **Compatibility Matrix**: Complete testing documentation for all supported providers (:doc:`../index`)
2. **Python Version Support**: Full validation across Python 3.11, 3.12, 3.13
3. **Dynamic Generation**: Automated maintenance reducing manual work by 75%
4. **Ecosystem-Specific Groups**: Convenient installation patterns for all supported providers

**Future Features**

1. **Instrumentor Registry**: Discover available instrumentors across ecosystems
2. **Auto-detection**: Suggest instrumentors based on installed packages
3. **Bundle Packages**: Pre-configured combinations for common use cases

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

This design philosophy aligns with modern software engineering practices:

- Loose coupling
- Explicit dependencies  
- Composable architectures

Troubleshooting BYOI Integration
--------------------------------

**Common Issue: "Existing provider doesn't support span processors"**

This warning indicates that OpenTelemetry's default ProxyTracerProvider is being used, which doesn't support the span processors needed for HoneyHive integration.

**Root Cause**: ProxyTracerProvider is OpenTelemetry's placeholder provider that only supports basic tracing operations.

**Solution**: Follow the correct initialization order:

.. code-block:: python

   # ✅ Correct: HoneyHive creates real TracerProvider first
   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   # Step 1: Initialize HoneyHive tracer (creates real TracerProvider)
   tracer = HoneyHiveTracer.init(
       api_key="your-key",      # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   # Step 2: Initialize instrumentor with HoneyHive's provider
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

.. code-block:: python

   # ❌ INCORRECT: Passing instrumentors to init() (causes ProxyTracerProvider bug)
   tracer = HoneyHiveTracer.init(
       api_key="your-key",      # Or set HH_API_KEY environment variable
       project="your-project",  # Or set HH_PROJECT environment variable
       instrumentors=[OpenAIInstrumentor()]  # This causes ProxyTracerProvider bug!
   )
   
   # ✅ CORRECT: Initialize separately
   tracer = HoneyHiveTracer.init(
       api_key="your-key",      # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

**Verification**: Look for these success messages:

- ``🔧 Creating new TracerProvider as main provider``
- ``✓ OTLP exporter configured to send spans``
- ``🔍 SPAN INTERCEPTED`` (during LLM calls)

Provider Strategy Intelligence
------------------------------

**Critical Feature: Preventing Span Loss**

HoneyHive includes intelligent provider detection to prevent a common but serious issue: **instrumentor spans being lost in empty TracerProviders**.

**The Problem:**

.. code-block:: python

   # Common scenario that causes span loss:
   
   # 1. Application creates empty TracerProvider
   empty_provider = TracerProvider()  # No processors, no exporters
   trace.set_tracer_provider(empty_provider)
   
   # 2. Instrumentors create spans on empty provider
   openai_client = OpenAI()  # Creates spans on empty_provider
   response = openai_client.chat.completions.create(...)  # Span lost!
   
   # 3. HoneyHive creates isolated provider (traditional approach)
   honeyhive_provider = TracerProvider()  # Separate provider
   # Result: OpenAI spans go to empty provider → disappear forever

**HoneyHive's Solution: Provider Strategy Intelligence**

HoneyHive automatically detects the OpenTelemetry environment and chooses the optimal strategy:

.. code-block:: text

   Provider Detection Logic:
   
   1. Detect existing provider type (NoOp/Proxy/TracerProvider/Custom)
   2. Check if TracerProvider is functioning (has processors/exporters)
   3. Choose strategy:
      - MAIN_PROVIDER: Replace non-functioning providers
      - INDEPENDENT_PROVIDER: Coexist with functioning providers

**Strategy 1: Main Provider (Prevent Span Loss)**

.. code-block:: python

   # When: NoOp, Proxy, or Empty TracerProvider detected
   # HoneyHive becomes the global provider
   
   # Before (empty provider):
   empty_provider = TracerProvider()  # No processors
   trace.set_tracer_provider(empty_provider)
   
   # HoneyHive initialization:
   tracer = HoneyHiveTracer.init(
       api_key="your-key",      # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   # Result: tracer.is_main_provider = True
   
   # After (HoneyHive provider):
   # trace.get_tracer_provider() → HoneyHive's TracerProvider
   # OpenAI spans → HoneyHive backend ✅

**Strategy 2: Independent Provider (Coexistence)**

.. code-block:: python

   # When: Functioning TracerProvider with processors detected
   # HoneyHive creates isolated provider
   
   # Existing functioning provider:
   existing_provider = TracerProvider()
   existing_provider.add_span_processor(ConsoleSpanProcessor())
   trace.set_tracer_provider(existing_provider)
   
   # HoneyHive initialization:
   tracer = HoneyHiveTracer.init(
       api_key="your-key",      # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   # Result: tracer.is_main_provider = False
   
   # Coexistence:
   # OpenAI spans → existing_provider → console ✅
   # HoneyHive spans → honeyhive_provider → HoneyHive backend ✅

**Verification Commands:**

.. code-block:: python

   # Check which strategy was chosen:
   tracer = HoneyHiveTracer.init(
       api_key="your-key",      # Or set HH_API_KEY environment variable
       project="your-project"   # Or set HH_PROJECT environment variable
   )
   
   if tracer.is_main_provider:
       print("✅ HoneyHive is main provider - all spans captured")
   else:
       print("✅ HoneyHive is independent - coexisting with other system")

**Next Steps:**

- :doc:`../../tutorials/02-add-llm-tracing-5min` - Try BYOI integration
- :doc:`../../how-to/index` - Integration patterns
- :doc:`../concepts/llm-observability` - LLM observability concepts
