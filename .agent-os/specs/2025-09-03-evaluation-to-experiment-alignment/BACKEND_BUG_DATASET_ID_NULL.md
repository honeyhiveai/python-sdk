# Backend Bug: Managed Dataset ID Returns Null

**Discovered**: 2025-10-02  
**Severity**: Medium (Workaround exists - sessions have dataset_id in metadata)  
**Component**: Backend - Experiment Run Service  
**Status**: Needs Investigation

---

## 🐛 **Issue Summary**

When creating an experiment run with a managed HoneyHive dataset, the SDK correctly sends `dataset_id` and `datapoint_ids` to the backend, but the backend returns `dataset_id: null` in the GET response.

**Impact**:
- Run object shows `dataset_id: null` in platform UI
- Session metadata correctly includes `dataset_id` (experiments still work)
- Dataset linkage appears broken in run view
- Comparison workflows work because they use session metadata

---

## 📊 **Evidence**

### **SDK Sends Correct Data** ✅

**POST /runs Request** (from integration test logs):
```json
{
    "run": {
        "project": "strands-test",
        "name": "managed-dataset-test-1759435583",
        "event_ids": [],
        "dataset_id": "yg7t2FIRhe3Zw3zfsWAlXx_W",  // ✅ Correct managed dataset ID
        "datapoint_ids": [
            "dH85xeEXkIUUYlmwNCtPhYiy",
            "Qy3TskEMgF2U-I1znBhLR8gr",
            "vLG2Br-NQXchG-KfM9geZ7gg"
        ],
        "configuration": {...},
        "metadata": {},  // Empty (not EXT- dataset)
        "status": "pending"
    }
}
```

**Verification**:
- Dataset ID `yg7t2FIRhe3Zw3zfsWAlXx_W` exists (created via POST /datasets)
- Dataset ID matches Prisma `dataset.id` field (confirmed by user)
- Datapoint IDs are valid and linked to the dataset

### **Backend Returns Null** ❌

**GET /runs/:run_id Response** (from platform UI):
```json
{
    "id": "-D8R-BeVUwFnUm9YqZDpja_A",
    "run_id": "e52ad928-91fd-4500-9dd8-062d346863a6",
    "name": "managed-dataset-test-1759434199",
    "status": "completed",
    "dataset_id": null,  // ❌ Should be the dataset ID we sent
    "metadata": {
        "datapoint_ids": [  // ⚠️ Moved to metadata instead of top-level
            "0t2p7aEI38dfMC7RRFFCAx33",
            "BKaCfpfypmClc4s-48Lo4AVv",
            "k0h7rmZ2gplykSxMUJblqKtD"
        ],
        "evaluator_metrics": {...}
    },
    "event_ids": [...]
}
```

**What's Wrong**:
1. `dataset_id` is `null` (should be `yg7t2FIRhe3Zw3zfsWAlXx_W`)
2. `datapoint_ids` moved to `metadata` (should be top-level field)

---

## 🔍 **Backend Code Analysis**

### **createExperimentRun Service** (experiment_run.service.ts)

**Lines 50-58**: EXT- transformation (WORKING CORRECTLY)
```typescript
// Handle offline datasets
let datasetId = data.dataset_id;
const datasetMetadata = data.metadata || {};
if (datasetId?.startsWith('EXT-')) {
    datasetMetadata.offline_dataset_id = datasetId;
    datasetId = undefined;  // Clear for EXT- to avoid FK error
}
// For non-EXT- datasets: datasetId remains unchanged ✅
```

**Lines 60-74**: Prisma create (LOOKS CORRECT)
```typescript
const experimentRun = await tx.experimentRun.create({
    data: {
        run_id: runId,
        name: data.name,
        dataset_id: datasetId,  // ✅ Should save for managed datasets
        event_ids: data.event_ids || [],
        // ❌ MISSING: datapoint_ids - never passed to Prisma!
        metadata: datasetMetadata,
        results: data.results || {},
        configuration: data.configuration || {},
        status: data.status || ExperimentRunStatus.PENDING,
        org_id: orgId,
        project_id: projectId,
    },
});
```

