# V3 Framework Analysis: test_managed_dataset_evaluation

**Test ID**: REL-001  
**Test Path**: Integration  
**Target**: `tests/integration/test_experiments_integration.py`  
**Feature**: Upload dataset via SDK and run experiment with managed HoneyHive dataset

---

## 📋 **V3 Framework Acknowledgment**

✅ I acknowledge the V3 Framework binding contract:
- I will follow ALL 8 phases systematically
- I will NOT skip steps or claim premature completion
- I will provide quantified evidence for each phase
- I will achieve 100% pass rate + integration functional coverage
- I will use real API calls with backend verification

**Path**: Integration  
**Strategy**: Real API usage with backend verification  
**Fixtures**: `real_api_key`, `real_project`, `integration_client`, `verify_backend_event`

---

## Phase 1: Method Verification

### Components to Test

#### 1. **Dataset Upload API** (`src/honeyhive/api/datasets.py`)
- **Method**: `create_dataset(request: CreateDatasetRequest) -> Dataset`
- **Purpose**: Create a new dataset in HoneyHive platform
- **Backend Endpoint**: `POST /datasets`
- **Response Handling**: Supports both legacy and new format with `insertedId`

#### 2. **Datapoint Creation API** (`src/honeyhive/api/datapoints.py`)
- **Method**: `create_datapoint(request: CreateDatapointRequest) -> Datapoint`
- **Purpose**: Add datapoints to a dataset
- **Backend Endpoint**: `POST /datapoints`
- **Required Fields**: `inputs`, `ground_truth`, `linked_datasets` (to link to dataset)

#### 3. **Dataset Fetching** (`src/honeyhive/api/datasets.py`)
- **Method**: `list_datasets(project: Optional[str], limit: int) -> List[Dataset]`
- **Purpose**: Verify dataset was created
- **Backend Endpoint**: `GET /datasets`
- **Note**: Returns `testcases` key in response

#### 4. **Datapoints Fetching** (`src/honeyhive/api/datapoints.py`)
- **Method**: `list_datapoints(dataset_id: str) -> List[Datapoint]`
- **Purpose**: Fetch datapoints for evaluation
- **Backend Endpoint**: `GET /datapoints?dataset_id={dataset_id}`

#### 5. **Experiment Execution** (`src/honeyhive/experiments/core.py`)
- **Method**: `evaluate(function, dataset_id, evaluators, api_key, project, name, ...)`
- **Purpose**: Run experiment using managed dataset
- **Key Parameter**: `dataset_id` (instead of `dataset` list)

### Quantified Analysis

**Total API Methods**: 5 core methods
**Backend Endpoints**: 4 unique endpoints
- `POST /datasets` - dataset creation
- `POST /datapoints` - datapoint creation  
- `GET /datasets` - dataset list/verification
- `GET /datapoints` - datapoint fetching

**Generated Models Used**:
- `CreateDatasetRequest`
- `Dataset`
- `CreateDatapointRequest`
- `Datapoint`

---

## Phase 2: Logging Analysis

### Logging Points

1. **Dataset Creation**:
   - Client logs via `safe_log` in base client
   - API request/response logging
   
2. **Datapoint Creation**:
   - Batch creation logging (if multiple datapoints)
   - Individual datapoint confirmation

3. **Experiment Execution**:
   - Run initialization logging
   - Dataset fetch logging (`verbose=True`)
   - Datapoint processing logs
   - Session creation logs
   - Evaluator execution logs

### Logging Strategy for Test

**Test Logging Level**: `verbose=True` for `evaluate()`
**Verification**: Console output validation for key steps
**Assertions**: Backend state validation (not just logs)

---

## Phase 3: Dependency Analysis

### External Dependencies (Real APIs - Integration Path)

1. **HoneyHive Backend**:
   - Dataset creation endpoint
   - Datapoint creation endpoint
   - Experiment run endpoints
   - Event/session endpoints

2. **Network Layer**:
   - `httpx` for HTTP requests
   - Real network calls (no mocking)

3. **Authentication**:
   - Real API key from `real_api_key` fixture
   - Real project from `real_project` fixture

### Internal Dependencies

1. **`honeyhive.experiments.evaluate`**:
   - Depends on: `HoneyHive` client
   - Depends on: `DatasetsAPI`, `DatapointsAPI`
   - Depends on: `EvaluationsAPI`
   - Depends on: `HoneyHiveTracer`

2. **`HoneyHive` client**:
   - Initialization with API key
   - Multiple API modules

### Mocking Strategy

❌ **NO MOCKING** (Integration Path)
✅ **Real Backend Verification** using `verify_backend_event` if needed
✅ **Backend State Validation** via GET endpoints

---

## Phase 4: Usage Pattern Analysis

### Test Flow

