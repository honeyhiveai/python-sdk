LLM Application Patterns
========================

**Problem:** You need proven architectural patterns and tracing strategies for building complex LLM applications like agents, RAG systems, and multi-step reasoning workflows.

**Solution:** Use these battle-tested LLM-specific patterns with HoneyHive tracing to build observable, maintainable, and debuggable AI systems.

This guide focuses on LLM-specific architectures and patterns, not generic software patterns.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Agent Architecture Patterns
---------------------------

Pattern 1: ReAct (Reasoning + Acting)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Use Case:** Agents that alternate between reasoning about the problem and taking actions with tools.

**Architecture:**

.. mermaid::

   graph TD
       A[User Query] --> B[Reasoning Step]
       B --> C{Need Tool?}
       C -->|Yes| D[Tool Call]
       C -->|No| E[Final Answer]
       D --> F[Observe Result]
       F --> B
       E --> G[Response]

**Implementation with Tracing:**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, enrich_span
   from honeyhive.models import EventType
   import openai
   
   tracer = HoneyHiveTracer.init(project="react-agent")
   
   @trace(tracer=tracer, event_type=EventType.chain)
   def react_agent(query: str, max_steps: int = 5) -> str:
       """ReAct agent with reasoning and acting."""
       enrich_span({
           "agent.type": "react",
           "agent.query": query,
           "agent.max_steps": max_steps
       })
       
       conversation_history = []
       
       for step in range(max_steps):
           # Reasoning step
           thought = reason_about_problem(query, conversation_history, step)
           
           if thought["action"] == "final_answer":
               enrich_span({"agent.steps_used": step + 1})
               return thought["answer"]
           
           # Acting step  
           observation = execute_tool(thought["tool"], thought["input"])
           conversation_history.append({
               "step": step,
               "thought": thought,
               "observation": observation
           })
       
       return "Max steps reached"
   
   @trace(tracer=tracer, event_type=EventType.model)
   def reason_about_problem(query: str, history: list, step: int) -> dict:
       """Reasoning step using LLM."""
       enrich_span({"reasoning.step": step, "reasoning.history_length": len(history)})
       
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[
               {"role": "system", "content": "Think step by step. Decide action: use tool or give final answer."},
               {"role": "user", "content": f"Query: {query}\nHistory: {history}"}
           ]
       )
       
       # Parse response into thought/action/input
       return parse_reasoning(response.choices[0].message.content)

**Trace Hierarchy:**

- Session: `react_agent`
  - Chain: `reason_about_problem` (step 1)
  - Tool: `execute_tool` (step 1)
  - Chain: `reason_about_problem` (step 2)
  - Tool: `execute_tool` (step 2)
  - Chain: `reason_about_problem` (final)

**Tradeoffs:**

- ✅ **Pros**: Flexible, handles dynamic situations, transparent reasoning
- ❌ **Cons**: Higher token cost (multiple LLM calls), slower than pre-planned approaches
- 💡 **When to Use**: Open-ended problems, unpredictable tool needs, exploratory tasks
- 🚫 **When to Avoid**: High-latency sensitivity, token budget constraints, predictable workflows

Pattern 2: Plan-and-Execute
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Use Case:** Complex queries requiring upfront planning before execution.

**Implementation:**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain)
   def plan_and_execute_agent(query: str) -> str:
       """Agent that plans first, then executes."""
       enrich_span({"agent.type": "plan_and_execute", "agent.query": query})
       
       # Phase 1: Planning
       plan = create_execution_plan(query)
       enrich_span({"agent.plan_steps": len(plan["steps"])})
       
       # Phase 2: Execution
       results = []
       for i, step in enumerate(plan["steps"]):
           result = execute_step(step, results)
           results.append(result)
           enrich_span({f"agent.step_{i}_status": "complete"})
       
       # Phase 3: Synthesis
       final_answer = synthesize_results(query, results)
       return final_answer
   
   @trace(tracer=tracer, event_type=EventType.model)
   def create_execution_plan(query: str) -> dict:
       """Create step-by-step execution plan."""
       enrich_span({"planning.query_complexity": estimate_complexity(query)})
       
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{
               "role": "user",
               "content": f"Create a step-by-step plan for: {query}"
           }]
       )
       
       plan = parse_plan(response.choices[0].message.content)
       enrich_span({"planning.steps_generated": len(plan["steps"])})
       return plan

