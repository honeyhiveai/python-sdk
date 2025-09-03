Common LLM Application Patterns
================================

Learn proven patterns and best practices for building robust, scalable LLM applications with comprehensive observability.

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
--------

This guide covers common architectural patterns and implementation strategies for LLM applications, with focus on observability, reliability, and performance optimization.

**Pattern Categories**:
- Agent and workflow patterns
- Error handling and resilience
- Performance optimization
- Cost management
- Quality assurance

Agent and Workflow Patterns
---------------------------

**Multi-Step Reasoning Agent (Decorator-First Approach)**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, trace_class, enrich_span, set_default_tracer
   from honeyhive.models import EventType
   from typing import List, Dict, Any
   import time

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="agent-patterns"
   )
   set_default_tracer(tracer)

   @trace_class(event_type=EventType.chain, event_name="ReasoningAgent")
   class ReasoningAgent:
       """Multi-step reasoning agent with comprehensive tracing."""
       
       def __init__(self, llm_client, tools: List[Any]):
           self.llm_client = llm_client
           self.tools = {tool.name: tool for tool in tools}
           self.max_iterations = 10
       
       def solve_problem(self, problem: str, context: Dict = None) -> Dict:
           """Solve complex problem using multi-step reasoning."""
           # Method automatically traced as "ReasoningAgent.solve_problem"
           
           enrich_span({
               "agent.problem": problem,
               "agent.tools_available": list(self.tools.keys()),
               "agent.max_iterations": self.max_iterations,
               "agent.has_context": context is not None
           })
           
           reasoning_history = []
           iteration = 0
           solution_found = False
           
           while iteration < self.max_iterations and not solution_found:
               # Use context manager only for iteration-level spans
               with tracer.start_span(f"reasoning_iteration_{iteration + 1}") as iter_span:
                   iter_span.set_attribute("iteration.number", iteration + 1)
                   iter_span.set_attribute("iteration.reasoning_steps", len(reasoning_history))
                   
                   # Step 1: Analyze current state (method is automatically traced)
                   current_state = self.analyze_current_state(problem, reasoning_history, context)
                   
                   # Step 2: Decide on action (method is automatically traced)
                   action_plan = self.select_action(current_state, reasoning_history)
                   
                   # Step 3: Execute action (method is automatically traced)
                   try:
                       action_result = self.execute_action(action_plan)
                       
                       reasoning_history.append({
                           "iteration": iteration + 1,
                           "state": current_state,
                           "action": action_plan,
                           "result": action_result,
                           "timestamp": time.time()
                       })
                       
                       # Check if solution is found
                       if action_result.get("solution_found"):
                           solution_found = True
                           iter_span.set_attribute("execution.solution_found", True)
                               
                   except Exception as e:
                       iter_span.set_attribute("execution.success", False)
                       iter_span.set_attribute("execution.error", str(e))
                       # Continue to next iteration on error
                       
                   iteration += 1
               
               return {
                   "solution_found": solution_found,
                   "iterations": iteration,
                   "reasoning_history": reasoning_history,
                   "final_result": reasoning_history[-1] if reasoning_history else None
               }
       
       def analyze_current_state(self, problem: str, history: List, context: Dict = None) -> Dict:
           """Analyze current state - automatically traced by @trace_class."""
           enrich_span({
               "analysis.problem_length": len(problem),
               "analysis.history_steps": len(history),
               "analysis.has_context": context is not None
           })
           
           # Simulate analysis logic
           confidence = 0.8 if len(history) > 0 else 0.3
           next_action = "continue" if confidence > 0.5 else "explore"
           
           return {
               "confidence": confidence,
               "next_action": next_action,
               "step_count": len(history)
           }
       
       def select_action(self, state: Dict, history: List) -> Dict:
           """Select next action - automatically traced by @trace_class."""
           enrich_span({
               "action.confidence_level": state.get("confidence", 0),
               "action.history_length": len(history)
           })
           
           # Simulate action selection logic
           return {
               "type": "reasoning",
               "tool": "llm_call" if state.get("confidence", 0) < 0.7 else None,
               "confidence": state.get("confidence", 0)
           }
       
       def execute_action(self, action_plan: Dict) -> Dict:
           """Execute planned action - automatically traced by @trace_class."""
           enrich_span({
               "execution.action_type": action_plan.get("type"),
               "execution.uses_tool": action_plan.get("tool") is not None
           })
           
           # Simulate action execution
           import random
           success = random.random() > 0.2  # 80% success rate
           solution_found = success and random.random() > 0.7  # 30% chance of finding solution
           
           return {
               "success": success,
               "solution_found": solution_found,
               "result": f"Action {action_plan.get('type')} completed"
           }

   # Usage example with clean decorator-based approach
   agent = ReasoningAgent(llm_client=None, tools=[])
   result = agent.solve_problem("How can I optimize my database queries?")