### **Prisma Schema** (schema.prisma)

```prisma
model ExperimentRun {
    id            String    @id
    run_id        String    @unique
    dataset_id    String?
    datapoint_ids String[]? @default([])  // Likely this field exists
    Dataset       Dataset?  @relation(fields: [dataset_id], references: [id])
    ...
}

model Dataset {
    id               String             @id  // NO @default - manually set
    name             String
    ...
}
```

---

## 🔬 **Root Cause Hypotheses**

### **Hypothesis 1: Missing datapoint_ids in Prisma Create** (MOST LIKELY)

**Evidence**:
- Backend code doesn't pass `datapoint_ids` to `tx.experimentRun.create()`
- `datapoint_ids` is in the input `data` but never used
- Backend response shows `datapoint_ids` in `metadata` instead of top-level

**Code Location**: `app/services/experiment_run.service.ts:61-74`

**Fix Needed**:
```typescript
const experimentRun = await tx.experimentRun.create({
    data: {
        // ... existing fields
        dataset_id: datasetId,
        datapoint_ids: data.datapoint_ids || [],  // ← ADD THIS
        // ... rest
    },
});
```

### **Hypothesis 2: Foreign Key Constraint Failing Silently**

**Evidence**:
- `dataset_id` is sent correctly
- Backend code assigns it correctly
- But Prisma saves as `null`

**Possible Causes**:
1. **Dataset doesn't exist** in database when run is created
   - Unlikely - we verify dataset exists before creating run
   - Dataset ID matches what Prisma created

2. **org_id/project_id mismatch** between Dataset and ExperimentRun
   - Dataset created with one org/project
   - Run created with different org/project
   - FK constraint fails, Prisma sets to null

3. **Prisma Optional Field Behavior**
   - Field is `String?` (optional)
   - FK constraint fail → silently sets to null instead of error
   - No exception thrown

### **Hypothesis 3: datapoint_ids Moving to Metadata**

**Evidence**:
- POST sends: `datapoint_ids: [...]` (top-level)
- GET returns: `metadata.datapoint_ids: [...]` (in metadata)

**Possible Causes**:
1. **Zod schema transformation** moves field to metadata
2. **Response serialization logic** restructures the data
3. **Database trigger** or middleware moves it

---

## 🧪 **Diagnostic Steps**

### **Step 1: Enable Backend Logging**

Add detailed logging in `experiment_run.service.ts:60-75`:

```typescript
console.debug(`About to create experiment run with:`);
console.debug(`  dataset_id: ${datasetId}`);
console.debug(`  datapoint_ids: ${JSON.stringify(data.datapoint_ids)}`);

const experimentRun = await tx.experimentRun.create({...});

console.debug(`Created experiment run:`);
console.debug(`  run.dataset_id: ${experimentRun.dataset_id}`);
console.debug(`  run.datapoint_ids: ${experimentRun.datapoint_ids}`);
console.debug(`  run.metadata: ${JSON.stringify(experimentRun.metadata)}`);
```

### **Step 2: Check Actual Database Value**

Query Prisma database directly:
```sql
SELECT run_id, dataset_id, datapoint_ids, metadata
FROM "ExperimentRun"
WHERE run_id = 'e52ad928-91fd-4500-9dd8-062d346863a6';
```

This will show if Prisma is saving `null` or if it's a serialization issue.

### **Step 3: Verify Dataset Exists with Matching org_id/project_id**

```sql
SELECT id, name, org_id, project_id
FROM "Dataset"
WHERE id = 'yg7t2FIRhe3Zw3zfsWAlXx_W';
```

Compare org_id/project_id with the ExperimentRun to check FK constraints.

### **Step 4: Check Zod Schema**

File: `packages/core/src/schemas/experiment_run.schema.ts`

Look for:
- `PostExperimentRunRequestSchema` - Does it accept `dataset_id`?
- `GetExperimentRunResponseSchema` - Does it include `dataset_id`?
- Any `.transform()` calls that might move fields

---

## 💡 **Recommended Fixes**

### **Fix 1: Add datapoint_ids to Prisma Create** (HIGH PRIORITY)

