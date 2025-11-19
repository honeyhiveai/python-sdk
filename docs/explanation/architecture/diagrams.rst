.. note::
   Visual representations of HoneyHive's architecture and key concepts to help you understand the system design.

This page provides comprehensive diagrams explaining HoneyHive's architecture, data flow, and integration patterns.

System Overview
---------------

**HoneyHive SDK Architecture**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#000000', 'clusterBkg': 'transparent', 'clusterBorder': '#000000', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2, 'nodeSpacing': 50, 'rankSpacing': 50}}}%%
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
       
       classDef appClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef sdkClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef tracerClass fill:#7b1fa2,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef evalClass fill:#2e7d32,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef apiClass fill:#ef6c00,stroke:#000000,stroke-width:2px,color:#ffffff
       
       class App,SDK appClass
       class Tracer,OTEL,Instrumentors,OpenAI,Anthropic,Custom,Exporter tracerClass
       class Eval,Evaluators,Results evalClass
       class API,Dashboard apiClass

BYOI Architecture
-----------------

**Bring Your Own Instrumentor Pattern**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#000000', 'clusterBkg': 'transparent', 'clusterBorder': '#000000', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2, 'nodeSpacing': 50, 'rankSpacing': 50}}}%%
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
       
       classDef appClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef coreClass fill:#7b1fa2,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef instClass fill:#2e7d32,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef apiClass fill:#ef6c00,stroke:#000000,stroke-width:2px,color:#ffffff
       
       class Code,LLM1,LLM2,LLM3 appClass
       class Core,Tracer,Exporter coreClass
       class Inst1,Inst2,Inst3 instClass
       class API apiClass

**Benefits of BYOI**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#000000', 'clusterBkg': 'transparent', 'clusterBorder': '#000000', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2, 'nodeSpacing': 50, 'rankSpacing': 50}}}%%
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
       
       classDef tradClass fill:#c62828,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef byoiClass fill:#2e7d32,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef appClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef depClass fill:#ef6c00,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef conflictClass fill:#7b1fa2,stroke:#000000,stroke-width:2px,color:#ffffff
       
       class TradSDK tradClass
       class BYOISDK byoiClass
       class App1,App2 appClass
       class OpenAIDep,AnthropicDep,GoogleDep depClass
       class YourOpenAI,YourOpenAI2,YourInst conflictClass

Multi-Instance Architecture
---------------------------

**Multiple Tracer Instances**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#000000', 'clusterBkg': 'transparent', 'clusterBorder': '#000000', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2, 'nodeSpacing': 50, 'rankSpacing': 50}}}%%
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
       
       classDef serviceClass fill:#2e7d32,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef tracerClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef projectClass fill:#ef6c00,stroke:#000000,stroke-width:2px,color:#ffffff
       
       class Service1,Service2,Service3 serviceClass
       class Tracer1,Tracer2,Tracer3 tracerClass
       class Project1,Project2,Project3 projectClass

Data Flow
---------

**Trace Data Journey**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#666666', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent'}}}%%
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

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#666666', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent'}}}%%
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

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#000000', 'clusterBkg': 'transparent', 'clusterBorder': '#000000', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2, 'nodeSpacing': 50, 'rankSpacing': 50}}}%%
   graph TB
       subgraph "Kubernetes Cluster"
           subgraph "Namespace: production"
               Service1["API Gateway<br/>HoneyHive: api-gateway"]
               Service2["User Service<br/>HoneyHive: user-service"]
               Service3["LLM Service<br/>HoneyHive: llm-service"]
           end
           
           subgraph "Namespace: staging"
               Service4["API Gateway<br/>(Staging)"]
               Service5["User Service<br/>(Staging)"]
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
       
       classDef prodServiceClass fill:#2e7d32,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef stagingServiceClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef dashboardClass fill:#ef6c00,stroke:#000000,stroke-width:2px,color:#ffffff
       
       class Service1,Service2,Service3 prodServiceClass
       class Service4,Service5 stagingServiceClass
       class Dashboard1,Dashboard2 dashboardClass

