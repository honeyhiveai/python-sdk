Architecture Diagrams
=====================

.. note::
   Visual representations of HoneyHive's architecture and key concepts to help you understand the system design.

This page provides comprehensive diagrams explaining HoneyHive's architecture, data flow, and integration patterns.

System Overview
---------------

**HoneyHive SDK Architecture**

.. mermaid::

   graph TB
       App["Your Application"] --> SDK["HoneyHive SDK"]
       SDK --> Tracer["HoneyHiveTracer"]
       SDK --> Eval["Evaluation Framework"]
       
       Tracer --> OTEL["OpenTelemetry"]
       OTEL --> Instrumentors["Instrumentors"]
       
       Instrumentors --> OpenAI["OpenAI<br/>Instrumentor"]
       Instrumentors --> Anthropic["Anthropic<br/>Instrumentor"]
       Instrumentors --> Custom["Custom<br/>Instrumentor"]
       
       OTEL --> Exporter["HoneyHive<br/>Exporter"]
       Exporter --> API["HoneyHive API"]
       API --> Dashboard["HoneyHive<br/>Dashboard"]
       
       Eval --> Evaluators["Built-in &<br/>Custom Evaluators"]
       Evaluators --> Results["Evaluation<br/>Results"]
       Results --> API
       
       style SDK fill:#e1f5fe
       style Tracer fill:#f3e5f5
       style Eval fill:#e8f5e8
       style API fill:#fff3e0

BYOI Architecture
-----------------

**Bring Your Own Instrumentor Pattern**

.. mermaid::

   graph TD
       subgraph "Your Application"
           Code["Application Code"]
           LLM1["OpenAI Client"]
           LLM2["Anthropic Client"]
           LLM3["Custom LLM Client"]
       end
       
       subgraph "HoneyHive Core"
           Core["HoneyHive SDK<br/>(No LLM Dependencies)"]
           Tracer["Tracer Provider"]
           Exporter["Span Exporter"]
       end
       
       subgraph "Instrumentors (Your Choice)"
           Inst1["OpenInference<br/>OpenAI"]
           Inst2["OpenInference<br/>Anthropic"]
           Inst3["Custom<br/>Instrumentor"]
       end
       
       Code --> Core
       Core --> Tracer
       Tracer --> Exporter
       
       LLM1 -.-> Inst1
       LLM2 -.-> Inst2
       LLM3 -.-> Inst3
       
       Inst1 --> Tracer
       Inst2 --> Tracer
       Inst3 --> Tracer
       
       Exporter --> API["HoneyHive API"]
       
       style Core fill:#e3f2fd
       style Inst1 fill:#f1f8e9
       style Inst2 fill:#f1f8e9
       style Inst3 fill:#f1f8e9

**Benefits of BYOI**

.. mermaid::

   graph LR
       subgraph "Traditional Approach"
           TradSDK["Observability SDK"]
           TradSDK --> OpenAIDep["openai==1.5.0"]
           TradSDK --> AnthropicDep["anthropic==0.8.0"]
           TradSDK --> GoogleDep["google-ai==2.1.0"]
           
           App1["Your App"] --> TradSDK
           App1 --> YourOpenAI["openai==1.8.0"]
           
           YourOpenAI -.->|"❌ Conflict"| OpenAIDep
       end
       
       subgraph "BYOI Approach"
           BYOISDK["HoneyHive SDK<br/>(No LLM deps)"]
           
           App2["Your App"] --> BYOISDK
           App2 --> YourOpenAI2["openai==1.8.0<br/>✅ Your choice"]
           App2 --> YourInst["OpenAI Instrumentor<br/>✅ Your choice"]
           
           YourInst --> BYOISDK
       end
       
       style TradSDK fill:#ffebee
       style BYOISDK fill:#e8f5e8

Multi-Instance Architecture
----------------------------

**Multiple Tracer Instances**

