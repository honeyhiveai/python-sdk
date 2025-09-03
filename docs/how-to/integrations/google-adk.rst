Integrate with Google ADK
=========================

Learn how to integrate HoneyHive with Google's Agent Development Kit (ADK) using the BYOI (Bring Your Own Instrumentor) approach for comprehensive agent observability.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

Google's Agent Development Kit (ADK) provides a framework for building sophisticated AI agents capable of complex reasoning, tool integration, and multi-step workflows. HoneyHive provides automatic tracing through OpenInference instrumentors, capturing agent behavior, tool calls, and decision-making processes.

**Benefits**:

- **Agent Workflow Tracing**: Complete visibility into multi-step agent processes
- **Tool Integration Monitoring**: Track external tool calls and integrations
- **Decision Process Insights**: Understand agent reasoning and state transitions
- **Performance Analytics**: Monitor agent efficiency and bottlenecks
- **Error Detection**: Identify and debug agent failures
- **Zero Code Changes**: Works with existing Google ADK implementations

**Key Differences from GenAI**:

- **Scope**: ADK instruments entire agent workflows vs single model calls
- **Complexity**: Supports multi-step reasoning chains and tool orchestration
- **Architecture**: Designed for agent-based applications with complex state management

Quick Start
-----------

**1. Install Required Packages**

.. code-block:: bash

   pip install honeyhive google-adk openinference-instrumentation-google-adk

**2. Initialize HoneyHive with Google ADK Instrumentor**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.models import EventType
   from openinference.instrumentation.google_adk import GoogleADKInstrumentor
   import google.adk as adk

   # Initialize HoneyHive tracer with Google ADK instrumentor
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-api-key",
       instrumentors=[GoogleADKInstrumentor()]
   )

   # Configure Google ADK
   adk.configure(api_key="your-google-adk-api-key")

**3. Use Google ADK Normally - Automatically Traced**

.. code-block:: python

   # All ADK agent interactions are now automatically traced
   agent = adk.Agent(name="research_agent")
   result = agent.execute("Research the latest developments in quantum computing")
   print(result)

Basic Agent Creation
--------------------

**Problem**: Create and trace a basic agent with tool capabilities.

**Solution**:

.. code-block:: python

   import google.adk as adk
   from honeyhive import HoneyHiveTracer
   from honeyhive.models import EventType
   from openinference.instrumentation.google_adk import GoogleADKInstrumentor

   # Setup (do once at application startup)
   tracer = HoneyHiveTracer.init(
       api_key="your-honeyhive-api-key",
       instrumentors=[GoogleADKInstrumentor()]
   )

   adk.configure(api_key="your-google-adk-api-key")

   @trace(tracer=tracer, event_type=EventType.chain, event_name="agent_setup")
   def create_research_agent() -> adk.Agent:
       """Create a research agent with tools."""
       
       # Define available tools
       tools = [
           adk.Tool(
               name="web_search",
               description="Search the web for current information",
               function=web_search_function
           ),
           adk.Tool(
               name="calculator",
               description="Perform mathematical calculations",
               function=calculator_function
           )
       ]
       
       # Create agent with automatic tracing
       # This captures agent initialization, tool registration, etc.
       agent = adk.Agent(
           name="research_agent",
           description="A research assistant that can search and analyze information",
           tools=tools,
           model="gemini-pro"
       )
       
       return agent

   def web_search_function(query: str) -> str:
       """Example web search tool function."""
       # This tool call will be automatically traced
       return f"Search results for: {query}"

   def calculator_function(expression: str) -> str:
       """Example calculator tool function."""
       # This tool call will be automatically traced
       try:
           result = eval(expression)  # Note: Use safe eval in production
           return str(result)
       except Exception as e:
           return f"Error: {e}"

   # Usage
   agent = create_research_agent()
   response = agent.execute("What is 15% of the global renewable energy capacity?")
   print(response)

Multi-Step Agent Workflows
---------------------------

**Problem**: Trace complex multi-step agent workflows with decision points.

