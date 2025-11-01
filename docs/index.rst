HoneyHive Python SDK Documentation
==================================

**LLM Observability and Evaluation Platform**

The HoneyHive Python SDK provides comprehensive observability, tracing, and evaluation capabilities for LLM applications with OpenTelemetry integration and a "Bring Your Own Instrumentor" architecture.

.. note::
   **Project Configuration**: The ``project`` parameter is required when initializing the tracer. This identifies which HoneyHive project your traces belong to and must match your project name in the HoneyHive dashboard.

🚀 **Quick Start**

New to HoneyHive? Start here:

.. raw:: html

   <div class="quick-start-grid">
   <a href="tutorials/01-setup-first-tracer.html" class="quick-start-card">
     <h3>🎯 5-Minute Quickstart</h3>
     <p>Get tracing working in 5 minutes</p>
   </a>
   <a href="tutorials/02-add-llm-tracing-5min.html" class="quick-start-card">
     <h3>🤖 LLM Integration</h3>
     <p>Add OpenAI, Anthropic, or Google AI tracing</p>
   </a>
   </div>

.. raw:: html

   <style>
   .quick-start-grid {
     display: grid;
     grid-template-columns: 1fr 1fr;
     gap: 1rem;
     margin: 1rem 0;
   }
   .quick-start-card {
     display: block;
     padding: 1rem;
     border: 1px solid #ddd;
     border-radius: 4px;
     text-decoration: none;
     color: inherit;
   }
   .quick-start-card:hover {
     border-color: #2980b9;
     background-color: #f8f9fa;
   }
   .quick-start-card h3 {
     margin-top: 0;
     color: #2980b9;
   }
   </style>

📚 **Documentation Structure**

**Documentation Sections:**

.. raw:: html

   <div class="doc-sections">
   <div class="doc-card">
     <h3><a href="tutorials/index.html">📖 Tutorials</a></h3>
     <p>Step-by-step guides that take you through building complete examples. Perfect for learning by doing.</p>
     <a href="tutorials/01-setup-first-tracer.html" class="quick-link">→ Quick Start</a>
   </div>
   <div class="doc-card">
     <h3><a href="how-to/index.html">🛠️ How-to Guides</a></h3>
     <p>Practical guides for solving specific problems. Jump straight to solutions for your use case.</p>
     <a href="how-to/index.html#troubleshooting" class="quick-link">→ Troubleshooting</a>
   </div>
   <div class="doc-card">
     <h3><a href="reference/index.html">📋 Reference</a></h3>
     <p>Comprehensive API documentation. Look up exact parameters, return values, and technical specifications.</p>
     <a href="reference/api/tracer.html" class="quick-link">→ API Reference</a>
   </div>
   <div class="doc-card">
     <h3><a href="explanation/index.html">💡 Explanation</a></h3>
     <p>Conceptual guides explaining why HoneyHive works the way it does. Understand the design and architecture.</p>
     <a href="explanation/architecture/byoi-design.html" class="quick-link">→ BYOI Design</a>
   </div>
   <div class="doc-card">
     <h3><a href="changelog.html">📝 Changelog</a></h3>
     <p>Release history, version notes, and upgrade guides. Stay updated with latest changes.</p>
     <a href="changelog.html" class="quick-link">→ Latest Release</a>
   </div>
   <div class="doc-card">
     <h3><a href="development/index.html">🔧 SDK Development</a></h3>
     <p>For contributors and maintainers working on the SDK itself. Testing practices and development standards.</p>
     <a href="development/index.html#testing" class="quick-link">→ SDK Testing</a>
   </div>
   </div>

.. raw:: html

   <style>
   .doc-sections {
     display: grid;
     grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
     gap: 1.5rem;
     margin: 2rem 0;
   }
   .doc-card {
     padding: 1.5rem;
     border: 1px solid #ddd;
     border-radius: 8px;
     background: #f8f9fa;
     box-shadow: 0 2px 4px rgba(0,0,0,0.1);
     transition: transform 0.2s ease, box-shadow 0.2s ease;
   }
   .doc-card:hover {
     transform: translateY(-2px);
     box-shadow: 0 4px 8px rgba(0,0,0,0.15);
     border-color: #2980b9;
   }
   .doc-card h3 {
     margin-top: 0;
     margin-bottom: 0.5rem;
   }
   .doc-card h3 a {
     color: #2980b9;
     text-decoration: none;
   }
   .doc-card h3 a:hover {
     text-decoration: underline;
   }
   .doc-card p {
     margin-bottom: 0.75rem;
     color: #555;
   }
   .quick-link {
     display: inline-block;
     color: #2980b9;
     text-decoration: none;
     font-weight: 500;
     margin-top: 0.5rem;
   }
   .quick-link:hover {
     text-decoration: underline;
   }
   </style>

