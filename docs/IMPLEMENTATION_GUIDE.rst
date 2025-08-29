Implementation Guide
====================

Technical implementation details for the HoneyHive Python SDK.

.. contents:: Table of Contents
   :local:
   :depth: 2

Architecture Overview
---------------------

High-Level Architecture
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────┐
   │                    Application Layer                        │
   ├─────────────────────────────────────────────────────────────┤
   │                    HoneyHive SDK                           │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
   │  │   Tracers   │  │ API Client  │  │   Evaluation        │ │
   │  │(Multi-Inst)│  │             │  │                     │ │
   │  └─────────────┘  └─────────────┘  └─────────────────────┘ │
   ├─────────────────────────────────────────────────────────────┤
   │                  OpenTelemetry Layer                        │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
   │  │TracerProvider│  │Span Exporter│  │   Instrumentation   │ │
   │  │(Smart Mgmt) │  │             │  │                     │ │
   │  └─────────────┘  └─────────────┘  └─────────────────────┘ │
   ├─────────────────────────────────────────────────────────────┤
   │                     Transport Layer                         │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
   │  │   HTTPX     │  │  Connection │  │      Retry          │ │
   │  │             │  │    Pool     │  │                     │ │
   │  └─────────────┘  └─────────────┘  └─────────────────────┘ │
   ├─────────────────────────────────────────────────────────────┤
   │                     HoneyHive API                          │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
   │  │  Sessions   │  │   Events    │  │     Metrics         │ │
   │  │             │  │             │  │                     │ │
   │  └─────────────┘  └─────────────┘  └─────────────────────┘ │
   └─────────────────────────────────────────────────────────────┘

Key Design Principles
~~~~~~~~~~~~~~~~~~~~~

1. **Minimal Dependencies** - Core SDK has minimal dependencies to prevent conflicts
2. **Bring Your Own Instrumentor** - Users choose what gets instrumented, not us
3. **Separation of Concerns** - Each component has a single responsibility
4. **Dependency Injection** - Components are loosely coupled
5. **Configuration as Code** - Environment-based configuration
6. **Graceful Degradation** - Fallback mechanisms for missing dependencies
7. **Testability** - All components are designed for easy testing
8. **LLM Agent Focus** - Built specifically for multi-step AI workflows
9. **Multi-Instance Support** - Modern architecture supporting multiple tracer instances
10. **Smart Provider Management** - Intelligent OpenTelemetry provider integration

Core Components
---------------

1. HoneyHiveTracer
~~~~~~~~~~~~~~~~~~

The central component that orchestrates OpenTelemetry integration and session management. Now supports multiple independent instances within the same runtime.

Implementation Details
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class HoneyHiveTracer:
       def __init__(self, api_key=None, project=None, source="production", 
                    test_mode=False, session_name=None, instrumentors=None):
           """Initialize a new tracer instance."""
           # Each instance is independent
           self.api_key = api_key or config.api_key
           self.project = project or config.project
           self.source = source or config.source
           self.test_mode = test_mode
           self.session_name = session_name or self._generate_session_name()
           self.instrumentors = instrumentors or []
           
           # Smart TracerProvider management
           self.provider = None
           self.is_main_provider = False
           self._initialize_otel()

**Key Features:**

* **Multi-Instance Support** - Create multiple independent tracer instances
* **Dynamic Session Naming** - Automatic session naming based on initialization file
* **Smart TracerProvider Management** - Integrates with existing providers or creates new ones
* **Thread Safety** - Each instance is thread-safe and independent
* **Lazy Initialization** - Components initialized only when needed
* **Session Auto-Creation** - Automatically creates HoneyHive sessions
* **Dependency Conflict Prevention** - Minimal core dependencies with optional instrumentors

Multi-Instance Architecture
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The new architecture supports creating multiple tracer instances for different workflows:

.. code-block:: python

   # Production tracer
   prod_tracer = HoneyHiveTracer.init(
       api_key="prod-key",
       project="production-app",
       source="prod"
   )
   
   # Development tracer
   dev_tracer = HoneyHiveTracer.init(
       api_key="dev-key",
       project="development-app",
       source="dev"
   )
   
   # Testing tracer
   test_tracer = HoneyHiveTracer.init(
       api_key="test-key",
       project="testing-app",
       source="test"
   )
   
   # Each tracer operates independently
   with prod_tracer.start_span("prod-operation") as span:
       # Production tracing
       pass
   
   with dev_tracer.start_span("dev-operation") as span:
       # Development tracing
       pass

Dynamic Session Naming
^^^^^^^^^^^^^^^^^^^^^^

Sessions are automatically named based on the file where the tracer is initialized:

.. code-block:: python

   def _generate_session_name(self):
       """Generate session name from the calling file."""
       import inspect
       import os
       
       # Get the frame where HoneyHiveTracer was called
       frame = inspect.currentframe()
       while frame:
           if frame.f_code.co_name == '__init__':
               frame = frame.f_back
               break
           frame = frame.f_back
       
       if frame:
           filename = os.path.basename(frame.f_code.co_filename)
           name, _ = os.path.splitext(filename)
           return name
       
       return "honeyhive_session"

TracerProvider Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^

Smart integration with existing OpenTelemetry providers:

.. code-block:: python

   def _initialize_otel(self):
       """Initialize OpenTelemetry with smart provider management."""
       from opentelemetry import trace
       
       # Check if a provider already exists
       existing_provider = trace.get_tracer_provider()
       
       if existing_provider and str(type(existing_provider).__name__) != "NoOpTracerProvider":
           # Integrate with existing provider
           self.provider = existing_provider
           self.is_main_provider = False
       else:
           # Create new provider
           self.provider = self._create_new_provider()
           self.is_main_provider = True

Initialization Flow
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def __init__(self, api_key=None, project=None, source="production", 
                test_mode=False, session_name=None, instrumentors=None):
       # 1. Validate API key
       self.api_key = api_key or config.api_key
       
       # 2. Set configuration
       self.project = project or config.project
       self.source = source or config.source
       self.test_mode = test_mode
       
       # 3. Generate session name
       self.session_name = session_name or self._generate_session_name()
       
       # 4. Initialize OpenTelemetry
       self._initialize_otel()
       
       # 5. Create session
       self._create_session()
       
       # 6. Setup instrumentors
       self._setup_instrumentors(instrumentors)

Dependency Philosophy
^^^^^^^^^^^^^^^^^^^^^

**Why Minimal Dependencies?**

The HoneyHive SDK intentionally keeps core dependencies minimal to prevent conflicts in customer environments:

* **No Hard LLM Dependencies**: We don't force specific versions of OpenAI, Anthropic, or other LLM libraries
* **Optional Instrumentors**: Users choose what gets instrumented based on their needs
* **OpenTelemetry Standards**: Core functionality relies on industry-standard OpenTelemetry
* **Conflict Prevention**: Your existing LLM workflows continue working unchanged

**What Gets Excluded:**

* Specific LLM library versions
* Framework-specific dependencies
* Optional features that could cause conflicts
* Vendor-specific implementations

**What Gets Included:**

* Essential OpenTelemetry components
* HTTP client for API communication
* Basic data validation and configuration
* Core tracing and session management
       
       # 5. Set up baggage context
       self._setup_baggage_context()

Design Patterns
---------------

1. Factory Pattern
~~~~~~~~~~~~~~~~~~

Provides flexible object creation through the init method:

.. code-block:: python

   @classmethod
   def init(cls, **kwargs):
       """Factory method for creating tracer instances."""
       return cls(**kwargs)

3. Strategy Pattern
~~~~~~~~~~~~~~~~~~~

Configurable behavior through dependency injection:

.. code-block:: python

   def _initialize_otel(self):
       """Initialize OpenTelemetry with configurable strategies."""
       
       # Strategy 1: Standard OTLP export
       if config.otlp_enabled:
           self._setup_otlp_export()
       
       # Strategy 2: Console export for debugging
       if self.test_mode:
           self._setup_console_export()
       
       # Strategy 3: Custom instrumentors
       if self.instrumentors:
           self._integrate_instrumentors()

