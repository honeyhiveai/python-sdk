# Result & Metrics Endpoints Analysis
## Backend Aggregation vs Client-Side Computation

**Last Updated:** October 2, 2025  
**Critical Discovery:** Backend already computes all aggregates - SDK should NOT duplicate this logic

---

## 🚨 Critical Finding

**The backend already has sophisticated aggregation endpoints!**

The current approach (in spec/main branch) tries to compute aggregates in Python, but **backend already does this better**:

```python
# ❌ WRONG: Computing aggregates in SDK
results = []
for datapoint in dataset:
    result = run_evaluator(datapoint)
    results.append(result)

# Compute statistics manually
total_score = sum(r.score for r in results) / len(results)
passed = [r for r in results if r.score > threshold]
failed = [r for r in results if r.score <= threshold]
```

```python
# ✅ CORRECT: Let backend compute aggregates
# 1. Run experiment (creates run_id)
run = create_run(project="...", name="...", dataset_id="...")

# 2. Execute evaluations (tracer sends events to backend)
for datapoint in dataset:
    tracer = HoneyHiveTracer(run_id=run.run_id, ...)
    run_evaluator(datapoint, tracer)
    tracer.flush()

# 3. Get aggregated results from backend
results = get_run_result(run_id=run.run_id)
# Backend returns: total score, passed/failed, metrics per event, etc.
```

---

## 1. Backend Aggregation Endpoints

### 1.1 GET /runs/:run_id/result - Get Aggregated Results

**Purpose:** Compute comprehensive evaluation summary with aggregates

**From `experiment_run.route.ts:444-527`:**
```typescript
// GET /runs/:run_id/result
router.get('/:run_id/result', asyncWrapper(async (req, res) => {
  const { run_id } = req.params;
  const { aggregate_function, filters } = req.query;
  
  // Call the existing JavaScript service function
  const summary = await computeEvaluationSummary(
    orgId,
    projectId,
    run_id,
    aggregate_function,  // 'average', 'sum', 'min', 'max', etc.
    parsedFilters,
  );
  
  res.status(200).json(summary);
}));
```

**Query Parameters:**
```typescript
{
  aggregate_function?: string,  // 'average' (default), 'sum', 'min', 'max'
  filters?: any[],              // Optional filters for events
}
```

### 1.2 Backend Computation Logic

**From `run_processing_service.js:5-269`:**

The backend does **sophisticated aggregation**:

1. **Fetches All Event Data**
   ```javascript
   const eventData = await getEventMetrics(orgId, projectId, null, filters, runId);
   ```

2. **Groups by Session/Datapoint**
   ```javascript
   const sessionMap = new Map();
   events.forEach((event) => {
     const sessionId = event.session_id;
     if (!sessionMap.has(sessionId)) {
       sessionMap.set(sessionId, {
         datapoint_id: event.metadata.datapoint_id,
         session_id: sessionId,
         passed: true,
         metrics: [],
       });
     }
     // ... aggregate metrics
   });
   ```

3. **Calculates Composite Metrics**
   ```javascript
   const compositeResults = calculateCompositeMetrics(
     applicableComposites, 
     metricValues
   );
   ```

4. **Determines Pass/Fail**
   ```javascript
   const allPassed = session.metrics.every((m) => m.passed);
   if (allPassed) {
     result.passed.push(session.datapoint_id || sessionId);
   } else {
     result.failed.push(session.datapoint_id || sessionId);
   }
   ```

5. **Aggregates Metrics**
   ```javascript
   metric.values.push(value);
   // Later computes aggregate (average, sum, min, max)
   metric.aggregate = aggregateValues(metric.values, aggregationFunction);
   ```

### 1.3 Response Schema

**From `run_processing_service.js:39-49` + full logic:**

