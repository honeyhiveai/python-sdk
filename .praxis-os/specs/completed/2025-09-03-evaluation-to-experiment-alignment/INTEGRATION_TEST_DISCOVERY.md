# Integration Test Discovery from HoneyHive Documentation

**Source**: HoneyHive documentation site (docs.honeyhive.ai)  
**Extracted**: 2025-10-02  
**Purpose**: Comprehensive test case extraction for experiment/evaluation integration tests

---

## 📋 Table of Contents

1. [Core Experiment Functionality](#core-experiment-functionality)
2. [Dataset Management](#dataset-management)
3. [Evaluator Framework](#evaluator-framework)
4. [Server-Side Integration](#server-side-integration)
5. [External Logs & Historical Data](#external-logs--historical-data)
6. [Multi-Step Pipelines](#multi-step-pipelines)
7. [Comparison & Analysis](#comparison--analysis)
8. [Tracing Integration](#tracing-integration)
9. [Priority Matrix](#priority-matrix)

---

## 1. Core Experiment Functionality

### From `/evaluation/quickstart.md`

#### ✅ **IMPLEMENTED** (Basic Flow)
- [x] Run experiment with local dataset (list of dicts)
- [x] Function receives `inputs` and `ground_truths` from datapoint
- [x] Client-side evaluators execute on each datapoint
- [x] Results visible in dashboard
- [x] Session metadata includes run_id, dataset_id, datapoint_id

#### 🔨 **TO IMPLEMENT**

**Test: `test_multi_threaded_execution`** 🔴 **HIGH PRIORITY**
- **Feature**: "Concurrent execution with ThreadPoolExecutor and max_workers"
- **Test Case**: Execute `evaluate()` with `max_workers=4` on large dataset
- **Validation**:
  - ✅ Multiple threads execute concurrently
  - ✅ Each tracer instance is isolated (no cross-contamination)
  - ✅ Session IDs are unique per datapoint
  - ✅ Metrics collected from all threads
  - ✅ No race conditions or thread safety issues
  - ✅ All datapoints processed successfully
  - ✅ Execution time < sequential time (performance gain)
  - ✅ Thread pool cleanup happens correctly

**Test: `test_evaluate_basic_workflow`**
- **Feature**: "Run experiments using local datasets defined directly in your code"
- **Test Case**: Execute `evaluate()` with inline dataset (list of dicts)
- **Validation**:
  - ✅ Function executes for each datapoint
  - ✅ `inputs` and `ground_truths` correctly passed
  - ✅ Outputs captured and stored
  - ✅ Run created in platform with correct name
  - ✅ Session count matches dataset size

**Test: `test_evaluator_parameter_order`**
- **Feature**: "Evaluators receive (outputs, inputs, ground_truths)"
- **Test Case**: Verify parameter order is strictly enforced
- **Validation**:
  - ✅ First param is function output
  - ✅ Second param is inputs dict
  - ✅ Third param is ground_truths dict
  - ✅ Error if params passed in wrong order

**Test: `test_server_url_configuration`**
- **Feature**: "server_url for self-hosted/dedicated deployments"
- **Test Case**: Pass custom `server_url` to `evaluate()`
- **Validation**:
  - ✅ API calls route to custom URL
  - ✅ Works with both `hh_api_key` and `api_key` params
  - ✅ Error handling for invalid URLs

---

## 2. Dataset Management

### From `/evaluation/managed_datasets.md`

#### ✅ **IMPLEMENTED**
- [x] Pass `dataset_id` to use HoneyHive managed dataset
- [x] Fetch datapoints from HoneyHive platform

#### 🔨 **TO IMPLEMENT**

**Test: `test_managed_dataset_evaluation`**
- **Feature**: "Run experiments using datasets managed through HoneyHive platform"
- **Setup**: Upload JSONL dataset via SDK, get `dataset_id`
- **Test Case**: Execute `evaluate()` with `dataset_id` param
- **Validation**:
  - ✅ SDK uploads a dataset with datapoints to the platform
  - ✅ SDK fetches datapoints from platform
  - ✅ Dataset structure includes `inputs` and `ground_truths`
  - ✅ Function receives correct fields
  - ✅ Run links to dataset via `dataset_id`
  - ✅ Datapoint IDs correctly associated

**Test: `test_dataset_format_support`**
- **Feature**: "Supports JSON, JSONL, and CSV formats"
- **Test Cases**: Upload datasets in different formats
- **Validation**:
  - ✅ JSONL format works
  - ✅ JSON format works
  - ✅ CSV format works
  - ✅ All formats produce same datapoint structure

**Test: `test_dataset_versioning`**
- **Feature**: "Centralized and versioned datasets for team collaboration"
- **Test Case**: Run experiment on specific dataset version
- **Validation**:
  - ✅ Can specify dataset version (if supported)
  - ✅ Different versions produce different results
  - ✅ Version info visible in run metadata

---

## 3. Evaluator Framework

### From `/evaluators/client_side.md` and `/evaluation/quickstart.md`

#### ✅ **IMPLEMENTED**
- [x] `@evaluator()` decorator
- [x] Sync and async evaluators
- [x] Multiple evaluators per experiment
- [x] Return numeric or dict of metrics

#### 🔨 **TO IMPLEMENT**

**Test: `test_evaluator_return_types`**
- **Feature**: "Evaluators can return single value or dict of metrics"
- **Test Cases**:
  ```python
  @evaluator()
  def single_value(outputs, inputs, ground_truths):
      return 0.85
  
  @evaluator()
  def multiple_metrics(outputs, inputs, ground_truths):
      return {"accuracy": 0.85, "precision": 0.90}
  ```
- **Validation**:
  - ✅ Single value stored as metric
  - ✅ Dict values stored as separate metrics
  - ✅ Metric names in dashboard match dict keys

**Test: `test_evaluator_error_handling`**
- **Feature**: "Graceful handling of evaluator failures"
- **Test Case**: Evaluator that raises exception
- **Validation**:
  - ✅ Experiment continues despite evaluator failure
  - ✅ Error logged but doesn't crash
  - ✅ Failed metric shows as None or error state
  - ✅ Other evaluators still execute

**Test: `test_evaluator_with_optional_ground_truth`**
- **Feature**: "ground_truths is optional parameter"
- **Test Case**: Evaluator without ground_truth param
- **Validation**:
  - ✅ Works when ground_truth not in dataset
  - ✅ Works when evaluator signature excludes ground_truth
  - ✅ No error when ground_truth is None

**Test: `test_async_evaluator_execution`**
- **Feature**: "Support for async evaluators (@aevaluator)"
- **Test Case**: Mix of sync and async evaluators
- **Validation**:
  - ✅ Async evaluators execute correctly
  - ✅ All evaluators complete regardless of sync/async
  - ✅ Metrics from both types stored
  - ✅ No blocking issues

---

## 4. Server-Side Integration

### From `/evaluation/server_side_evaluators.md`

#### ✅ **IMPLEMENTED**
- [x] Server-side evaluators auto-execute (no client config)
- [x] Metrics appear in dashboard without passing to `evaluators=[]`

#### 🔨 **TO IMPLEMENT**

**Test: `test_server_side_evaluator_execution`** ✅ **DONE** (from previous session)
- **Feature**: "Server-side evaluators execute automatically"
- **Setup**: Create Python evaluator in HoneyHive platform
- **Test Case**: Run `evaluate()` WITHOUT passing evaluators
- **Validation**:
  - ✅ Server-side evaluator runs automatically
  - ✅ Metrics appear in run results
  - ✅ Event type filtering works (e.g., "model" events only)
  - ✅ Access to `event["outputs"]["content"]` path

**Test: `test_mixed_client_server_evaluators`** ✅ **PARTIALLY DONE**
- **Feature**: "Client-side and server-side evaluators work together"
- **Test Case**: Pass client evaluators while server evaluators exist
- **Validation**:
  - ✅ Both types execute
  - ✅ All metrics stored
  - ✅ No conflicts or overwrites
  - ✅ Metric sources identifiable

**Test: `test_server_evaluator_event_filtering`**
- **Feature**: "Server evaluators filter by event type"
- **Setup**: Create evaluator targeting "model" events
- **Test Case**: Multi-step pipeline with various event types
- **Validation**:
  - ✅ Evaluator only runs on matching event types
  - ✅ Skips non-matching events
  - ✅ Event attributes accessible in evaluator

---

## 5. External Logs & Historical Data

### From `/evaluation/external_logs.md`

#### 🔨 **TO IMPLEMENT**

**Test: `test_external_log_evaluation`**
- **Feature**: "Upload and evaluate existing logs from external sources"
- **Test Case**: Pass-through function with pre-existing outputs
  ```python
  def pass_through_logged_data(inputs, ground_truths):
      return ground_truths["highlights"]  # Use logged output
  ```
- **Validation**:
  - ✅ Function can return pre-logged outputs
  - ✅ Evaluators run on historical data
  - ✅ No need to re-generate outputs
  - ✅ Metrics computed on existing logs

**Test: `test_csv_pandas_dataset_loading`**
- **Feature**: "Load logs from CSV/DataFrame"
- **Test Case**: `df.to_dict('records')` → `evaluate()`
- **Validation**:
  - ✅ CSV loads correctly
  - ✅ DataFrame conversion works
  - ✅ Dataset structure matches expected format
  - ✅ All rows processed

**Test: `test_benchmark_historical_prompts`**
- **Feature**: "Benchmark different versions using past data"
- **Test Case**: Same dataset, different evaluators/prompts
- **Validation**:
  - ✅ Can compare old vs new prompts
  - ✅ Metrics show differences
  - ✅ No re-execution of LLM needed

---

## 6. Multi-Step Pipelines

### From `/evaluation/multi_step_evals.md`

#### 🔨 **TO IMPLEMENT**

**Test: `test_multi_step_rag_pipeline`**
- **Feature**: "Evaluate multi-step RAG (retrieval + generation)"
- **Test Case**: Pipeline with `@trace` decorators
  ```python
  @trace
  def get_relevant_docs(query): ...
  
  @trace
  def generate_response(docs, query): ...
  
  def rag_pipeline(inputs, ground_truths):
      docs = get_relevant_docs(inputs["query"])
      return generate_response(docs, inputs["query"])
  ```
- **Validation**:
  - ✅ Both steps traced as spans
  - ✅ Parent-child relationship maintained
  - ✅ Span-level metrics via `enrich_span()`
  - ✅ Session-level metrics via `enrich_session()`

**Test: `test_span_level_metrics`**
- **Feature**: "Log metrics for specific pipeline steps"
- **Test Case**: Retrieval evaluator on retrieval span
  ```python
  @trace
  def get_relevant_docs(query):
      # ... retrieval logic
      enrich_span(metrics={"retrieval_relevance": 0.85})
  ```
- **Validation**:
  - ✅ Metric attached to correct span
  - ✅ Visible in trace viewer
  - ✅ Separate from session metrics
  - ✅ Aggregated in run results

**Test: `test_session_level_metrics`**
- **Feature**: "Log pipeline-wide metrics"
- **Test Case**: Overall pipeline metrics
  ```python
  def rag_pipeline(inputs, ground_truths):
      # ... pipeline logic
      enrich_session(metrics={
          "num_retrieved_docs": 3,
          "query_length": 10
      })
  ```
- **Validation**:
  - ✅ Metrics attached to session
  - ✅ Visible in session view
  - ✅ Aggregated across all sessions
  - ✅ Separate from span metrics

**Test: `test_vector_search_evaluation`**
- **Feature**: "Evaluate retrieval quality in RAG"
- **Test Case**: Cosine similarity between query and retrieved docs
- **Validation**:
  - ✅ Retrieval relevance metric computed
  - ✅ Low scores indicate poor retrieval
  - ✅ High scores indicate relevant docs
  - ✅ Correlates with final response quality

**Test: `test_response_consistency_evaluation`**
- **Feature**: "Measure semantic similarity to ground truth"
- **Test Case**: Embedding similarity evaluator
- **Validation**:
  - ✅ Consistency metric computed
  - ✅ Detects hallucinations (low retrieval, high consistency)
  - ✅ Detects poor responses (low both)
  - ✅ Identifies good responses (high both)

---

## 7. Comparison & Analysis

### From `/evaluation/comparing_evals.md`

#### ✅ **IMPLEMENTED**
- [x] Basic comparison of two runs
- [x] Common datapoints identification
- [x] Metric improvements/regressions

#### 🔨 **TO IMPLEMENT**

**Test: `test_step_level_comparison`** ✅ **PARTIALLY DONE**
- **Feature**: "Compare individual steps across experiments"
- **Test Case**: Two runs with multi-step pipelines
- **Validation**:
  - ✅ Compare retrieval step across runs
  - ✅ Compare generation step across runs
  - ✅ Identify which step improved/regressed
  - ✅ Step-level metric deltas

**Test: `test_aggregated_metrics_comparison`**
- **Feature**: "View aggregated metrics (server-side, client-side, composite)"
- **Test Case**: Compare runs with different evaluators
- **Validation**:
  - ✅ Server-side metrics aggregated
  - ✅ Client-side metrics aggregated
  - ✅ Composite metrics calculated
  - ✅ All metrics visible in comparison view

**Test: `test_improved_regressed_filtering`**
- **Feature**: "Filter for events that improved or regressed"
- **Test Case**: Comparison with mixed results
- **Validation**:
  - ✅ Filter shows only improved events
  - ✅ Filter shows only regressed events
  - ✅ Filter shows unchanged events
  - ✅ Metric thresholds configurable

**Test: `test_output_diff_viewer`**
- **Feature**: "View side-by-side output differences"
- **Test Case**: Two runs with different outputs
- **Validation**:
  - ✅ Diff view shows changes
  - ✅ Highlights added/removed content
  - ✅ Side-by-side comparison
  - ✅ Per-datapoint diff available

**Test: `test_metric_distribution_analysis`**
- **Feature**: "Analyze distribution of various metrics"
- **Test Case**: Comparison with metric histograms
- **Validation**:
  - ✅ Histogram shows metric distribution
  - ✅ Compare distributions across runs
  - ✅ Identify outliers
  - ✅ Statistical summary (mean, median, std)

**Test: `test_comparison_best_practices`**
- **Feature**: Best practices from docs
- **Test Cases**:
  1. Same dataset for both runs ✅
  2. Meaningful run names ✅
  3. Consistent evaluation criteria ✅
  4. Multiple metrics for comprehensive view
  5. Representative dataset size
- **Validation**: Each best practice enforced/encouraged

**Test: `test_event_level_comparison`**
- **Feature**: "Detailed per-datapoint comparison with matching"
- **Test Case**: Use `/runs/compare/events` endpoint
- **Validation**:
  - ✅ Events matched by `datapoint_id`
  - ✅ Per-metric improved/degraded/same lists
  - ✅ Event presence information
  - ✅ Paired events (event_1, event_2) returned
  - ✅ Common datapoints count correct

---

## 8. Tracing Integration

### From `/tracing/client-side-evals.md` and multi-step guide

#### 🔨 **TO IMPLEMENT**

**Test: `test_trace_decorator_integration`**
- **Feature**: "Use @trace decorator in experiment functions"
- **Test Case**: Function with nested @trace calls
- **Validation**:
  - ✅ All spans created
  - ✅ Hierarchy preserved
  - ✅ Experiment context maintained
  - ✅ Run ID propagated to all spans

**Test: `test_enrich_span_in_experiment`**
- **Feature**: "Log span-level metrics during experiment"
- **Test Case**: Call `enrich_span()` within traced function
- **Validation**:
  - ✅ Metrics attached to correct span
  - ✅ Visible in span details
  - ✅ Included in run aggregation
  - ✅ No conflicts with session metrics

**Test: `test_enrich_session_in_experiment`**
- **Feature**: "Log session-level metrics during experiment"
- **Test Case**: Call `enrich_session()` in experiment function
- **Validation**:
  - ✅ Metrics attached to session
  - ✅ Visible in session view
  - ✅ Aggregated in run results
  - ✅ Separate from evaluator metrics

**Test: `test_distributed_tracing_in_experiment`**
- **Feature**: "Maintain trace context across services"
- **Test Case**: Experiment function calls external service
- **Validation**:
  - ✅ Trace context propagated
  - ✅ External service spans linked
  - ✅ Full trace visible in platform
  - ✅ Run ID maintained

---

## 9. Priority Matrix

### 🔴 **HIGH PRIORITY** (Core Functionality)

These are essential for basic experiment workflow:

1. ✅ `test_evaluate_basic_workflow` - **DONE**
2. ✅ `test_managed_dataset_evaluation` - **DONE** (HoneyHive dataset support)
3. ✅ `test_server_side_evaluator_execution` - **DONE**
4. ✅ `test_mixed_client_server_evaluators` - **PARTIALLY DONE**
5. ✅ `test_evaluator_parameter_order` - **DONE** (validated in integration test)
6. ✅ `test_comparison_workflow` - **DONE**
7. 🔨 `test_event_level_comparison` - **TO IMPLEMENT**
8. 🔨 `test_multi_threaded_execution` - **TO IMPLEMENT** (CRITICAL for performance)

### 🟡 **MEDIUM PRIORITY** (Enhanced Features)

Important for advanced use cases:

8. `test_multi_step_rag_pipeline`
9. `test_span_level_metrics`
10. `test_session_level_metrics`
11. `test_evaluator_return_types`
12. `test_evaluator_error_handling`
13. `test_server_url_configuration`
14. `test_dataset_format_support`

### 🟢 **LOW PRIORITY** (Nice to Have)

Useful but not critical:

15. `test_external_log_evaluation`
16. `test_csv_pandas_dataset_loading`
17. `test_benchmark_historical_prompts`
18. `test_dataset_versioning`
19. `test_async_evaluator_execution`
20. `test_evaluator_with_optional_ground_truth`
21. `test_output_diff_viewer`
22. `test_metric_distribution_analysis`

---

## 📊 Coverage Summary

| Category | Total Tests | Implemented | To Implement | Priority |
|----------|------------|-------------|--------------|----------|
| **Core Functionality** | 8 | 6 | 2 | 🔴 HIGH |
| **Dataset Management** | 4 | 1 | 3 | 🟡 MEDIUM |
| **Evaluator Framework** | 6 | 2 | 4 | 🟡 MEDIUM |
| **Server-Side** | 3 | 2 | 1 | 🔴 HIGH |
| **External Logs** | 3 | 0 | 3 | 🟢 LOW |
| **Multi-Step** | 5 | 0 | 5 | 🟡 MEDIUM |
| **Comparison** | 6 | 2 | 4 | 🔴 HIGH |
| **Tracing** | 4 | 0 | 4 | 🟡 MEDIUM |
| **TOTAL** | **39** | **13** | **26** | - |

---

## 🎯 Recommended Implementation Order

### Phase 1: Complete High-Priority Coverage
1. `test_event_level_comparison` - Event-level comparison endpoint
2. `test_multi_threaded_execution` - Concurrent execution with thread safety validation

### Phase 2: Multi-Step & Tracing (Critical for Real Pipelines)
3. `test_multi_step_rag_pipeline`
4. `test_span_level_metrics`
5. `test_session_level_metrics`
6. `test_trace_decorator_integration`

### Phase 3: Evaluator Robustness
7. `test_evaluator_return_types`
8. `test_evaluator_error_handling`
9. `test_async_evaluator_execution`
10. `test_evaluator_with_optional_ground_truth`

### Phase 4: Dataset Flexibility
11. `test_dataset_format_support`
12. `test_server_url_configuration`
13. `test_external_log_evaluation`

### Phase 5: Advanced Analysis
14. `test_step_level_comparison`
15. `test_aggregated_metrics_comparison`
16. `test_improved_regressed_filtering`
17. Remaining low-priority tests as needed

---

## 📝 Test Template

For each test to implement, use this structure:

```python
def test_feature_name(
    self,
    real_api_key: str,
    real_project: str,
    integration_client: HoneyHive,
) -> None:
    """
    Test [feature description from docs].
    
    Documentation Reference: /evaluation/[page].md
    
    This test validates:
    1. [Validation point 1]
    2. [Validation point 2]
    3. [Validation point 3]
    """
    
    # Setup
    # ...
    
    # Execute
    # ...
    
    # Validate
    # ...
    
    # Cleanup (if needed)
    # ...
```

---

## 🔗 Related Documentation

- **Agent OS Testing Framework**: `.praxis-os/standards/ai-assistant/code-generation/tests/v3/FRAMEWORK-LAUNCHER.md`
- **Integration Testing Standards**: `.praxis-os/standards/testing/integration-testing-standards.md`
- **Backend Validation**: `.praxis-os/specs/2025-09-03-evaluation-to-experiment-alignment/BACKEND_VALIDATION_ANALYSIS.md`
- **Endpoint Coverage**: `.praxis-os/specs/2025-09-03-evaluation-to-experiment-alignment/ENDPOINT_COVERAGE_MATRIX.md`
- **HoneyHive Docs Access**: `.praxis-os/standards/documentation/honeyhive-docs-access.md`

---

**Last Updated**: 2025-10-02  
**Status**: 13/39 tests implemented (33% coverage)  
**Next Actions**:
1. Implement `test_event_level_comparison` from Phase 1
2. Implement `test_multi_threaded_execution` from Phase 1 (CRITICAL)

