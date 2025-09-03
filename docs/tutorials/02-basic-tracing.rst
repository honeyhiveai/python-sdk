Basic Tracing Patterns
======================

.. note::
   **Tutorial Goal**: Learn essential tracing patterns including manual spans, async functions, and error handling.

In this tutorial, you'll master the fundamental tracing patterns that form the backbone of effective LLM observability.

What You'll Learn
-----------------

- How to create manual spans for fine-grained control
- Tracing asynchronous functions
- Adding custom attributes and metadata
- Handling errors and exceptions in traces
- Nested function tracing
- Class-level tracing with @trace_class decorator
- Performance considerations

Prerequisites
-------------

- Complete :doc:`01-quick-start` tutorial
- HoneyHive SDK installed and API key configured

Tracing Patterns Overview
--------------------------

The HoneyHive SDK provides multiple ways to add observability:

1. **@trace decorator** - Automatic function tracing (easiest)
2. **@trace_class decorator** - Automatic class-level tracing
3. **Manual spans** - Fine-grained control
4. **Context enrichment** - Adding custom data
5. **Async tracing** - For asynchronous workflows

Let's explore each pattern with practical examples.

Pattern 1: Automatic Tracing with @trace
-----------------------------------------

The ``@trace`` decorator is the simplest way to add tracing:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="tracing-tutorial"
   )
   
   @trace(tracer=tracer)
   def process_document(document: str, language: str = "en") -> dict:
       """Process a document and return analysis results."""
       word_count = len(document.split())
       char_count = len(document)
       
       return {
           "word_count": word_count,
           "char_count": char_count,
           "language": language,
           "processed": True
       }
   
   # This function call will be automatically traced
   result = process_document("Hello world from HoneyHive!", "en")

**What gets captured automatically:**

- Function name (``process_document``)
- Input arguments (``document``, ``language``)
- Return value (the analysis dictionary)
- Execution time
- Any exceptions that occur

Pattern 2: Manual Span Management
---------------------------------

For more control, create spans manually:

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="tracing-tutorial"
   )
   
   def analyze_text_manually(text: str):
       """Demonstrate manual span creation for fine-grained tracing."""
       
       # Create a parent span for the entire operation
       with tracer.trace("analyze_text") as span:
           span.set_attribute("input.text_length", len(text))
           span.set_attribute("operation.type", "text_analysis")
           
           # Create a child span for preprocessing
           with tracer.trace("preprocess_text") as preprocess_span:
               cleaned_text = text.strip().lower()
               preprocess_span.set_attribute("output.cleaned_length", len(cleaned_text))
           
           # Create another child span for analysis
           with tracer.trace("extract_features") as analysis_span:
               words = cleaned_text.split()
               unique_words = set(words)
               
               analysis_span.set_attribute("features.word_count", len(words))
               analysis_span.set_attribute("features.unique_words", len(unique_words))
               
               result = {
                   "word_count": len(words),
                   "unique_words": len(unique_words),
                   "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0
               }
           
           # Set the final result on the parent span
           span.set_attribute("result.avg_word_length", result["avg_word_length"])
           
           return result

**Benefits of manual spans:**

- Granular visibility into sub-operations
- Custom attributes and metadata
- Control over span timing and hierarchy
- Ability to trace non-function operations

Pattern 3: Async Function Tracing
---------------------------------

The ``@trace`` decorator works seamlessly with async functions:

.. code-block:: python

   import asyncio
   import aiohttp
   from honeyhive import HoneyHiveTracer, trace
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="async-tutorial"
   )
   
   @trace(tracer=tracer)
   async def fetch_data(url: str) -> dict:
       """Async function to fetch data from an API."""
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               return {
                   "status_code": response.status,
                   "content_type": response.headers.get("content-type"),
                   "data_size": len(await response.text())
               }
   
   @trace(tracer=tracer)
   async def process_multiple_urls(urls: list[str]) -> list[dict]:
       """Process multiple URLs concurrently."""
       tasks = [fetch_data(url) for url in urls]
       results = await asyncio.gather(*tasks, return_exceptions=True)
       
       # Filter out exceptions and return successful results
       return [r for r in results if not isinstance(r, Exception)]
   
   # Run the async function
   async def main():
       urls = [
           "https://api.github.com/users/octocat",
           "https://httpbin.org/json",
           "https://jsonplaceholder.typicode.com/posts/1"
       ]
       results = await process_multiple_urls(urls)
       print(f"Successfully processed {len(results)} URLs")
   
   # asyncio.run(main())

