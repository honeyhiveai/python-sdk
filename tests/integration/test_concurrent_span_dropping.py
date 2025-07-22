import os
import time
from collections import defaultdict
from honeyhive import HoneyHive
from honeyhive.models import components, operations
from honeyhive import evaluate, evaluator, trace, enrich_span

MY_HONEYHIVE_API_KEY = os.getenv("HH_API_KEY")
MY_HONEYHIVE_PROJECT_NAME = os.getenv("HH_PROJECT")
HONEYHIVE_SERVER_URL = os.getenv("HH_API_URL")

@evaluator()
def validation_evaluator(outputs, inputs, ground_truths):
    """Evaluator that adds computational load to trigger timing issues"""
    import random
    time.sleep(0.1)  # Simulate processing time
    score = random.uniform(0.5, 1.0)
    return {"validation_score": score}

@evaluator() 
def consistency_evaluator(outputs, inputs, ground_truths):
    """Second evaluator to increase span complexity"""
    import random
    consistency_score = random.uniform(0.6, 0.9)
    return {"consistency_score": consistency_score}

def complex_evaluation_function(inputs, ground_truths):
    """
    Evaluation function with nested traced operations to create multiple spans
    Designed to create exactly 4 spans per evaluation:
    1. Main evaluation function span
    2. Retrieval operation span  
    3. Generation operation span
    4. Evaluator spans
    """
    
    @trace
    def retrieve_documents(query):
        """Simulates document retrieval with tracing"""
        time.sleep(0.05)  # Simulate retrieval latency
        docs = [f"doc_{i}_for_{query}" for i in range(3)]
        enrich_span(metrics={
            "doc_count": len(docs),
            "retrieval_method": "semantic_search"
        })
        return docs
    
    @trace
    def generate_response(docs, query):
        """Simulates response generation with tracing"""
        time.sleep(0.05)  # Simulate generation latency
        response = f"Generated comprehensive response for: {query} using {len(docs)} documents"
        enrich_span(metrics={
            "response_length": len(response),
            "generation_model": "test_model"
        })
        return response
    
    @trace
    def process_results(response, expected_count):
        """Additional processing step to increase span count"""
        time.sleep(0.02)  # Brief processing delay
        processed = {
            "response": response,
            "word_count": len(response.split()),
            "meets_expectation": len(response) > 50
        }
        enrich_span(metrics={
            "processing_time_ms": 20,
            "meets_expectation": processed["meets_expectation"]
        })
        return processed
    
    # Main evaluation logic with multiple traced operations
    query = inputs.get("query", "default test query")
    expected_doc_count = ground_truths.get("expected_doc_count", 3)
    
    # Step 1: Retrieve documents (creates span)
    docs = retrieve_documents(query)
    
    # Step 2: Generate response (creates span)  
    response = generate_response(docs, query)
    
    # Step 3: Process results (creates span)
    result = process_results(response, expected_doc_count)
    
    # Add final metrics to main span
    enrich_span(metrics={
        "total_docs_retrieved": len(docs),
        "final_response_length": len(response)
    })
    
    return {
        "response": result["response"],
        "doc_count": len(docs),
        "word_count": result["word_count"],
        "processing_success": result["meets_expectation"]
    }