🔄 **Key Features**

**Bring Your Own Instrumentor (BYOI) Architecture**
   Avoid dependency conflicts by choosing exactly which LLM libraries to instrument. Supports multiple instrumentor providers:
   
   - OpenInference
   - Traceloop
   - Build your own custom instrumentors

**Multi-Instance Tracer Support**
   Create independent tracer instances for different environments, workflows, or services within the same application.

**Zero Code Changes for LLM Tracing**
   Add comprehensive observability to existing LLM provider code without modifications:
   
   - OpenAI
   - Anthropic
   - Google AI

**Production-Ready Evaluation**
   Built-in and custom evaluators with threading support for high-performance LLM evaluation workflows.

**OpenTelemetry Native**
   Built on industry-standard OpenTelemetry for maximum compatibility and future-proofing.

📖 **Getting Started Path**

**👋 New to HoneyHive?**

1. :doc:`tutorials/01-setup-first-tracer` - Set up your first tracer in minutes
2. :doc:`tutorials/02-add-llm-tracing-5min` - Add LLM tracing to existing apps
3. :doc:`tutorials/03-enable-span-enrichment` - Enrich traces with metadata
4. :doc:`tutorials/04-configure-multi-instance` - Configure multiple tracers

**🔧 Solving Specific Problems?**

- :doc:`how-to/index` - Fix common issues (see Troubleshooting section)
- :doc:`development/index` - SDK testing practices
- :doc:`how-to/deployment/production` - Deploy to production
- :doc:`how-to/integrations/openai` - OpenAI integration patterns
- :doc:`how-to/evaluation/index` - Evaluation and analysis

**📚 Need Technical Details?**

- :doc:`reference/api/tracer` - HoneyHiveTracer API
- :doc:`reference/api/decorators` - @trace and @evaluate decorators
- :doc:`reference/configuration/environment-vars` - Environment variables
- :doc:`explanation/index` - Python & instrumentor compatibility

**🤔 Want to Understand the Design?**

- :doc:`explanation/architecture/byoi-design` - Why "Bring Your Own Instrumentor"
- :doc:`explanation/concepts/llm-observability` - LLM observability concepts
- :doc:`explanation/architecture/overview` - System architecture

🔗 **Main Documentation Sections**

.. toctree::
   :maxdepth: 1

   tutorials/index
   how-to/index
   reference/index
   explanation/index
   changelog
   development/index

📦 **Installation**

.. code-block:: bash

   # Core SDK only (minimal dependencies)
   pip install honeyhive
   
   # With LLM provider support (recommended)
   pip install honeyhive[openinference-openai]      # OpenAI via OpenInference
   pip install honeyhive[openinference-anthropic]   # Anthropic via OpenInference
   pip install honeyhive[all-openinference]         # All OpenInference integrations

🔧 **Quick Example**

.. raw:: html

   <div class="code-example">
   <div class="code-tabs">
     <button class="tab-button active" onclick="showTab(event, 'basic-example')">Basic Usage</button>
     <button class="tab-button" onclick="showTab(event, 'advanced-example')">With Evaluation</button>
     <button class="tab-button" onclick="showTab(event, 'multi-llm')">Multi-LLM</button>
   </div>

   <div id="basic-example" class="tab-content active">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   # Initialize with BYOI architecture
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project"
   )
   
   # Initialize instrumentor separately (correct pattern)
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # Use @trace for custom functions
   @trace(tracer=tracer)
   def analyze_sentiment(text: str) -> str:
       # OpenAI calls automatically traced via instrumentor
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": f"Analyze sentiment: {text}"}]
       )
       return response.choices[0].message.content
   
   # Both the function and the OpenAI call are traced!
   result = analyze_sentiment("I love this new feature!")

.. raw:: html

   </div>
   <div id="advanced-example" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, evaluate
   from honeyhive.models import EventType
   from honeyhive.evaluation import QualityScoreEvaluator
   from openinference.instrumentation.openai import OpenAIInstrumentor
   import openai
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project"
   )
   
   # Initialize instrumentor separately (correct pattern)
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)
   
   # Add automatic evaluation
   quality_evaluator = QualityScoreEvaluator(criteria=["relevance", "clarity"])
   
   @trace(tracer=tracer, event_type=EventType.model)
   @evaluate(evaluator=quality_evaluator)
   def handle_customer_query(query: str) -> str:
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[
               {"role": "system", "content": "You are a helpful customer service agent."},
               {"role": "user", "content": query}
           ]
       )
       return response.choices[0].message.content
   
   # Automatically traced AND evaluated for quality
   result = handle_customer_query("How do I reset my password?")