```typescript
{
  status: string,              // Run status ('completed', 'running', etc.)
  success: boolean,            // Overall success (all datapoints passed)
  passed: string[],            // Array of passed datapoint IDs
  failed: string[],            // Array of failed datapoint IDs
  metrics: {
    aggregation_function: string,  // Which function was used
    [metricKey]: {
      metric_name: string,
      metric_type: string,     // 'CLIENT_SIDE', 'COMPOSITE', etc.
      event_name: string,
      event_type: string,
      aggregate: number,       // Aggregated value (avg, sum, etc.)
      values: number[],        // All raw values
      datapoints: {
        passed: string[],      // Datapoint IDs that passed this metric
        failed: string[],      // Datapoint IDs that failed this metric
      },
      passing_range?: {
        min: number,
        max: number,
      }
    }
  },
  datapoints: [
    {
      datapoint_id: string,
      session_id: string,
      passed: boolean,
      metrics: [
        {
          name: string,
          event_name: string,
          event_type: string,
          value: number,
          passed: boolean,
        }
      ]
    }
  ],
  event_details: [
    {
      event_name: string,
      event_type: string,
    }
  ]
}
```

---

## 2. GET /runs/:run_id/metrics - Get Event Metrics

**Purpose:** Get raw event metrics data (before aggregation)

**From `experiment_run.route.ts:348-442`:**
```typescript
router.get('/:run_id/metrics', asyncWrapper(async (req, res) => {
  const { run_id } = req.params;
  const { dateRange, filters } = req.query;
  
  const eventData = await getEventMetrics(
    orgId,
    projectId,
    parsedDateRange,
    parsedFilters,
    run_id,
  );
  
  res.status(200).json(eventData);
}));
```

**Query Parameters:**
```typescript
{
  dateRange?: string,  // JSON string: { start: timestamp, end: timestamp }
  filters?: any[],     // Event filters
}
```

**Use Case:** Raw event data for detailed analysis or custom aggregation

---

## 3. GET /runs/:new_run_id/compare-with/:old_run_id - Compare Runs

**Purpose:** Compare two experiment runs

**From `experiment_run.route.ts:530-614`:**
```typescript
router.get('/:new_run_id/compare-with/:old_run_id', asyncWrapper(async (req, res) => {
  const { new_run_id, old_run_id } = req.params;
  const { aggregate_function, filters } = req.query;
  
  // Get summaries for both runs in parallel
  const [newRunSummary, oldRunSummary] = await Promise.all([
    computeEvaluationSummary(orgId, projectId, new_run_id, aggregate_function, filters),
    computeEvaluationSummary(orgId, projectId, old_run_id, aggregate_function, filters),
  ]);
  
  // Compare the runs
  const comparison = compareRunMetrics(oldRunSummary, newRunSummary);
  
  res.status(200).json(comparison);
}));
```

### 3.1 Comparison Logic

**From `run_processing_service.js:300-463`:**

```javascript
function compareRunMetrics(oldRun, newRun) {
  let comparison = {
    metrics: [],
    commonDatapoints: [],
    event_details: [],
    old_run: oldRun.run_object,
    new_run: newRun.run_object,
  };
  
  // Get common datapoints between runs
  const oldRunDatapointIds = new Set(
    oldRun.datapoints.map((d) => d.datapoint_id)
  );
  const newRunDatapointIds = new Set(
    newRun.datapoints.map((d) => d.datapoint_id)
  );
  const commonDatapointIds = [...oldRunDatapointIds].filter(
    (id) => newRunDatapointIds.has(id)
  );
  
  comparison.commonDatapoints = commonDatapointIds;
  
  // Compare metrics
  Object.keys(oldRun.metrics).forEach((metricKey) => {
    if (metricKey === 'aggregation_function') return;
    
    const oldMetric = oldRun.metrics[metricKey];
    const newMetric = newRun.metrics[metricKey];
    
    if (newMetric) {
      const delta = newMetric.aggregate - oldMetric.aggregate;
      const percentChange = oldMetric.aggregate !== 0
        ? ((delta / oldMetric.aggregate) * 100).toFixed(2)
        : 'N/A';
      
      comparison.metrics.push({
        metric_name: oldMetric.metric_name,
        event_name: oldMetric.event_name,
        event_type: oldMetric.event_type,
        old_value: oldMetric.aggregate,
        new_value: newMetric.aggregate,
        delta: delta,
        percent_change: percentChange,
        improved: delta > 0,  // Assuming higher is better
      });
    }
  });
  
  return comparison;
}
```

### 3.2 Comparison Response