**Key Benefits of the Decorator-First Approach:**

- **@trace_class**: Automatically traces all public methods with consistent naming
- **enrich_span()**: Adds business context without complex span management
- **Context managers**: Used only for iteration-level grouping, not individual operations
- **Clean code**: Business logic isn't cluttered with tracing boilerplate

**Data Processing Pipeline Pattern**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, set_default_tracer
   from honeyhive.models import EventType
   import pandas as pd
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key", 
       project="data-pipeline"
   )
   set_default_tracer(tracer)
   
   @trace(event_type=EventType.tool)
   def load_data(source: str) -> pd.DataFrame:
       """Load data from source - automatically traced."""
       enrich_span({
           "data.source": source,
           "data.source_type": "database" if "db://" in source else "file"
       })
       
       # Simulate data loading
       data = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
       
       enrich_span({
           "data.rows_loaded": len(data),
           "data.columns": list(data.columns)
       })
       
       return data
   
   @trace(event_type=EventType.tool)
   def validate_data(data: pd.DataFrame) -> pd.DataFrame:
       """Validate data quality - automatically traced."""
       enrich_span({
           "validation.input_rows": len(data),
           "validation.has_nulls": data.isnull().any().any()
       })
       
       # Remove invalid rows
       clean_data = data.dropna()
       
       enrich_span({
           "validation.output_rows": len(clean_data),
           "validation.rows_removed": len(data) - len(clean_data)
       })
       
       return clean_data
   
   @trace(event_type=EventType.tool)
   def transform_data(data: pd.DataFrame) -> pd.DataFrame:
       """Transform data - automatically traced."""
       enrich_span({
           "transform.input_shape": data.shape,
           "transform.operation": "value_multiplication"
       })
       
       # Apply transformation
       transformed = data.copy()
       transformed["value"] = transformed["value"] * 2
       
       enrich_span({
           "transform.output_shape": transformed.shape
       })
       
       return transformed
   
   @trace(event_type=EventType.chain)
   def run_data_pipeline(source: str) -> pd.DataFrame:
       """Complete data pipeline - automatically traced."""
       enrich_span({
           "pipeline.source": source,
           "pipeline.version": "1.0"
       })
       
       # Clean pipeline using decorated functions
       raw_data = load_data(source)
       validated_data = validate_data(raw_data)
       final_data = transform_data(validated_data)
       
       enrich_span({
           "pipeline.status": "completed",
           "pipeline.final_rows": len(final_data)
       })
       
       return final_data
   
   # Usage
   result = run_data_pipeline("data/input.csv")

Error Handling and Resilience Patterns
---------------------------------------

.. code-block:: python

   class ToolUsingAgent:
       """Agent that can dynamically select and use tools."""
       
       def __init__(self, llm_client, available_tools: Dict):
           self.llm_client = llm_client
           self.tools = available_tools
       
       def process_request(self, user_request: str) -> Dict:
           """Process user request using appropriate tools."""
           
           with tracer.start_span("tool_using_agent") as agent_span:
               agent_span.set_attribute("request.user_input", user_request)
               agent_span.set_attribute("tools.available_count", len(self.tools))
               agent_span.set_attribute("tools.available_names", list(self.tools.keys()))
               
               # Step 1: Understand intent and extract parameters
               with tracer.start_span("intent_analysis") as intent_span:
                   intent_analysis = self._analyze_intent(user_request)
                   intent_span.set_attribute("intent.primary", intent_analysis.get("primary_intent"))
                   intent_span.set_attribute("intent.confidence", intent_analysis.get("confidence", 0))
                   intent_span.set_attribute("intent.parameters_count", len(intent_analysis.get("parameters", {})))
               
               # Step 2: Tool selection and planning
               with tracer.start_span("tool_selection") as selection_span:
                   tool_plan = self._select_tools(intent_analysis)
                   selection_span.set_attribute("plan.tools_selected", len(tool_plan.get("tools", [])))
                   selection_span.set_attribute("plan.sequential", tool_plan.get("sequential", True))
                   
                   if tool_plan.get("tools"):
                       selection_span.set_attribute("plan.tool_names", 
                                                  [t["name"] for t in tool_plan["tools"]])
               
               # Step 3: Execute tool sequence
               tool_results = []
               for i, tool_config in enumerate(tool_plan.get("tools", [])):
                   with tracer.start_span(f"tool_execution_{i+1}") as tool_span:
                       tool_name = tool_config["name"]
                       tool_params = tool_config.get("parameters", {})
                       
                       tool_span.set_attribute("tool.name", tool_name)
                       tool_span.set_attribute("tool.parameters", str(tool_params))
                       tool_span.set_attribute("tool.sequence_position", i + 1)
                       
                       try:
                           tool_result = self._execute_tool(tool_name, tool_params, tool_results)
                           tool_span.set_attribute("tool.success", True)
                           tool_span.set_attribute("tool.result_type", type(tool_result).__name__)
                           
                           tool_results.append({
                               "tool": tool_name,
                               "parameters": tool_params,
                               "result": tool_result,
                               "success": True
                           })
                           
                       except Exception as e:
                           tool_span.set_attribute("tool.success", False)
                           tool_span.set_attribute("tool.error", str(e))
                           tool_span.set_status("ERROR", str(e))
                           
                           tool_results.append({
                               "tool": tool_name,
                               "parameters": tool_params,
                               "error": str(e),
                               "success": False
                           })
               
               # Step 4: Synthesize final response
               with tracer.start_span("response_synthesis") as synthesis_span:
                   final_response = self._synthesize_response(
                       user_request, intent_analysis, tool_results
                   )
                   
                   synthesis_span.set_attribute("response.length", len(str(final_response)))
                   synthesis_span.set_attribute("response.tools_used", len(tool_results))
                   synthesis_span.set_attribute("response.successful_tools", 
                                               sum(1 for r in tool_results if r.get("success")))
               
               agent_span.set_attribute("agent.tools_executed", len(tool_results))
               agent_span.set_attribute("agent.success_rate", 
                                       sum(1 for r in tool_results if r.get("success")) / len(tool_results) 
                                       if tool_results else 0)
               
               return {
                   "response": final_response,
                   "intent_analysis": intent_analysis,
                   "tool_results": tool_results,
                   "execution_summary": {
                       "tools_used": len(tool_results),
                       "success_rate": sum(1 for r in tool_results if r.get("success")) / len(tool_results) if tool_results else 0
                   }
               }