.. raw:: html

   </div>
   <div id="multi-llm" class="tab-content">

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   import openai
   import anthropic
   
   # Multi-provider setup with BYOI
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project"
   )
   
   # Initialize instrumentors separately (correct pattern)
   openai_instrumentor = OpenAIInstrumentor()
   anthropic_instrumentor = AnthropicInstrumentor()
   
   openai_instrumentor.instrument(tracer_provider=tracer.provider)
   anthropic_instrumentor.instrument(tracer_provider=tracer.provider)
   
   @trace(tracer=tracer, event_type=EventType.chain)
   def compare_responses(prompt: str) -> dict:
       # Both calls automatically traced with provider context
       openai_client = openai.OpenAI()
       anthropic_client = anthropic.Anthropic()
       
       openai_response = openai_client.chat.completions.create(
           model="gpt-4", messages=[{"role": "user", "content": prompt}]
       )
       
       anthropic_response = anthropic_client.messages.create(
           model="claude-3-sonnet-20240229", max_tokens=100,
           messages=[{"role": "user", "content": prompt}]
       )
       
       return {
           "openai": openai_response.choices[0].message.content,
           "anthropic": anthropic_response.content[0].text
       }
   
   result = compare_responses("Explain quantum computing simply")

.. raw:: html

   </div>
   </div>
   
   <script>
   function showTab(evt, tabName) {
     var i, tabcontent, tablinks;
     tabcontent = document.getElementsByClassName("tab-content");
     for (i = 0; i < tabcontent.length; i++) {
       tabcontent[i].classList.remove("active");
     }
     tablinks = document.getElementsByClassName("tab-button");
     for (i = 0; i < tablinks.length; i++) {
       tablinks[i].classList.remove("active");
     }
     document.getElementById(tabName).classList.add("active");
     evt.currentTarget.classList.add("active");
   }
   </script>
   
   <style>
   .code-example {
     margin: 1.5rem 0;
     border: 1px solid #ddd;
     border-radius: 8px;
     overflow: hidden;
   }
   .code-tabs {
     display: flex;
     background: #f8f9fa;
     border-bottom: 1px solid #ddd;
   }
   .tab-button {
     background: none;
     border: none;
     padding: 12px 20px;
     cursor: pointer;
     font-weight: 500;
     color: #666;
     transition: all 0.2s ease;
   }
   .tab-button:hover {
     background: #e9ecef;
     color: #2980b9;
   }
   .tab-button.active {
     background: #2980b9;
     color: white;
     border-bottom: 2px solid #2980b9;
   }
   .tab-content {
     display: none;
     padding: 0;
   }
   .tab-content.active {
     display: block;
   }
   .tab-content .highlight {
     margin: 0;
     border-radius: 0;
   }
   </style>

🆘 **Need Help?**

- **Common Issues**: :doc:`how-to/index` (Troubleshooting section)
- **Discord Community**: `Join our Discord <https://discord.gg/honeyhive>`_
- **GitHub Issues**: `Report bugs <https://github.com/honeyhiveai/python-sdk/issues>`_
- **Email Support**: support@honeyhive.ai

📈 **What's New in This Version**

- **🔄 Major Architectural Refactor**: Multi-instance tracer support
- **📦 BYOI Architecture**: Bring Your Own Instrumentor for dependency freedom
- **⚡ Enhanced Performance**: Optimized for production workloads
- **🔧 Improved Developer Experience**: Simplified APIs with powerful capabilities
- **📊 Advanced Evaluation**: Threading support for high-performance evaluation

📝 **Release History**: See :doc:`changelog` for complete version history and upgrade notes

🔗 **External Links**

- `HoneyHive Platform <https://honeyhive.ai>`_
- `Python SDK on PyPI <https://pypi.org/project/honeyhive/>`_
- `GitHub Repository <https://github.com/honeyhiveai/python-sdk>`_
- `OpenInference Instrumentors <https://github.com/Arize-ai/openinference>`_ (supported instrumentor provider)
- `Traceloop Instrumentors <https://github.com/traceloop/openllmetry>`_ - Enhanced metrics and production optimizations
- Compatibility Matrix (full testing documentation coming soon)

Indices and Tables
==================

* :ref:`genindex`
* :ref:`search`