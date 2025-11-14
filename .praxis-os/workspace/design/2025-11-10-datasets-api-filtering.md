# DatasetsAPI Filtering Enhancement

**Date**: 2025-11-10  
**Status**: ⚠️ **PARTIAL - Completed Over Weekend**  
**Type**: API Enhancement (Non-Breaking)  
**Scope**: Small - Parameter Passthrough  
**Effort**: 1-1.5 hours (reduced from 2-3 hours)  

---

## Problem Statement

Customer reported that `DatasetsAPI.list_datasets()` lacks filtering capabilities that the backend already supports, making it inefficient to find specific datasets as projects grow.

**Customer Feedback**:
> "For now, projects will likely have less than 100 datasets, but once projects grow, if the team decides to keep datasets for historical purposes, it will become inefficient to paginate and iterate through all of the datasets searching for the one you are looking for."

---

## 🎉 Weekend Progress Update

**Team made significant progress over the weekend!**

The following filtering capabilities were **already implemented**:
- ✅ `dataset_type: Optional[Literal["evaluation", "fine-tuning"]]` - Filter by dataset type
- ✅ `dataset_id: Optional[str]` - Filter by specific dataset ID

**This leaves only 2 parameters to complete the feature:**
- ❌ `name: Optional[str]` - Filter by dataset name
- ❌ `include_datapoints: bool` - Include datapoints in response

**Impact**: Reduced implementation effort from ~2-3 hours to ~1-1.5 hours.

---

## Current State (After Weekend Changes)

### SDK Implementation (Updated 2025-11-10)
```python
# src/honeyhive/api/datasets.py (lines 138-168)
def list_datasets(
    self,
    project: Optional[str] = None,
    dataset_type: Optional[Literal["evaluation", "fine-tuning"]] = None,  # ✅ ADDED
    dataset_id: Optional[str] = None,  # ✅ ADDED
    limit: int = 100,
) -> List[Dataset]:
    """List datasets with optional filtering."""
    params = {"limit": str(limit)}
    if project:
        params["project"] = project
    if dataset_type:
        params["type"] = dataset_type  # ✅ ADDED
    if dataset_id:
        params["dataset_id"] = dataset_id  # ✅ ADDED
    
    response = self.client.request("GET", "/datasets", params=params)
    data = response.json()
    return self._process_data_dynamically(
        data.get("testcases", []), Dataset, "testcases"
    )
```

### Backend Capabilities
```typescript
// backend_service/app/routes/dataset.route.ts (lines 50, 83-89)
const { project, dataset_id, name, include_datapoints } = validatedQuery.data;

const datasets = await service.dataset_datapoint.getDatasets(
    orgId,
    projectId,
    dataset_id,  // ✅ NOW exposed in SDK
    name,        // ❌ STILL NOT exposed in SDK
    tx,
);
```

### Gap Analysis

| Parameter | Backend | SDK (Before) | SDK (After Weekend) | Still Missing? |
|-----------|---------|--------------|---------------------|----------------|
| `project` | ✅ | ✅ | ✅ | No |
| `type` (dataset_type) | ✅ | ❌ | ✅ | **No - DONE** |
| `dataset_id` | ✅ | ❌ | ✅ | **No - DONE** |
| `name` | ✅ | ❌ | ❌ | **YES** |
| `include_datapoints` | ✅ | ❌ | ❌ | **YES** |
| `limit` | ✅ | ✅ | ✅ | No |

**Remaining work:**
- ❌ `name` - Filter by dataset name (exact match)
- ❌ `include_datapoints` - Include datapoints in response (performance optimization)

---

## Proposed Solution

### Add Remaining Parameters to SDK

Complete the filtering implementation by adding the 2 missing parameters:

**Target Signature (After This Work):**
```python
def list_datasets(
    self,
    project: Optional[str] = None,
    dataset_type: Optional[Literal["evaluation", "fine-tuning"]] = None,  # ✅ Already done
    dataset_id: Optional[str] = None,      # ✅ Already done
    name: Optional[str] = None,            # ❌ TODO - ADD THIS
    include_datapoints: bool = False,      # ❌ TODO - ADD THIS
    limit: int = 100,
) -> List[Dataset]:
    """List datasets with optional filtering.
    
    Args:
        project: Filter by project name or ID
        dataset_type: Type of dataset - "evaluation" or "fine-tuning"
        dataset_id: Filter by specific dataset ID (returns single dataset if found)
        name: Filter by dataset name (exact match)
        include_datapoints: Include datapoints in response (may impact performance)
        limit: Maximum number of datasets to return
    
    Returns:
        List of Dataset objects matching the filters
    
    Example:
        # Find dataset by name
        datasets = datasets_api.list_datasets(
            project="My Project",
            name="Training Data Q4",
        )
        
        # Get specific dataset with datapoints
        datasets = datasets_api.list_datasets(
            dataset_id="663876ec4611c47f4970f0c3",
            include_datapoints=True
        )
    """
    params = {"limit": str(limit)}
    if project:
        params["project"] = project
    if dataset_type:
        params["type"] = dataset_type
    if dataset_id:
        params["dataset_id"] = dataset_id
    if name:                                    # ← ADD THIS
        params["name"] = name                   # ← ADD THIS
    if include_datapoints:                      # ← ADD THIS
        params["include_datapoints"] = str(include_datapoints).lower()  # ← ADD THIS
    
    response = self.client.request("GET", "/datasets", params=params)
    data = response.json()
    return self._process_data_dynamically(
        data.get("testcases", []), Dataset, "testcases"
    )
```

### Changes Required

**Only 2 parameters left to add:**
1. `name: Optional[str] = None` - for filtering by dataset name
2. `include_datapoints: bool = False` - for including datapoints in response

**Files to modify:**
- `src/honeyhive/api/datasets.py`: Update `list_datasets()` and `list_datasets_async()`

---

## Implementation Plan (Updated - Reduced Scope)

### 1. Code Changes (15-20 mins)

**Files to Modify:**
- `src/honeyhive/api/datasets.py`
  - Update `list_datasets()` signature (lines 138-168)
  - Update `list_datasets_async()` signature (lines 170-200)
  - Add parameter handling logic for `name` and `include_datapoints`
  - Update docstrings with examples

**Changes Required:**
- Add 2 new optional parameters to both methods (`name`, `include_datapoints`)
- Add parameter→query param mapping (4 lines of code)
- Update method docstrings with new parameters
- Add usage examples in docstrings

### 2. Unit Tests (20-30 mins)

**File**: `tests/unit/api/test_datasets.py`

**Test Cases to Add:**
```python
def test_list_datasets_with_name():
    """Test filtering by name"""
    # Verify name parameter is passed to backend
    
def test_list_datasets_with_include_datapoints():
    """Test include_datapoints parameter"""
    # Verify boolean is converted to string ("true"/"false")
    
def test_list_datasets_with_all_filters():
    """Test combining all filters including new ones"""
    # Verify all parameters work together (project, dataset_type, dataset_id, name, include_datapoints)
    
def test_list_datasets_async_with_new_filters():
    """Test async version with new filters"""
    # Verify async version has same behavior for name and include_datapoints
```

### 3. Integration Tests (20-30 mins)

**File**: `tests/integration/api/test_datasets_integration.py`

**Test Cases to Add:**
```python
@pytest.mark.integration
def test_list_datasets_filter_by_name_real_api():
    """Test name filtering with real backend"""
    # Create dataset with known name
    # Filter by name
    # Verify correct dataset returned

@pytest.mark.integration
def test_list_datasets_include_datapoints_real_api():
    """Test include_datapoints with real backend"""
    # Create dataset with datapoints
    # Query with include_datapoints=True
    # Verify datapoints present in response
    # Query with include_datapoints=False
    # Verify datapoints not included
```

**Note**: `dataset_id` filtering should already have tests from weekend implementation.

### 4. Documentation Updates (10-15 mins)

**Files to Update:**
- API method docstrings (inline, done during code changes)
- API reference docs (auto-generated from docstrings)
- Update `CHANGELOG.md` with enhancement note

**Documentation Examples to Add:**
```python
# Example 1: Find dataset by name
datasets = client.datasets.list_datasets(
    project="My Project",
    name="Training Data Q4 2024"
)

# Example 2: Get dataset with datapoints (efficient single query)
dataset_with_data = client.datasets.list_datasets(
    dataset_id="663876ec4611c47f4970f0c3",
    include_datapoints=True
)[0]

# Example 3: Filter by type and name
evaluation_datasets = client.datasets.list_datasets(
    dataset_type="evaluation",
    name="Regression Tests"
)
```

---

## Testing Strategy

### Unit Tests (Mocked Backend)
- ✅ Verify parameters are passed correctly
- ✅ Verify boolean→string conversion for `include_datapoints`
- ✅ Verify backward compatibility (no params = current behavior)
- ✅ Verify async version matches sync behavior