**Container Architecture**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#000000', 'clusterBkg': 'transparent', 'clusterBorder': '#000000', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2, 'nodeSpacing': 50, 'rankSpacing': 50}}}%%
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
       
       classDef appClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef envClass fill:#2e7d32,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef extClass fill:#ef6c00,stroke:#000000,stroke-width:2px,color:#ffffff
       
       class App,SDK,Inst appClass
       class Env,Secrets envClass
       class LLMProviders,HoneyHive extClass

Evaluation Architecture
-----------------------

**Evaluation Pipeline**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#000000', 'clusterBkg': 'transparent', 'clusterBorder': '#000000', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2, 'nodeSpacing': 50, 'rankSpacing': 50}}}%%
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
       
       classDef inputClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef pipelineClass fill:#2e7d32,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef evalClass fill:#7b1fa2,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef resultClass fill:#ef6c00,stroke:#000000,stroke-width:2px,color:#ffffff
       
       class Input inputClass
       class Pipeline,Parallel pipelineClass
       class Eval1,Eval2,Eval3 evalClass
       class Results1,Results2,Results3,Aggregator,Final,Storage resultClass

**Multi-Evaluator Patterns**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#000000', 'clusterBkg': 'transparent', 'clusterBorder': '#000000', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2, 'nodeSpacing': 50, 'rankSpacing': 50}}}%%
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
       
       classDef evalClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef strategyClass fill:#2e7d32,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef decisionClass fill:#ef6c00,stroke:#000000,stroke-width:2px,color:#ffffff
       
       class Technical,Quality,Business evalClass
       class Weighted,Threshold,Custom strategyClass
       class Decision decisionClass

Performance Optimization
------------------------

**Sampling Strategies**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#000000', 'clusterBkg': 'transparent', 'clusterBorder': '#000000', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2, 'nodeSpacing': 50, 'rankSpacing': 50}}}%%

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
       
       classDef requestClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef criticalClass fill:#c62828,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef importantClass fill:#ef6c00,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef standardClass fill:#7b1fa2,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef samplingClass fill:#2e7d32,stroke:#000000,stroke-width:2px,color:#ffffff
       
       class Request,Classifier requestClass
       class Critical criticalClass
       class Important importantClass
       class Standard standardClass
       class Sample100,Sample50,Sample5,Storage samplingClass

**Batch Processing**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#333333', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
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
       
       classDef inputClass fill:#1565c0,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef groupClass fill:#2e7d32,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef processClass fill:#ef6c00,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef spanClass fill:#7b1fa2,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class Items inputClass
       class Group1,Group2,Group3,GroupN groupClass
       class Thread1,Thread2,Thread3 processClass
       class Span1,Span2 spanClass

Security Architecture
---------------------

**Enterprise Security Flow**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#000000', 'clusterBkg': 'transparent', 'clusterBorder': '#000000', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2, 'nodeSpacing': 50, 'rankSpacing': 50}}}%%
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
       
       classDef appClass fill:#1565c0,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef securityClass fill:#c62828,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef storageClass fill:#2e7d32,stroke:#000000,stroke-width:2px,color:#ffffff
       classDef externalClass fill:#ef6c00,stroke:#000000,stroke-width:2px,color:#ffffff
       
       class App,SDK appClass
       class Config,Encrypt,Audit securityClass
       class AWS,Vault,K8s storageClass
       class HH externalClass

Integration Patterns
--------------------

**Service Mesh Integration**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#333333', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
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
       
       classDef proxyClass fill:#1565c0,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef serviceClass fill:#2e7d32,stroke:#333333,stroke-width:2px,color:#ffffff
       classDef observabilityClass fill:#ef6c00,stroke:#333333,stroke-width:2px,color:#ffffff
       
       class Proxy1,Proxy2,Proxy3 proxyClass
       class Service1,Service2,Service3 serviceClass
       class Jaeger,HoneyHive,Metrics observabilityClass

**Context Propagation**

.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#666666', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent'}}}%%
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
- :doc:`../../tutorials/advanced-configuration` - Advanced setup tutorial