Error Handling and Resilience Patterns
--------------------------------------

**Circuit Breaker Pattern for LLM Calls**

.. code-block:: python

   import time
   from enum import Enum
   from typing import Callable, Any

   class CircuitState(Enum):
       CLOSED = "closed"       # Normal operation
       OPEN = "open"          # Circuit is open, calls fail fast
       HALF_OPEN = "half_open" # Testing if service is back

   class LLMCircuitBreaker:
       """Circuit breaker pattern for LLM API calls."""
       
       def __init__(self, failure_threshold: int = 5, timeout: int = 60):
           self.failure_threshold = failure_threshold
           self.timeout = timeout
           self.failure_count = 0
           self.last_failure_time = None
           self.state = CircuitState.CLOSED
       
       def call(self, llm_function: Callable, *args, **kwargs) -> Any:
           """Execute LLM function with circuit breaker protection."""
           
           with tracer.start_span("circuit_breaker_call") as cb_span:
               cb_span.set_attribute("circuit.state", self.state.value)
               cb_span.set_attribute("circuit.failure_count", self.failure_count)
               cb_span.set_attribute("circuit.failure_threshold", self.failure_threshold)
               
               # Check circuit state
               if self.state == CircuitState.OPEN:
                   if self._should_attempt_reset():
                       self.state = CircuitState.HALF_OPEN
                       cb_span.set_attribute("circuit.state_transition", "open_to_half_open")
                   else:
                       cb_span.set_attribute("circuit.call_blocked", True)
                       cb_span.set_status("ERROR", "Circuit breaker is OPEN")
                       raise Exception("Circuit breaker is OPEN - calls are being blocked")
               
               # Attempt the call
               try:
                   with tracer.start_span("llm_function_call") as call_span:
                       call_span.set_attribute("function.name", llm_function.__name__)
                       call_span.set_attribute("function.args_count", len(args))
                       call_span.set_attribute("function.kwargs_count", len(kwargs))
                       
                       start_time = time.time()
                       result = llm_function(*args, **kwargs)
                       call_duration = time.time() - start_time
                       
                       call_span.set_attribute("function.duration_ms", call_duration * 1000)
                       call_span.set_attribute("function.success", True)
                   
                   # Success - reset circuit if needed
                   if self.state == CircuitState.HALF_OPEN:
                       self._reset_circuit()
                       cb_span.set_attribute("circuit.state_transition", "half_open_to_closed")
                   
                   cb_span.set_attribute("circuit.call_success", True)
                   return result
                   
               except Exception as e:
                   # Failure - update circuit state
                   self._record_failure()
                   
                   cb_span.set_attribute("circuit.call_success", False)
                   cb_span.set_attribute("circuit.failure_recorded", True)
                   cb_span.set_attribute("circuit.new_failure_count", self.failure_count)
                   
                   if self.failure_count >= self.failure_threshold:
                       self.state = CircuitState.OPEN
                       self.last_failure_time = time.time()
                       cb_span.set_attribute("circuit.state_transition", "closed_to_open")
                   
                   cb_span.set_status("ERROR", str(e))
                   raise
       
       def _should_attempt_reset(self) -> bool:
           """Check if enough time has passed to attempt reset."""
           return (time.time() - self.last_failure_time) >= self.timeout
       
       def _record_failure(self):
           """Record a failure and update counters."""
           self.failure_count += 1
           self.last_failure_time = time.time()
       
       def _reset_circuit(self):
           """Reset circuit to normal operation."""
           self.failure_count = 0
           self.last_failure_time = None
           self.state = CircuitState.CLOSED

