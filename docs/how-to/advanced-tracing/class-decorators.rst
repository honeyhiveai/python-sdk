Class-Level Decorator Patterns
==============================

**Problem:** You need to trace entire classes systematically, apply tracing to all methods automatically, or create reusable tracing patterns for object-oriented code.

**Solution:** Use class-level decorators and metaclasses to instrument entire classes with structured, consistent tracing.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Basic Class Decoration
----------------------

**When to Use:** Trace all public methods of a class automatically.

Simple Class Decorator
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   from functools import wraps
   import inspect
   
   tracer = HoneyHiveTracer.init(project="class-tracing")
   
   def trace_class(cls):
       """Decorator to trace all methods of a class."""
       for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
           if not name.startswith('_'):  # Skip private methods
               setattr(cls, name, trace(tracer=tracer)(method))
       return cls
   
   @trace_class
   class DataProcessor:
       """Example class with automatic method tracing."""
       
       def load_data(self, source: str):
           """Load data from source."""
           return {"data": [...]}
       
       def transform_data(self, data: dict):
           """Transform loaded data."""
           return {"transformed": [...]}
       
       def save_data(self, data: dict, destination: str):
           """Save processed data."""
           pass

**Usage:**

.. code-block:: python

   processor = DataProcessor()
   processor.load_data("input.csv")  # Automatically traced
   processor.transform_data(data)     # Automatically traced
   processor.save_data(data, "output.csv")  # Automatically traced

**Benefits:**

- ✅ Consistent tracing across all methods
- ✅ No need to decorate each method individually
- ✅ Easy to apply to existing classes

Selective Method Tracing
------------------------

**When to Use:** Trace only specific methods based on custom criteria.

Attribute-Based Selection
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def trace_class_selective(event_type=EventType.tool):
       """Decorator to trace methods marked with _trace attribute."""
       def decorator(cls):
           for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
               if getattr(method, '_trace', False):
                   wrapped = trace(tracer=tracer, event_type=event_type)(method)
                   setattr(cls, name, wrapped)
           return cls
       return decorator
   
   def traced_method(func):
       """Mark a method for tracing."""
       func._trace = True
       return func
   
   @trace_class_selective(event_type=EventType.chain)
   class LLMAgent:
       """Agent with selective method tracing."""
       
       @traced_method
       def run(self, query: str) -> str:
           """Main agent execution - TRACED."""
           plan = self._create_plan(query)
           return self._execute_plan(plan)
       
       def _create_plan(self, query: str):
           """Internal planning - NOT TRACED."""
           return {"steps": [...]}
       
       @traced_method
       def _execute_plan(self, plan: dict) -> str:
           """Plan execution - TRACED."""
           return "result"

**Trace Output:**

Only `run()` and `_execute_plan()` are traced, while `_create_plan()` remains untraced for performance.

Advanced Patterns
-----------------

Enrichment at Class Level
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Automatically add class-level context to all method traces.

**Solution:**

.. code-block:: python

   def trace_class_with_context(class_name_attr: str = None):
       """Trace class methods with automatic class context enrichment."""
       def decorator(cls):
           class_name = cls.__name__
           
           for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
               if not name.startswith('_'):
                   original_method = method
                   
                   @wraps(original_method)
                   def wrapped(self, *args, **kwargs):
                       # Add class-level context
                       enrich_span({
                           "class.name": class_name,
                           "class.method": name,
                           "instance.id": id(self)
                       })
                       
                       # Add custom class attribute if specified
                       if class_name_attr and hasattr(self, class_name_attr):
                           enrich_span({
                               f"class.{class_name_attr}": getattr(self, class_name_attr)
                           })
                       
                       return original_method(self, *args, **kwargs)
                   
                   traced_wrapped = trace(tracer=tracer)(wrapped)
                   setattr(cls, name, traced_wrapped)
           
           return cls
       return decorator
   
   @trace_class_with_context(class_name_attr="agent_type")
   class ConfigurableAgent:
       """Agent with class-level configuration tracing."""
       
       def __init__(self, agent_type: str):
           self.agent_type = agent_type
       
       def process(self, query: str) -> str:
           """Process query with agent."""
           return f"Processed by {self.agent_type}"

**Trace Span Enrichment:**