**Solution**:

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain, event_name="multi_step_workflow")
   def complex_research_workflow(topic: str) -> dict:
       """Execute a complex research workflow with multiple steps."""
       
       agent = adk.Agent(
           name="advanced_researcher",
           tools=[web_search_tool, analysis_tool, summary_tool]
       )
       
       # Step 1: Initial research
       with tracer.enrich_span(
           metadata={"step": "initial_research", "topic": topic}
       ) as step1_span:
           initial_research = agent.execute(f"Research basic information about {topic}")
           step1_span.set_attribute("research.initial_results_length", len(initial_research))
       
       # Step 2: Deep dive analysis
       with tracer.enrich_span(
           metadata={"step": "deep_analysis", "topic": topic}
       ) as step2_span:
           analysis_prompt = f"""
           Based on this initial research: {initial_research}
           
           Perform a deeper analysis focusing on:
           1. Recent developments
           2. Key challenges
           3. Future prospects
           """
           deep_analysis = agent.execute(analysis_prompt)
           step2_span.set_attribute("analysis.depth_score", calculate_depth_score(deep_analysis))
       
       # Step 3: Synthesis and summary
       with tracer.enrich_span(
           metadata={"step": "synthesis", "topic": topic}
       ) as step3_span:
           summary = agent.execute(f"Create a comprehensive summary combining all research on {topic}")
           step3_span.set_attribute("summary.word_count", len(summary.split()))
       
       return {
           "topic": topic,
           "initial_research": initial_research,
           "deep_analysis": deep_analysis,
           "summary": summary,
           "workflow_complete": True
       }

   def calculate_depth_score(text: str) -> float:
       """Calculate a depth score for analysis quality."""
       # Simple heuristic - in practice, use more sophisticated metrics
       return min(len(text) / 1000.0, 10.0)

   # Usage
   workflow_result = complex_research_workflow("artificial general intelligence")

Agent Tool Integration
----------------------

**Problem**: Create agents with custom tools and trace tool interactions.

**Solution**:

.. code-block:: python

   import json
   import requests
   from typing import Dict, Any

   class CustomToolAgent:
       """Agent with custom tools and comprehensive tracing."""
       
       def __init__(self, tracer: HoneyHiveTracer):
           self.tracer = tracer
           self.agent = self._create_agent()
       
       def _create_agent(self) -> adk.Agent:
           """Create agent with custom tools."""
           
           tools = [
               adk.Tool(
                   name="api_caller",
                   description="Make API calls to external services",
                   function=self._api_tool
               ),
               adk.Tool(
                   name="data_analyzer",
                   description="Analyze structured data",
                   function=self._data_analysis_tool
               ),
               adk.Tool(
                   name="file_processor",
                   description="Process and analyze files",
                   function=self._file_processing_tool
               )
           ]
           
           return adk.Agent(
               name="custom_tool_agent",
               description="Agent with specialized custom tools",
               tools=tools,
               model="gemini-pro"
           )
       
       @trace(tracer=tracer, event_type=EventType.tool, event_name="api_call")
       def _api_tool(self, url: str, method: str = "GET", **kwargs) -> str:
           """Custom API calling tool with tracing."""
           
           with self.tracer.enrich_span(
               metadata={"tool": "api_caller", "url": url, "method": method}
           ) as span:
               try:
                   response = requests.request(method, url, **kwargs)
                   span.set_attribute("api.status_code", response.status_code)
                   span.set_attribute("api.response_size", len(response.text))
                   return response.text
               except Exception as e:
                   span.set_attribute("api.error", str(e))
                   return f"API call failed: {e}"
       
       @trace(tracer=tracer, event_type=EventType.tool, event_name="data_analysis")
       def _data_analysis_tool(self, data: str) -> str:
           """Data analysis tool with tracing."""
           
           with self.tracer.enrich_span(
               metadata={"tool": "data_analyzer"}
           ) as span:
               try:
                   # Parse data
                   parsed_data = json.loads(data)
                   span.set_attribute("data.type", type(parsed_data).__name__)
                   span.set_attribute("data.size", len(str(parsed_data)))
                   
                   # Perform analysis
                   if isinstance(parsed_data, list):
                       analysis = {
                           "count": len(parsed_data),
                           "type": "array",
                           "summary": f"Array with {len(parsed_data)} items"
                       }
                   elif isinstance(parsed_data, dict):
                       analysis = {
                           "keys": list(parsed_data.keys()),
                           "type": "object",
                           "summary": f"Object with {len(parsed_data)} properties"
                       }
                   else:
                       analysis = {
                           "value": parsed_data,
                           "type": type(parsed_data).__name__,
                           "summary": str(parsed_data)
                       }
                   
                   span.set_attribute("analysis.result_keys", len(analysis))
                   return json.dumps(analysis, indent=2)
                   
               except Exception as e:
                   span.set_attribute("analysis.error", str(e))
                   return f"Analysis failed: {e}"
       
       @trace(tracer=tracer, event_type=EventType.tool, event_name="file_processing")
       def _file_processing_tool(self, file_path: str, operation: str = "read") -> str:
           """File processing tool with tracing."""
           
           with self.tracer.enrich_span(
               metadata={"tool": "file_processor", "file_path": file_path, "operation": operation}
           ) as span:
               try:
                   if operation == "read":
                       with open(file_path, 'r') as f:
                           content = f.read()
                       span.set_attribute("file.size_bytes", len(content))
                       span.set_attribute("file.line_count", len(content.split('\n')))
                       return content
                   else:
                       return f"Operation '{operation}' not supported"
                       
               except Exception as e:
                   span.set_attribute("file.error", str(e))
                   return f"File processing failed: {e}"
       
       def execute_task(self, task: str) -> str:
           """Execute a task using the agent."""
           return self.agent.execute(task)

   # Usage
   custom_agent = CustomToolAgent(tracer)
   result = custom_agent.execute_task("Analyze the API response from https://api.example.com/data")