**Tradeoffs:**

- ✅ **Pros**: Better for complex tasks, clear execution path, easier to debug
- ❌ **Cons**: Less flexible, planning overhead, struggles with dynamic environments
- 💡 **When to Use**: Multi-step tasks, parallel execution needs, known problem space
- 🚫 **When to Avoid**: Rapidly changing conditions, simple single-step tasks

Pattern 3: Reflexion (Self-Reflection)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Use Case:** Agents that critique and improve their own outputs.

**Implementation:**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain)
   def reflexion_agent(query: str, max_iterations: int = 3) -> str:
       """Agent that reflects on and improves its output."""
       enrich_span({
           "agent.type": "reflexion",
           "agent.max_iterations": max_iterations
       })
       
       current_answer = generate_initial_answer(query)
       
       for iteration in range(max_iterations):
           critique = self_critique(query, current_answer)
           
           if critique["quality_score"] >= 0.9:
               enrich_span({"agent.converged_at_iteration": iteration})
               break
           
           current_answer = improve_answer(query, current_answer, critique)
       
       return current_answer
   
   @trace(tracer=tracer, event_type=EventType.model)
   def self_critique(query: str, answer: str) -> dict:
       """Self-critique the current answer."""
       enrich_span({"critique.answer_length": len(answer)})
       
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{
               "role": "user",
               "content": f"Critique this answer to '{query}': {answer}\nScore 0-1 for quality."
           }]
       )
       
       critique = parse_critique(response.choices[0].message.content)
       enrich_span({"critique.quality_score": critique["quality_score"]})
       return critique

**Tradeoffs:**

- ✅ **Pros**: Higher quality outputs, self-correction, learns from mistakes
- ❌ **Cons**: Expensive (multiple critique cycles), slow convergence possible
- 💡 **When to Use**: Quality-critical tasks, creative work, complex reasoning
- 🚫 **When to Avoid**: Real-time applications, simple factual queries, tight budgets

Pattern 4: Multi-Agent Collaboration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Use Case:** Multiple specialized agents working together.

**Implementation:**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain)
   def multi_agent_system(task: str) -> str:
       """System with multiple specialized agents."""
       enrich_span({"system.type": "multi_agent", "system.task": task})
       
       # Agent 1: Research specialist
       research = research_agent(task)
       
       # Agent 2: Analysis specialist
       analysis = analysis_agent(research)
       
       # Agent 3: Synthesis specialist
       final_output = synthesis_agent(task, research, analysis)
       
       enrich_span({"system.agents_used": 3})
       return final_output
   
   @trace(tracer=tracer, event_type=EventType.model)
   def research_agent(task: str) -> dict:
       """Specialized research agent."""
       enrich_span({"agent.role": "researcher", "agent.specialty": "information_gathering"})
       # Research logic...
       return {"findings": [...]}

**Tradeoffs:**

- ✅ **Pros**: Specialized expertise, parallel execution, diverse perspectives
- ❌ **Cons**: Complex coordination, high resource usage, potential conflicts
- 💡 **When to Use**: Multi-domain problems, need for specialization, parallel work
- 🚫 **When to Avoid**: Simple tasks, tight latency requirements, limited resources

Pattern 5: Tool-Using Agents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Use Case:** Agents that can discover and use external tools dynamically.

**Implementation:**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain)
   def tool_using_agent(query: str, available_tools: list) -> str:
       """Agent that selects and uses appropriate tools."""
       enrich_span({
           "agent.type": "tool_user",
           "agent.available_tools": len(available_tools),
           "agent.tool_names": [t.name for t in available_tools]
       })
       
       # Select appropriate tool
       selected_tool = select_tool(query, available_tools)
       enrich_span({"agent.selected_tool": selected_tool.name})
       
       # Use the tool
       result = execute_tool_with_llm(query, selected_tool)
       
       return result
   
   @trace(tracer=tracer, event_type=EventType.model)
   def select_tool(query: str, tools: list) -> object:
       """LLM selects the best tool for the query."""
       tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in tools])
       
       enrich_span({"tool_selection.options": len(tools)})
       
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{
               "role": "user",
               "content": f"Select best tool for: {query}\n\nTools:\n{tool_descriptions}"
           }]
       )
       
       selected = parse_tool_selection(response.choices[0].message.content, tools)
       enrich_span({"tool_selection.chosen": selected.name})
       return selected

