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

## Gotchas

- **`tox -e lint` fails (pylint scores 9.51/10, threshold is 9.99).** Tox stops at the first failing command, so **mypy never runs**. To run mypy independently: `python -m mypy src/honeyhive --config-file=pyproject.toml`. The pylint violations are a mix of cyclic-import (R0401), duplicate-code (R0801), and other issues; disabling R0401+R0801 only raises the score to ~9.59.
- **8 unit tests in `test_tracer_infra_environment.py` fail inside Docker** due to a test isolation bug: `/.dockerenv` exists in the container, so `detect_primary_environment_type()` returns `"docker"` before ever checking cloud-provider env vars. The tests mock env vars (e.g., `GOOGLE_CLOUD_PROJECT`) but don't mock `os.path.exists("/.dockerenv")`. These tests pass on bare-metal CI runners.
- **OTLP warnings** (`No valid export method: OTLP exporter is False`) appear when running with `HH_OTLP_ENABLED=false`; this is expected in test mode.
- `tox` creates its own virtualenvs under `.tox/` and installs dependencies there, so `.venv` is primarily for IDE support and direct `make` commands (e.g., `make format`, `make typecheck`).
- Integration tests (`tox -e integration`) require a real `HH_API_KEY` and optional LLM provider API keys; unit tests (`tox -e unit`) run fully offline with mocked credentials.