**Retry with Exponential Backoff**

.. code-block:: python

   import random
   from typing import Type, Tuple

   class RetryableOperation:
       """Retry mechanism with exponential backoff and jitter."""
       
       def __init__(self, 
                    max_retries: int = 3,
                    base_delay: float = 1.0,
                    max_delay: float = 60.0,
                    exponential_factor: float = 2.0,
                    jitter: bool = True,
                    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)):
           
           self.max_retries = max_retries
           self.base_delay = base_delay
           self.max_delay = max_delay
           self.exponential_factor = exponential_factor
           self.jitter = jitter
           self.retryable_exceptions = retryable_exceptions
       
       def execute(self, operation: Callable, *args, **kwargs) -> Any:
           """Execute operation with retry logic."""
           
           with tracer.start_span("retryable_operation") as retry_span:
               retry_span.set_attribute("retry.max_attempts", self.max_retries + 1)
               retry_span.set_attribute("retry.base_delay", self.base_delay)
               retry_span.set_attribute("retry.max_delay", self.max_delay)
               retry_span.set_attribute("retry.operation", operation.__name__)
               
               last_exception = None
               
               for attempt in range(self.max_retries + 1):
                   with tracer.start_span(f"attempt_{attempt + 1}") as attempt_span:
                       attempt_span.set_attribute("attempt.number", attempt + 1)
                       attempt_span.set_attribute("attempt.is_retry", attempt > 0)
                       
                       try:
                           result = operation(*args, **kwargs)
                           attempt_span.set_attribute("attempt.success", True)
                           retry_span.set_attribute("retry.successful_attempt", attempt + 1)
                           retry_span.set_attribute("retry.total_attempts", attempt + 1)
                           return result
                           
                       except self.retryable_exceptions as e:
                           last_exception = e
                           attempt_span.set_attribute("attempt.success", False)
                           attempt_span.set_attribute("attempt.error_type", type(e).__name__)
                           attempt_span.set_attribute("attempt.error_message", str(e))
                           attempt_span.set_status("ERROR", str(e))
                           
                           # Don't wait after the last attempt
                           if attempt < self.max_retries:
                               delay = self._calculate_delay(attempt)
                               attempt_span.set_attribute("attempt.retry_delay_seconds", delay)
                               
                               with tracer.start_span("retry_delay") as delay_span:
                                   delay_span.set_attribute("delay.duration_seconds", delay)
                                   delay_span.set_attribute("delay.attempt", attempt + 1)
                                   time.sleep(delay)
               
               # All attempts failed
               retry_span.set_attribute("retry.all_attempts_failed", True)
               retry_span.set_attribute("retry.total_attempts", self.max_retries + 1)
               retry_span.set_attribute("retry.final_error", str(last_exception))
               retry_span.set_status("ERROR", f"All {self.max_retries + 1} attempts failed")
               
               raise last_exception
       
       def _calculate_delay(self, attempt: int) -> float:
           """Calculate delay for given attempt with exponential backoff and jitter."""
           
           delay = min(
               self.base_delay * (self.exponential_factor ** attempt),
               self.max_delay
           )
           
           if self.jitter:
               # Add random jitter (±25%)
               jitter_amount = delay * 0.25
               delay += random.uniform(-jitter_amount, jitter_amount)
           
           return max(0, delay)

**Graceful Degradation Pattern**

