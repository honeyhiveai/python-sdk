# V1 SDK: Auto-Generated Client with Ergonomic Wrapper

## Overview

This plan describes a clean-break approach to shipping the v1 HoneyHive Python SDK:
1. **Fully auto-generate** the API client from the v1 OpenAPI spec
2. **Provide a thin ergonomic wrapper** for better developer experience
3. **No backwards compatibility shims** - this is a new major version

## Rationale

- v1 OpenAPI spec has fundamentally different schema shapes than v0
- Field names, required/optional status, and model structures have changed
- Attempting to shim v0 names onto v1 shapes creates confusion and maintenance burden
- Clean break allows customers to migrate once with clear documentation

## Directory Structure

```
src/honeyhive/
├── __init__.py              # Public exports: HoneyHive, models
├── client.py                # Ergonomic wrapper (~200 lines)
├── models.py                # Re-exports from _generated/models
├── _generated/              # 100% auto-generated, never manually edit
│   ├── __init__.py
│   ├── client.py            # AuthenticatedClient
│   ├── api/
│   │   ├── __init__.py
│   │   ├── sessions.py
│   │   ├── events.py
│   │   ├── experiments.py
│   │   ├── configurations.py
│   │   ├── datasets.py
│   │   ├── datapoints.py
│   │   ├── metrics.py
│   │   ├── projects.py
│   │   └── tools.py
│   └── models/
│       ├── __init__.py
│       └── *.py             # All generated Pydantic models
├── tracer/                  # Existing tracer code (unchanged)
├── utils/                   # Existing utilities (unchanged)
└── config/                  # Existing config (unchanged)
```

## Implementation Steps

### Step 1: Clean Up Current State

Delete files related to old generation approach:
- `src/honeyhive/api/` (entire directory - handwritten client)
- `src/honeyhive/models/generated.py`
- `src/honeyhive/models/__init__.py` (will recreate)
- `scripts/generate_models.py`
- `SCHEMA_MAPPING_TODO.md`
- `API_CLIENT_IMPACT.md`

Keep:
- `src/honeyhive/tracer/`
- `src/honeyhive/utils/`
- `src/honeyhive/config/`
- `src/honeyhive/evaluation/`
- `src/honeyhive/experiments/`
- `openapi/v1.yaml`

### Step 2: Set Up Code Generation

Install openapi-python-client:
```bash
pip install openapi-python-client
```

Add to `pyproject.toml` dev dependencies:
```toml
[project.optional-dependencies]
dev = [
    # ... existing
    "openapi-python-client>=0.20.0",
]
```

Create generation script `scripts/generate_client.py`:
```python
#!/usr/bin/env python3
"""Generate API client from OpenAPI spec."""

import subprocess
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
OPENAPI_SPEC = REPO_ROOT / "openapi" / "v1.yaml"
OUTPUT_DIR = REPO_ROOT / "src" / "honeyhive" / "_generated"
TEMP_DIR = REPO_ROOT / ".generated_temp"

def main():
    # Clean previous
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)

    # Generate to temp directory
    subprocess.run([
        "openapi-python-client", "generate",
        "--path", str(OPENAPI_SPEC),
        "--output-path", str(TEMP_DIR),
        "--config", str(REPO_ROOT / "openapi" / "generator-config.yaml"),
    ], check=True)

    # Move generated client to _generated/
    generated_pkg = TEMP_DIR / "honeyhive_client"  # default name
    shutil.move(str(generated_pkg), str(OUTPUT_DIR))

    # Clean up
    shutil.rmtree(TEMP_DIR)

    print(f"Generated client at {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
```

Create `openapi/generator-config.yaml`:
```yaml
project_name_override: honeyhive_client
package_name_override: honeyhive._generated
```

### Step 3: Create Ergonomic Wrapper

Create `src/honeyhive/client.py`:
```python
"""HoneyHive API Client - Ergonomic wrapper over generated client."""

from typing import Any, Dict, List, Optional

from honeyhive._generated.client import AuthenticatedClient
from honeyhive._generated.api.experiments import (
    post_experiment_run,
    get_experiment_run,
    get_experiment_runs,
    put_experiment_run,
    delete_experiment_run,
)
from honeyhive._generated.api.configurations import (
    get_configurations,
    create_configuration,
    update_configuration,
    delete_configuration,
)
# ... import other API modules

# Re-export all models for convenience
from honeyhive._generated.models import *  # noqa: F401, F403


class HoneyHive:
    """Main HoneyHive API client with ergonomic interface."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.honeyhive.ai",
        timeout: float = 30.0,
    ):
        """Initialize the HoneyHive client.

        Args:
            api_key: HoneyHive API key (starts with 'hh_')
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        self._client = AuthenticatedClient(
            base_url=base_url,
            token=api_key,
            timeout=timeout,
        )

        # Initialize API namespaces
        self.runs = RunsAPI(self._client)
        self.configurations = ConfigurationsAPI(self._client)
        self.datasets = DatasetsAPI(self._client)
        self.datapoints = DatapointsAPI(self._client)
        self.metrics = MetricsAPI(self._client)
        self.tools = ToolsAPI(self._client)
        self.projects = ProjectsAPI(self._client)
        self.sessions = SessionsAPI(self._client)
        self.events = EventsAPI(self._client)

    def close(self):
        """Close the client connections."""
        self._client.__exit__(None, None, None)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class RunsAPI:
    """Experiment runs API."""

    def __init__(self, client: AuthenticatedClient):
        self._client = client

    def create(self, request):
        """Create a new experiment run."""
        return post_experiment_run.sync(client=self._client, body=request)

    async def create_async(self, request):
        """Create a new experiment run (async)."""
        return await post_experiment_run.asyncio(client=self._client, body=request)

    def get(self, run_id: str):
        """Get an experiment run by ID."""
        return get_experiment_run.sync(client=self._client, run_id=run_id)

    async def get_async(self, run_id: str):
        """Get an experiment run by ID (async)."""
        return await get_experiment_run.asyncio(client=self._client, run_id=run_id)

    def list(self, **kwargs):
        """List experiment runs."""
        return get_experiment_runs.sync(client=self._client, **kwargs)

    async def list_async(self, **kwargs):
        """List experiment runs (async)."""
        return await get_experiment_runs.asyncio(client=self._client, **kwargs)

    def update(self, run_id: str, request):
        """Update an experiment run."""
        return put_experiment_run.sync(client=self._client, run_id=run_id, body=request)

    async def update_async(self, run_id: str, request):
        """Update an experiment run (async)."""
        return await put_experiment_run.asyncio(client=self._client, run_id=run_id, body=request)

    def delete(self, run_id: str):
        """Delete an experiment run."""
        return delete_experiment_run.sync(client=self._client, run_id=run_id)

    async def delete_async(self, run_id: str):
        """Delete an experiment run (async)."""
        return await delete_experiment_run.asyncio(client=self._client, run_id=run_id)


# Similar classes for:
# - ConfigurationsAPI
# - DatasetsAPI
# - DatapointsAPI
# - MetricsAPI
# - ToolsAPI
# - ProjectsAPI
# - SessionsAPI
# - EventsAPI
```