```typescript
{
  metrics: [
    {
      metric_name: string,
      event_name: string,
      event_type: string,
      old_value: number,
      new_value: number,
      delta: number,
      percent_change: string,
      improved: boolean,
    }
  ],
  commonDatapoints: string[],  // Datapoint IDs present in both runs
  event_details: any[],
  old_run: ExperimentRun,
  new_run: ExperimentRun,
}
```

---

## 4. GET /runs/compare/events - Compare Events Between Runs

**Purpose:** Get side-by-side event comparison for detailed analysis

**From `experiment_run.route.ts:616-690`:**
```typescript
router.get('/compare/events', asyncWrapper(async (req, res) => {
  const { run_id_1, run_id_2, event_name, event_type, filter, limit, page } = req.query;
  
  const eventData = await getSessionComparisonForEvaluations(
    orgId,
    projectId,
    parsedFilter,
    run_id_1,
    run_id_2,
    event_name,
    event_type,
    limit,
    skip,
  );
  
  res.status(200).json(eventData);
}));
```

**Query Parameters:**
```typescript
{
  run_id_1: string,         // First run ID (UUID v4)
  run_id_2: string,         // Second run ID (UUID v4)
  event_name?: string,      // Filter by event name
  event_type?: string,      // Filter by event type
  filter?: any,             // Additional filters
  limit?: number,           // Max 1000, default 1000
  page?: number,            // Page number, default 1
}
```

---

## 5. Why Backend Aggregation is Better

### 5.1 Performance

**❌ Client-Side:**
- Fetch all individual events
- Transfer large amounts of data over network
- Compute aggregates in Python (slower)

**✅ Backend:**
- Query database efficiently (ClickHouse optimized for analytics)
- Compute aggregates in-place
- Transfer only summary data

### 5.2 Accuracy

**❌ Client-Side:**
- May miss events due to timing issues
- Harder to handle composite metrics
- Risk of inconsistencies

**✅ Backend:**
- Single source of truth
- Consistent aggregation logic
- Handles complex composite metrics

### 5.3 Features

**Backend provides:**
- ✅ Multiple aggregation functions (average, sum, min, max)
- ✅ Pass/fail determination based on project thresholds
- ✅ Composite metrics calculation
- ✅ Event filtering
- ✅ Common datapoint detection for comparisons
- ✅ Delta and percent change calculations

**Client-side would need to:**
- ❌ Re-implement all aggregation logic
- ❌ Fetch and store project metric thresholds
- ❌ Implement composite metric calculations
- ❌ Maintain consistency with backend

---

## 6. SDK Implementation Strategy

### 6.1 High-Level Experiment Flow

**✅ CORRECT Approach:**

```python
from honeyhive.experiments import run_experiment, get_experiment_results

# 1. Run experiment (SDK creates run, executes with tracer)
result = run_experiment(
    name="My Experiment",
    dataset=dataset,
    function=my_llm_function,
    evaluators=[accuracy_evaluator, f1_evaluator],
    api_key=api_key,
    project=project,
)

print(f"Run ID: {result.run_id}")
print(f"Status: {result.status}")

# 2. Get aggregated results (backend computes everything)
summary = get_experiment_results(
    run_id=result.run_id,
    aggregate_function="average",  # or 'sum', 'min', 'max'
)

print(f"Overall Success: {summary.success}")
print(f"Passed: {len(summary.passed)} datapoints")
print(f"Failed: {len(summary.failed)} datapoints")

# 3. Access per-metric aggregates
for metric_key, metric_data in summary.metrics.items():
    print(f"{metric_data.metric_name}: {metric_data.aggregate}")
    print(f"  Passed: {len(metric_data.datapoints.passed)}")
    print(f"  Failed: {len(metric_data.datapoints.failed)}")
```

### 6.2 SDK Functions Needed

