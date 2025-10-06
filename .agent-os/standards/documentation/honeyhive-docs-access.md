# HoneyHive Documentation Access Guide

**Purpose**: Guide for AI assistants to efficiently access and extract information from HoneyHive's documentation site.

---

## 📚 Documentation Structure

HoneyHive documentation is available at **https://docs.honeyhive.ai/** with two powerful access methods:

### 1. **llms.txt Index File**
- **URL**: `https://docs.honeyhive.ai/llms.txt`
- **Purpose**: Master index of all documentation pages
- **Format**: Text file with markdown links to all documentation pages

### 2. **Direct Markdown Access**
- **Pattern**: `https://docs.honeyhive.ai/{category}/{page}.md`
- **Purpose**: Fetch raw markdown content of any documentation page
- **Format**: Clean markdown without HTML/UI elements

---

## 🔍 How to Use

### Step 1: Start with llms.txt

**Always begin** by fetching the index to understand available documentation:

```bash
curl -s "https://docs.honeyhive.ai/llms.txt"
```

**What you get**:
- Complete list of all documentation pages
- Organized by category (API Reference, Evaluation, SDK Reference, etc.)
- Links to specific markdown files

**Example index entries**:
```
- [Quickstart](https://docs.honeyhive.ai/evaluation/quickstart.md)
- [Comparing Experiments](https://docs.honeyhive.ai/evaluation/comparing_evals.md)
- [Python SDK](https://docs.honeyhive.ai/sdk-reference/python-experiments-ref.md)
- [Create a new evaluation run](https://docs.honeyhive.ai/api-reference/experiments/create-a-new-evaluation-run.md)
```

### Step 2: Extract Relevant URLs

From the index, identify documentation pages relevant to your task:

**For Experiments/Evaluation**:
- `/evaluation/quickstart.md` - Basic workflow
- `/evaluation/comparing_evals.md` - Comparison features
- `/evaluation/managed_datasets.md` - Using HoneyHive datasets
- `/evaluation/server_side_evaluators.md` - Server-side evaluators
- `/evaluation/external_logs.md` - External log evaluation
- `/evaluation/multi_step_evals.md` - Multi-step pipelines

**For API Reference**:
- `/api-reference/experiments/create-a-new-evaluation-run.md`
- `/api-reference/experiments/retrieve-experiment-comparison.md`
- `/api-reference/experiments/retrieve-experiment-result.md`
- `/api-reference/experiments/update-an-evaluation-run.md`

**For SDK Reference**:
- `/sdk-reference/python-experiments-ref.md`
- `/sdk-reference/python-tracer-ref.md`
- `/sdk-reference/typescript-experiments-ref.md`

### Step 3: Fetch Markdown Content

Use `curl` to fetch the raw markdown:

```bash
curl -s "https://docs.honeyhive.ai/evaluation/quickstart.md"
curl -s "https://docs.honeyhive.ai/evaluation/comparing_evals.md"
curl -s "https://docs.honeyhive.ai/api-reference/experiments/retrieve-experiment-comparison.md"
```

**Advantages**:
- ✅ Clean markdown format (no HTML/CSS)
- ✅ Includes code examples
- ✅ Shows function signatures
- ✅ Reveals workflow details
- ✅ Fast and lightweight

---

## 📋 Documentation Categories

### From llms.txt Analysis:

#### **🧪 Experiments & Evaluation**
- **Core Guides**:
  - `evaluation/introduction.md` - Overview
  - `evaluation/quickstart.md` - Getting started
  - `evaluation/comparing_evals.md` - Comparison features
  - `evaluation/managed_datasets.md` - Using HoneyHive datasets
  - `evaluation/external_logs.md` - External log evaluation
  - `evaluation/multi_step_evals.md` - Multi-step experiments
  - `evaluation/server_side_evaluators.md` - Server-side evaluators

#### **📊 API Reference - Experiments**
- `api-reference/experiments/create-a-new-evaluation-run.md`
- `api-reference/experiments/delete-an-evaluation-run.md`
- `api-reference/experiments/get-a-list-of-evaluation-runs.md`
- `api-reference/experiments/get-details-of-an-evaluation-run.md`
- `api-reference/experiments/retrieve-experiment-comparison.md`
- `api-reference/experiments/retrieve-experiment-result.md`
- `api-reference/experiments/update-an-evaluation-run.md`

#### **🔧 SDK Reference**
- `sdk-reference/python-experiments-ref.md` - Python `evaluate()` function
- `sdk-reference/typescript-experiments-ref.md` - TypeScript `evaluate()` function
- `sdk-reference/python-tracer-ref.md` - Tracer for instrumentation
- `sdk-reference/manual-eval-instrumentation.md` - Manual evaluation logging

