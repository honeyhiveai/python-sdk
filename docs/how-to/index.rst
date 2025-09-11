How-to Guides
=============

.. note::
   **Problem-oriented documentation**
   
   These guides help you solve specific problems and accomplish particular tasks. They assume you have basic familiarity with HoneyHive and focus on practical solutions.

**Quick Navigation:**

.. contents::
   :local:
   :depth: 2

Overview
--------

How-to guides are organized by problem domain. Each guide provides step-by-step instructions to solve real-world challenges you might encounter when using HoneyHive.

**When to use these guides:**

- You have a specific problem to solve
- You need to integrate with a particular system
- You want to implement a specific pattern or technique
- You're troubleshooting an issue

Getting Started
---------------

Essential setup and configuration guides for HoneyHive SDK usage.

.. toctree::
   :maxdepth: 1

   backwards-compatibility-guide

LLM Provider Integration
-------------------------

Quick solutions for specific provider integration challenges. HoneyHive supports both OpenInference and OpenLLMetry instrumentors to automatically trace LLM calls from any provider with zero code changes.

.. toctree::
   :maxdepth: 1

   integrations/openai
   integrations/anthropic
   integrations/google-ai
   integrations/google-adk
   integrations/bedrock
   integrations/azure-openai
   integrations/mcp
   integrations/multi-provider
   integrations/non-instrumentor-frameworks
   migration-guide

Custom Tracing
--------------

Build sophisticated observability:

.. toctree::
   :maxdepth: 1

   advanced-tracing/index

Testing Your Application
-------------------------

.. note::
   **Testing HoneyHive SDK Usage**
   
   For testing applications that use the HoneyHive SDK, use standard Python testing practices with pytest, unittest, or your preferred testing framework. The SDK is designed to be easily mockable and testable.
   
   For mocking HoneyHive in tests, simply mock the tracer instance or use dependency injection patterns.

.. code-block:: python

   # Example: Mocking HoneyHive in tests
   from unittest.mock import Mock, patch
   import pytest
   
   @patch('honeyhive.HoneyHiveTracer')
   def test_my_traced_function(mock_tracer):
       # Your test code here
       pass

**SDK Development Testing**: For testing the HoneyHive SDK itself, see :doc:`../development/index`.


Evaluate LLM Outputs
---------------------

Set up quality monitoring and evaluation:

.. toctree::
   :maxdepth: 1

   evaluation/index

Monitor in Production
---------------------

Keep applications running reliably:

.. toctree::
   :maxdepth: 1

   monitoring/index
   deployment/pyproject-integration
   deployment/production

Build Common Patterns
----------------------

Implement proven architectural patterns:

.. toctree::
   :maxdepth: 1

   common-patterns

**Quick Solutions:**

- See "Troubleshooting" section below - Fix common issues and setup problems
- :doc:`integrations/openai` - Add OpenAI tracing in 5 minutes  
- :doc:`advanced-tracing/custom-spans` - Create custom trace spans
- :doc:`integrations/multi-provider` - Use multiple LLM providers
- :doc:`evaluation/index` - Set up basic evaluation

**Production Workflows:**

- :doc:`deployment/pyproject-integration` - Include HoneyHive in your pyproject.toml
- :doc:`deployment/production` - Deploy HoneyHive to production
- :doc:`monitoring/index` - Set up monitoring and alerts
- :doc:`evaluation/index` - Build comprehensive evaluation pipelines
- :doc:`common-patterns` - Implement resilient agent patterns

Troubleshooting
---------------

Common issues and step-by-step solutions for HoneyHive integration challenges.

**Not seeing traces in your dashboard?**

1. **Check API key configuration**:

   .. code-block:: python

      import os
      print(f"API Key set: {'HH_API_KEY' in os.environ}")
      print(f"Source set: {'HH_SOURCE' in os.environ}")  # Optional environment identifier

2. **Verify network connectivity**:

   .. code-block:: bash

      # Test HoneyHive API connectivity
      curl -H "Authorization: Bearer YOUR_API_KEY" https://api.honeyhive.ai/health

3. **Check project settings** - Ensure your project name matches exactly in the HoneyHive dashboard.

**Import or installation errors?**

1. **Installation problems**:

   .. code-block:: bash

      # Update pip and install in clean environment
      pip install --upgrade pip
      python -m venv honeyhive-env
      source honeyhive-env/bin/activate  # Linux/Mac
      # honeyhive-env\Scripts\activate   # Windows
      pip install honeyhive

2. **Dependency conflicts**:

   .. code-block:: bash

      # Check for conflicts
      pip check
      
      # Use fresh virtual environment (recommended)
      python -m venv fresh-env
      source fresh-env/bin/activate
      pip install honeyhive

3. **Python version compatibility** - HoneyHive requires Python 3.11+:

   .. code-block:: python

      import sys
      if sys.version_info < (3, 11):
          print("❌ Python 3.11+ required")
      else:
          print("✅ Python version compatible")

**Tracing not working as expected?**

1. **Debug trace collection**:

   .. code-block:: python

      # Enable debug logging
      import logging
      logging.basicConfig(level=logging.DEBUG)
      
      # Check tracer initialization
      from honeyhive import HoneyHiveTracer
      tracer = HoneyHiveTracer.init(
          api_key="your-key",      # Or set HH_API_KEY environment variable
          project="your-project",  # Or set HH_PROJECT environment variable
          source="debug"           # Or set HH_SOURCE environment variable
      )
      print(f"Tracer initialized: {tracer is not None}")

2. **Validate event_type values** - Use proper EventType enum:

   .. code-block:: python

      from honeyhive.models import EventType
      
      # ✅ Correct usage
      with tracer.trace("my_operation", event_type=EventType.tool) as span:
          pass
      
      # ❌ Incorrect - don't use strings
      # event_type="tool"

3. **Instrumentor initialization order** - Initialize tracer before instrumentors:

   .. code-block:: python

      # ✅ Correct order
      from honeyhive import HoneyHiveTracer
      
      # Step 1: Initialize HoneyHive tracer FIRST (without instrumentors)
      tracer = HoneyHiveTracer.init(
          api_key="...",           # Or set HH_API_KEY environment variable
          project="your-project"   # Or set HH_PROJECT environment variable
      )
      
      # Step 2: Initialize instrumentors separately with tracer_provider
      from openinference.instrumentation.openai import OpenAIInstrumentor
      instrumentor = OpenAIInstrumentor()
      instrumentor.instrument(tracer_provider=tracer.provider)

   .. warning::
      **Common Issue**: If you see "⚠️ Existing provider doesn't support span processors", this indicates a ProxyTracerProvider issue. The fix above resolves this by ensuring HoneyHive creates a real TracerProvider first.

For additional troubleshooting resources, see the HoneyHive documentation or contact support.

Getting Help
------------

If you can't find what you're looking for:

1. Check the "Troubleshooting" section above for common issues
2. Search the :doc:`../reference/index` for API details
3. Read :doc:`../explanation/index` for conceptual understanding
4. Join our `Discord community <https://discord.gg/honeyhive>`_
5. Email support@honeyhive.ai

**Contributing:**

Found a gap in our guides? We'd love to add more how-to content based on real user needs. Please let us know what problems you're trying to solve!