```python
# Step 1: Setup - Create dataset in HoneyHive
dataset_request = CreateDatasetRequest(
    project=real_project,
    name=f"integration-test-dataset-{timestamp}",
    description="Test dataset for managed evaluation"
)
created_dataset = integration_client.datasets.create_dataset(dataset_request)
dataset_id = created_dataset._id  # Get the ID

# Step 2: Add datapoints to dataset
for datapoint_data in test_datapoints:
    datapoint_request = CreateDatapointRequest(
        inputs=datapoint_data["inputs"],
        ground_truth=datapoint_data["ground_truth"],
        linked_datasets=[dataset_id],  # Link to our dataset
        project=real_project
    )
    integration_client.datapoints.create_datapoint(datapoint_request)

# Step 3: Verify dataset has datapoints
datapoints = integration_client.datapoints.list_datapoints(dataset_id=dataset_id)
assert len(datapoints) == len(test_datapoints)

# Step 4: Run experiment using dataset_id
result = evaluate(
    function=test_function,
    dataset_id=dataset_id,  # Use managed dataset
    evaluators=[test_evaluator],
    api_key=real_api_key,
    project=real_project,
    name=f"managed-dataset-test-{timestamp}",
    verbose=True
)

# Step 5: Validate results
assert result is not None
assert result.run_id
assert result.status == "completed"

# Step 6: Verify backend state
backend_run = integration_client.evaluations.get_run(result.run_id)
assert backend_run.evaluation.dataset_id == dataset_id
assert len(backend_run.evaluation.event_ids) == len(test_datapoints)

# Step 7: Cleanup
integration_client.datasets.delete_dataset(dataset_id)
```

### Error Paths

1. Dataset creation fails → Test fails with clear error
2. Datapoint creation fails → Test fails with clear error
3. evaluate() with invalid dataset_id → Should raise error
4. Backend verification fails → Test fails with diagnostic info

---

## Phase 5: Coverage Analysis

### Functional Coverage (Integration Test)

**Critical Paths**:
- ✅ Dataset creation via SDK
- ✅ Datapoint addition to dataset
- ✅ Dataset-datapoint linkage
- ✅ Experiment execution with `dataset_id`
- ✅ Datapoint fetching from managed dataset
- ✅ Backend run-dataset association
- ✅ Event-dataset-datapoint linkage

**Edge Cases**:
- Empty dataset (no datapoints)
- Large dataset (10+ datapoints for performance)
- Dataset with complex inputs/ground_truth
- Cleanup/teardown validation

**Not Covered** (Out of Scope):
- Line/branch coverage percentages (unit test concern)
- Dataset versioning
- Dataset sharing across projects
- Concurrent dataset access

---

## Phase 6: Pre-Generation Validation

### Test Prerequisites

✅ **Fixtures Available**:
- `real_api_key`: pytest fixture for API authentication
- `real_project`: pytest fixture for project context
- `integration_client`: pytest fixture for `HoneyHive` client instance
- `verify_backend_event`: pytest fixture for backend state validation (if needed)

✅ **Generated Models Available**:
- `CreateDatasetRequest` from `honeyhive.models`
- `CreateDatapointRequest` from `honeyhive.models`
- `Dataset` from `honeyhive.models`
- `Datapoint` from `honeyhive.models`

✅ **API Methods Available**:
- `client.datasets.create_dataset()`
- `client.datapoints.create_datapoint()`
- `client.datasets.list_datasets()`
- `client.datapoints.list_datapoints()`
- `client.datasets.delete_dataset()`
- `client.evaluations.get_run()`

✅ **Integration Path Requirements**:
- Real API calls: Yes
- Backend verification: Yes (via `get_run()`)
- Cleanup strategy: Delete dataset in teardown

### Pylint Disables Required

```python
# pylint: disable=protected-access,redefined-outer-name,too-many-locals
```

**Justification**:
- `protected-access`: May need to access `_id` from Dataset/Datapoint models
- `redefined-outer-name`: pytest fixtures (standard pattern)
- `too-many-locals`: Integration tests often have many setup variables

---

## Phase 7: Test Generation

### Test Structure

```python
@pytest.mark.integration
@pytest.mark.real_api
@pytest.mark.skipif(
    os.environ.get("HH_SOURCE", "").startswith("github-actions"),
    reason="Requires write permissions not available in CI",
)
class TestExperimentsIntegration:
    """Integration tests for experiments module with real API validation."""
    
    def test_managed_dataset_evaluation(
        self,
        real_api_key: str,
        real_project: str,
        integration_client: HoneyHive,
    ) -> None:
        """Test evaluate() with managed HoneyHive dataset.
        
        This test validates:
        1. Dataset creation via SDK
        2. Datapoint addition to dataset
        3. Experiment execution with dataset_id parameter
        4. Backend verification of dataset-run linkage
        5. Datapoint fetching and processing
        6. Proper cleanup/teardown
        """
        # [Implementation follows Phase 4 flow]
```

---

## Phase 8: Quality Validation

### Success Criteria

**Test Execution**:
- ✅ Test passes with 100% success rate
- ✅ Real API calls execute successfully
- ✅ Backend state verified correctly
- ✅ Cleanup completes without errors

**Backend Validation**:
- ✅ Dataset created in HoneyHive platform
- ✅ Datapoints linked to dataset
- ✅ Run associated with dataset_id
- ✅ Events created for each datapoint
- ✅ Dataset deleted successfully (teardown)

**Code Quality**:
- ✅ Pylint: No new violations (approved disables used)
- ✅ Black: Formatting compliant
- ✅ MyPy: No type errors

### Validation Command

```bash
# Run the specific test
pytest tests/integration/test_experiments_integration.py::TestExperimentsIntegration::test_managed_dataset_evaluation -v -s --real-api

# Verify no linter issues
pylint tests/integration/test_experiments_integration.py

# Verify formatting
black --check tests/integration/test_experiments_integration.py
```

---

**Status**: ✅ Analysis Complete - Ready for Implementation  
**Next Step**: Generate test code following Phase 7 structure

