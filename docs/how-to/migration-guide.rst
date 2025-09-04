Migration Guide: OpenInference ↔ OpenLLMetry
==============================================

This guide helps you migrate between OpenInference and OpenLLMetry instrumentors for LLM provider integrations.

.. contents:: Table of Contents
   :local:
   :depth: 2

When to Migrate
---------------

**Migrate to OpenLLMetry when you need:**
- Enhanced LLM-specific metrics and cost tracking
- Production-optimized performance monitoring
- Detailed token usage analysis
- Advanced error handling and retry mechanisms

**Migrate to OpenInference when you need:**
- Lightweight, minimal overhead instrumentation
- Open-source community support
- Simple development and testing setups
- Consistent API across all providers

Migration is Safe and Reversible
---------------------------------

**Key Points:**
- Both instrumentors use the same OpenTelemetry standard
- Your existing HoneyHive traces remain unchanged
- No data loss during migration
- You can switch back at any time
- Code changes are minimal (just import statements)

OpenInference → OpenLLMetry Migration
-------------------------------------

**Step 1: Update Dependencies**

Replace OpenInference packages with OpenLLMetry equivalents:

.. code-block:: bash

   # Before: OpenInference packages
   pip uninstall openinference-instrumentation-openai
   pip uninstall openinference-instrumentation-anthropic
   
   # After: OpenLLMetry packages
   pip install opentelemetry-instrumentation-openai
   pip install opentelemetry-instrumentation-anthropic

**Or use HoneyHive's convenience packages:**

.. code-block:: bash

   # Before: OpenInference extras
   pip install honeyhive[openinference-openai,openinference-anthropic]
   
   # After: OpenLLMetry extras
   pip install honeyhive[traceloop-openai,traceloop-anthropic]

**Step 2: Update Import Statements**

Change your import statements to use OpenLLMetry packages:

.. code-block:: python

   # Before: OpenInference imports
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor
   
   # After: OpenLLMetry imports
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

**Step 3: Update Initialization (No Changes Needed)**

Your HoneyHive initialization code remains identical:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   # Import statements changed above, but usage is identical
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
   
   # Initialization code is identical
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[
           OpenAIInstrumentor(),
           AnthropicInstrumentor()
       ]
   )

**Step 4: Your LLM Code Remains Unchanged**

All your existing LLM calls work exactly the same:

.. code-block:: python

   import openai
   import anthropic
   
   # These calls work identically with both instrumentors
   openai_client = openai.OpenAI()
   anthropic_client = anthropic.Anthropic()
   
   # No changes needed to your LLM calls
   response = openai_client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello!"}]
   )

OpenLLMetry → OpenInference Migration
-------------------------------------

**Step 1: Update Dependencies**

Replace OpenLLMetry packages with OpenInference equivalents:

.. code-block:: bash

   # Before: OpenLLMetry packages
   pip uninstall opentelemetry-instrumentation-openai
   pip uninstall opentelemetry-instrumentation-anthropic
   
   # After: OpenInference packages
   pip install openinference-instrumentation-openai
   pip install openinference-instrumentation-anthropic

**Or use HoneyHive's convenience packages:**

.. code-block:: bash

   # Before: OpenLLMetry extras
   pip install honeyhive[traceloop-openai,traceloop-anthropic]
   
   # After: OpenInference extras
   pip install honeyhive[openinference-openai,openinference-anthropic]

**Step 2: Update Import Statements**

Change your import statements to use OpenInference packages:

.. code-block:: python

   # Before: OpenLLMetry imports
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor
   from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
   
   # After: OpenInference imports
   from openinference.instrumentation.openai import OpenAIInstrumentor
   from openinference.instrumentation.anthropic import AnthropicInstrumentor

**Step 3: Everything Else Remains Identical**

Your HoneyHive initialization and LLM code work exactly the same.

Provider-Specific Migration Notes
---------------------------------

**OpenAI**
- Both instrumentors support identical OpenAI SDK versions
- All model types (GPT-3.5, GPT-4, etc.) work with both
- Function calling and streaming are supported by both

**Anthropic**
- Both instrumentors support Claude 3 models
- Message API and legacy completion API both supported
- Streaming responses work with both instrumentors

**Google AI**
- Both instrumentors support Gemini models
- Google AI Studio and Vertex AI both supported
- Multi-modal inputs (text + images) work with both

**AWS Bedrock**
- Both instrumentors support all Bedrock model providers
- Cross-region access works with both
- Custom model endpoints supported by both

**Azure OpenAI**
- Both instrumentors use the same OpenAI instrumentor
- Azure-specific authentication works with both
- Deployment-specific endpoints supported by both

**MCP (Model Context Protocol)**
- Both instrumentors support MCP client-server communication
- Tool orchestration tracing works with both
- Async/await patterns supported by both

**Google ADK**
- Only OpenInference instrumentor is available
- No migration needed - continue using OpenInference

Mixed Instrumentor Setups
-------------------------