Pattern 4: Error Handling and Exception Tracing
-----------------------------------------------

HoneyHive automatically captures exceptions, but you can add context:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   import random
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="error-tutorial"
   )
   
   @trace(tracer=tracer)
   def risky_operation(data: list, threshold: float = 0.5) -> dict:
       """A function that might fail, demonstrating error tracing."""
       
       if not data:
           raise ValueError("Data list cannot be empty")
       
       if random.random() < threshold:
           raise RuntimeError("Simulated random failure")
       
       # This will be captured if successful
       result = {
           "processed_items": len(data),
           "success": True,
           "random_value": random.random()
       }
       
       return result
   
   # Example with error handling
   def safe_risky_operation(data: list):
       """Wrapper that handles errors gracefully."""
       try:
           result = risky_operation(data, threshold=0.3)  # Lower chance of failure
           print(f"✅ Success: {result}")
           return result
       except Exception as e:
           print(f"❌ Error: {e}")
           # The error is still captured in the trace!
           return {"error": str(e), "success": False}

**What happens when errors occur:**

- Exception type and message are captured
- Stack trace is recorded
- Span is marked with error status
- Execution time up to the error is measured

Pattern 5: Enriching Spans with Custom Data
-------------------------------------------

Add business context and metadata to your spans:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="enrichment-tutorial"
   )
   
   @trace(tracer=tracer, event_type="document_processing")
   def process_customer_document(customer_id: str, document_type: str, content: str):
       """Process a customer document with rich context."""
       
       # Add business context to the current span
       enrich_span({
           "customer.id": customer_id,
           "customer.tier": get_customer_tier(customer_id),
           "document.type": document_type,
           "document.size_kb": len(content.encode('utf-8')) / 1024,
           "processing.version": "2.1.0"
       })
       
       # Simulate processing
       word_count = len(content.split())
       processing_complexity = "high" if word_count > 1000 else "low"
       
       # Add processing results
       enrich_span({
           "processing.word_count": word_count,
           "processing.complexity": processing_complexity,
           "processing.completed": True
       })
       
       return {
           "status": "processed",
           "word_count": word_count,
           "complexity": processing_complexity
       }
   
   def get_customer_tier(customer_id: str) -> str:
       """Simulate customer tier lookup."""
       return "premium" if customer_id.startswith("PREM") else "standard"

Pattern 6: Nested Function Tracing
----------------------------------

See how function calls flow through your application:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="nested-tutorial"
   )
   
   @trace(tracer=tracer)
   def parse_content(content: str) -> dict:
       """Parse content into structured data."""
       lines = content.strip().split('\n')
       return {
           "lines": len(lines),
           "paragraphs": len([l for l in lines if l.strip()]),
           "words": len(content.split())
       }
   
   @trace(tracer=tracer)
   def validate_content(parsed_data: dict) -> bool:
       """Validate that parsed content meets requirements."""
       return (
           parsed_data["words"] > 10 and 
           parsed_data["lines"] > 1
       )
   
   @trace(tracer=tracer)
   def process_article(title: str, content: str) -> dict:
       """Main processing function that calls other traced functions."""
       
       # These calls will appear as child spans
       parsed = parse_content(content)
       is_valid = validate_content(parsed)
       
       result = {
           "title": title,
           "parsed_data": parsed,
           "is_valid": is_valid,
           "status": "completed" if is_valid else "failed_validation"
       }
       
       return result
   
   # This creates a trace hierarchy:
   # process_article (parent)
   # ├── parse_content (child)
   # └── validate_content (child)
   article_result = process_article(
       "My Article", 
       "This is a sample article.\n\nIt has multiple paragraphs and enough words to pass validation."
   )