.. code-block:: python

   class GracefulDegradationService:
       """Service that gracefully degrades when dependencies fail."""
       
       def __init__(self, primary_llm, fallback_llm=None, cache_service=None):
           self.primary_llm = primary_llm
           self.fallback_llm = fallback_llm
           self.cache_service = cache_service
           self.circuit_breaker = LLMCircuitBreaker()
           self.retry_handler = RetryableOperation()
       
       def generate_response(self, prompt: str, context: Dict = None) -> Dict:
           """Generate response with graceful degradation."""
           
           with tracer.start_span("graceful_degradation_service") as service_span:
               service_span.set_attribute("service.prompt", prompt)
               service_span.set_attribute("service.has_context", context is not None)
               service_span.set_attribute("service.has_fallback", self.fallback_llm is not None)
               service_span.set_attribute("service.has_cache", self.cache_service is not None)
               
               # Level 1: Try cache first
               if self.cache_service:
                   with tracer.start_span("cache_lookup") as cache_span:
                       try:
                           cache_key = self._generate_cache_key(prompt, context)
                           cached_response = self.cache_service.get(cache_key)
                           
                           if cached_response:
                               cache_span.set_attribute("cache.hit", True)
                               service_span.set_attribute("service.response_source", "cache")
                               return {
                                   "response": cached_response,
                                   "source": "cache",
                                   "degradation_level": 0
                               }
                           
                           cache_span.set_attribute("cache.hit", False)
                           
                       except Exception as e:
                           cache_span.set_attribute("cache.error", str(e))
                           cache_span.set_status("ERROR", str(e))
               
               # Level 2: Try primary LLM with circuit breaker
               try:
                   with tracer.start_span("primary_llm_attempt") as primary_span:
                       primary_span.set_attribute("llm.type", "primary")
                       
                       response = self.circuit_breaker.call(
                           self.retry_handler.execute,
                           self.primary_llm.generate,
                           prompt,
                           context=context
                       )
                       
                       primary_span.set_attribute("llm.success", True)
                       service_span.set_attribute("service.response_source", "primary_llm")
                       
                       # Cache successful response
                       if self.cache_service:
                           self._cache_response(prompt, context, response)
                       
                       return {
                           "response": response,
                           "source": "primary_llm",
                           "degradation_level": 1
                       }
                       
               except Exception as e:
                   with tracer.start_span("primary_llm_failure") as failure_span:
                       failure_span.set_attribute("primary.error", str(e))
                       failure_span.set_status("ERROR", str(e))
               
               # Level 3: Try fallback LLM
               if self.fallback_llm:
                   try:
                       with tracer.start_span("fallback_llm_attempt") as fallback_span:
                           fallback_span.set_attribute("llm.type", "fallback")
                           
                           response = self.fallback_llm.generate(prompt, context=context)
                           
                           fallback_span.set_attribute("llm.success", True)
                           service_span.set_attribute("service.response_source", "fallback_llm")
                           
                           return {
                               "response": response,
                               "source": "fallback_llm",
                               "degradation_level": 2
                           }
                           
                   except Exception as e:
                       with tracer.start_span("fallback_llm_failure") as fallback_failure_span:
                           fallback_failure_span.set_attribute("fallback.error", str(e))
                           fallback_failure_span.set_status("ERROR", str(e))
               
               # Level 4: Return static/template response
               with tracer.start_span("static_response_fallback") as static_span:
                   static_response = self._generate_static_response(prompt, context)
                   static_span.set_attribute("response.type", "static_fallback")
                   service_span.set_attribute("service.response_source", "static_fallback")
                   
                   return {
                       "response": static_response,
                       "source": "static_fallback",
                       "degradation_level": 3,
                       "warning": "Service is experiencing issues. This is a fallback response."
                   }

Performance Optimization Patterns
---------------------------------

**Batching and Parallel Processing**