.. mermaid::

   graph TB
       subgraph "Application"
           Service1["User Service"]
           Service2["Payment Service"]
           Service3["ML Service"]
       end
       
       subgraph "HoneyHive Tracers"
           Tracer1["Tracer Instance 1<br/>Project: user-service<br/>Source: production"]
           Tracer2["Tracer Instance 2<br/>Project: payment-service<br/>Source: production"]
           Tracer3["Tracer Instance 3<br/>Project: ml-service<br/>Source: development"]
       end
       
       subgraph "HoneyHive Platform"
           Project1["user-service<br/>Dashboard"]
           Project2["payment-service<br/>Dashboard"]
           Project3["ml-service<br/>Dashboard"]
       end
       
       Service1 --> Tracer1
       Service2 --> Tracer2
       Service3 --> Tracer3
       
       Tracer1 --> Project1
       Tracer2 --> Project2
       Tracer3 --> Project3
       
       style Tracer1 fill:#e3f2fd
       style Tracer2 fill:#f3e5f5
       style Tracer3 fill:#e8f5e8

Data Flow
---------

**Trace Data Journey**

.. mermaid::

   sequenceDiagram
       participant App as Application
       participant SDK as HoneyHive SDK
       participant Inst as Instrumentor
       participant LLM as LLM Provider
       participant OTEL as OpenTelemetry
       participant Exp as Exporter
       participant API as HoneyHive API
       
       App->>SDK: @trace decorator
       SDK->>OTEL: Create span
       
       App->>LLM: LLM API call
       Inst->>OTEL: Instrument call
       LLM-->>Inst: API response
       Inst->>OTEL: Add LLM attributes
       
       OTEL->>Exp: Span completed
       Exp->>API: Send trace data
       API-->>Exp: Acknowledge
       
       Note over App,API: Automatic, zero-code-change tracing

**Evaluation Flow**

.. mermaid::

   sequenceDiagram
       participant App as Application
       participant SDK as HoneyHive SDK
       participant Eval as Evaluator
       participant API as HoneyHive API
       
       App->>SDK: @evaluate decorator
       SDK->>Eval: evaluate(input, output)
       
       alt Built-in Evaluator
           Eval->>Eval: Run evaluation logic
       else Custom Evaluator
           Eval->>API: Call external service
           API-->>Eval: Evaluation result
       end
       
       Eval-->>SDK: Return score & feedback
       SDK->>API: Send evaluation data
       
       Note over App,API: Automatic quality assessment

Deployment Patterns
-------------------

**Microservices Deployment**

.. mermaid::

   graph TB
       subgraph "Kubernetes Cluster"
           subgraph "Namespace: production"
               Service1["API Gateway<br/>HoneyHive: api-gateway"]
               Service2["User Service<br/>HoneyHive: user-service"]
               Service3["LLM Service<br/>HoneyHive: llm-service"]
           end
           
           subgraph "Namespace: staging"
               Service4["API Gateway<br/>HoneyHive: api-gateway-staging"]
               Service5["User Service<br/>HoneyHive: user-service-staging"]
           end
       end
       
       subgraph "HoneyHive SaaS"
           Dashboard1["Production<br/>Dashboards"]
           Dashboard2["Staging<br/>Dashboards"]
       end
       
       Service1 --> Dashboard1
       Service2 --> Dashboard1
       Service3 --> Dashboard1
       
       Service4 --> Dashboard2
       Service5 --> Dashboard2
       
       style Service1 fill:#e8f5e8
       style Service2 fill:#e8f5e8
       style Service3 fill:#e8f5e8
       style Service4 fill:#fff3e0
       style Service5 fill:#fff3e0

**Container Architecture**

.. mermaid::

   graph LR
       subgraph "Docker Container"
           App["Application<br/>Process"]
           SDK["HoneyHive SDK"]
           Inst["Instrumentors"]
           
           App --> SDK
           SDK --> Inst
       end
       
       subgraph "Environment"
           Env["Environment Variables<br/>HH_API_KEY<br/>HH_PROJECT<br/>HH_SOURCE"]
           Secrets["Secrets Management<br/>AWS Secrets Manager<br/>Kubernetes Secrets"]
       end
       
       subgraph "External"
           LLMProviders["LLM Providers<br/>OpenAI, Anthropic, etc."]
           HoneyHive["HoneyHive API"]
       end
       
       Env --> SDK
       Secrets --> SDK
       Inst --> LLMProviders
       SDK --> HoneyHive