Agent State Management
----------------------

**Problem**: Track agent state changes and decision-making processes.

**Solution**:

.. code-block:: python

   from enum import Enum
   from typing import Optional

   class AgentState(Enum):
       IDLE = "idle"
       PLANNING = "planning" 
       EXECUTING = "executing"
       ANALYZING = "analyzing"
       COMPLETED = "completed"
       ERROR = "error"

   class StatefulAgent:
       """Agent with state management and tracing."""
       
       def __init__(self, tracer: HoneyHiveTracer):
           self.tracer = tracer
           self.state = AgentState.IDLE
           self.execution_history = []
           self.agent = adk.Agent(
               name="stateful_agent",
               model="gemini-pro"
           )
       
       @trace(tracer=tracer, event_type=EventType.chain, event_name="state_transition")
       def _transition_state(self, new_state: AgentState, reason: str = "") -> None:
           """Transition agent state with tracing."""
           
           old_state = self.state
           self.state = new_state
           
           with self.tracer.enrich_span(
               metadata={
                   "state_transition": f"{old_state.value} -> {new_state.value}",
                   "reason": reason
               }
           ) as span:
               span.set_attribute("agent.previous_state", old_state.value)
               span.set_attribute("agent.new_state", new_state.value)
               span.set_attribute("agent.execution_count", len(self.execution_history))
               
               print(f"Agent state: {old_state.value} -> {new_state.value}")
               if reason:
                   print(f"Reason: {reason}")
       
       @trace(tracer=tracer, event_type=EventType.chain, event_name="agent_execution")
       def execute_with_state_tracking(self, task: str) -> dict:
           """Execute task with comprehensive state tracking."""
           
           execution_id = len(self.execution_history)
           
           try:
               # Planning phase
               self._transition_state(AgentState.PLANNING, f"Starting task: {task}")
               
               with self.tracer.enrich_span(
                   metadata={"phase": "planning", "task": task, "execution_id": execution_id}
               ) as planning_span:
                   plan = self._create_plan(task)
                   planning_span.set_attribute("plan.steps_count", len(plan.get("steps", [])))
               
               # Execution phase
               self._transition_state(AgentState.EXECUTING, "Executing planned steps")
               
               with self.tracer.enrich_span(
                   metadata={"phase": "execution", "execution_id": execution_id}
               ) as execution_span:
                   result = self.agent.execute(task)
                   execution_span.set_attribute("execution.result_length", len(result))
               
               # Analysis phase
               self._transition_state(AgentState.ANALYZING, "Analyzing results")
               
               with self.tracer.enrich_span(
                   metadata={"phase": "analysis", "execution_id": execution_id}
               ) as analysis_span:
                   analysis = self._analyze_result(result)
                   analysis_span.set_attribute("analysis.confidence_score", analysis.get("confidence", 0))
               
               # Completion
               self._transition_state(AgentState.COMPLETED, "Task completed successfully")
               
               execution_record = {
                   "id": execution_id,
                   "task": task,
                   "plan": plan,
                   "result": result,
                   "analysis": analysis,
                   "status": "completed",
                   "state_history": [state.value for state in AgentState]
               }
               
               self.execution_history.append(execution_record)
               return execution_record
               
           except Exception as e:
               self._transition_state(AgentState.ERROR, f"Error occurred: {e}")
               
               error_record = {
                   "id": execution_id,
                   "task": task,
                   "error": str(e),
                   "status": "error"
               }
               
               self.execution_history.append(error_record)
               raise
           
           finally:
               # Always return to idle
               self._transition_state(AgentState.IDLE, "Ready for next task")
       
       def _create_plan(self, task: str) -> dict:
           """Create execution plan for the task."""
           # Simplified planning logic
           return {
               "task": task,
               "steps": [
                   "Analyze task requirements",
                   "Gather necessary information", 
                   "Process and synthesize data",
                   "Generate response"
               ],
               "estimated_duration": "5-10 minutes"
           }
       
       def _analyze_result(self, result: str) -> dict:
           """Analyze execution result."""
           # Simplified analysis
           return {
               "length": len(result),
               "confidence": 0.85,
               "quality_score": len(result.split()) / 100.0,
               "completeness": "high" if len(result) > 500 else "medium"
           }

   # Usage
   stateful_agent = StatefulAgent(tracer)
   execution_result = stateful_agent.execute_with_state_tracking(
       "Create a comprehensive analysis of renewable energy trends"
   )

