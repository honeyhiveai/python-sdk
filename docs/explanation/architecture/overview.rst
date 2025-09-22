Architecture Overview
=====================

.. note::
   This document provides a high-level overview of the HoneyHive SDK architecture and how its components work together.

System Overview
---------------

The HoneyHive Python SDK is built around several key architectural principles:

- **OpenTelemetry Native**: Built on industry-standard observability frameworks
- **BYOI (Bring Your Own Instrumentor)**: Flexible dependency management
- **Multi-Instance Support**: Independent tracer instances for complex applications
- **Graceful Degradation**: Never crashes your application

**High-Level Architecture:**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#333333', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph TB
       subgraph "Application Layer"
           UA[User Code]
       end
       
       subgraph "HoneyHive SDK"
           subgraph "SDK Layer"
               T["Tracers<br/>(Multi-Instance)"] 
               API[API Client]
               E[Evaluation]
           end
           
           subgraph "OpenTelemetry Layer"
               TP["TracerProvider<br/>(Smart Management)"]
               SE[Span Exporter]
               I[Instrumentation]
           end
           
           subgraph "Transport Layer"
               H[HTTPX]
               CP[Connection Pool]
               R[Retry Logic]
           end
       end
       
       subgraph "HoneyHive API"
           S[Sessions]
           EV[Events]
           M[Metrics]
       end
       
       UA ==> T
       UA ==> API
       UA ==> E
       
       T ==> TP
       API ==> H
       E ==> API
       
       TP ==> SE
       SE ==> H
       H ==> CP
       CP ==> R
       
       R ==> S
       R ==> EV
       R ==> M
       
       classDef sdkLayer fill:#1a237e,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef otelLayer fill:#e65100,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef transportLayer fill:#ad1457,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef apiLayer fill:#4a148c,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef userLayer fill:#1b5e20,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class T,API,E sdkLayer
       class TP,SE,I otelLayer
       class H,CP,R transportLayer
       class S,EV,M apiLayer
       class UA userLayer

Core Architecture Components
----------------------------

**1. HoneyHiveTracer**

The central component that manages observability:

.. code-block:: text

   HoneyHiveTracer
   ├── OpenTelemetry TracerProvider
   ├── Span Processors
   ├── Exporters (HoneyHive API)
   └── Instrumentor Management

**2. Instrumentor System**

Pluggable components for different LLM providers:

.. code-block:: text

   Instrumentor Architecture
   ├── OpenAI Instrumentor
   ├── Anthropic Instrumentor
   ├── Google AI Instrumentor
   └── Custom Instrumentors

**3. Evaluation Framework**

Built-in and custom evaluation capabilities:

.. code-block:: text

   Evaluation System
   ├── Built-in Evaluators
   ├── Custom Evaluator Base Classes
   ├── Multi-Evaluator Support
   └── Batch Evaluation

**4. Data Pipeline**

How observability data flows through the system:

.. code-block:: text

   Data Flow
   Function Call → Span Creation → Attribute Collection → 
   Evaluation (optional) → Export → HoneyHive Platform

Key Design Decisions
--------------------

**OpenTelemetry Foundation**

Built on OpenTelemetry for:
- Industry standard compliance
- Interoperability with existing tools
- Future-proofing
- Community support

**BYOI Architecture**

Separates concerns between:
- Core observability infrastructure (HoneyHive)
- LLM library integration (Instrumentors)
- Business logic (Your application)

**Multi-Instance Design**

Enables:
- Environment separation (dev/staging/prod)
- Service isolation in microservices
- Workflow-specific configuration
- Team-based access control

**Provider Strategy Intelligence**

HoneyHive automatically detects the OpenTelemetry environment and chooses the optimal integration strategy:

- **Main Provider**: When no functioning provider exists (NoOp/Proxy/Empty TracerProvider)
  
  - HoneyHive becomes the global TracerProvider
  - All instrumentor spans (OpenAI, Anthropic, etc.) flow through HoneyHive
  - Prevents span loss from empty providers
  
- **Independent Provider**: When a functioning provider already exists
  
  - HoneyHive creates an isolated TracerProvider
  - Maintains complete separation from existing observability systems
  - Ensures no interference with existing tracing infrastructure

See Also
--------

- :doc:`byoi-design` - Detailed BYOI architecture explanation
- :doc:`diagrams` - Architecture diagrams and visual guides