Evaluation Architecture
-----------------------

**Evaluation Pipeline**

.. mermaid::

   graph TD
       Input["LLM Input/Output"] --> Pipeline["Evaluation Pipeline"]
       
       Pipeline --> Parallel["Parallel Evaluation"]
       
       Parallel --> Eval1["Factual Accuracy<br/>Evaluator"]
       Parallel --> Eval2["Quality Score<br/>Evaluator"]
       Parallel --> Eval3["Custom Domain<br/>Evaluator"]
       
       Eval1 --> Results1["Score: 0.85<br/>Feedback: Accurate"]
       Eval2 --> Results2["Score: 0.92<br/>Feedback: High quality"]
       Eval3 --> Results3["Score: 0.78<br/>Feedback: Domain appropriate"]
       
       Results1 --> Aggregator["Result Aggregator"]
       Results2 --> Aggregator
       Results3 --> Aggregator
       
       Aggregator --> Final["Final Score: 0.85<br/>Detailed Feedback"]
       Final --> Storage["HoneyHive Storage"]
       
       style Pipeline fill:#e3f2fd
       style Aggregator fill:#f3e5f5

**Multi-Evaluator Patterns**

.. mermaid::

   graph LR
       subgraph "Evaluation Types"
           Technical["Technical Evaluators<br/>• Token efficiency<br/>• Response time<br/>• Error rates"]
           Quality["Quality Evaluators<br/>• Factual accuracy<br/>• Relevance<br/>• Clarity"]
           Business["Business Evaluators<br/>• Customer satisfaction<br/>• Goal achievement<br/>• Cost efficiency"]
       end
       
       subgraph "Aggregation Strategies"
           Weighted["Weighted Average<br/>Different weights for<br/>different evaluators"]
           Threshold["Threshold-based<br/>Must pass all<br/>critical evaluators"]
           Custom["Custom Logic<br/>Business-specific<br/>aggregation rules"]
       end
       
       Technical --> Weighted
       Quality --> Threshold
       Business --> Custom
       
       Weighted --> Decision["Final Decision"]
       Threshold --> Decision
       Custom --> Decision

Performance Optimization
-------------------------

**Sampling Strategies**

.. mermaid::

   graph TD
       Request["Incoming Request"] --> Classifier["Request Classifier"]
       
       Classifier --> Critical["Critical Requests<br/>• Errors<br/>• Premium users<br/>• Slow requests"]
       Classifier --> Important["Important Requests<br/>• Key endpoints<br/>• New features"]
       Classifier --> Standard["Standard Requests<br/>• Regular traffic"]
       
       Critical --> Sample100["100% Sampling<br/>Always trace"]
       Important --> Sample50["50% Sampling<br/>Higher coverage"]
       Standard --> Sample5["5% Sampling<br/>Representative sample"]
       
       Sample100 --> Storage["HoneyHive Storage"]
       Sample50 --> Storage
       Sample5 --> Storage
       
       style Critical fill:#ffebee
       style Important fill:#fff3e0
       style Standard fill:#f3e5f5

**Batch Processing**

.. mermaid::

   graph LR
       subgraph "Input"
           Items["1000 Items<br/>to Process"]
       end
       
       subgraph "Grouping Strategy"
           Group1["Group A<br/>100 similar items"]
           Group2["Group B<br/>150 similar items"]
           Group3["Group C<br/>200 similar items"]
           GroupN["Group N<br/>..."]
       end
       
       subgraph "Processing"
           Thread1["Thread Pool<br/>Executor"]
           Thread2["Thread Pool<br/>Executor"]
           Thread3["Thread Pool<br/>Executor"]
       end
       
       subgraph "Tracing Strategy"
           Span1["1 Span per Group<br/>Not per item"]
           Span2["Aggregate metrics<br/>Success/failure rates"]
       end
       
       Items --> Group1
       Items --> Group2
       Items --> Group3
       Items --> GroupN
       
       Group1 --> Thread1
       Group2 --> Thread2
       Group3 --> Thread3
       
       Thread1 --> Span1
       Thread2 --> Span2