Error Handling and Reliability
-------------------------------

**Problem**: Handle Google ADK errors gracefully while maintaining comprehensive tracing.

**Solution**:

.. code-block:: python

   import time
   from typing import Optional, Dict, Any
   from google.adk.exceptions import ADKException, RateLimitError, AuthenticationError

   @trace(tracer=tracer, event_type=EventType.chain, event_name="reliable_agent_execution")
   def reliable_agent_execution(
       task: str, 
       max_retries: int = 3,
       retry_strategies: Optional[Dict[str, Any]] = None
   ) -> dict:
       """Reliable agent execution with comprehensive error handling and tracing."""
       
       if retry_strategies is None:
           retry_strategies = {
               "exponential_backoff": True,
               "max_delay": 60,
               "backoff_factor": 2
           }
       
       agent = adk.Agent(name="reliable_agent", model="gemini-pro")
       
       for attempt in range(max_retries):
           try:
               with tracer.enrich_span(
                   metadata={
                       "attempt": attempt + 1,
                       "max_retries": max_retries,
                       "task": task
                   }
               ) as attempt_span:
                   attempt_span.set_attribute("attempt.number", attempt + 1)
                   attempt_span.set_attribute("attempt.is_retry", attempt > 0)
                   
                   # Execute agent task with full tracing
                   result = agent.execute(task)
                   
                   attempt_span.set_attribute("attempt.success", True)
                   attempt_span.set_attribute("result.length", len(result))
                   
                   return {
                       "result": result,
                       "attempts": attempt + 1,
                       "status": "success",
                       "task": task
                   }
                   
           except RateLimitError as e:
               # Rate limit - implement exponential backoff
               attempt_span.set_attribute("attempt.success", False)
               attempt_span.set_attribute("error.type", "rate_limit")
               attempt_span.set_attribute("error.message", str(e))
               
               if attempt < max_retries - 1:
                   if retry_strategies.get("exponential_backoff"):
                       base_delay = retry_strategies.get("backoff_factor", 2)
                       wait_time = min(
                           base_delay ** attempt,
                           retry_strategies.get("max_delay", 60)
                       )
                   else:
                       wait_time = 5  # Fixed delay
                   
                   attempt_span.set_attribute("retry.wait_seconds", wait_time)
                   
                   with tracer.enrich_span(
                       metadata={"retry_delay": wait_time}
                   ) as delay_span:
                       time.sleep(wait_time)
               else:
                   raise
                   
           except AuthenticationError as e:
               # Authentication error - don't retry
               attempt_span.set_attribute("attempt.success", False)
               attempt_span.set_attribute("error.type", "authentication")
               attempt_span.set_attribute("error.message", str(e))
               
               return {
                   "error": "Authentication failed",
                   "attempts": attempt + 1,
                   "status": "auth_error",
                   "task": task
               }
               
           except ADKException as e:
               # ADK-specific error
               attempt_span.set_attribute("attempt.success", False)
               attempt_span.set_attribute("error.type", "adk_exception")
               attempt_span.set_attribute("error.message", str(e))
               attempt_span.set_attribute("error.code", getattr(e, 'code', 'unknown'))
               
               if attempt < max_retries - 1:
                   time.sleep(1)  # Brief delay for ADK errors
               else:
                   raise
                   
           except Exception as e:
               # Generic error
               attempt_span.set_attribute("attempt.success", False)
               attempt_span.set_attribute("error.type", type(e).__name__)
               attempt_span.set_attribute("error.message", str(e))
               
               if attempt < max_retries - 1:
                   time.sleep(1)
               else:
                   raise

   # Usage examples
   try:
       result = reliable_agent_execution(
           "Analyze market trends for renewable energy stocks",
           max_retries=3,
           retry_strategies={
               "exponential_backoff": True,
               "max_delay": 30,
               "backoff_factor": 1.5
           }
       )
       print(f"Success: {result}")
   except Exception as e:
       print(f"Final failure: {e}")