Every method call automatically includes:

.. code-block:: python

   {
       "class.name": "ConfigurableAgent",
       "class.method": "process",
       "instance.id": 140234567890,
       "class.agent_type": "research"
   }

Metaclass-Based Tracing
~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Apply tracing at class definition time with full control.

**Solution:**

.. code-block:: python

   from honeyhive import trace
   from honeyhive.models import EventType
   
   class TracedMeta(type):
       """Metaclass that automatically traces all public methods."""
       
       def __new__(mcs, name, bases, namespace, **kwargs):
           trace_config = kwargs.get('trace_config', {})
           event_type = trace_config.get('event_type', EventType.tool)
           
           for attr_name, attr_value in namespace.items():
               if callable(attr_value) and not attr_name.startswith('_'):
                   namespace[attr_name] = trace(
                       tracer=tracer,
                       event_type=event_type
                   )(attr_value)
           
           return super().__new__(mcs, name, bases, namespace)
   
   class TracedService(metaclass=TracedMeta, trace_config={'event_type': EventType.chain}):
       """Service with metaclass-based automatic tracing."""
       
       def fetch_data(self, source: str):
           """Fetch data from source."""
           return {"data": [...]}
       
       def process_data(self, data: dict):
           """Process fetched data."""
           return {"processed": [...]}

**Benefits:**

- ✅ Tracing applied at class definition time
- ✅ Configurable event types per class
- ✅ No explicit decorator syntax needed

Hierarchical Tracing
--------------------

**Problem:** Trace class hierarchies while preserving inheritance.

Parent-Child Trace Hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def trace_class_hierarchy(base_event_type=EventType.chain):
       """Trace classes with parent-child awareness."""
       def decorator(cls):
           class_hierarchy = [c.__name__ for c in cls.__mro__[:-1]]
           
           for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
               if not name.startswith('_'):
                   original_method = method
                   
                   @wraps(original_method)
                   def wrapped(self, *args, **kwargs):
                       enrich_span({
                           "class.hierarchy": " -> ".join(class_hierarchy),
                           "class.current": cls.__name__,
                           "class.method": name
                       })
                       return original_method(self, *args, **kwargs)
                   
                   traced = trace(tracer=tracer, event_type=base_event_type)(wrapped)
                   setattr(cls, name, traced)
           
           return cls
       return decorator
   
   @trace_class_hierarchy()
   class BaseAgent:
       """Base agent class."""
       
       def initialize(self):
           """Initialize agent."""
           pass
   
   @trace_class_hierarchy()
   class ResearchAgent(BaseAgent):
       """Research-specialized agent."""
       
       def research(self, topic: str):
           """Perform research."""
           self.initialize()  # Calls parent method
           return {"findings": [...]}

**Trace Hierarchy Output:**

.. code-block:: python

   {
       "class.hierarchy": "ResearchAgent -> BaseAgent",
       "class.current": "ResearchAgent",
       "class.method": "research"
   }

Real-World Patterns
-------------------

Pattern 1: Repository Pattern with Tracing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def trace_repository(entity_name: str):
       """Decorator for repository pattern classes."""
       def decorator(cls):
           for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
               if not name.startswith('_'):
                   original_method = method
                   
                   @wraps(original_method)
                   def wrapped(self, *args, **kwargs):
                       # Repository-specific enrichment
                       enrich_span({
                           "repository.entity": entity_name,
                           "repository.operation": name,
                           "repository.class": cls.__name__
                       })
                       
                       # Add operation timing
                       import time
                       start = time.time()
                       result = original_method(self, *args, **kwargs)
                       duration = (time.time() - start) * 1000
                       
                       enrich_span({
                           "repository.duration_ms": duration,
                           "repository.success": True
                       })
                       
                       return result
                   
                   traced = trace(tracer=tracer, event_type=EventType.tool)(wrapped)
                   setattr(cls, name, traced)
           
           return cls
       return decorator
   
   @trace_repository(entity_name="User")
   class UserRepository:
       """User data repository with automatic tracing."""
       
       def find_by_id(self, user_id: str):
           """Find user by ID."""
           return {"id": user_id, "name": "John"}
       
       def save(self, user: dict):
           """Save user to database."""
           pass
       
       def delete(self, user_id: str):
           """Delete user from database."""
           pass