Pattern 6: Memory-Augmented Agents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Use Case:** Agents that maintain and query long-term memory.

**Implementation:**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain)
   def memory_augmented_agent(query: str, user_id: str) -> str:
       """Agent with long-term memory."""
       enrich_span({
           "agent.type": "memory_augmented",
           "agent.user_id": user_id
       })
       
       # Retrieve relevant memories
       relevant_memories = retrieve_memories(user_id, query)
       enrich_span({"agent.memories_retrieved": len(relevant_memories)})
       
       # Generate response with memory context
       response = generate_with_memory(query, relevant_memories)
       
       # Store new memory
       store_memory(user_id, query, response)
       
       return response
   
   @trace(tracer=tracer, event_type=EventType.tool)
   def retrieve_memories(user_id: str, query: str) -> list:
       """Retrieve relevant memories from vector store."""
       enrich_span({
           "memory.user_id": user_id,
           "memory.query_embedding": "generated"
       })
       
       # Vector similarity search
       memories = vector_store.search(user_id, query, top_k=5)
       
       enrich_span({"memory.results_found": len(memories)})
       return memories

**Tradeoffs:**

- ✅ **Pros**: Personalization, context preservation, improves over time
- ❌ **Cons**: Privacy concerns, storage costs, retrieval accuracy challenges
- 💡 **When to Use**: Conversational agents, personalized systems, long-term interactions
- 🚫 **When to Avoid**: Stateless services, privacy-sensitive domains, simple one-shot tasks

LLM Workflow Patterns
---------------------

Pattern 1: RAG (Retrieval-Augmented Generation)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Implementation:**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain)
   def rag_pipeline(query: str, knowledge_base: str) -> str:
       """RAG pipeline with full tracing."""
       enrich_span({
           "workflow.type": "rag",
           "workflow.query": query,
           "workflow.kb": knowledge_base
       })
       
       # Stage 1: Retrieval
       documents = retrieve_documents(query, knowledge_base)
       
       # Stage 2: Context building
       context = build_context(documents)
       
       # Stage 3: Generation
       response = generate_with_context(query, context)
       
       return response
   
   @trace(tracer=tracer, event_type=EventType.tool)
   def retrieve_documents(query: str, kb: str) -> list:
       """Retrieve relevant documents."""
       enrich_span({
           "retrieval.query_length": len(query),
           "retrieval.kb": kb
       })
       
       # Vector search
       docs = vector_search(query, kb, top_k=5)
       
       enrich_span({
           "retrieval.docs_found": len(docs),
           "retrieval.avg_relevance": calculate_avg_relevance(docs)
       })
       
       return docs

**Trace Hierarchy:**

.. mermaid::

   graph TD
       A[RAG Pipeline] --> B[Retrieve Documents]
       A --> C[Build Context]
       A --> D[Generate with Context]
       B --> E[Vector Search]
       D --> F[LLM Generation]

**Tradeoffs:**

- ✅ **Pros**: Factual accuracy, up-to-date information, reduces hallucinations
- ❌ **Cons**: Retrieval quality dependency, increased latency, context window limits
- 💡 **When to Use**: Knowledge-intensive tasks, factual QA, domain-specific content
- 🚫 **When to Avoid**: Creative generation, general reasoning, low-latency needs

Pattern 2: Chain-of-Thought
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Implementation:**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.model)
   def chain_of_thought_reasoning(problem: str) -> str:
       """LLM uses chain-of-thought prompting."""
       enrich_span({
           "workflow.type": "chain_of_thought",
           "workflow.problem_complexity": estimate_complexity(problem)
       })
       
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{
               "role": "system",
               "content": "Think step-by-step. Show your reasoning."
           }, {
               "role": "user",
               "content": problem
           }]
       )
       
       reasoning = response.choices[0].message.content
       steps = extract_reasoning_steps(reasoning)
       
       enrich_span({
           "workflow.reasoning_steps": len(steps),
           "workflow.tokens_used": len(reasoning.split())
       })
       
       return reasoning