Performance Monitoring
----------------------

**Problem**: Monitor and optimize Google ADK agent performance across different configurations.

**Solution**:

.. code-block:: python

   import time
   from typing import List, Dict, Any
   from dataclasses import dataclass

   @dataclass
   class AgentConfig:
       name: str
       model: str
       tools: List[str]
       max_iterations: int = 10
       temperature: float = 0.7

   @trace(tracer=tracer, event_type=EventType.chain, event_name="agent_benchmark")
   def benchmark_agent_configurations(
       task: str, 
       configurations: List[AgentConfig]
   ) -> Dict[str, Any]:
       """Benchmark different agent configurations with detailed performance tracing."""
       
       results = {}
       
       with tracer.enrich_span(
           metadata={
               "benchmark": {
                   "task": task,
                   "config_count": len(configurations)
               }
           }
       ) as benchmark_span:
           
           for config in configurations:
               with tracer.enrich_span(
                   metadata={
                       "config_name": config.name,
                       "model": config.model,
                       "tool_count": len(config.tools)
                   }
               ) as config_span:
                   
                   start_time = time.time()
                   
                   try:
                       # Create agent with specific configuration
                       agent = adk.Agent(
                           name=config.name,
                           model=config.model,
                           tools=[create_tool(tool_name) for tool_name in config.tools],
                           max_iterations=config.max_iterations,
                           temperature=config.temperature
                       )
                       
                       # Execute task
                       result = agent.execute(task)
                       
                       end_time = time.time()
                       execution_time = end_time - start_time
                       
                       # Calculate performance metrics
                       metrics = {
                           "execution_time": execution_time,
                           "result_length": len(result),
                           "chars_per_second": len(result) / execution_time if execution_time > 0 else 0,
                           "iterations_used": getattr(agent, 'iterations_used', 0),
                           "tool_calls": getattr(agent, 'tool_call_count', 0),
                           "success": True
                       }
                       
                       # Add metrics to span
                       for key, value in metrics.items():
                           config_span.set_attribute(f"performance.{key}", value)
                       
                       results[config.name] = {
                           "config": config,
                           "result": result,
                           "metrics": metrics
                       }
                       
                   except Exception as e:
                       end_time = time.time()
                       execution_time = end_time - start_time
                       
                       config_span.set_attribute("performance.execution_time", execution_time)
                       config_span.set_attribute("performance.success", False)
                       config_span.set_attribute("performance.error", str(e))
                       
                       results[config.name] = {
                           "config": config,
                           "error": str(e),
                           "metrics": {
                               "execution_time": execution_time,
                               "success": False
                           }
                       }
           
           # Calculate benchmark summary
           successful_configs = [r for r in results.values() if r["metrics"]["success"]]
           benchmark_span.set_attribute("benchmark.successful_configs", len(successful_configs))
           benchmark_span.set_attribute("benchmark.success_rate", len(successful_configs) / len(configurations))
           
           if successful_configs:
               avg_time = sum(r["metrics"]["execution_time"] for r in successful_configs) / len(successful_configs)
               benchmark_span.set_attribute("benchmark.avg_execution_time", avg_time)
       
       return results

   def create_tool(tool_name: str) -> adk.Tool:
       """Factory function to create tools by name."""
       tool_functions = {
           "web_search": lambda q: f"Search results for: {q}",
           "calculator": lambda expr: str(eval(expr)),  # Use safe eval in production
           "file_reader": lambda path: f"File content from: {path}",
           "api_caller": lambda url: f"API response from: {url}"
       }
       
       return adk.Tool(
           name=tool_name,
           function=tool_functions.get(tool_name, lambda x: f"Unknown tool: {tool_name}")
       )

   # Usage
   configs = [
       AgentConfig("fast_agent", "gemini-pro", ["web_search"], max_iterations=5, temperature=0.3),
       AgentConfig("comprehensive_agent", "gemini-pro", ["web_search", "calculator", "api_caller"], max_iterations=15, temperature=0.7),
       AgentConfig("precise_agent", "gemini-pro", ["calculator"], max_iterations=3, temperature=0.1)
   ]

   benchmark_results = benchmark_agent_configurations(
       "Calculate the compound annual growth rate of renewable energy investment over the past 5 years",
       configs
   )

   # Print results
   for config_name, result in benchmark_results.items():
       if result["metrics"]["success"]:
           metrics = result["metrics"]
           print(f"{config_name}: {metrics['execution_time']:.2f}s, {metrics['chars_per_second']:.0f} chars/sec")
       else:
           print(f"{config_name}: Failed - {result['error']}")