You can use both instrumentor types in the same application:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   # Mix OpenInference and OpenLLMetry
   from openinference.instrumentation.anthropic import AnthropicInstrumentor as OIAnthropic
   from opentelemetry.instrumentation.openai import OpenAIInstrumentor as OLOpenAI
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       instrumentors=[
           OLOpenAI(),     # OpenLLMetry for OpenAI (enhanced metrics)
           OIAnthropic()   # OpenInference for Anthropic (lightweight)
       ]
   )

**Strategic Mixed Usage:**
- Use OpenLLMetry for high-volume, cost-sensitive providers
- Use OpenInference for occasional or development providers
- Gradually migrate providers based on monitoring needs

Validation After Migration
--------------------------

**1. Verify Traces Are Still Appearing**

Check your HoneyHive dashboard to ensure traces are being captured:

.. code-block:: python

   # Test with a simple LLM call
   import openai
   
   client = openai.OpenAI()
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Test migration"}]
   )
   print("Migration test successful!")

**2. Check Trace Attributes**

Both instrumentors capture similar attributes, but OpenLLMetry may include additional LLM-specific metrics:

- Model name and version
- Token usage (input, output, total)
- Request/response content
- Timing information
- Error details

**3. Monitor Performance**

Compare performance before and after migration:
- Trace collection latency
- Application overhead
- Memory usage
- Network traffic to HoneyHive

Rollback Procedure
------------------

If you need to rollback a migration:

**1. Reinstall Previous Packages**

.. code-block:: bash

   # Rollback to OpenInference
   pip uninstall opentelemetry-instrumentation-openai
   pip install openinference-instrumentation-openai

**2. Revert Import Statements**

.. code-block:: python

   # Change back to previous imports
   from openinference.instrumentation.openai import OpenAIInstrumentor

**3. Restart Your Application**

No other changes needed - your application will work exactly as before.

Common Migration Issues
-----------------------

**Import Errors After Migration**

.. code-block:: bash

   # Solution: Clear Python cache and reinstall
   pip cache purge
   pip uninstall honeyhive
   pip install honeyhive[traceloop-openai]  # or your desired extras

**Traces Not Appearing After Migration**

1. Verify the new instrumentor packages are installed:

.. code-block:: python

   # Check installed packages
   import pkg_resources
   
   try:
       pkg_resources.get_distribution("opentelemetry-instrumentation-openai")
       print("OpenLLMetry OpenAI instrumentor installed")
   except pkg_resources.DistributionNotFound:
       print("OpenLLMetry OpenAI instrumentor NOT installed")

2. Restart your application completely
3. Check HoneyHive API key and project settings

**Performance Differences**

- OpenLLMetry may have slightly higher overhead due to enhanced metrics
- OpenInference is generally lighter weight
- Both are production-ready with minimal performance impact

**Package Conflicts**

If you encounter dependency conflicts:

.. code-block:: bash

   # Create a fresh virtual environment
   python -m venv fresh_env
   source fresh_env/bin/activate  # On Windows: fresh_env\Scripts\activate
   pip install honeyhive[traceloop-openai]  # Install fresh

Migration Checklist
--------------------

**Pre-Migration:**
- [ ] Document current instrumentor packages and versions
- [ ] Test current setup to ensure traces are working
- [ ] Backup your requirements.txt or pyproject.toml
- [ ] Plan migration during low-traffic period

**During Migration:**
- [ ] Update package dependencies
- [ ] Change import statements
- [ ] Test with simple LLM calls
- [ ] Verify traces appear in HoneyHive dashboard
- [ ] Check for any error logs

**Post-Migration:**
- [ ] Monitor application performance
- [ ] Validate all LLM providers are working
- [ ] Update documentation and deployment scripts
- [ ] Train team on any new features (if migrating to OpenLLMetry)

Best Practices for Migration
-----------------------------

**1. Migrate One Provider at a Time**

.. code-block:: python

   # Good: Gradual migration
   tracer = HoneyHiveTracer.init(
       instrumentors=[
           OpenAIInstrumentor(),           # Migrated to OpenLLMetry
           OIAnthropicInstrumentor()       # Still using OpenInference
       ]
   )

**2. Test in Development First**

Always test migrations in development/staging before production.

**3. Use Version Pinning**

.. code-block:: bash

   # Good: Pin versions for stability
   pip install opentelemetry-instrumentation-openai==1.20.0

**4. Monitor After Migration**

Set up alerts for:
- Trace collection failures
- Performance regressions
- Error rate increases

**5. Document Your Choice**

Document why you chose each instrumentor type for future team members.

Need Help?
----------

If you encounter issues during migration:

1. Check the :doc:`troubleshooting` guide
2. Review provider-specific integration docs:
   - :doc:`integrations/openai`
   - :doc:`integrations/anthropic`
   - :doc:`integrations/google-ai`
3. Contact HoneyHive support with:
   - Your current instrumentor setup
   - Error messages or logs
   - Steps you've already tried

Remember: Migration between instrumentors is safe, reversible, and requires minimal code changes. Both instrumentor types are production-ready and work seamlessly with HoneyHive's BYOI architecture.