**High-Level API:**
```python
# experiments/core.py
def run_experiment(
    name: str,
    dataset: List[Dict[str, Any]],
    function: Callable,
    evaluators: List[BaseEvaluator],
    *,
    api_key: str,
    project: str,
    aggregate_function: str = "average",
    **kwargs
) -> ExperimentRunResult:
    """Run an experiment and get aggregated results.
    
    This function:
    1. Creates an experiment run
    2. Executes function on each datapoint with tracer
    3. Runs evaluators
    4. Fetches aggregated results from backend
    
    Returns:
        ExperimentRunResult with aggregated statistics
    """
    # Create run
    run = create_run(...)
    
    # Execute with tracer (multi-instance)
    for datapoint in dataset:
        tracer = create_tracer_for_datapoint(run.run_id, datapoint)
        execute_datapoint(function, evaluators, datapoint, tracer)
        tracer.flush()
    
    # Update run status
    update_run(run.run_id, status="completed")
    
    # Get aggregated results from backend
    results = get_run_result(
        run_id=run.run_id,
        aggregate_function=aggregate_function
    )
    
    return ExperimentRunResult(
        run_id=run.run_id,
        summary=results,
        ...
    )
```

**Low-Level API:**
```python
# experiments/results.py
def get_run_result(
    client: HoneyHive,
    run_id: str,
    aggregate_function: str = "average",
    filters: Optional[List[Any]] = None,
) -> ExperimentResultSummary:
    """Get aggregated experiment results.
    
    Calls: GET /runs/:run_id/result
    
    Args:
        client: HoneyHive client
        run_id: Experiment run ID
        aggregate_function: 'average', 'sum', 'min', 'max'
        filters: Optional event filters
        
    Returns:
        ExperimentResultSummary with all aggregates
    """
    response = client.request(
        "GET",
        f"/runs/{run_id}/result",
        params={
            "aggregate_function": aggregate_function,
            "filters": json.dumps(filters) if filters else None,
        }
    )
    
    return ExperimentResultSummary(**response.json())


def get_run_metrics(
    client: HoneyHive,
    run_id: str,
    date_range: Optional[Dict[str, int]] = None,
    filters: Optional[List[Any]] = None,
) -> EventMetricsResponse:
    """Get raw event metrics (before aggregation).
    
    Calls: GET /runs/:run_id/metrics
    
    Use this for custom analysis or detailed inspection.
    """
    response = client.request(
        "GET",
        f"/runs/{run_id}/metrics",
        params={
            "dateRange": json.dumps(date_range) if date_range else None,
            "filters": json.dumps(filters) if filters else None,
        }
    )
    
    return EventMetricsResponse(**response.json())


def compare_runs(
    client: HoneyHive,
    new_run_id: str,
    old_run_id: str,
    aggregate_function: str = "average",
    filters: Optional[List[Any]] = None,
) -> RunComparisonResult:
    """Compare two experiment runs.
    
    Calls: GET /runs/:new_run_id/compare-with/:old_run_id
    
    Args:
        client: HoneyHive client
        new_run_id: Newer run ID
        old_run_id: Older run ID (baseline)
        aggregate_function: 'average', 'sum', 'min', 'max'
        filters: Optional event filters
        
    Returns:
        RunComparisonResult with deltas and percent changes
    """
    response = client.request(
        "GET",
        f"/runs/{new_run_id}/compare-with/{old_run_id}",
        params={
            "aggregate_function": aggregate_function,
            "filters": json.dumps(filters) if filters else None,
        }
    )
    
    return RunComparisonResult(**response.json())
```

### 6.3 Response Models

**Pydantic Models Needed:**

