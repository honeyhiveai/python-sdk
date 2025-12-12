# V1 Migration Plan

This document outlines the plan to support both v0.x and v1.x SDK versions from a single repository.

## Goals

1. **Single repo, two PyPI versions**: `honeyhive==0.x.x` ships v0 client, `honeyhive==1.x.x` ships v1 client
2. **v1 is fully auto-generated**: No handwritten client code for v1
3. **Shared code unchanged**: Tracer, instrumentation, experiments, config stay the same
4. **No runtime switching**: Each published package contains only one client implementation
5. **v1 is a breaking change**: No backwards compatibility shims needed

## Current State

### v0 Structure
```
src/honeyhive/
├── api/                      # Handwritten domain-specific modules
│   ├── client.py             # Main HoneyHiveClient class
│   ├── events.py
│   ├── session.py
│   ├── configurations.py
│   └── ...
├── models/
│   └── generated.py          # Single file (datamodel-codegen output)
├── tracer/                   # Shared - OpenTelemetry tracing
├── config/                   # Shared - Configuration models
├── experiments/              # Shared - Experiment execution
├── evaluation/               # Shared - Legacy evaluators
├── cli/                      # Shared - CLI
└── utils/                    # Shared - Utilities
```

### v1 Generated Structure (from comparison_output/)
```
honeyhive_generated/
├── __init__.py
├── client/
│   ├── __init__.py
│   └── client.py             # attrs-based Client class (httpx)
├── models/                   # Many individual model files
│   ├── __init__.py           # Re-exports all models
│   ├── event.py
│   ├── configuration.py
│   └── ... (150+ files)
├── api/                      # API endpoint functions
│   └── __init__.py
└── types/
    └── __init__.py
```

## Target Structure

```
src/honeyhive/
├── _v0/                      # v0 client (excluded in v1 builds)
│   ├── api/                  # Current handwritten client
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── events.py
│   │   └── ...
│   └── models/
│       ├── __init__.py
│       └── generated.py
│
├── _v1/                      # v1 client (excluded in v0 builds)
│   ├── __init__.py
│   ├── client/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── event.py
│   │   └── ... (many files)
│   ├── api/
│   │   └── __init__.py
│   └── types/
│       └── __init__.py
│
├── api/                      # Public facade - routes to _v0 or _v1
│   └── __init__.py
├── models/                   # Public facade - routes to _v0 or _v1
│   └── __init__.py
│
├── tracer/                   # Shared (unchanged)
├── config/                   # Shared (unchanged)
├── experiments/              # Shared (unchanged)
├── evaluation/               # Shared (unchanged)
├── cli/                      # Shared (unchanged)
└── utils/                    # Shared (unchanged)

openapi/
├── v0.yaml                   # Current spec (moved from ./openapi.yaml)
└── v1.yaml                   # New v1 spec (start minimal, expand later)
```

## How It Works

### Facade Pattern (api/__init__.py)

```python
# src/honeyhive/api/__init__.py
"""
Public API client facade.

Imports from _v0 or _v1 depending on which is available.
Only one will be present in a published package.
"""

try:
    # v1 is preferred if present
    from honeyhive._v1.client.client import Client as HoneyHiveClient
    from honeyhive._v1 import api, models, types
    __version_api__ = "v1"
except ImportError:
    # Fall back to v0
    from honeyhive._v0.api.client import HoneyHiveClient
    from honeyhive._v0 import api, models
    __version_api__ = "v0"

__all__ = ["HoneyHiveClient", "api", "models"]
```

### Build-Time Exclusion (pyproject.toml)

```toml
[tool.hatch.build.targets.wheel]
# Controlled by HONEYHIVE_BUILD_VERSION env var or version number

# For v0.x releases:
exclude = ["src/honeyhive/_v1/**"]

# For v1.x releases:
exclude = ["src/honeyhive/_v0/**"]
```

We'll use a hatch build hook or separate build configs to switch between these.

## Implementation Phases

### Phase 1: Reorganize v0 Code