.. code-block:: python

   import asyncio
   from concurrent.futures import ThreadPoolExecutor, as_completed
   from typing import List, Callable, Any

   class BatchProcessor:
       """Efficient batch processing for LLM operations."""
       
       def __init__(self, max_workers: int = 4, batch_size: int = 10):
           self.max_workers = max_workers
           self.batch_size = batch_size
       
       def process_batch_parallel(self, items: List[Any], 
                                processor_func: Callable, 
                                **kwargs) -> List[Any]:
           """Process items in parallel batches."""
           
           with tracer.start_span("batch_parallel_processing") as batch_span:
               batch_span.set_attribute("batch.total_items", len(items))
               batch_span.set_attribute("batch.max_workers", self.max_workers)
               batch_span.set_attribute("batch.batch_size", self.batch_size)
               
               results = []
               
               # Split items into batches
               batches = [items[i:i + self.batch_size] 
                         for i in range(0, len(items), self.batch_size)]
               
               batch_span.set_attribute("batch.number_of_batches", len(batches))
               
               with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                   # Submit all batches
                   future_to_batch = {}
                   
                   for i, batch in enumerate(batches):
                       with tracer.start_span(f"batch_submission_{i+1}") as submit_span:
                           submit_span.set_attribute("batch.index", i + 1)
                           submit_span.set_attribute("batch.size", len(batch))
                           
                           future = executor.submit(
                               self._process_single_batch, 
                               batch, processor_func, i + 1, **kwargs
                           )
                           future_to_batch[future] = i + 1
                   
                   # Collect results as they complete
                   for future in as_completed(future_to_batch):
                       batch_index = future_to_batch[future]
                       
                       with tracer.start_span(f"batch_completion_{batch_index}") as complete_span:
                           complete_span.set_attribute("batch.index", batch_index)
                           
                           try:
                               batch_results = future.result()
                               results.extend(batch_results)
                               complete_span.set_attribute("batch.success", True)
                               complete_span.set_attribute("batch.results_count", len(batch_results))
                               
                           except Exception as e:
                               complete_span.set_attribute("batch.success", False)
                               complete_span.set_attribute("batch.error", str(e))
                               complete_span.set_status("ERROR", str(e))
                               raise
               
               batch_span.set_attribute("batch.total_results", len(results))
               batch_span.set_attribute("batch.success", True)
               
               return results
       
       def _process_single_batch(self, batch: List[Any], 
                               processor_func: Callable, 
                               batch_index: int, 
                               **kwargs) -> List[Any]:
           """Process a single batch of items."""
           
           with tracer.start_span(f"single_batch_processing") as batch_span:
               batch_span.set_attribute("batch.index", batch_index)
               batch_span.set_attribute("batch.size", len(batch))
               
               results = []
               
               for i, item in enumerate(batch):
                   with tracer.start_span(f"item_processing_{i+1}") as item_span:
                       item_span.set_attribute("item.index_in_batch", i + 1)
                       item_span.set_attribute("item.global_index", 
                                              (batch_index - 1) * self.batch_size + i + 1)
                       
                       try:
                           result = processor_func(item, **kwargs)
                           item_span.set_attribute("item.success", True)
                           item_span.set_attribute("item.result_type", type(result).__name__)
                           results.append(result)
                           
                       except Exception as e:
                           item_span.set_attribute("item.success", False)
                           item_span.set_attribute("item.error", str(e))
                           item_span.set_status("ERROR", str(e))
                           raise
               
               batch_span.set_attribute("batch.processed_items", len(results))
               return results

**Caching Strategies**

.. code-block:: python

   import hashlib
   import json
   from typing import Optional, Union, Dict, Any

   class LLMCacheManager:
       """Intelligent caching for LLM responses."""
       
       def __init__(self, cache_backend, ttl_seconds: int = 3600):
           self.cache = cache_backend
           self.ttl = ttl_seconds
       
       def get_cached_response(self, prompt: str, 
                             model_config: Dict,
                             context: Optional[Dict] = None) -> Optional[str]:
           """Get cached response if available."""
           
           with tracer.start_span("cache_lookup") as cache_span:
               cache_key = self._generate_cache_key(prompt, model_config, context)
               cache_span.set_attribute("cache.key", cache_key[:50] + "..." if len(cache_key) > 50 else cache_key)
               
               try:
                   cached_data = self.cache.get(cache_key)
                   
                   if cached_data:
                       cache_span.set_attribute("cache.hit", True)
                       cache_span.set_attribute("cache.response_length", len(cached_data.get("response", "")))
                       cache_span.set_attribute("cache.age_seconds", 
                                              time.time() - cached_data.get("timestamp", 0))
                       
                       return cached_data["response"]
                   
                   cache_span.set_attribute("cache.hit", False)
                   return None
                   
               except Exception as e:
                   cache_span.set_attribute("cache.error", str(e))
                   cache_span.set_status("ERROR", str(e))
                   return None
       
       def cache_response(self, prompt: str, 
                         model_config: Dict,
                         response: str,
                         context: Optional[Dict] = None,
                         quality_score: Optional[float] = None) -> bool:
           """Cache response with metadata."""
           
           with tracer.start_span("cache_store") as store_span:
               cache_key = self._generate_cache_key(prompt, model_config, context)
               store_span.set_attribute("cache.key", cache_key[:50] + "..." if len(cache_key) > 50 else cache_key)
               store_span.set_attribute("cache.response_length", len(response))
               store_span.set_attribute("cache.has_quality_score", quality_score is not None)
               
               # Only cache high-quality responses
               if quality_score is not None and quality_score < 0.7:
                   store_span.set_attribute("cache.skipped_low_quality", True)
                   store_span.set_attribute("cache.quality_threshold", 0.7)
                   return False
               
               try:
                   cache_data = {
                       "response": response,
                       "timestamp": time.time(),
                       "model_config": model_config,
                       "quality_score": quality_score,
                       "prompt_hash": hashlib.md5(prompt.encode()).hexdigest()
                   }
                   
                   success = self.cache.set(cache_key, cache_data, ttl=self.ttl)
                   store_span.set_attribute("cache.stored", success)
                   
                   return success
                   
               except Exception as e:
                   store_span.set_attribute("cache.store_error", str(e))
                   store_span.set_status("ERROR", str(e))
                   return False
       
       def _generate_cache_key(self, prompt: str, 
                             model_config: Dict,
                             context: Optional[Dict] = None) -> str:
           """Generate deterministic cache key."""
           
           key_components = {
               "prompt": prompt,
               "model": model_config.get("model", "unknown"),
               "temperature": model_config.get("temperature", 0.7),
               "max_tokens": model_config.get("max_tokens", 100),
               "context": context or {}
           }
           
           key_string = json.dumps(key_components, sort_keys=True)
           return hashlib.sha256(key_string.encode()).hexdigest()