Pattern 7: Class-Level Tracing with @trace_class
--------------------------------------------------

The ``@trace_class`` decorator provides automatic tracing for all public methods of a class, making it ideal for service classes, agents, and other object-oriented patterns:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace_class, enrich_span
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="class-tracing-tutorial"
   )
   
   @trace_class(event_type="tool", event_name="DocumentProcessor")
   class DocumentProcessor:
       """Document processing service with automatic method tracing."""
       
       def __init__(self, config: dict):
           # Constructor is not traced by @trace_class
           self.config = config
           self.processed_count = 0
       
       def validate_document(self, doc_content: str) -> bool:
           """Validate document format and content."""
           # This method is automatically traced as "DocumentProcessor.validate_document"
           enrich_span({
               "document.content_length": len(doc_content),
               "validation.strict_mode": self.config.get("strict", False)
           })
           
           if not doc_content.strip():
               return False
           
           # Additional validation logic
           word_count = len(doc_content.split())
           return word_count >= self.config.get("min_words", 10)
       
       def extract_metadata(self, doc_content: str) -> dict:
           """Extract metadata from document."""
           # This method is automatically traced as "DocumentProcessor.extract_metadata"
           lines = doc_content.split('\n')
           words = doc_content.split()
           
           metadata = {
               "line_count": len(lines),
               "word_count": len(words),
               "char_count": len(doc_content),
               "has_title": bool(lines and lines[0].strip())
           }
           
           enrich_span({
               "metadata.line_count": metadata["line_count"],
               "metadata.word_count": metadata["word_count"],
               "metadata.has_title": metadata["has_title"]
           })
           
           return metadata
       
       def process_document(self, doc_content: str) -> dict:
           """Process a complete document."""
           # This method is automatically traced as "DocumentProcessor.process_document"
           
           enrich_span({
               "processor.total_processed": self.processed_count,
               "document.size_category": "large" if len(doc_content) > 1000 else "small"
           })
           
           # Call other traced methods - creates nested spans
           if not self.validate_document(doc_content):
               raise ValueError("Document validation failed")
           
           metadata = self.extract_metadata(doc_content)
           
           # Update internal state
           self.processed_count += 1
           
           return {
               "status": "processed",
               "metadata": metadata,
               "processor_state": {
                   "total_processed": self.processed_count
               }
           }
       
       async def async_process_batch(self, documents: list) -> list:
           """Async batch processing with automatic tracing."""
           # This async method is automatically traced as "DocumentProcessor.async_process_batch"
           import asyncio
           
           enrich_span({
               "batch.document_count": len(documents),
               "batch.processing_mode": "async"
           })
           
           results = []
           for i, doc in enumerate(documents):
               enrich_span({f"batch.document_{i}.length": len(doc)})
               
               # Simulate async processing
               await asyncio.sleep(0.01)
               result = self.process_document(doc)
               results.append(result)
           
           return results
       
       def _private_helper(self):
           """Private methods are not traced by @trace_class."""
           return "helper result"

**Using the traced class:**

.. code-block:: python

   # Initialize the processor
   processor = DocumentProcessor({
       "strict": True,
       "min_words": 5
   })
   
   # Each method call creates traces automatically
   doc_content = "Sample Document\n\nThis is a sample document with multiple paragraphs."
   
   try:
       result = processor.process_document(doc_content)
       print(f"Processed document: {result['status']}")
       print(f"Word count: {result['metadata']['word_count']}")
   except ValueError as e:
       print(f"Processing failed: {e}")

**Advanced Class Tracing Patterns:**

