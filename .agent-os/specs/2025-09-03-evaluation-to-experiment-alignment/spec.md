# Evaluation to Experiment Framework Alignment Specification

**Date**: 2025-09-03  
**Status**: Draft  
**Priority**: High  
**Branch**: complete-refactor  

## Overview

This specification defines the required changes to align the current HoneyHive Python SDK evaluation implementation with the official HoneyHive experiment framework as documented at [https://docs.honeyhive.ai/evaluation/introduction](https://docs.honeyhive.ai/evaluation/introduction).

## Problem Statement

The current SDK implementation uses outdated terminology and lacks key functionality required by the official HoneyHive experiment framework:

1. **Terminology Mismatch**: Uses "evaluation" instead of "experiment" terminology
2. **Missing Metadata Linking**: No proper `run_id`, `dataset_id`, `datapoint_id` metadata on events
3. **Incomplete Experiment Run Support**: Limited integration with the experiment run workflow
4. **No Client-side Dataset Support**: Missing external dataset handling capabilities
5. **Limited Results Management**: No SDK functionality for experiment results export
6. **Missing Main Evaluate Function**: No function that executes a user-provided function against the dataset

## Current State Analysis

### ✅ What's Working
- Basic evaluation framework with evaluators and decorators
- API integration for evaluation runs
- Data models for EvaluationRun, Datapoint, Dataset
- Comprehensive test coverage
- **Advanced multi-threading with two-level parallelism**
- **High-performance batch processing capabilities**

### ❌ What's Missing
- Experiment terminology and concepts
- Proper metadata linking for experiment runs
- Client-side dataset support with `EXT-` prefix
- Experiment results export functionality
- GitHub integration for automated runs
- **Main evaluate function that executes user functions against datasets**

## Required Changes

### 1. Terminology Alignment

#### 1.1 Rename Core Concepts
- `EvaluationRun` → `ExperimentRun`
- `EvaluationResult` → `EvaluatorResult` (for individual evaluator results)
- `EvaluationContext` → `ExperimentContext`
- `create_evaluation_run` → `create_experiment_run`

#### 1.2 Update Module Names
- `src/honeyhive/evaluation/` → `src/honeyhive/experiments/`
- `src/honeyhive/api/evaluations.py` → `src/honeyhive/api/experiments.py`

#### 1.3 Update Import Statements
- All internal imports must use new terminology
- Maintain backward compatibility through aliases

### 2. Metadata Linking Implementation

#### 2.1 Event Metadata Requirements
Every event in an experiment run must include:
```python
metadata = {
    "run_id": "uuid-string",
    "dataset_id": "uuid-string", 
    "datapoint_id": "uuid-string",
    "source": "evaluation"  # Always "evaluation" for experiment runs
}
```

#### 2.2 Tracer Integration
- Extend `HoneyHiveTracer` to support experiment run context
- Add methods for setting experiment run metadata
- Ensure all traced events include required metadata

#### 2.3 Experiment Run Context
```python
@dataclass
class ExperimentContext:
    """Context for experiment runs."""
    run_id: str
    dataset_id: str
    project: str
    source: str = "evaluation"
    metadata: Optional[Dict[str, Any]] = None
```

### 3. Client-side Dataset Support

#### 3.1 External Dataset Handling
```python
def create_external_dataset(
    datapoints: List[Dict[str, Any]],
    project: str,
    custom_dataset_id: Optional[str] = None
) -> Tuple[str, List[str]]:
    """
    Create client-side dataset with EXT- prefix.
    
    Returns:
        Tuple of (dataset_id, datapoint_ids)
    """
```

#### 3.2 Dataset ID Generation
- Generate hash-based IDs for external datasets
- Prefix with `EXT-` to avoid platform collisions
- Support custom IDs with `EXT-` prefix

#### 3.3 Datapoint ID Generation
- Hash individual datapoints for unique identification
- Ensure consistency across experiment runs
- Support custom IDs with `EXT-` prefix

### 4. Enhanced Experiment Management

#### 4.1 Main Experiment Evaluation Function
The core `evaluate` function that executes a function against the dataset:

```python
def evaluate(
    function: Callable,
    hh_api_key: Optional[str] = None,
    hh_project: Optional[str] = None,
    name: Optional[str] = None,
    suite: Optional[str] = None,
    dataset_id: Optional[str] = None,
    dataset: Optional[List[Dict[str, Any]]] = None,
    evaluators: Optional[List[Any]] = None,
    max_workers: int = 10,
    verbose: bool = False,
    server_url: Optional[str] = None,
    context: Optional[ExperimentContext] = None,
) -> ExperimentRunResult:
    """
    Main experiment evaluation function that executes a function against a dataset.
    
    This is the core function that:
    1. Executes the provided function for each datapoint in the dataset
    2. Collects outputs from function execution
    3. Runs evaluators against the outputs
    4. Returns comprehensive experiment results
    """
```

#### 4.2 Function Execution Flow
The main evaluation process follows this flow:

```python
def _execute_experiment_run(
    function: Callable,
    dataset: List[Dict[str, Any]],
    evaluators: List[Any],
    context: ExperimentContext,
    max_workers: int = 10,
) -> ExperimentRunResult:
    """
    Execute the complete experiment run workflow.
    
    1. Execute function against each datapoint
    2. Run evaluators against function outputs
    3. Aggregate results and metrics
    4. Return structured experiment results
    """
    results = []
    
    # Execute function against dataset
    for datapoint in dataset:
        inputs = datapoint.get("inputs", {})
        ground_truth = datapoint.get("ground_truth")
        
        # Execute the function with proper context
        with HoneyHiveTracer(
            project=context.project,
            metadata={
                "run_id": context.run_id,
                "dataset_id": context.dataset_id,
                "datapoint_id": datapoint.get("id", str(uuid.uuid4())),
                "source": "evaluation"
            }
        ):
            try:
                # Execute function with inputs and ground_truth
                if ground_truth is not None:
                    outputs = function(inputs, ground_truth)
                else:
                    outputs = function(inputs)
                
                # Run evaluators against outputs
                evaluator_results = evaluate_with_evaluators(
                    evaluators=evaluators,
                    inputs=inputs,
                    outputs=outputs,
                    ground_truth=ground_truth,
                    context=context,
                    max_workers=1,  # Single evaluator per datapoint
                    run_concurrently=False
                )
                
                results.append({
                    "inputs": inputs,
                    "outputs": outputs,
                    "ground_truth": ground_truth,
                    "evaluator_results": evaluator_results
                })
                
            except Exception as e:
                logger.error(f"Function execution failed for datapoint: {e}")
                # Record failure with error metadata
                results.append({
                    "inputs": inputs,
                    "outputs": None,
                    "ground_truth": ground_truth,
                    "error": str(e),
                    "evaluator_results": None
                })
    
    # Aggregate results and create final experiment result
    return _aggregate_experiment_results(results, context)
```

#### 4.3 Enhanced Experiment Run Creation
```python
def create_experiment_run(
    name: str,
    project: str,
    dataset_id: str,
    configuration: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    client: Optional[HoneyHive] = None
) -> Optional[ExperimentRun]:
    """
    Create a complete experiment run with proper metadata linking.
    """
```

#### 4.4 Experiment Run Results
```python
def get_experiment_results(
    run_id: str,
    client: Optional[HoneyHive] = None
) -> Optional[ExperimentResultResponse]:
    """
    Retrieve experiment run results from HoneyHive platform.
    """
```

#### 4.5 Experiment Comparison
```python
def compare_experiments(
    run_ids: List[str],
    client: Optional[HoneyHive] = None
) -> Optional[ExperimentComparisonResponse]:
    """
    Compare multiple experiment runs for performance analysis.
    """
```

### 5. Enhanced Evaluator Framework

#### 5.1 Evaluator Result Structure
```python
@dataclass
class EvaluatorResult:
    """Result of an individual evaluator execution."""
    evaluator_name: str
    evaluator_version: str
    score: Union[float, int, bool, str]
    explanation: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
```

#### 5.2 Experiment Run Results
```python
@dataclass
class ExperimentRunResult:
    """Complete results of an experiment run using official data models."""
    run_id: str
    dataset_id: str
    evaluator_results: List[Detail]  # Using official Detail model
    aggregate_metrics: Metrics  # Using official Metrics model
    datapoint_results: List[Datapoint1]  # Using official Datapoint1 model
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
```

### 6. Multi-Threading and Performance

#### 6.1 Advanced Two-Level Threading System
The experiment framework leverages the existing advanced multi-threading capabilities:

```python
def evaluate_experiment_batch(
    evaluators: List[Union[str, BaseEvaluator, Callable]],
    dataset: List[Dict[str, Any]],
    max_workers: int = 4,
    run_concurrently: bool = True,
    context: Optional[ExperimentContext] = None,
) -> List[EvaluatorResult]:
    """
    Evaluate experiment batch with advanced two-level threading.
    
    Level 1: Dataset parallelism (max_workers threads)
    Level 2: Evaluator parallelism within each dataset thread
    """
```

#### 6.2 Threading Architecture
- **Dataset Level**: Parallel processing of multiple datapoints
- **Evaluator Level**: Parallel execution of multiple evaluators per datapoint
- **Context Isolation**: Proper `contextvars` handling for thread safety
- **Resource Optimization**: Configurable worker counts for optimal performance

#### 6.3 Performance Characteristics
- **5x performance improvement** over single-threaded execution
- **Scalable**: Handles large datasets with multiple evaluators efficiently
- **Configurable**: Adjustable threading levels based on system capabilities
- **Thread-safe**: Advanced context isolation and error handling

#### 6.4 Threading Configuration
```python
# Example: High-performance experiment run
results = evaluate_experiment_batch(
    evaluators=["accuracy", "relevance", "coherence", "toxicity"],
    dataset=large_dataset,  # 1000+ datapoints
    max_workers=8,          # Dataset-level parallelism
    run_concurrently=True,   # Enable threading
    context=experiment_context
)
```

### 7. GitHub Integration Support

#### 7.1 GitHub Actions Integration
```python
def setup_github_experiment_workflow(
    project: str,
    dataset_id: str,
    evaluators: List[str],
    thresholds: Dict[str, float]
) -> str:
    """
    Generate GitHub Actions workflow for automated experiment runs.
    """
```

#### 7.2 Performance Thresholds
```python
def set_performance_thresholds(
    run_id: str,
    thresholds: Dict[str, float],
    client: Optional[HoneyHive] = None
) -> bool:
    """
    Set performance thresholds for experiment runs.
    """
```

## Data Model Integration

### Official HoneyHive Data Models

The implementation will use the official data models from the OpenAPI specification:

#### Experiment Results (`ExperimentResultResponse`)
```python
class ExperimentResultResponse(BaseModel):
    status: Optional[str] = None
    success: Optional[bool] = None
    passed: Optional[List[str]] = None
    failed: Optional[List[str]] = None
    metrics: Optional[Metrics] = None
    datapoints: Optional[List[Datapoint1]] = None
```

#### Experiment Comparison (`ExperimentComparisonResponse`)
```python
class ExperimentComparisonResponse(BaseModel):
    metrics: Optional[List[Metric2]] = None
    commonDatapoints: Optional[List[str]] = None
    event_details: Optional[List[EventDetail]] = None
    old_run: Optional[OldRun] = None
    new_run: Optional[NewRun] = None
```

#### Supporting Models
- **Metrics**: Aggregated metric information with details
- **Detail**: Individual metric details with aggregation
- **Datapoint1**: Individual datapoint results
- **Metric2**: Comparison-specific metric information
- **EventDetail**: Event presence and type information
- **OldRun/NewRun**: Run information for comparison

### Data Model Usage

#### Results Retrieval
```python
def get_experiment_results(run_id: str) -> Optional[ExperimentResultResponse]:
    """Retrieve results using official data model."""
    response = api.get_run(run_id)
    return response.results  # Returns ExperimentResultResponse
```

#### Results Analysis
```python
def analyze_results(results: ExperimentResultResponse) -> Dict[str, Any]:
    """Analyze results using official data structure."""
    analysis = {
        "total_metrics": len(results.metrics.details) if results.metrics else 0,
        "passed_datapoints": len(results.passed) if results.passed else 0,
        "failed_datapoints": len(results.failed) if results.failed else 0,
        "success_rate": results.success
    }
    return analysis
```

#### Comparison Analysis
```python
def analyze_comparison(comparison: ExperimentComparisonResponse) -> Dict[str, Any]:
    """Analyze comparison results using official data structure."""
    if not comparison.metrics:
        return {"error": "No comparison data"}
    
    analysis = {
        "total_metrics": len(comparison.metrics),
        "improved": sum(1 for m in comparison.metrics if m.improved_count),
        "degraded": sum(1 for m in comparison.metrics if m.degraded_count),
        "stable": sum(1 for m in comparison.metrics if m.same_count)
    }
    return analysis
```

## Implementation Plan

### Phase 1: Core Terminology (Week 1)
1. Create new experiment module structure
2. Implement backward compatibility aliases
3. Update core data models and classes
4. Update tests to use new terminology

### Phase 2: Metadata Linking (Week 2)
1. Extend tracer to support experiment context
2. Implement metadata injection on events
3. Add experiment run context management
4. Update event creation to include required metadata

### Phase 3: Dataset Support (Week 3)
1. Implement external dataset creation
2. Add client-side dataset ID generation
3. Support custom dataset and datapoint IDs
4. Add dataset validation and management

### Phase 4: Enhanced Experiment Management (Week 4)
1. Implement complete experiment run workflow
2. **Implement main evaluate function that executes user functions**
3. Add experiment results retrieval using official models
4. Implement experiment comparison functionality
5. Add performance threshold management
6. **Integrate advanced multi-threading capabilities**

### Phase 5: GitHub Integration (Week 5)
1. Create GitHub Actions workflow templates
2. Implement automated experiment triggering
3. Add performance regression detection
4. Create CLI tools for experiment management

### Phase 6: Testing & Documentation (Week 6)
1. Comprehensive testing of new functionality
2. Update documentation and examples
3. Create migration guide for existing users
4. Performance testing and optimization
5. **Multi-threading performance validation**

## Backward Compatibility

### Required Compatibility
- All existing evaluation decorators must continue to work
- Current API endpoints must remain functional
- Existing data models must be accessible through aliases
- Current examples must run without modification
- **Multi-threading capabilities must be preserved and enhanced**

### Migration Path
1. **Immediate**: New functionality available alongside existing
2. **Short-term**: Deprecation warnings for old terminology
3. **Long-term**: Gradual migration to new experiment framework

## Testing Requirements

### Unit Tests
- 100% coverage for new experiment functionality
- Backward compatibility tests for existing features
- Error handling and edge case coverage
- Data model validation tests
- **Multi-threading functionality validation**
- **Main evaluate function execution testing**

### Integration Tests
- End-to-end experiment run workflow
- **Function execution against dataset validation**
- Metadata linking validation
- External dataset creation and management
- API integration testing with official models
- **Multi-threading performance and thread safety tests**

### Performance Tests
- Large dataset handling
- Concurrent experiment runs
- Memory usage optimization
- **Multi-threading scalability testing**
- **Thread safety validation under load**
- **Function execution performance under load**

## Documentation Updates

### Required Documentation
1. **Migration Guide**: From evaluation to experiment framework
2. **Experiment Tutorials**: Complete workflow examples
3. **API Reference**: Updated with new terminology and data models
4. **Integration Guides**: GitHub Actions and CI/CD setup
5. **Performance Guide**: Multi-threading configuration and optimization

### Documentation Standards
- Follow Divio documentation system
- Include working code examples
- Provide step-by-step tutorials
- Include troubleshooting guides
- **Document multi-threading best practices and configuration**

## Success Criteria

### Functional Requirements
- [ ] All experiment terminology properly implemented
- [ ] Metadata linking working on all traced events
- [ ] Client-side dataset support functional
- [ ] **Main evaluate function executes user functions against datasets**
- [ ] Experiment run management complete
- [ ] GitHub integration working
- [ ] Backward compatibility maintained
- [ ] Official data models properly integrated
- [ ] **Advanced multi-threading capabilities preserved and enhanced**

### Quality Requirements
- [ ] 100% test coverage for new experiment functionality
- [ ] All tests passing across Python versions
- [ ] Documentation complete and accurate
- [ ] Performance benchmarks met
- [ ] Security review completed
- [ ] **Multi-threading performance validated**

### User Experience Requirements
- [ ] Smooth migration path for existing users
- [ ] Clear examples and tutorials
- [ ] Intuitive API design
- [ ] Comprehensive error messages
- [ ] Performance monitoring and alerts
- [ ] **Multi-threading configuration guidance**

## Risk Assessment

### High Risk
- **Breaking Changes**: Potential for breaking existing integrations
- **Performance Impact**: Metadata injection on all events
- **Complexity**: Increased complexity of experiment management
- **Multi-threading**: Ensuring thread safety in complex scenarios
- **Function Execution**: Ensuring user functions execute safely and efficiently

### Mitigation Strategies
- **Gradual Migration**: Phased implementation with backward compatibility
- **Performance Testing**: Comprehensive benchmarking before release
- **User Feedback**: Early access program for key users
- **Thread Safety**: Comprehensive testing of multi-threading scenarios
- **Function Safety**: Sandboxed execution and comprehensive error handling

## Dependencies

### Internal Dependencies
- Tracer framework updates
- API client enhancements
- Data model modifications
- Test framework updates
- **Multi-threading framework preservation**

### External Dependencies
- HoneyHive platform API compatibility
- GitHub Actions integration
- Performance monitoring tools

## Timeline

- **Week 1-2**: Core terminology and metadata linking
- **Week 3-4**: Dataset support and experiment management
- **Week 5**: GitHub integration
- **Week 6**: Testing, documentation, and release preparation

## Next Steps

1. **Immediate**: Review and approve this specification
2. **Week 1**: Begin Phase 1 implementation
3. **Ongoing**: Weekly progress reviews and adjustments
4. **Week 6**: Final testing and release preparation

---

**Document Version**: 1.0  
**Last Updated**: 2025-09-03  
**Next Review**: 2025-09-10