### Step 4: Create Models Re-export

Create `src/honeyhive/models.py`:
```python
"""HoneyHive API Models - Re-exported from generated code."""

# Re-export all generated models
from honeyhive._generated.models import *  # noqa: F401, F403

# Tracer-specific models (not generated)
from honeyhive.models.tracing import TracingParams

__all__ = [
    # List key models for IDE autocompletion
    "PostExperimentRunRequest",
    "PostExperimentRunResponse",
    "GetExperimentRunResponse",
    "GetExperimentRunsResponse",
    "CreateConfigurationRequest",
    "GetConfigurationsResponseItem",
    "CreateDatasetRequest",
    "CreateDatapointRequest",
    "CreateMetricRequest",
    "CreateToolRequest",
    "EventNode",
    # ... etc
    "TracingParams",
]
```

### Step 5: Update Package Exports

Update `src/honeyhive/__init__.py`:
```python
"""HoneyHive Python SDK."""

from honeyhive.client import HoneyHive
from honeyhive.tracer import HoneyHiveTracer, trace

# Version
__version__ = "1.0.0"

__all__ = [
    "HoneyHive",
    "HoneyHiveTracer",
    "trace",
    "__version__",
]
```

### Step 6: Update Makefile

```makefile
# SDK Generation
generate:
	python scripts/generate_client.py
	$(MAKE) format

regenerate: clean-generated generate

clean-generated:
	rm -rf src/honeyhive/_generated/
```

### Step 7: Update CI Workflow

Update `.github/workflows/tox-full-suite.yml`:
```yaml
generated-code-check:
  name: "Generated Code Check"
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - run: pip install -e ".[dev]"
    - run: python scripts/generate_client.py
    - name: Check for uncommitted changes
      run: |
        if [ -n "$(git status --porcelain)" ]; then
          echo "Generated code is out of sync!"
          git diff --stat
          exit 1
        fi
```

### Step 8: Update Tests

- Update test imports from `honeyhive.api.*` to `honeyhive.client`
- Update model imports to use v1 names
- Update test assertions for new field names

### Step 9: Documentation

Create migration guide documenting:
- Import changes
- Model name changes
- Field name changes for each model
- New API patterns

## Usage Examples

### Before (v0)
```python
from honeyhive import HoneyHive
from honeyhive.models import CreateRunRequest, Configuration

client = HoneyHive(api_key="hh_...")
request = CreateRunRequest(project="proj", name="run", event_ids=[...])
response = client.evaluations.create_run(request)
config = client.configurations.get_configuration("id")
print(config.project)  # v0 field
```

### After (v1)
```python
from honeyhive import HoneyHive
from honeyhive.models import PostExperimentRunRequest

client = HoneyHive(api_key="hh_...")
request = PostExperimentRunRequest(name="run", event_ids=[...])
response = client.runs.create(request)
configs = client.configurations.list()
print(configs[0].id)  # v1 field
```

## Files to Create/Modify

| Action | File |
|--------|------|
| CREATE | `scripts/generate_client.py` |
| CREATE | `openapi/generator-config.yaml` |
| CREATE | `src/honeyhive/client.py` |
| CREATE | `src/honeyhive/models.py` |
| CREATE | `src/honeyhive/_generated/` (auto-generated) |
| MODIFY | `src/honeyhive/__init__.py` |
| MODIFY | `Makefile` |
| MODIFY | `.github/workflows/tox-full-suite.yml` |
| DELETE | `src/honeyhive/api/` (entire directory) |
| DELETE | `src/honeyhive/models/generated.py` |
| DELETE | `src/honeyhive/models/__init__.py` |
| DELETE | `scripts/generate_models.py` |

## Open Questions

1. **Generator choice**: `openapi-python-client` vs `openapi-generator` (Java-based)?
   - openapi-python-client: Pure Python, Pydantic v2 native, simpler
   - openapi-generator: More mature, more options, requires Java

2. **TODOSchema endpoints**: Sessions, Events, Projects use placeholder schemas
   - Option A: Generate anyway, they'll have placeholder types
   - Option B: Wait for proper Zod schemas before shipping v1
   - Option C: Keep handwritten code for those endpoints only

3. **Tracer integration**: Does tracer code need updates for new client?
   - Review `src/honeyhive/tracer/` for API client usage

4. **Version bump**: Ship as 1.0.0 or 0.x with deprecation warnings?