**File**: `app/services/experiment_run.service.ts`

```typescript
const experimentRun = await tx.experimentRun.create({
    data: {
        run_id: runId,
        name: data.name,
        description: data.description,
        status: data.status || ExperimentRunStatus.PENDING,
        metadata: datasetMetadata,
        results: data.results || {},
        org_id: orgId,
        project_id: projectId,
        dataset_id: datasetId,
        event_ids: data.event_ids || [],
        datapoint_ids: data.datapoint_ids || [],  // ← ADD THIS LINE
        configuration: data.configuration || {},
    },
});
```

### **Fix 2: Add Logging for FK Constraint Failures**

**File**: `app/services/experiment_run.service.ts`

```typescript
try {
    const experimentRun = await tx.experimentRun.create({...});
    
    // Verify dataset_id was saved correctly
    if (data.dataset_id && !data.dataset_id.startsWith('EXT-')) {
        if (!experimentRun.dataset_id) {
            console.error(`CRITICAL: dataset_id was not saved!`);
            console.error(`  Input: ${data.dataset_id}`);
            console.error(`  Saved: ${experimentRun.dataset_id}`);
            console.error(`  This indicates FK constraint failure`);
        }
    }
    
    return { experiment_run: experimentRun, run_id: runId };
} catch (error) {
    console.error('Prisma error:', error);
    // Log if it's a FK constraint error
    if (error.code === 'P2003') {
        console.error('Foreign key constraint failed!');
        console.error(`  dataset_id: ${datasetId}`);
    }
    throw error;
}
```

### **Fix 3: Validate Dataset Exists Before Creating Run**

**File**: `app/services/experiment_run.service.ts`

```typescript
// Before creating run, verify dataset exists if dataset_id provided
if (datasetId && !datasetId.startsWith('EXT-')) {
    const dataset = await tx.dataset.findUnique({
        where: { id: datasetId }
    });
    
    if (!dataset) {
        throw new HttpError(400, `Dataset not found: ${datasetId}`);
    }
    
    // Verify org/project match
    if (dataset.org_id !== orgId || dataset.project_id !== projectId) {
        console.warn(`Dataset org/project mismatch!`);
        console.warn(`  Dataset: ${dataset.org_id}/${dataset.project_id}`);
        console.warn(`  Run: ${orgId}/${projectId}`);
    }
}
```

---

## 🎯 **Acceptance Criteria for Fix**

### **Before Fix**:
```json
GET /runs/:run_id
{
    "dataset_id": null,  // ❌
    "metadata": {
        "datapoint_ids": [...]  // ⚠️ Wrong location
    }
}
```

### **After Fix**:
```json
GET /runs/:run_id
{
    "dataset_id": "yg7t2FIRhe3Zw3zfsWAlXx_W",  // ✅
    "datapoint_ids": ["id1", "id2", "id3"],  // ✅ Top-level
    "metadata": {
        "evaluator_metrics": {...}  // ✅ Only metrics
    }
}
```

---

## 📝 **Integration Test Evidence**

**Test File**: `tests/integration/test_experiments_integration.py`  
**Test Method**: `test_managed_dataset_evaluation`

**What It Tests**:
1. Create dataset via SDK → Get insertedId
2. Add datapoints to dataset
3. Run evaluate() with dataset_id parameter
4. Verify backend state

**Current Result**: ✅ PASSES (with workaround - sessions have dataset_id)  
**Expected After Fix**: ✅ PASSES (run object shows dataset_id)

**Debug Logs Available**:
- SDK sends: `"dataset_id": "yg7t2FIRhe3Zw3zfsWAlXx_W"`
- POST payload: Confirmed in logs
- Backend receives: Confirmed
- Backend saves: `null` (bug)

---

## 🔗 **Related Files**

### **Backend**:
- `app/services/experiment_run.service.ts:25-90` - createExperimentRun
- `app/routes/experiment_run.route.ts:160-239` - POST /runs route
- `packages/core/src/schemas/experiment_run.schema.ts` - Zod schemas
- `scripts/mongo_to_rds/prisma_current/schema.prisma` - Prisma schema