Implementation Details
----------------------

1. Session Management
~~~~~~~~~~~~~~~~~~~~~

Automatic session creation and management for tracking user interactions.

Session Creation Flow
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def _initialize_session(self):
       """Initialize session management."""
       
       try:
           # 1. Import session API
           from ..api.session import SessionAPI
           from ..api.client import HoneyHive
           
           # 2. Create client and session API
           self.client = HoneyHive(
               api_key=self.api_key,
               base_url=config.api_url,
               test_mode=self.test_mode
           )
           self.session_api = SessionAPI(self.client)
           
           # 3. Create new session automatically
           session_response = self.session_api.start_session({
               "project": self.project,
               "session_name": self.session_name,
               "source": self.source
           })
           
           # 4. Extract session ID
           if hasattr(session_response, 'session_id'):
               self.session_id = session_response.session_id
           else:
               self.session_id = None
               
       except Exception as e:
           if not self.test_mode:
               print(f"Warning: Failed to create session: {e}")
           self.session_id = None
           self.client = None
           self.session_api = None

2. Baggage Management
~~~~~~~~~~~~~~~~~~~~~

Context propagation across service boundaries using OpenTelemetry baggage.

Baggage Operations
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def set_baggage(self, key: str, value: str):
       """Set baggage item in current context."""
       
       try:
           ctx = context.get_current()
           ctx = baggage.set_baggage(key, value, ctx)
           context.attach(ctx)
           return True
       except Exception as e:
           print(f"Warning: Failed to set baggage {key}: {e}")
           return False

   def get_baggage(self, key: str, default=None):
       """Get baggage item from current context."""
       
       try:
           ctx = context.get_current()
           return baggage.get_baggage(key, ctx) or default
       except Exception as e:
           print(f"Warning: Failed to get baggage {key}: {e}")
           return default

Testing Strategy
----------------

1. Test Architecture
~~~~~~~~~~~~~~~~~~~~

Multi-layered testing approach:

.. code-block:: python

   # Unit tests - test individual components
   def test_tracer_initialization():
       tracer = HoneyHiveTracer(api_key="test", test_mode=True)
       assert tracer.api_key == "test"
       assert tracer.test_mode is True

   # Integration tests - test component interactions
   def test_tracer_session_integration():
       tracer = HoneyHiveTracer(api_key="test", test_mode=True)
       assert tracer.session_id is not None

   # End-to-end tests - test complete workflows
   def test_complete_tracing_workflow():
       # Test full tracing workflow
       pass

Performance Optimizations
-------------------------

1. Span Processing Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Efficient span processing and export:

.. code-block:: python

   def _setup_span_processing(self):
       """Optimize span processing for performance."""
       
       # Batch processing for efficiency
       batch_processor = BatchSpanProcessor(
           self.exporter,
           max_queue_size=1000,
           max_export_batch_size=100,
           schedule_delay_millis=5000
       )
       
       # Add to provider
       self.provider.add_span_processor(batch_processor)

Security Considerations
-----------------------

1. API Key Management
~~~~~~~~~~~~~~~~~~~~~

Secure handling of sensitive credentials:

.. code-block:: python

   def _validate_api_key(self, api_key: str):
       """Validate and secure API key."""
       
       if not api_key:
           raise ValueError("API key is required")
       
       # Store securely (not in plain text)
       self._api_key = api_key
       
       # Clear from memory after use
       del api_key

Deployment Guide
----------------

1. Production Deployment
~~~~~~~~~~~~~~~~~~~~~~~~

Production-ready configuration:

.. code-block:: python

   # Production configuration
   tracer = HoneyHiveTracer.init(
       api_key=os.environ["HH_API_KEY"],
       project=os.environ["HH_PROJECT"],
       source="production",
       disable_http_tracing=False,  # Enable for production
       instrumentors=[OpenAIInstrumentor()]  # Enable AI tracing
   )