Cost Management Patterns
------------------------

**Token Budget Management**

.. code-block:: python

   class TokenBudgetManager:
       """Manage token usage and costs across models."""
       
       def __init__(self, daily_budget_usd: float, 
                    model_costs: Dict[str, float]):
           self.daily_budget = daily_budget_usd
           self.model_costs = model_costs  # cost per 1K tokens
           self.daily_usage = {}
           self.reset_daily_usage()
       
       def check_budget_before_call(self, model: str, 
                                   estimated_tokens: int) -> Dict[str, Any]:
           """Check if call is within budget."""
           
           with tracer.start_span("budget_check") as budget_span:
               today = time.strftime("%Y-%m-%d")
               estimated_cost = self._calculate_cost(model, estimated_tokens)
               
               budget_span.set_attribute("budget.model", model)
               budget_span.set_attribute("budget.estimated_tokens", estimated_tokens)
               budget_span.set_attribute("budget.estimated_cost_usd", estimated_cost)
               budget_span.set_attribute("budget.daily_budget_usd", self.daily_budget)
               
               current_spend = self.daily_usage.get(today, {}).get("total_cost", 0)
               projected_spend = current_spend + estimated_cost
               
               budget_span.set_attribute("budget.current_spend_usd", current_spend)
               budget_span.set_attribute("budget.projected_spend_usd", projected_spend)
               budget_span.set_attribute("budget.utilization_percent", 
                                        (projected_spend / self.daily_budget) * 100)
               
               within_budget = projected_spend <= self.daily_budget
               budget_span.set_attribute("budget.within_limit", within_budget)
               
               result = {
                   "within_budget": within_budget,
                   "estimated_cost": estimated_cost,
                   "current_spend": current_spend,
                   "projected_spend": projected_spend,
                   "budget_utilization": projected_spend / self.daily_budget,
                   "remaining_budget": self.daily_budget - current_spend
               }
               
               if not within_budget:
                   budget_span.set_attribute("budget.exceeded_by_usd", projected_spend - self.daily_budget)
                   budget_span.set_status("ERROR", "Budget limit would be exceeded")
               
               return result
       
       def record_actual_usage(self, model: str, actual_tokens: int) -> Dict[str, Any]:
           """Record actual token usage after LLM call."""
           
           with tracer.start_span("usage_recording") as usage_span:
               today = time.strftime("%Y-%m-%d")
               actual_cost = self._calculate_cost(model, actual_tokens)
               
               usage_span.set_attribute("usage.model", model)
               usage_span.set_attribute("usage.actual_tokens", actual_tokens)
               usage_span.set_attribute("usage.actual_cost_usd", actual_cost)
               
               if today not in self.daily_usage:
                   self.daily_usage[today] = {"total_cost": 0, "total_tokens": 0, "by_model": {}}
               
               self.daily_usage[today]["total_cost"] += actual_cost
               self.daily_usage[today]["total_tokens"] += actual_tokens
               
               if model not in self.daily_usage[today]["by_model"]:
                   self.daily_usage[today]["by_model"][model] = {"cost": 0, "tokens": 0, "calls": 0}
               
               self.daily_usage[today]["by_model"][model]["cost"] += actual_cost
               self.daily_usage[today]["by_model"][model]["tokens"] += actual_tokens
               self.daily_usage[today]["by_model"][model]["calls"] += 1
               
               usage_span.set_attribute("usage.total_daily_cost_usd", self.daily_usage[today]["total_cost"])
               usage_span.set_attribute("usage.total_daily_tokens", self.daily_usage[today]["total_tokens"])
               usage_span.set_attribute("usage.budget_utilization_percent", 
                                       (self.daily_usage[today]["total_cost"] / self.daily_budget) * 100)
               
               return {
                   "actual_cost": actual_cost,
                   "daily_total_cost": self.daily_usage[today]["total_cost"],
                   "daily_total_tokens": self.daily_usage[today]["total_tokens"],
                   "budget_utilization": self.daily_usage[today]["total_cost"] / self.daily_budget
               }

Quality Assurance Patterns
--------------------------

**Real-time Quality Monitoring**