Security Architecture
---------------------

**Enterprise Security Flow**

.. mermaid::

   graph TD
       subgraph "Application Layer"
           App["Application"]
           SDK["HoneyHive SDK"]
       end
       
       subgraph "Security Layer"
           Config["Secure Config<br/>Manager"]
           Encrypt["Encryption/<br/>Decryption"]
           Audit["Audit Logger"]
       end
       
       subgraph "Secret Storage"
           AWS["AWS Secrets<br/>Manager"]
           Vault["HashiCorp<br/>Vault"]
           K8s["Kubernetes<br/>Secrets"]
       end
       
       subgraph "External"
           HH["HoneyHive API<br/>(HTTPS only)"]
       end
       
       App --> SDK
       SDK --> Config
       Config --> Encrypt
       Config --> AWS
       Config --> Vault
       Config --> K8s
       
       SDK --> Audit
       SDK --> HH
       
       style Config fill:#ffebee
       style Encrypt fill:#ffebee
       style Audit fill:#ffebee

Integration Patterns
--------------------

**Service Mesh Integration**

.. mermaid::

   graph TB
       subgraph "Service Mesh (Istio)"
           Proxy1["Envoy Proxy"]
           Proxy2["Envoy Proxy"]
           Proxy3["Envoy Proxy"]
       end
       
       subgraph "Services"
           Service1["Service A<br/>HoneyHive SDK"]
           Service2["Service B<br/>HoneyHive SDK"]
           Service3["Service C<br/>HoneyHive SDK"]
       end
       
       subgraph "Observability"
           Jaeger["Jaeger<br/>(OpenTelemetry)"]
           HoneyHive["HoneyHive<br/>(LLM-specific)"]
           Metrics["Prometheus<br/>(Metrics)"]
       end
       
       Service1 --> Proxy1
       Service2 --> Proxy2
       Service3 --> Proxy3
       
       Proxy1 --> Jaeger
       Proxy2 --> Jaeger
       Proxy3 --> Jaeger
       
       Service1 --> HoneyHive
       Service2 --> HoneyHive
       Service3 --> HoneyHive
       
       Proxy1 --> Metrics
       Proxy2 --> Metrics
       Proxy3 --> Metrics

**Context Propagation**

.. mermaid::

   sequenceDiagram
       participant Client as Client Request
       participant Gateway as API Gateway
       participant UserSvc as User Service
       participant LLMSvc as LLM Service
       participant DB as Database
       
       Client->>Gateway: HTTP Request<br/>trace-id: abc123
       
       Gateway->>UserSvc: Internal Call<br/>trace-id: abc123<br/>span-id: def456
       UserSvc->>DB: Query<br/>trace-id: abc123<br/>span-id: ghi789
       DB-->>UserSvc: Result
       
       UserSvc->>LLMSvc: LLM Request<br/>trace-id: abc123<br/>span-id: jkl012
       LLMSvc->>LLMSvc: OpenAI Call<br/>trace-id: abc123<br/>span-id: mno345
       LLMSvc-->>UserSvc: LLM Response
       
       UserSvc-->>Gateway: Aggregated Result
       Gateway-->>Client: Final Response
       
       Note over Client,DB: All operations linked by trace-id: abc123

These diagrams provide visual representations of HoneyHive's architecture and help developers understand complex concepts like BYOI, multi-instance patterns, and data flow.

See Also
--------

- :doc:`overview` - Architecture overview
- :doc:`byoi-design` - BYOI design explanation
- :doc:`overview` - Architecture overview
- :doc:`../../tutorials/advanced-setup` - Advanced setup tutorial
