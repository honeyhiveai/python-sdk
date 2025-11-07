Multi-Step Experiments
======================

How do I evaluate a pipeline with multiple steps (e.g., RAG)?
-------------------------------------------------------------

Use component-level tracing and metrics within your evaluation function.

How do I evaluate each component separately?
--------------------------------------------

**Using Context Manager (Explicit Tracer)**

.. code-block:: python

   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   from honeyhive import HoneyHiveTracer
   
   def rag_pipeline(datapoint: Dict[str, Any], tracer: HoneyHiveTracer) -> Dict[str, Any]:
       """Multi-step RAG pipeline with explicit tracer parameter.
       
       Args:
           datapoint: Contains 'inputs' and 'ground_truth'
           tracer: Auto-injected by evaluate()
       
       Returns:
           Dictionary with pipeline outputs
       """
       inputs = datapoint.get("inputs", {})
       query = inputs["question"]
       
       # Step 1: Retrieval
       with tracer.trace("retrieval"):
           docs = retrieve_documents(query)
           # Add component metric
           tracer.enrich_span(metrics={"retrieval_count": len(docs)})
       
       # Step 2: Reranking
       with tracer.trace("reranking"):
           ranked_docs = rerank(docs, query)
           # Add component metric
           tracer.enrich_span(metrics={"rerank_score": ranked_docs[0].score})
       
       # Step 3: Generation
       with tracer.trace("generation"):
           answer = generate_answer(query, ranked_docs)
           # Add component metric
           tracer.enrich_span(metrics={"answer_length": len(answer)})
       
       return {"answer": answer, "sources": ranked_docs}
   
   # Evaluate entire pipeline
   result = evaluate(
       function=rag_pipeline,
       dataset=dataset,
       api_key="your-api-key",
       project="your-project"
   )

**Using @trace Decorator**

.. code-block:: python

   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   from honeyhive import HoneyHiveTracer, trace
   
   # Initialize tracer for decorators
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project"
   )
   
   @trace(tracer=tracer, event_name="retrieval", event_type="tool")
   def retrieve_documents(query: str) -> list:
       """Retrieval component with automatic tracing."""
       docs = vector_db.search(query, top_k=10)
       # Metrics automatically captured by @trace
       tracer.enrich_span(metrics={"retrieval_count": len(docs)})
       return docs
   
   @trace(tracer=tracer, event_name="reranking", event_type="tool")
   def rerank(docs: list, query: str) -> list:
       """Reranking component with automatic tracing."""
       ranked = reranker.rerank(query, docs)
       tracer.enrich_span(metrics={"rerank_score": ranked[0].score})
       return ranked
   
   @trace(tracer=tracer, event_name="generation", event_type="tool")
   def generate_answer(query: str, docs: list) -> str:
       """Generation component with automatic tracing."""
       context = "\n".join([d.content for d in docs])
       answer = llm.generate(f"Context: {context}\n\nQuestion: {query}")
       tracer.enrich_span(metrics={"answer_length": len(answer)})
       return answer
   
   def rag_pipeline(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Multi-step RAG pipeline using decorated helper functions.
       
       Args:
           datapoint: Contains 'inputs' and 'ground_truth'
       
       Returns:
           Dictionary with pipeline outputs
       """
       inputs = datapoint.get("inputs", {})
       query = inputs["question"]
       
       # Each function call is automatically traced
       docs = retrieve_documents(query)
       ranked_docs = rerank(docs, query)
       answer = generate_answer(query, ranked_docs)
       
       return {"answer": answer, "sources": ranked_docs}
   
   # Evaluate entire pipeline
   result = evaluate(
       function=rag_pipeline,
       dataset=dataset,
       api_key="your-api-key",
       project="your-project"
   )

Component-Level Metrics
-----------------------

Each component can have its own metrics that are tracked separately in HoneyHive:

- Retrieval: precision, recall, relevance scores
- Reranking: rerank confidence, position changes
- Generation: length, quality, fact accuracy

These appear as separate metric traces in the dashboard.

See Also
--------

- :doc:`running-experiments` - Run multi-step experiments
- :doc:`../advanced-tracing/custom-spans` - Create custom spans
- :doc:`../../tutorials/03-enable-span-enrichment` - Enrich traces with metrics