Environment Configuration
-------------------------

**Problem**: Manage Google ADK credentials and settings across environments.

**Solution**:

.. code-block:: python

   import os
   from typing import Optional, Dict, Any
   from honeyhive.models import EventType

   @trace(tracer=tracer, event_type=EventType.session, event_name="adk_environment_setup")
   def setup_google_adk_environment(
       honeyhive_api_key: Optional[str] = None,
       google_adk_api_key: Optional[str] = None,
       project_name: Optional[str] = None,
       environment: str = "development",
       agent_config: Optional[Dict[str, Any]] = None
   ) -> tuple:
       """Setup Google ADK with HoneyHive for different environments."""
       
       # Use environment variables if not provided
       honeyhive_key = honeyhive_api_key or os.getenv("HH_API_KEY")
       adk_key = google_adk_api_key or os.getenv("GOOGLE_ADK_API_KEY")
       project = project_name or os.getenv("HH_PROJECT", f"google-adk-{environment}")
       
       if not honeyhive_key:
           raise ValueError("HoneyHive API key required (HH_API_KEY)")
       if not adk_key:
           raise ValueError("Google ADK API key required (GOOGLE_ADK_API_KEY)")
       
       # Default agent configuration
       default_agent_config = {
           "model": "gemini-pro",
           "max_iterations": 10,
           "temperature": 0.7,
           "timeout": 300
       }
       
       if agent_config:
           default_agent_config.update(agent_config)
       
       # Initialize HoneyHive with environment-specific settings
       tracer_config = {
           "api_key": honeyhive_key,
           "project": project,
           "source": environment,
           "instrumentors": [GoogleADKInstrumentor()]
       }
       
       # Environment-specific configuration
       if environment == "production":
           tracer_config.update({
               "disable_http_tracing": False,  # Enable full tracing
               "test_mode": False
           })
           default_agent_config.update({
               "temperature": 0.3,  # More deterministic for production
               "max_iterations": 15  # Allow more thorough processing
           })
       elif environment == "development":
           tracer_config.update({
               "test_mode": True,  # Enable debug mode
               "disable_http_tracing": True  # Reduce noise in development
           })
       elif environment == "staging":
           tracer_config.update({
               "test_mode": False,
               "disable_http_tracing": False
           })
       
       tracer = HoneyHiveTracer.init(**tracer_config)
       
       # Configure Google ADK
       adk.configure(
           api_key=adk_key,
           environment=environment,
           **default_agent_config
       )
       
       with tracer.enrich_span(
           metadata={
               "environment": environment,
               "project": project,
               "agent_config": default_agent_config
           }
       ) as span:
           span.set_attribute("setup.environment", environment)
           span.set_attribute("setup.project", project)
           span.set_attribute("setup.adk_configured", True)
           span.set_attribute("setup.tracer_configured", True)
       
       return tracer, default_agent_config

   # Usage for different environments
   
   # Development
   dev_tracer, dev_config = setup_google_adk_environment(
       environment="development",
       agent_config={"temperature": 0.8, "max_iterations": 5}  # Fast iteration
   )
   
   # Production
   prod_tracer, prod_config = setup_google_adk_environment(
       environment="production",
       agent_config={"temperature": 0.2, "max_iterations": 20}  # Thorough and deterministic
   )
   
   # Staging
   staging_tracer, staging_config = setup_google_adk_environment(
       environment="staging",
       agent_config={"temperature": 0.5, "max_iterations": 12}  # Balanced
   )