**Trace Output:**

.. code-block:: python

   {
       "repository.entity": "User",
       "repository.operation": "find_by_id",
       "repository.class": "UserRepository",
       "repository.duration_ms": 12.5,
       "repository.success": True
   }

Pattern 2: Service Layer with Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def trace_service(service_name: str):
       """Decorator for service layer with error handling."""
       def decorator(cls):
           for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
               if not name.startswith('_'):
                   original_method = method
                   
                   @wraps(original_method)
                   def wrapped(self, *args, **kwargs):
                       enrich_span({
                           "service.name": service_name,
                           "service.operation": name,
                           "service.method": method.__name__
                       })
                       
                       try:
                           result = original_method(self, *args, **kwargs)
                           enrich_span({"service.status": "success"})
                           return result
                       except Exception as e:
                           enrich_span({
                               "service.status": "error",
                               "service.error_type": type(e).__name__,
                               "service.error_message": str(e)
                           })
                           raise
                   
                   traced = trace(tracer=tracer, event_type=EventType.chain)(wrapped)
                   setattr(cls, name, traced)
           
           return cls
       return decorator
   
   @trace_service(service_name="LLMOrchestrator")
   class LLMOrchestrationService:
       """Service for orchestrating LLM calls."""
       
       def generate_response(self, prompt: str) -> str:
           """Generate LLM response."""
           # LLM logic here
           return "response"
       
       def batch_generate(self, prompts: list) -> list:
           """Batch generate responses."""
           return [self.generate_response(p) for p in prompts]

Best Practices
--------------

**1. Choose the Right Approach**

- **Simple decorator (`@trace_class`)**: Quick, all public methods
- **Selective decorator**: Performance-critical code
- **Metaclass**: Framework-level instrumentation
- **Custom decorator**: Domain-specific patterns (Repository, Service)

**2. Performance Considerations**

.. code-block:: python

   # Good: Trace high-level operations
   @trace_class
   class WorkflowOrchestrator:
       def execute_workflow(self): pass  # Traced
       def _validate_step(self): pass    # Not traced

   # Avoid: Tracing low-level utility methods
   # @trace_class  # DON'T trace utility classes
   class StringUtils:
       def trim(self, s: str): pass
       def uppercase(self, s: str): pass

**3. Enrichment Strategy**

.. code-block:: python

   # Good: Add meaningful class-level context
   enrich_span({
       "class.name": cls.__name__,
       "class.instance_id": id(self),
       "business.entity_type": "User",
       "business.operation": "create"
   })
   
   # Avoid: Generic low-value attributes
   # enrich_span({"class": "SomeClass"})  # Too generic

**4. Error Handling**

Always wrap decorated methods with try-except to capture errors in spans:

.. code-block:: python

   try:
       result = original_method(self, *args, **kwargs)
       enrich_span({"success": True})
       return result
   except Exception as e:
       enrich_span({
           "error": True,
           "error_type": type(e).__name__,
           "error_message": str(e)
       })
       raise

Comparison with Method Decorators
---------------------------------

**Class Decorators:**

- ✅ Apply to all methods at once
- ✅ Consistent tracing strategy
- ❌ Less granular control per method

**Method Decorators:**

- ✅ Fine-grained control
- ✅ Method-specific event types
- ❌ Repetitive for large classes

**Recommendation:** Use class decorators for uniform tracing, method decorators for exceptions.

.. code-block:: python

   @trace_class  # Default tracing for most methods
   class DataPipeline:
       
       @trace(tracer=tracer, event_type=EventType.chain)  # Override for specific method
       def run_full_pipeline(self):
           """Critical operation with custom event type."""
           pass
       
       def load_data(self):
           """Standard method - uses class-level tracing."""
           pass

Next Steps
----------

- :doc:`custom-spans` - Create custom span structures
- :doc:`span-enrichment` - Advanced enrichment patterns
- :doc:`/how-to/llm-application-patterns` - Apply to LLM agent patterns
- :doc:`/reference/api/tracer` - Tracing API reference

**Key Takeaway:** Class-level decorators enable systematic, consistent tracing across object-oriented codebases. Use them to instrument entire classes automatically while maintaining flexibility for method-specific customization. ✨