.. code-block:: python

   @trace_class(
       event_type=EventType.chain,
       event_name="LLMAgent",
       agent_type="reasoning",  # Custom attribute for all methods
       version="1.0"           # Another custom attribute
   )
   class ReasoningAgent:
       """LLM-powered reasoning agent with comprehensive tracing."""
       
       def __init__(self, llm_client, max_iterations: int = 5):
           self.llm_client = llm_client
           self.max_iterations = max_iterations
           self.conversation_history = []
       
       def analyze_problem(self, problem: str) -> dict:
           """Analyze problem complexity and requirements."""
           # Automatically traced with event_name "LLMAgent.analyze_problem"
           # and custom attributes: agent_type="reasoning", version="1.0"
           
           complexity_score = len(problem.split()) / 10  # Simple heuristic
           
           enrich_span({
               "problem.length": len(problem),
               "problem.complexity_score": complexity_score,
               "analysis.requires_llm": complexity_score > 2
           })
           
           return {
               "complexity": complexity_score,
               "requires_llm": complexity_score > 2,
               "estimated_iterations": min(int(complexity_score), self.max_iterations)
           }
       
       def generate_reasoning_step(self, problem: str, context: str) -> str:
           """Generate one reasoning step using LLM."""
           # Automatically traced with all class-level attributes
           
           prompt = f"Problem: {problem}\nContext: {context}\nNext reasoning step:"
           
           enrich_span({
               "llm.prompt_length": len(prompt),
               "reasoning.step_number": len(self.conversation_history) + 1
           })
           
           # Simulate LLM call (replace with actual LLM client)
           response = f"Reasoning step for: {problem[:50]}..."
           
           self.conversation_history.append({
               "prompt": prompt,
               "response": response
           })
           
           return response
       
       def solve(self, problem: str) -> dict:
           """Solve problem using multi-step reasoning."""
           analysis = self.analyze_problem(problem)
           
           if not analysis["requires_llm"]:
               return {"solution": "Simple problem, no LLM needed", "steps": []}
           
           steps = []
           context = ""
           
           for i in range(analysis["estimated_iterations"]):
               step = self.generate_reasoning_step(problem, context)
               steps.append(step)
               context += f"\nStep {i+1}: {step}"
           
           enrich_span({
               "solution.total_steps": len(steps),
               "solution.conversation_length": len(self.conversation_history)
           })
           
           return {
               "solution": f"Solved in {len(steps)} steps",
               "steps": steps,
               "analysis": analysis
           }

**Class Decorator Benefits:**

1. **Automatic Coverage**: All public methods are traced without individual decorators
2. **Consistent Naming**: Method names are automatically prefixed with class name
3. **Mixed Sync/Async**: Handles both synchronous and asynchronous methods
4. **Custom Attributes**: Apply common attributes to all methods
5. **Clean Code**: Reduces decorator boilerplate in service classes

**When to Use @trace_class:**

- **Service Classes**: API clients, data processors, business logic services
- **Agent Classes**: LLM agents, workflow orchestrators, decision engines
- **State Machines**: Classes that manage complex state transitions
- **Batch Processors**: Classes that handle multiple items with similar operations

**Class Decorator Limitations:**

- Does not trace ``__init__``, ``__new__``, or private methods (starting with ``_``)
- Cannot provide method-specific event types (all methods use the class-level event_type)
- Performance overhead applies to all methods, not just critical ones

Best Practices
--------------

**1. Use Meaningful Names**

.. code-block:: python

   # Good
   @trace(tracer=tracer, event_type="user_authentication")
   def authenticate_user(username: str) -> bool:
       pass
   
   # Less helpful
   @trace(tracer=tracer)
   def auth(u: str) -> bool:
       pass

**2. Add Business Context**

.. code-block:: python

   @trace(tracer=tracer)
   def process_order(order_id: str):
       enrich_span({
           "order.id": order_id,
           "order.value": get_order_value(order_id),
           "customer.segment": get_customer_segment(order_id)
       })

**3. Trace at the Right Level**

- Trace business operations, not every utility function
- Focus on functions that represent meaningful work
- Balance detail with performance

**4. Choose the Right Decorator**

.. code-block:: python

   # Use @trace for individual functions
   @trace(tracer=tracer, event_type=EventType.model)
   def call_llm(prompt: str) -> str:
       pass
   
   # Use @trace_class for service classes with multiple related methods
   @trace_class(event_type="tool", event_name="DataService")
   class DataProcessor:
       def validate(self, data): pass
       def transform(self, data): pass  
       def save(self, data): pass