Pattern 3: Self-Correction Loops
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Implementation:**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain)
   def self_correcting_generation(task: str) -> str:
       """Generate, validate, and correct output."""
       enrich_span({"workflow.type": "self_correction"})
       
       max_attempts = 3
       for attempt in range(max_attempts):
           output = generate_output(task)
           validation = validate_output(output, task)
           
           if validation["is_valid"]:
               enrich_span({"workflow.succeeded_at_attempt": attempt + 1})
               return output
           
           # Self-correct based on validation feedback
           task = f"{task}\n\nPrevious attempt had issues: {validation['issues']}"
       
       return output  # Return best attempt

Pattern 4: Prompt Chaining
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Implementation:**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain)
   def prompt_chain_workflow(input_text: str) -> str:
       """Chain multiple prompts for complex tasks."""
       enrich_span({
           "workflow.type": "prompt_chain",
           "workflow.input_length": len(input_text)
       })
       
       # Step 1: Extract key information
       key_info = extract_information(input_text)
       
       # Step 2: Analyze extracted info
       analysis = analyze_information(key_info)
       
       # Step 3: Generate final output
       final_output = generate_final_response(analysis)
       
       enrich_span({"workflow.chain_steps": 3})
       return final_output

Pattern 5: Dynamic Few-Shot Learning
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Implementation:**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.model)
   def dynamic_few_shot(query: str, example_pool: list) -> str:
       """Select relevant examples dynamically."""
       enrich_span({
           "workflow.type": "dynamic_few_shot",
           "workflow.example_pool_size": len(example_pool)
       })
       
       # Select most relevant examples
       selected_examples = select_relevant_examples(query, example_pool, k=3)
       enrich_span({"workflow.examples_selected": len(selected_examples)})
       
       # Build few-shot prompt
       prompt = build_few_shot_prompt(query, selected_examples)
       
       # Generate with examples
       client = openai.OpenAI()
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )
       
       return response.choices[0].message.content

Best Practices for LLM Applications
-----------------------------------

1. **Always Enrich with Agent Context**

.. code-block:: python

   enrich_span({
       "agent.type": "react",
       "agent.step": current_step,
       "agent.decision": "tool_call",
       "agent.confidence": 0.95
   })

2. **Track Workflow Performance**

.. code-block:: python

   import time
   
   start = time.time()
   result = execute_workflow()
   
   enrich_span({
       "workflow.duration_ms": (time.time() - start) * 1000,
       "workflow.steps_executed": step_count,
       "workflow.cost_estimate": calculate_cost()
   })

3. **Use Consistent Event Types**

- `EventType.chain` - Multi-step workflows
- `EventType.model` - LLM calls
- `EventType.tool` - Tool/function executions
- `EventType.session` - Complete user sessions

4. **Implement Fallbacks with Tracing**

.. code-block:: python

   @trace(tracer=tracer, event_type=EventType.chain)
   def resilient_agent(query: str) -> str:
       strategies = ["gpt-4", "gpt-3.5-turbo", "claude-3"]
       
       for i, model in enumerate(strategies):
           try:
               result = try_model(query, model)
               enrich_span({
                   "resilience.succeeded_with": model,
                   "resilience.attempts": i + 1
               })
               return result
           except Exception as e:
               enrich_span({f"resilience.attempt_{i}_failed": str(e)})
               continue
       
       raise Exception("All strategies failed")

Next Steps
----------

- :doc:`/how-to/deployment/production` - Production deployment patterns
- :doc:`/how-to/advanced-tracing/span-enrichment` - Advanced enrichment patterns
- :doc:`/how-to/advanced-tracing/custom-spans` - Custom span creation
- :doc:`/tutorials/index` - Complete LLM application tutorials

**Key Takeaway:** LLM applications require specialized architectural patterns. Use these proven agent and workflow patterns with comprehensive tracing to build observable, debuggable AI systems. ✨