```python
# experiments/models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MetricDatapoints(BaseModel):
    """Passed/failed datapoint IDs for a metric."""
    passed: List[str] = Field(..., description="Datapoint IDs that passed")
    failed: List[str] = Field(..., description="Datapoint IDs that failed")


class PassingRange(BaseModel):
    """Metric threshold range."""
    min: float
    max: float


class AggregatedMetric(BaseModel):
    """Aggregated metric data."""
    metric_name: str
    metric_type: str  # 'CLIENT_SIDE', 'COMPOSITE', etc.
    event_name: str
    event_type: str
    aggregate: float = Field(..., description="Aggregated value (avg, sum, etc.)")
    values: List[float] = Field(..., description="All raw values")
    datapoints: MetricDatapoints
    passing_range: Optional[PassingRange] = None


class DatapointMetric(BaseModel):
    """Individual metric value for a datapoint."""
    name: str
    event_name: str
    event_type: str
    value: float
    passed: bool


class DatapointResult(BaseModel):
    """Result for a single datapoint."""
    datapoint_id: str
    session_id: str
    passed: bool
    metrics: List[DatapointMetric]


class EventDetail(BaseModel):
    """Event type detail."""
    event_name: str
    event_type: str


class ExperimentResultSummary(BaseModel):
    """Aggregated experiment result summary."""
    status: str = Field(..., description="Run status")
    success: bool = Field(..., description="All datapoints passed")
    passed: List[str] = Field(..., description="Passed datapoint IDs")
    failed: List[str] = Field(..., description="Failed datapoint IDs")
    metrics: Dict[str, AggregatedMetric] = Field(..., description="Metrics by key")
    datapoints: List[DatapointResult]
    event_details: List[EventDetail]


class MetricComparison(BaseModel):
    """Comparison of a single metric between runs."""
    metric_name: str
    event_name: str
    event_type: str
    old_value: float
    new_value: float
    delta: float
    percent_change: str
    improved: bool


class RunComparisonResult(BaseModel):
    """Comparison between two runs."""
    metrics: List[MetricComparison]
    commonDatapoints: List[str] = Field(..., alias="commonDatapoints")
    event_details: List[Any]
    old_run: Any  # ExperimentRun
    new_run: Any  # ExperimentRun
```

---

## 7. What NOT To Do

### 7.1 ❌ DON'T Compute Aggregates in SDK

```python
# ❌ BAD: Computing aggregates client-side
def compute_experiment_stats(results: List[EvaluationResult]):
    """DON'T DO THIS - backend already does it!"""
    total_score = sum(r.score for r in results) / len(results)
    passed = [r for r in results if r.score > 0.7]
    failed = [r for r in results if r.score <= 0.7]
    
    metrics = {}
    for result in results:
        for metric_name, value in result.metrics.items():
            if metric_name not in metrics:
                metrics[metric_name] = []
            metrics[metric_name].append(value)
    
    aggregated_metrics = {
        name: sum(values) / len(values)
        for name, values in metrics.items()
    }
    
    return {
        "overall_score": total_score,
        "passed": passed,
        "failed": failed,
        "metrics": aggregated_metrics,
    }
```

### 7.2 ❌ DON'T Fetch All Events and Aggregate

```python
# ❌ BAD: Fetching all events and computing locally
def get_experiment_summary(run_id: str):
    """DON'T DO THIS - use /runs/:run_id/result endpoint!"""
    # Fetch all events
    events = client.events.list(run_id=run_id)
    
    # Group by session
    sessions = {}
    for event in events:
        session_id = event.session_id
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append(event)
    
    # Compute aggregates manually
    # ... hundreds of lines of aggregation logic ...
```

### 7.3 ❌ DON'T Re-implement Composite Metrics

```python
# ❌ BAD: Re-implementing composite metric logic
def calculate_composite_metrics(metrics: Dict[str, float]):
    """DON'T DO THIS - backend handles composite metrics!"""
    # This logic would need to:
    # - Match backend's composite metric formulas
    # - Stay in sync with backend changes
    # - Handle all edge cases
    # BAD IDEA!
    pass
```

---

## 8. Migration from Main Branch

### 8.1 Current Main Branch (Manual Aggregation)

**Current (wrong) approach:**
```python
# Main branch likely does this
results = []
for datapoint in dataset:
    result = evaluate_datapoint(datapoint)
    results.append(result)

# Compute stats manually
stats = {
    "total": len(results),
    "passed": len([r for r in results if r.passed]),
    "failed": len([r for r in results if not r.passed]),
    "average_score": sum(r.score for r in results) / len(results),
}

return EvaluationResult(
    run_id=run_id,
    stats=stats,
    data=results,
)
```

### 8.2 New Approach (Use Backend)

**New (correct) approach:**
```python
# 1. Create run
run = create_run(name="...", dataset_id="...")

# 2. Execute with tracer
for datapoint in dataset:
    tracer = HoneyHiveTracer(run_id=run.run_id, ...)
    evaluate_datapoint(datapoint, tracer)
    tracer.flush()

# 3. Update run status
update_run(run.run_id, status="completed")

# 4. Get aggregated results from backend
summary = get_run_result(run_id=run.run_id)

# summary contains:
# - overall stats
# - per-metric aggregates
# - per-datapoint results
# - pass/fail determination
# All computed by backend!
```