### Integration Tests (Real Backend)
- ✅ Test filtering actually works against backend
- ✅ Test each parameter independently
- ✅ Test parameter combinations
- ✅ Verify `include_datapoints` affects response

### Manual Testing
- Test against actual HoneyHive API
- Verify performance with `include_datapoints`
- Test edge cases (empty results, special characters in names)

---

## Backward Compatibility

**✅ FULLY BACKWARD COMPATIBLE**

Weekend changes already added optional parameters, and this work continues that pattern:
- ✅ Already added: `dataset_type: Optional[Literal["evaluation", "fine-tuning"]] = None`
- ✅ Already added: `dataset_id: Optional[str] = None`
- ❌ To add: `name: Optional[str] = None`
- ❌ To add: `include_datapoints: bool = False`

Existing code will continue to work without changes:
```python
# Old code (before weekend, still works)
datasets = client.datasets.list_datasets(project="My Project")

# Weekend code (still works)
datasets = client.datasets.list_datasets(
    project="My Project",
    dataset_type="evaluation"
)

# This PR (fully compatible, just adds more options)
datasets = client.datasets.list_datasets(
    project="My Project",
    dataset_type="evaluation",
    name="Specific Dataset"
)
```

---

## OpenAPI Spec Verification

**Check if OpenAPI needs updating:**
```bash
grep -A 20 "/datasets" openapi.yaml
```

**Backend endpoint**: `GET /datasets`  
**Expected query params**: `project`, `dataset_id`, `name`, `include_datapoints`, `limit`

If OpenAPI spec doesn't document these params, consider updating it for completeness (separate task, not blocking).

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Backend params not working as documented | High | Integration tests will catch this |
| Boolean→string conversion incorrect | Medium | Unit tests verify conversion logic |
| Performance impact with `include_datapoints` | Low | Document performance consideration |
| Name filtering case-sensitivity | Low | Document exact match behavior |

---

## Success Criteria

- [ ] `list_datasets()` accepts and passes `name` and `include_datapoints` parameters
- [ ] `list_datasets_async()` has identical signature and behavior
- [ ] All unit tests pass (mocked backend)
  - [ ] Test `name` parameter
  - [ ] Test `include_datapoints` parameter (boolean→string conversion)
  - [ ] Test all filters combined
- [ ] All integration tests pass (real backend)
  - [ ] Verify `name` filtering works
  - [ ] Verify `include_datapoints` affects response
- [ ] Docstrings include clear usage examples
- [ ] Backward compatibility maintained (existing code works)
- [ ] `CHANGELOG.md` updated with enhancement
- [ ] Code review approved
- [ ] Customer informed of complete filtering solution

---

## Implementation Order

1. **Code changes** (add `name` and `include_datapoints` to sync + async methods)
2. **Unit tests** (verify parameter passing and boolean conversion)
3. **Integration tests** (verify backend filtering works)
4. **Run full test suite** (ensure no regressions)
5. **Update CHANGELOG.md**
6. **Manual verification** (optional, test against real API)

**Total Estimated Time**: 1-1.5 hours (reduced from original 2-3 hours due to weekend progress)

---

## Customer Communication

After implementation, respond to customer with:

1. ✅ **Acknowledge the issue**: "You're right, the SDK wasn't exposing all backend filtering capabilities"
2. ✅ **Highlight weekend progress**: "Good news - we've already added `dataset_type` and `dataset_id` filtering"
3. ✅ **Explain the remaining fix**: "We're completing the work by adding `name` and `include_datapoints` parameters"
4. ✅ **Show examples**: Provide code examples of all new filtering options
5. ✅ **Timeline**: Let them know when it's available (version)

---

## Follow-Up Tasks (Optional)

- Update OpenAPI spec if parameters not documented
- Add similar filtering to other list methods if customer requests
- Document common filtering patterns in user guide
- Consider adding pagination support if datasets exceed limits

---

## Notes

- **Weekend Update (2025-11-10)**: Team already implemented `dataset_type` and `dataset_id` filtering
- Backend code confirmed in: `backend_service/app/routes/dataset.route.ts` lines 50, 83-89
- Backend schema: `GetDatasetsQuerySchema` (line 42) - validates all params
- Remaining parameters (`name`, `include_datapoints`) follow the same pattern
- All parameters are optional → safe, non-breaking change
- Simple parameter passthrough → low complexity, high value
- This work completes the filtering feature started over the weekend