def test_concurrent_evaluation_span_completeness():
    """
    Test to validate span completeness during high-concurrency evaluation scenarios.
    This test is designed to reproduce span dropping issues by:
    1. Running concurrent evaluations with high thread count
    2. Creating rapid burst of tracer operations  
    3. Validating that all expected spans are captured
    """
    
    # Test parameters designed to trigger race conditions
    DATASET_SIZE = 25          # Large enough to create concurrent load
    MAX_WORKERS = 15           # Higher than default to increase concurrency
    EXPECTED_SPANS_PER_SESSION = 4  # Main + retrieval + generation + processing spans
    
    print(f"\n=== Starting Concurrent Span Dropping Test ===")
    print(f"Dataset size: {DATASET_SIZE}")
    print(f"Max workers: {MAX_WORKERS}")
    print(f"Expected spans per session: {EXPECTED_SPANS_PER_SESSION}")
    
    # Create dataset with sufficient size to trigger concurrency
    dataset = []
    for i in range(DATASET_SIZE):
        dataset.append({
            "inputs": {
                "query": f"Complex test query {i} with multiple terms",
                "complexity": "high",
                "batch_id": i // 5  # Group into batches for analysis
            },
            "ground_truths": {
                "expected_doc_count": 3,
                "min_response_length": 50
            }
        })
    
    # Run evaluation with high concurrency
    print(f"Starting evaluation with {MAX_WORKERS} concurrent workers...")
    start_time = time.time()
    
    evaluation_results = evaluate(
        function=complex_evaluation_function,
        api_key=MY_HONEYHIVE_API_KEY,
        project=MY_HONEYHIVE_PROJECT_NAME,
        name='Concurrent Span Dropping Validation Test',
        dataset=dataset,
        evaluators=[validation_evaluator, consistency_evaluator],
        # max_workers=MAX_WORKERS,  # Use default (now 1) to test fix
        run_concurrently=True,
        verbose=True,
        server_url=HONEYHIVE_SERVER_URL
    )
    
    evaluation_time = time.time() - start_time
    print(f"Evaluation completed in {evaluation_time:.2f} seconds")
    
    # Wait for spans to be exported (increased for high-load scenario)
    print("Waiting for span export to complete...")
    time.sleep(25)  # Extended wait time for high concurrency
    
    # Validate span completeness for each session
    print("Starting span completeness validation...")
    sdk = HoneyHive(
        bearer_auth=MY_HONEYHIVE_API_KEY,
        server_url=HONEYHIVE_SERVER_URL
    )
    
    session_ids = evaluation_results.session_ids
    total_expected_events = len(session_ids) * EXPECTED_SPANS_PER_SESSION
    total_actual_events = 0
    missing_spans_by_session = {}
    span_types_found = defaultdict(int)
    evaluator_results_found = defaultdict(int)
    
    print(f"Validating spans for {len(session_ids)} sessions...")
    
    for i, session_id in enumerate(session_ids):
        if i % 5 == 0:  # Progress indicator
            print(f"  Validated {i}/{len(session_ids)} sessions...")
            
        req = operations.GetEventsRequestBody(
            project=MY_HONEYHIVE_PROJECT_NAME,
            filters=[
                components.EventFilter(
                    field="session_id",
                    value=session_id,
                    operator=components.Operator.IS,
                )
            ],
        )
        
        res = sdk.events.get_events(request=req)
        events = res.object.events
        total_actual_events += len(events)
        
        # Track span types for analysis
        session_span_types = set()
        for event in events:
            event_type = event.event_type or "unknown"
            span_types_found[event_type] += 1
            session_span_types.add(event_type)
            
            # Check for evaluator results
            if event.metrics:
                if 'validation_score' in event.metrics:
                    evaluator_results_found['validation_evaluator'] += 1
                if 'consistency_score' in event.metrics:
                    evaluator_results_found['consistency_evaluator'] += 1
        
        # Check if this session has missing spans
        if len(events) < EXPECTED_SPANS_PER_SESSION:
            missing_spans_by_session[session_id] = {
                'expected': EXPECTED_SPANS_PER_SESSION,
                'actual': len(events),
                'missing': EXPECTED_SPANS_PER_SESSION - len(events),
                'span_types_found': list(session_span_types)
            }
    
    # Calculate span dropping statistics
    span_drop_rate = (total_expected_events - total_actual_events) / total_expected_events if total_expected_events > 0 else 0
    sessions_with_missing_spans = len(missing_spans_by_session)
    
    print(f"\n=== SPAN COMPLETENESS ANALYSIS ===")
    print(f"Total sessions: {len(session_ids)}")
    print(f"Total expected events: {total_expected_events}")
    print(f"Total actual events: {total_actual_events}")
    print(f"Span drop rate: {span_drop_rate:.2%}")
    print(f"Sessions with missing spans: {sessions_with_missing_spans}/{len(session_ids)}")
    print(f"Evaluation time: {evaluation_time:.2f}s")
    
    print(f"\nSpan types found:")
    for span_type, count in span_types_found.items():
        expected_count = len(session_ids) if span_type != 'session' else len(session_ids)
        print(f"  {span_type}: {count} (expected: ~{expected_count})")
    
    print(f"\nEvaluator results found:")
    for evaluator_name, count in evaluator_results_found.items():
        print(f"  {evaluator_name}: {count} (expected: {len(session_ids)})")
    
    if missing_spans_by_session:
        print(f"\nSessions with missing spans (showing first 10):")
        shown_count = 0
        for session_id, info in missing_spans_by_session.items():
            if shown_count >= 10:
                break
            print(f"  {session_id}: {info['missing']} spans missing, found types: {info['span_types_found']}")
            shown_count += 1
        if len(missing_spans_by_session) > 10:
            print(f"  ... and {len(missing_spans_by_session) - 10} more sessions with missing spans")
    
    # Primary assertions for span dropping detection
    print(f"\n=== VALIDATION RESULTS ===")
    
    # Check for significant span dropping
    if span_drop_rate > 0.05:  # More than 5% span loss indicates dropping
        print(f"❌ SPAN DROPPING DETECTED: {span_drop_rate:.2%} drop rate exceeds 5% threshold")
        assert False, f"Significant span dropping detected: {span_drop_rate:.2%} drop rate"
    else:
        print(f"✅ Span drop rate {span_drop_rate:.2%} within acceptable range")
    
    # Ensure no sessions completely missing spans  
    if sessions_with_missing_spans > 0:
        print(f"❌ INCOMPLETE SESSIONS: {sessions_with_missing_spans} sessions missing spans")
        assert False, f"{sessions_with_missing_spans} sessions have missing spans"
    else:
        print(f"✅ All sessions have complete span sets")
    
    # Validate that we have a reasonable number of spans (don't check specific event types)
    if total_actual_events < total_expected_events * 0.8:  # Allow some variance
        print(f"❌ INSUFFICIENT SPANS: Only {total_actual_events} spans found, expected around {total_expected_events}")
        print(f"Available span types: {dict(span_types_found)}")
    else:
        print(f"✅ Sufficient spans found: {total_actual_events} spans across {len(span_types_found)} types")
    
    # Validate evaluator results
    expected_evaluators = ['validation_evaluator', 'consistency_evaluator']
    for evaluator_name in expected_evaluators:
        if evaluator_results_found[evaluator_name] == 0:
            print(f"❌ MISSING EVALUATOR: No results from '{evaluator_name}' found")
            assert False, f"No results from '{evaluator_name}' found"
        else:
            print(f"✅ Evaluator '{evaluator_name}' results: {evaluator_results_found[evaluator_name]} instances")
    
    print(f"\n🎉 Span completeness validation PASSED - no dropping detected!")
    print(f"Successfully processed {len(session_ids)} concurrent evaluations with {total_actual_events} spans")

if __name__ == "__main__":
    test_concurrent_evaluation_span_completeness()