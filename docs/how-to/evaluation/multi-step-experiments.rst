Multi-Step Experiments
======================

How do I evaluate a pipeline with multiple steps (e.g., RAG)?
-------------------------------------------------------------

Use component-level tracing and metrics within your evaluation function.

How do I evaluate each component separately?
--------------------------------------------

**Add Metrics to Each Step**

.. code-block:: python

   from honeyhive.experiments import evaluate
   from honeyhive import HoneyHiveTracer, enrich_span
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="your-project"
   )
   
   def rag_pipeline(inputs, ground_truth):
       """Multi-step RAG pipeline."""
       query = inputs["question"]
       
       # Step 1: Retrieval
       with tracer.trace("retrieval") as span:
           docs = retrieve_documents(query)
           # Add component metric
           enrich_span(metrics={"retrieval_count": len(docs)})
       
       # Step 2: Reranking
       with tracer.trace("reranking") as span:
           ranked_docs = rerank(docs, query)
           # Add component metric
           enrich_span(metrics={"rerank_score": ranked_docs[0].score})
       
       # Step 3: Generation
       with tracer.trace("generation") as span:
           answer = generate_answer(query, ranked_docs)
           # Add component metric
           enrich_span(metrics={"answer_length": len(answer)})
       
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

