---
name: cursor-cloud-dev-setup
description: >
  Use this skill when setting up, building, testing, or running the HoneyHive Python SDK
  in a Cursor Cloud (or similar containerized) development environment. Covers environment
  bootstrap, dependency installation, test/lint/build commands, and known gotchas.
---

# Cursor Cloud Dev Setup — HoneyHive Python SDK

This is a **client-side Python library** for LLM observability, evaluation, and tracing.
There are no databases or backend services to run locally.

## Quick reference

| Task | Command |
|------|---------|
| Unit tests | `tox -e unit` |
| Lint (pylint + mypy) | `tox -e lint` |
| Format check (black + isort) | `tox -e format` |
| Build package | `python -m build` |
| All quality checks | `make check` |
| See all commands | `make help` |

Per project convention (see `.claude/CLAUDE.md`), **always use `tox` for testing** — do not invoke `pytest` directly.

## Environment setup

- Python 3.12 is the primary development version (`requires-python = ">=3.11"`).
- The virtual environment lives at `.venv/` and is created with `uv venv .venv --python 3.12`.
- Dependencies: `uv pip install -e ".[dev,docs]"` (user preference: use `uv` instead of `pip`).
- Activate with `source .venv/bin/activate` (also `source $HOME/.local/bin/env` for `uv` on PATH).

## Known failures and workarounds

Neither `tox -e lint` nor `tox -e unit` exits cleanly in this environment. **You cannot rely on exit codes alone**; compare output against the baselines below to detect regressions.

### `tox -e lint` — always fails (pylint 9.51/10, threshold 9.99)

Pylint scores ~9.51 due to cyclic-import (R0401), duplicate-code (R0801), and other violations. Because tox stops at the first failing command, **mypy never runs** (it has 274 pre-existing errors across 28 files).

**Workaround**: run mypy independently to check type safety:

```
python -m mypy src/honeyhive --config-file=pyproject.toml
```

When making changes, compare pylint score and mypy error count against these baselines to catch regressions.

### `tox -e unit` — always has 8 failures

**Baseline**: 2256 passed, 8 failed, 249 skipped (numbers will shift as tests are added).

All 8 failures are in `tests/unit/test_tracer_infra_environment.py` — a test isolation bug where `/.dockerenv` exists in the container, so `detect_primary_environment_type()` returns `"docker"` before checking cloud-provider env vars. The tests mock env vars but not `os.path.exists("/.dockerenv")`. These pass on bare-metal CI runners.

**Workaround**: after running `tox -e unit`, verify that the only failures are the 8 known environment-detection tests. Any new failures indicate a real regression.

### Running pytest directly (not via tox)

Avoid this (project convention is `tox`). If you do, expect 5 additional config-test failures because `HH_API_URL` and `HH_PROJECT` secrets in the environment override the expected defaults. Tox isolates these via its `setenv`/`passenv` configuration.

### Minor

- **OTLP warnings** (`No valid export method: OTLP exporter is False`) appear with `HH_OTLP_ENABLED=false`; expected in test mode.
- `tox` creates its own virtualenvs under `.tox/`, so `.venv` is for IDE support and direct `make` commands.
- Integration tests (`tox -e integration`) require a real `HH_API_KEY` and optional LLM provider API keys; unit tests run fully offline with mocked credentials.