#### **📝 Evaluators**
- `evaluators/introduction.md` - Overview
- `evaluators/client_side.md` - Client-side evaluators
- `evaluators/llm.md` - LLM-based evaluators
- `evaluators/python.md` - Python evaluators
- `evaluators/human.md` - Human annotation
- `evaluators/composites.md` - Composite evaluators
- `evaluators/evaluator-templates.md` - Pre-built templates

#### **📦 Datasets**
- `datasets/introduction.md`
- `datasets/import.md` - Upload datasets
- `datasets/export.md` - Export datasets
- `datasets/dataset-curation.md` - Curate from traces
- `datasets/hf-datasets.md` - Import from Hugging Face

#### **🔍 Tracing**
- `tracing/introduction.md`
- `tracing/client-side-evals.md` - Log evaluations with traces
- `tracing/custom-spans.md`
- `tracing/distributed-tracing.md`
- `tracing/multithreading.md`
- `tracing/online-experimentation.md` - A/B testing

---

## 🎯 Best Practices for AI Assistants

### 1. **Always Start with llms.txt**
```bash
# STEP 1: Get the index
curl -s "https://docs.honeyhive.ai/llms.txt"

# STEP 2: Identify relevant pages from index
# Look for keywords like "evaluation", "experiment", "compare", etc.

# STEP 3: Fetch specific markdown files
curl -s "https://docs.honeyhive.ai/evaluation/quickstart.md"
```

### 2. **Fetch Multiple Pages in Parallel**
When you need comprehensive information, fetch related pages together:

```bash
# Fetch all experiment-related guides at once
curl -s "https://docs.honeyhive.ai/evaluation/quickstart.md" &
curl -s "https://docs.honeyhive.ai/evaluation/comparing_evals.md" &
curl -s "https://docs.honeyhive.ai/sdk-reference/python-experiments-ref.md" &
wait
```

### 3. **Extract Testable Functionality**
When analyzing documentation for test cases, look for:

**In Code Examples**:
- Function signatures and parameters
- Expected inputs/outputs
- Error handling patterns
- Edge cases mentioned

**In Feature Descriptions**:
- "allows you to..." → Feature to test
- "automatically calculates..." → Behavior to verify
- "supports..." → Capability to validate
- "filters for..." → Filter functionality to test

### 4. **Map Documentation to Implementation**

Create a mapping between docs and code:

| Documentation Page | SDK Implementation | Test Coverage |
|-------------------|-------------------|---------------|
| `/evaluation/quickstart.md` | `experiments/core.py:evaluate()` | `test_experiments_integration.py` |
| `/evaluation/comparing_evals.md` | `experiments/results.py:compare_runs()` | `test_compare_runs_*` |
| `/api-reference/experiments/retrieve-experiment-comparison.md` | `api/evaluations.py:compare_runs()` | `test_experiments_results.py` |

---

## 📝 Example: Extracting Test Cases from Documentation

### Workflow Example

```bash
# 1. Get index to find relevant pages
curl -s "https://docs.honeyhive.ai/llms.txt" | grep -i "compar"

# Output shows:
# - [Comparing Experiments](https://docs.honeyhive.ai/evaluation/comparing_evals.md)
# - [Retrieve experiment comparison](https://docs.honeyhive.ai/api-reference/experiments/retrieve-experiment-comparison.md)

# 2. Fetch comparison guide
curl -s "https://docs.honeyhive.ai/evaluation/comparing_evals.md"

# 3. Extract features from markdown:
# - "Step level comparisons" → Test multi-step comparison
# - "Aggregated metrics" → Test metric aggregation
# - "Improved/regressed events" → Test improvement/regression detection
# - "Output diff viewer" → Test output comparison
# - "Metric distribution" → Test distribution analysis

# 4. Fetch API reference
curl -s "https://docs.honeyhive.ai/api-reference/experiments/retrieve-experiment-comparison.md"

# 5. Extract API details:
# - Endpoint: GET /runs/:new_run_id/compare-with/:old_run_id
# - Parameters: aggregate_function, filters
# - Response structure: commonDatapoints, metrics, event_details
```

### Test Case Extraction Template

**From Feature Description** → **To Test Case**:

| Feature (from docs) | Test Case |
|---------------------|-----------|
| "Compare outputs and metrics of corresponding events" | `test_compare_outputs_and_metrics()` |
| "Filter for events that have improved or regressed" | `test_filter_improved_regressed_events()` |
| "Automatically calculates aggregates from server-side metrics" | `test_automatic_aggregate_calculation()` |
| "View metric aggregates" | `test_view_metric_aggregates()` |
| "Analyze distribution of various metrics" | `test_metric_distribution_analysis()` |