Best Practices
--------------

**1. Agent Design Patterns**

.. code-block:: python

   # Use specialized agents for different task types
   def create_specialized_agents() -> Dict[str, adk.Agent]:
       """Create a suite of specialized agents for different purposes."""
       
       agents = {
           "researcher": adk.Agent(
               name="research_specialist",
               tools=["web_search", "academic_search", "data_analysis"],
               model="gemini-pro",
               temperature=0.3  # More factual
           ),
           "creative": adk.Agent(
               name="creative_assistant", 
               tools=["text_generation", "image_analysis"],
               model="gemini-pro",
               temperature=0.8  # More creative
           ),
           "analyst": adk.Agent(
               name="data_analyst",
               tools=["calculator", "data_processor", "chart_generator"],
               model="gemini-pro",
               temperature=0.1  # Very precise
           )
       }
       
       return agents

**2. Tool Management**

.. code-block:: python

   # Organize tools by category for better tracing
   class ToolManager:
       """Centralized tool management with categorization."""
       
       def __init__(self):
           self.tools = {
               "data": ["calculator", "data_analyzer", "chart_maker"],
               "web": ["web_search", "api_caller", "scraper"],
               "files": ["file_reader", "file_writer", "pdf_processor"],
               "ai": ["text_generator", "summarizer", "translator"]
           }
       
       def get_tools_by_category(self, category: str) -> List[adk.Tool]:
           """Get tools by category with automatic tracing."""
           return [self.create_tool(tool_name) for tool_name in self.tools.get(category, [])]

**3. State Persistence**