**5. Event Type Selection for Classes**

- Use ``"tool"`` for service classes and utility classes
- Use ``"model"`` for LLM-focused classes
- Use ``"chain"`` for workflow orchestration classes

**6. Handle Errors Gracefully**

.. code-block:: python

   @trace(tracer=tracer)
   def safe_operation():
       try:
           return risky_function()
       except SpecificError as e:
           enrich_span({"error.type": "expected", "error.handled": True})
           return default_value()

Performance Considerations
---------------------------

**Tracing Overhead**

- The ``@trace`` decorator adds minimal overhead (microseconds)
- Manual spans have slightly more overhead but still negligible
- Async tracing is optimized for concurrent operations

**When to Use Each Pattern**

- **@trace decorator**: Most functions (80% of cases)
- **Manual spans**: Complex operations needing fine-grained visibility
- **enrich_span**: Adding business context to automatic traces

Complete Example: Document Processing Pipeline
-----------------------------------------------

Here's a complete example combining all patterns:

.. code-block:: python

   import asyncio
   from honeyhive import HoneyHiveTracer, trace, enrich_span
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="document-pipeline"
   )
   
   @trace(tracer=tracer, event_type="document_validation")
   def validate_document(content: str) -> bool:
       """Validate document meets requirements."""
       word_count = len(content.split())
       char_count = len(content)
       
       enrich_span({
           "validation.word_count": word_count,
           "validation.char_count": char_count,
           "validation.min_words": 50
       })
       
       return word_count >= 50
   
   @trace(tracer=tracer, event_type="document_analysis")
   async def analyze_document(content: str) -> dict:
       """Analyze document content asynchronously."""
       
       # Simulate async analysis
       await asyncio.sleep(0.1)
       
       analysis = {
           "sentiment": "positive" if "good" in content.lower() else "neutral",
           "topics": ["technology", "tutorial"],
           "readability": "high"
       }
       
       enrich_span({
           "analysis.sentiment": analysis["sentiment"],
           "analysis.topic_count": len(analysis["topics"])
       })
       
       return analysis
   
   @trace(tracer=tracer, event_type="document_processing")
   async def process_document_pipeline(doc_id: str, content: str) -> dict:
       """Complete document processing pipeline."""
       
       enrich_span({
           "document.id": doc_id,
           "document.size_bytes": len(content.encode('utf-8')),
           "pipeline.version": "1.0"
       })
       
       try:
           # Step 1: Validate
           is_valid = validate_document(content)
           if not is_valid:
               raise ValueError("Document validation failed")
           
           # Step 2: Analyze
           analysis = await analyze_document(content)
           
           # Step 3: Combine results
           result = {
               "document_id": doc_id,
               "validation_passed": is_valid,
               "analysis": analysis,
               "processing_status": "completed"
           }
           
           enrich_span({
               "pipeline.status": "success",
               "pipeline.steps_completed": 3
           })
           
           return result
           
       except Exception as e:
           enrich_span({
               "pipeline.status": "failed",
               "pipeline.error": str(e)
           })
           raise
   
   # Usage
   async def main():
       result = await process_document_pipeline(
           "doc_123",
           "This is a good example document with enough words to pass validation. " * 10
       )
       print(f"Pipeline result: {result['processing_status']}")
   
   # asyncio.run(main())

What's Next?
------------

You now understand the core tracing patterns! Next steps:

- :doc:`03-llm-integration` - Add LLM provider tracing
- :doc:`04-evaluation-basics` - Start evaluating your traced operations
- :doc:`../how-to/advanced-tracing/index` - Advanced tracing techniques

Key Takeaways
-------------

- **@trace decorator**: Easiest way to add observability
- **Manual spans**: Fine-grained control and custom attributes
- **Async support**: Works seamlessly with async/await
- **Error handling**: Automatic exception capture with custom context
- **Enrichment**: Add business context with ``enrich_span()``
- **Nesting**: Automatic hierarchy for function call chains

.. tip::
   Start simple with ``@trace`` decorators, then add manual spans and enrichment where you need more detail. The goal is actionable observability, not just data collection!
