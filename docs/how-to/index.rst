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

Essential setup and configuration:

.. toctree::
   :maxdepth: 1

   troubleshooting

Integrate with LLM Providers
-----------------------------

Connect OpenAI, Anthropic, Google AI, and more:

.. toctree::
   :maxdepth: 1

   integrations/index

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

**SDK Development Testing**: For testing the HoneyHive SDK itself, see :doc:`../development/testing/index`.


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
   deployment/production

Build Common Patterns
----------------------

Implement proven architectural patterns:

.. toctree::
   :maxdepth: 1

   common-patterns

**Quick Solutions:**

- :doc:`troubleshooting` - Fix common issues and setup problems
- :doc:`integrations/openai` - Add OpenAI tracing in 5 minutes  
- :doc:`advanced-tracing/custom-spans` - Create custom trace spans
- :doc:`integrations/multi-provider` - Use multiple LLM providers
- :doc:`evaluation/index` - Set up basic evaluation

**Production Workflows:**

- :doc:`deployment/production` - Deploy HoneyHive to production
- :doc:`monitoring/index` - Set up monitoring and alerts
- :doc:`evaluation/index` - Build comprehensive evaluation pipelines
- :doc:`common-patterns` - Implement resilient agent patterns

Getting Help
------------

If you can't find what you're looking for:

1. Check :doc:`troubleshooting` for common issues
2. Search the :doc:`../reference/index` for API details
3. Read :doc:`../explanation/index` for conceptual understanding
4. Join our `Discord community <https://discord.gg/honeyhive>`_
5. Email support@honeyhive.ai

**Contributing:**

Found a gap in our guides? We'd love to add more how-to content based on real user needs. Please let us know what problems you're trying to solve!