.. code-block:: python

   # Implement agent state persistence for long-running workflows
   class PersistentAgent:
       """Agent with state persistence across sessions."""
       
       def save_state(self) -> dict:
           """Save agent state for later restoration."""
           return {
               "execution_history": self.execution_history,
               "learned_patterns": self.learned_patterns,
               "performance_metrics": self.performance_metrics
           }
       
       def restore_state(self, state: dict) -> None:
           """Restore agent state from saved data."""
           self.execution_history = state.get("execution_history", [])
           self.learned_patterns = state.get("learned_patterns", {})
           self.performance_metrics = state.get("performance_metrics", {})

**4. Resource Management**

.. code-block:: python

   # Implement resource limits and monitoring
   class ResourceAwareAgent:
       """Agent with resource monitoring and limits."""
       
       def __init__(self, max_memory_mb: int = 512, max_execution_time: int = 600):
           self.max_memory_mb = max_memory_mb
           self.max_execution_time = max_execution_time
           self.resource_monitor = ResourceMonitor()
       
       @trace(tracer=tracer, event_type=EventType.chain, event_name="resource_check")
       def check_resources(self) -> bool:
           """Check if agent has sufficient resources to continue."""
           memory_usage = self.resource_monitor.get_memory_usage()
           execution_time = self.resource_monitor.get_execution_time()
           
           return (memory_usage < self.max_memory_mb and 
                   execution_time < self.max_execution_time)

Common Issues & Solutions
-------------------------

**Issue 1: Agent Authentication Errors**

.. code-block:: python

   # Verify ADK setup and credentials
   @trace(tracer=tracer, event_type=EventType.tool, event_name="adk_health_check")
   def verify_adk_setup():
       """Verify Google ADK configuration and connectivity."""
       try:
           # Test basic ADK functionality
           test_agent = adk.Agent(name="health_check_agent")
           response = test_agent.execute("Say hello")
           print("✅ Google ADK configured successfully")
           return True
       except Exception as e:
           print(f"❌ ADK configuration failed: {e}")
           return False

**Issue 2: Tool Integration Failures**

.. code-block:: python

   # Test tool functionality independently
   @trace(tracer=tracer, event_type=EventType.tool, event_name="tool_validation")
   def validate_tools(tools: List[adk.Tool]) -> Dict[str, bool]:
       """Validate that all tools are working correctly."""
       results = {}
       
       for tool in tools:
           try:
               # Test tool with simple input
               test_result = tool.function("test")
               results[tool.name] = True
               print(f"✅ Tool {tool.name} is working")
           except Exception as e:
               results[tool.name] = False
               print(f"❌ Tool {tool.name} failed: {e}")
       
       return results

**Issue 3: Performance Optimization**

.. code-block:: python

   # Monitor and optimize agent performance
   @trace(tracer=tracer, event_type=EventType.chain, event_name="performance_optimization")
   def optimize_agent_performance(agent: adk.Agent, task: str) -> dict:
       """Analyze and optimize agent performance."""
       
       # Baseline performance
       start_time = time.time()
       result = agent.execute(task)
       baseline_time = time.time() - start_time
       
       # Try optimized settings
       optimizations = [
           {"temperature": 0.3, "max_iterations": 5},  # Faster, less thorough
           {"temperature": 0.1, "max_iterations": 15}, # Slower, more thorough
           {"temperature": 0.5, "max_iterations": 8}   # Balanced
       ]
       
       best_config = None
       best_time = baseline_time
       
       for opt_config in optimizations:
           opt_agent = adk.Agent(
               name=f"optimized_{agent.name}",
               **opt_config
           )
           
           start_time = time.time()
           opt_result = opt_agent.execute(task)
           opt_time = time.time() - start_time
           
           if opt_time < best_time:
               best_time = opt_time
               best_config = opt_config
       
       return {
           "baseline_time": baseline_time,
           "optimized_time": best_time,
           "improvement": (baseline_time - best_time) / baseline_time * 100,
           "best_config": best_config
       }

See Also
--------

- :doc:`multi-provider` - Use Google ADK with other providers
- :doc:`../troubleshooting` - Common integration issues  
- :doc:`../../tutorials/03-llm-integration` - LLM integration tutorial