---

## 🚀 Quick Reference Commands

### Get Full Documentation Index
```bash
curl -s "https://docs.honeyhive.ai/llms.txt"
```

### Fetch Experiment Quickstart
```bash
curl -s "https://docs.honeyhive.ai/evaluation/quickstart.md"
```

### Fetch Comparison Guide
```bash
curl -s "https://docs.honeyhive.ai/evaluation/comparing_evals.md"
```

### Fetch API Reference for Experiments
```bash
curl -s "https://docs.honeyhive.ai/api-reference/experiments/create-a-new-evaluation-run.md"
curl -s "https://docs.honeyhive.ai/api-reference/experiments/retrieve-experiment-comparison.md"
curl -s "https://docs.honeyhive.ai/api-reference/experiments/retrieve-experiment-result.md"
```

### Fetch Python SDK Reference
```bash
curl -s "https://docs.honeyhive.ai/sdk-reference/python-experiments-ref.md"
```

### Search Index for Specific Topics
```bash
# Find all pages related to "dataset"
curl -s "https://docs.honeyhive.ai/llms.txt" | grep -i "dataset"

# Find all pages related to "evaluator"
curl -s "https://docs.honeyhive.ai/llms.txt" | grep -i "evaluator"

# Find all API reference pages
curl -s "https://docs.honeyhive.ai/llms.txt" | grep "api-reference"
```

---

## ⚠️ Important Notes

### 1. **No Web Search Required**
- ❌ DON'T use web search tools
- ✅ DO use direct `curl` commands
- The documentation is already in markdown format and accessible via direct URLs

### 2. **URL Pattern Consistency**
- Base: `https://docs.honeyhive.ai/`
- Index: `https://docs.honeyhive.ai/llms.txt`
- Pages: `https://docs.honeyhive.ai/{category}/{page}.md`
- Always use `.md` extension for page content

### 3. **Content Format**
- llms.txt returns plain text with markdown links
- Page URLs return raw markdown (not HTML)
- Code examples are included in markdown code blocks
- Images/diagrams are referenced but not embedded

### 4. **Update Frequency**
- Documentation may be updated independently of SDK
- Always fetch fresh content during analysis
- Cross-reference with actual SDK implementation

---

## 📚 Common Documentation Paths

### Experiments
```
/evaluation/introduction.md
/evaluation/quickstart.md
/evaluation/comparing_evals.md
/evaluation/managed_datasets.md
/evaluation/external_logs.md
/evaluation/multi_step_evals.md
/evaluation/server_side_evaluators.md
```

### API Reference - Experiments
```
/api-reference/experiments/create-a-new-evaluation-run.md
/api-reference/experiments/delete-an-evaluation-run.md
/api-reference/experiments/get-a-list-of-evaluation-runs.md
/api-reference/experiments/get-details-of-an-evaluation-run.md
/api-reference/experiments/retrieve-experiment-comparison.md
/api-reference/experiments/retrieve-experiment-result.md
/api-reference/experiments/update-an-evaluation-run.md
```

### SDK Reference
```
/sdk-reference/python-experiments-ref.md
/sdk-reference/python-tracer-ref.md
/sdk-reference/python-logger-ref.md
/sdk-reference/typescript-experiments-ref.md
/sdk-reference/authentication.md
```

### Evaluators
```
/evaluators/introduction.md
/evaluators/client_side.md
/evaluators/llm.md
/evaluators/python.md
/evaluators/human.md
/evaluators/composites.md
/evaluators/evaluator-templates.md
```

### Datasets
```
/datasets/introduction.md
/datasets/import.md
/datasets/export.md
/datasets/dataset-curation.md
/datasets/hf-datasets.md
```

---

## ✅ Checklist for Future Sessions

When analyzing HoneyHive documentation:

- [ ] Start by fetching `https://docs.honeyhive.ai/llms.txt`
- [ ] Identify relevant pages from the index
- [ ] Fetch markdown content using direct URLs
- [ ] Extract function signatures, parameters, and examples
- [ ] Map documentation features to SDK implementation
- [ ] Identify testable functionality
- [ ] Create test cases based on documented behavior
- [ ] Cross-reference with actual backend/SDK code
- [ ] Validate assumptions with integration tests

---

**Last Updated**: 2025-10-02  
**Maintained By**: HoneyHive SDK Team  
**Related Standards**: 
- `.agent-os/standards/ai-assistant/code-generation/tests/v3/FRAMEWORK-LAUNCHER.md`
- `.agent-os/specs/2025-09-03-evaluation-to-experiment-alignment/ENDPOINT_COVERAGE_MATRIX.md`