1. Create `src/honeyhive/_v0/` directory
2. Move `src/honeyhive/api/` → `src/honeyhive/_v0/api/`
3. Move `src/honeyhive/models/` → `src/honeyhive/_v0/models/`
4. Create public facade at `src/honeyhive/api/__init__.py`
5. Create public facade at `src/honeyhive/models/__init__.py`
6. Update all internal imports to use facades
7. Verify tests pass with new structure

### Phase 2: Set Up OpenAPI Specs

1. Create `openapi/` directory
2. Move `openapi.yaml` → `openapi/v0.yaml`
3. Create minimal `openapi/v1.yaml` for prototyping:
   ```yaml
   openapi: 3.1.0
   info:
     title: HoneyHive API
     version: 1.0.0
   servers:
     - url: https://api.honeyhive.ai
   paths:
     /session/start:
       post:
         operationId: startSession
         # ... minimal endpoint for testing
   ```

### Phase 3: Set Up v1 Generation Pipeline

1. Create `scripts/generate_v1_client.py`
2. Configure `openapi-python-client` to output to `src/honeyhive/_v1/`
3. Add `make generate-v1` target
4. Test generation with minimal spec

### Phase 4: Configure Build System

1. Add hatch build hook for version-based exclusion
2. Create separate build configurations:
   - `make build-v0` → builds with `_v1/` excluded
   - `make build-v1` → builds with `_v0/` excluded
3. Test local installs of both versions

### Phase 5: Update CI/CD

1. Add workflow for building v0.x releases from `main` branch
2. Add workflow for building v1.x releases from `v1` branch (or tag-based)
3. Ensure both versions can be published to PyPI

### Phase 6: Expand v1 Spec

1. Import full v1 OpenAPI spec
2. Regenerate v1 client
3. Verify generation completes without errors
4. Run type checking on generated code

## Makefile Targets

```makefile
# OpenAPI specs
OPENAPI_V0 := openapi/v0.yaml
OPENAPI_V1 := openapi/v1.yaml

# Generation
generate-v0:
	python scripts/generate_v0_models.py --spec $(OPENAPI_V0) --output src/honeyhive/_v0/models/
	$(MAKE) format

generate-v1:
	python scripts/generate_v1_client.py --spec $(OPENAPI_V1) --output src/honeyhive/_v1/
	$(MAKE) format

generate-all: generate-v0 generate-v1

# Building
build-v0:
	HONEYHIVE_BUILD_VERSION=v0 python -m build

build-v1:
	HONEYHIVE_BUILD_VERSION=v1 python -m build

# Testing
test-v0:
	HONEYHIVE_BUILD_VERSION=v0 tox -e py311

test-v1:
	HONEYHIVE_BUILD_VERSION=v1 tox -e py311
```

## Version Strategy

| PyPI Version | Contains | Branch/Tag |
|--------------|----------|------------|
| `0.x.x` | `_v0/` only | `main` branch |
| `1.x.x` | `_v1/` only | `v1` branch or `v1.*` tags |

The version number in `pyproject.toml` determines which client is included.

## Open Questions

1. **Branch strategy**: Should v1 development happen on a `v1` branch, or use tags?
2. **Shared code changes**: How do we sync shared code changes between v0 and v1?
3. **Dependencies**: v1 uses `attrs` (from openapi-python-client), v0 doesn't. How to handle?
4. **Testing**: Should we have separate test suites for v0 and v1 clients?

## Migration Checklist

- [x] Phase 1: Reorganize v0 code into `_v0/`
- [x] Phase 1: Create public facades
- [x] Phase 1: Create backwards-compat shims for deep imports
- [x] Phase 1: Update test mock paths to `_v0` locations
- [x] Phase 1: Verify tests pass (165/166 in affected files, 1 pre-existing mock issue)
- [x] Phase 2: Move OpenAPI spec to `openapi/v0.yaml`
- [x] Phase 2: Create minimal `openapi/v1.yaml`
- [ ] Phase 3: Create v1 generation script
- [ ] Phase 3: Add `make generate-v1` target
- [ ] Phase 4: Configure hatch build exclusions
- [ ] Phase 4: Test local builds of both versions
- [ ] Phase 5: Set up CI/CD for dual publishing
- [ ] Phase 6: Import full v1 spec and regenerate