---

## 9. Implementation Checklist

### 9.1 Core Functions

- [ ] `get_run_result()` - Get aggregated summary
- [ ] `get_run_metrics()` - Get raw event metrics
- [ ] `compare_runs()` - Compare two runs
- [ ] `compare_run_events()` - Compare events side-by-side

### 9.2 Response Models

- [ ] `ExperimentResultSummary` - Aggregated results
- [ ] `AggregatedMetric` - Per-metric aggregates
- [ ] `DatapointResult` - Per-datapoint results
- [ ] `RunComparisonResult` - Run comparison
- [ ] `MetricComparison` - Metric-level comparison

### 9.3 Integration

- [ ] Use result endpoints in `run_experiment()`
- [ ] Remove any manual aggregation code
- [ ] Support all aggregation functions
- [ ] Support filters parameter
- [ ] Handle pagination for event comparisons

### 9.4 Documentation

- [ ] Document result endpoints
- [ ] Examples of using aggregation
- [ ] Examples of comparing runs
- [ ] Migration guide from manual aggregation

---

## 10. Example Usage

### 10.1 Complete Experiment with Results

```python
from honeyhive.experiments import run_experiment, get_experiment_results

# Run experiment
result = run_experiment(
    name="GPT-4 vs GPT-3.5",
    dataset=my_dataset,
    function=my_llm_function,
    evaluators=[accuracy, coherence, relevance],
    api_key=api_key,
    project="my-project",
)

# Get aggregated results (backend computes everything)
summary = get_experiment_results(
    run_id=result.run_id,
    aggregate_function="average",
)

# Print summary statistics
print(f"Overall Success: {summary.success}")
print(f"Total Datapoints: {len(summary.datapoints)}")
print(f"Passed: {len(summary.passed)}")
print(f"Failed: {len(summary.failed)}")

# Print per-metric results
for metric_key, metric in summary.metrics.items():
    print(f"\n{metric.metric_name} ({metric.event_name}):")
    print(f"  Average: {metric.aggregate:.2f}")
    print(f"  Values: {metric.values}")
    print(f"  Passed: {len(metric.datapoints.passed)}")
    print(f"  Failed: {len(metric.datapoints.failed)}")
```

### 10.2 Compare Two Runs

```python
from honeyhive.experiments import compare_runs

# Compare baseline vs new model
comparison = compare_runs(
    new_run_id="new-model-run",
    old_run_id="baseline-run",
    aggregate_function="average",
)

# Print comparison
print(f"Common Datapoints: {len(comparison.commonDatapoints)}")

for metric_comp in comparison.metrics:
    direction = "↑" if metric_comp.improved else "↓"
    print(f"\n{metric_comp.metric_name}:")
    print(f"  Old: {metric_comp.old_value:.2f}")
    print(f"  New: {metric_comp.new_value:.2f}")
    print(f"  Change: {direction} {metric_comp.delta:.2f} ({metric_comp.percent_change}%)")
```

---

## 11. Summary

### ✅ What SDK Should Do

1. **Create experiment runs** (POST /runs)
2. **Execute with tracer** (tracer sends events to backend)
3. **Update run status** (PUT /runs/:run_id)
4. **Fetch aggregated results** (GET /runs/:run_id/result)
5. **Compare runs** (GET /runs/:new/compare-with/:old)

### ❌ What SDK Should NOT Do

1. ~~Fetch all individual events~~
2. ~~Compute aggregates client-side~~
3. ~~Re-implement composite metrics~~
4. ~~Manually determine pass/fail~~
5. ~~Calculate deltas and percent changes~~

### 🎯 Key Benefit

**Backend does all the heavy lifting!**
- Better performance (database-side aggregation)
- Single source of truth
- Consistent logic
- Handles complex composite metrics
- Supports multiple aggregation functions

---

**Document Status:** ✅ COMPLETE - Result endpoints analyzed  
**Last Updated:** October 2, 2025  
**Critical Action:** Remove manual aggregation code, use backend endpoints