.. code-block:: python

   from honeyhive.evaluation.evaluators import BaseEvaluator

   class RealTimeQualityMonitor:
       """Monitor quality in real-time with automatic alerts."""
       
       def __init__(self, evaluators: List[BaseEvaluator], 
                    quality_threshold: float = 0.8):
           self.evaluators = evaluators
           self.quality_threshold = quality_threshold
           self.quality_history = []
           self.window_size = 50
       
       def evaluate_response(self, prompt: str, 
                           response: str, 
                           context: Optional[Dict] = None) -> Dict[str, Any]:
           """Evaluate response quality in real-time."""
           
           with tracer.start_span("real_time_quality_evaluation") as eval_span:
               eval_span.set_attribute("quality.prompt", prompt)
               eval_span.set_attribute("quality.response_length", len(response))
               eval_span.set_attribute("quality.evaluators_count", len(self.evaluators))
               eval_span.set_attribute("quality.threshold", self.quality_threshold)
               
               evaluation_results = {}
               overall_score = 0
               
               for evaluator in self.evaluators:
                   with tracer.start_span(f"evaluator_{evaluator.name}") as evaluator_span:
                       evaluator_span.set_attribute("evaluator.name", evaluator.name)
                       
                       try:
                           result = evaluator.evaluate(
                               inputs={"prompt": prompt, "context": context},
                               outputs={"response": response}
                           )
                           
                           evaluator_span.set_attribute("evaluator.score", result.score)
                           evaluator_span.set_attribute("evaluator.success", True)
                           
                           evaluation_results[evaluator.name] = result
                           overall_score += result.score
                           
                       except Exception as e:
                           evaluator_span.set_attribute("evaluator.success", False)
                           evaluator_span.set_attribute("evaluator.error", str(e))
                           evaluator_span.set_status("ERROR", str(e))
               
               overall_score = overall_score / len(self.evaluators) if self.evaluators else 0
               eval_span.set_attribute("quality.overall_score", overall_score)
               
               # Record in quality history
               quality_entry = {
                   "timestamp": time.time(),
                   "overall_score": overall_score,
                   "evaluations": evaluation_results,
                   "prompt": prompt,
                   "response": response
               }
               
               self.quality_history.append(quality_entry)
               if len(self.quality_history) > self.window_size:
                   self.quality_history.pop(0)
               
               # Analyze trends
               quality_analysis = self._analyze_quality_trends()
               eval_span.set_attribute("quality.trend", quality_analysis.get("trend", "unknown"))
               eval_span.set_attribute("quality.avg_recent", quality_analysis.get("recent_average", 0))
               
               # Quality alerts
               alerts = []
               if overall_score < self.quality_threshold:
                   alerts.append({
                       "type": "low_quality",
                       "score": overall_score,
                       "threshold": self.quality_threshold
                   })
               
               if quality_analysis.get("trend") == "declining":
                   alerts.append({
                       "type": "quality_decline",
                       "recent_avg": quality_analysis.get("recent_average"),
                       "previous_avg": quality_analysis.get("previous_average")
                   })
               
               eval_span.set_attribute("quality.alerts_count", len(alerts))
               
               return {
                   "overall_score": overall_score,
                   "evaluations": evaluation_results,
                   "quality_analysis": quality_analysis,
                   "alerts": alerts,
                   "meets_threshold": overall_score >= self.quality_threshold
               }

Best Practices Summary
----------------------

**1. Observability First**

.. code-block:: python

   # Good: Comprehensive tracing throughout the application
   with tracer.start_span("user_request") as span:
       span.set_attribute("user.id", user_id)
       span.set_attribute("request.type", request_type)
       
       # All operations traced with context
       with tracer.start_span("business_logic") as logic_span:
           result = process_request(request_data)

**2. Graceful Error Handling**

.. code-block:: python

   # Good: Multiple layers of fallback
   try:
       result = primary_service.call()
   except PrimaryServiceError:
       try:
           result = fallback_service.call()
       except FallbackServiceError:
           result = generate_static_response()

**3. Performance Monitoring**

.. code-block:: python

   # Good: Track performance metrics for optimization
   start_time = time.perf_counter()
   result = expensive_operation()
   duration = time.perf_counter() - start_time
   
   span.set_attribute("performance.duration_ms", duration * 1000)
   span.set_attribute("performance.result_size", len(str(result)))

**4. Cost Awareness**

.. code-block:: python

   # Good: Check budget before expensive operations
   budget_check = budget_manager.check_budget_before_call(model, estimated_tokens)
   if not budget_check["within_budget"]:
       # Use cheaper model or cached response
       result = cheaper_alternative(prompt)
   else:
       result = premium_model.generate(prompt)

See Also
--------

- :doc:`advanced-tracing/index` - Advanced tracing techniques
- :doc:`evaluation/index` - Evaluation and analysis
- :doc:`monitoring/index` - Monitoring and operations
- :doc:`integrations/multi-provider` - Multi-provider patterns
- :doc:`../reference/api/tracer` - HoneyHiveTracer API reference