### **SDK**:
- `src/honeyhive/experiments/core.py:620-649` - Run creation with dataset_id
- `src/honeyhive/experiments/utils.py:209-217` - EXT- transformation
- `src/honeyhive/api/datasets.py:12-34` - Dataset creation (returns insertedId)

---

## ⚠️ **Workaround (Current Behavior)**

**Sessions include dataset_id in metadata**:
```json
{
    "session_id": "xxx",
    "metadata": {
        "run_id": "yyy",
        "dataset_id": "yg7t2FIRhe3Zw3zfsWAlXx_W",  // ✅ Present here
        "datapoint_id": "zzz"
    }
}
```

This allows:
- ✅ Event-level comparison (matches by datapoint_id in metadata)
- ✅ Session filtering by dataset
- ✅ Experiments work end-to-end
- ❌ Run object doesn't show dataset linkage in UI

---

## 🚀 **Action Items**

### **For Backend Team**:

1. **Add datapoint_ids to Prisma create** (Lines 60-74)
   - Currently missing from the create statement
   - Should be: `datapoint_ids: data.datapoint_ids || []`

2. **Investigate why dataset_id saves as null**
   - Enable Prisma query logging
   - Check for FK constraint errors
   - Verify dataset.id exists before run creation
   - Check org_id/project_id match between Dataset and ExperimentRun

3. **Add validation** before creating run
   - Verify dataset exists if dataset_id provided
   - Return 400 error if dataset not found
   - Log FK constraint failures explicitly

4. **Update response schema** if needed
   - Ensure dataset_id is in GET response
   - Ensure datapoint_ids is top-level, not in metadata

### **For SDK Team** (Us):

1. ✅ **DONE**: Correctly send dataset_id in POST /runs
2. ✅ **DONE**: Remove dataset_id from PUT /runs (backend doesn't accept it)
3. ✅ **DONE**: Integration tests expose the issue
4. ⏸️ **PENDING**: Update test to assert dataset_id is not null (will fail until backend fixed)

---

## 📊 **Test Data for Reproduction**

**Run these commands** to reproduce:

```bash
# 1. Create dataset
curl -X POST https://api.honeyhive.ai/datasets \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "strands-test",
    "name": "test-dataset",
    "description": "Debug dataset"
  }'

# Response: {"inserted": true, "result": {"insertedId": "ABC123XYZ"}}
# Extract insertedId

# 2. Create run with dataset_id
curl -X POST https://api.honeyhive.ai/runs \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "run": {
      "project": "strands-test",
      "name": "test-run",
      "dataset_id": "ABC123XYZ",
      "event_ids": [],
      "status": "pending"
    }
  }'

# Response: {"evaluation": {...}, "run_id": "run-uuid"}
# Extract run_id

# 3. GET run and check dataset_id
curl -X GET https://api.honeyhive.ai/runs/{run_id} \
  -H "Authorization: Bearer $API_KEY"

# Expected: {"evaluation": {"dataset_id": "ABC123XYZ", ...}}
# Actual: {"evaluation": {"dataset_id": null, ...}}  ← BUG
```

---

## 📅 **Timeline**

- **2025-10-02**: Issue discovered during integration test development
- **2025-10-02**: Root cause investigated (FK constraint or missing field)
- **2025-10-02**: Documented with evidence and fixes
- **TBD**: Backend fix implemented
- **TBD**: Integration test updated to assert dataset_id not null

---

## 🏷️ **Labels**

- `bug`
- `backend`
- `experiments`
- `dataset-linking`
- `medium-priority`
- `has-workaround`

---

**Assignee**: Backend Team  
**Related PR**: (SDK PR with integration tests)  
**Platform Run IDs for Verification**:
- `e52ad928-91fd-4500-9dd8-062d346863a6`
- `18e6c8e4-c917-43e4-aa55-ba22f5086281`
- Any run created via SDK with managed dataset

---

**Created By**: AI Assistant (V3 Framework Integration Test Development)  
**Contact**: @dhruvsingh for reproduction steps or questions

