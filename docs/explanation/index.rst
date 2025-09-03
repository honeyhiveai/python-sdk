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

Core Design Principles
~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   architecture/overview
   architecture/byoi-design
   architecture/diagrams

Key Concepts
------------

Fundamental Concepts
~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   concepts/tracing-fundamentals
   concepts/llm-observability

Design Decisions
----------------

Why We Built It This Way
~~~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2



Comparisons
-----------

How HoneyHive Relates to Other Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2



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
