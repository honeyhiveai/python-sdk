# AGENTS.md

## Cursor Cloud specific instructions

This is the **HoneyHive Python SDK** — a client-side Python library for LLM observability, evaluation, and tracing. It is **not** a server application; there are no databases or backend services to run locally.

### Quick reference

| Task | Command |
|------|---------|
| Unit tests | `tox -e unit` |
| Lint (pylint + mypy) | `tox -e lint` |
| Format check (black + isort) | `tox -e format` |
| Build package | `python -m build` |
| All quality checks | `make check` |
| See all commands | `make help` |

Per project convention (see `.claude/CLAUDE.md`), **always use `tox` for testing** — do not invoke `pytest` directly.

### Environment setup

- Python 3.12 is the primary development version (`requires-python = ">=3.11"`).
- The virtual environment lives at `.venv/` and is created with `uv venv .venv --python 3.12`.
- Dependencies: `uv pip install -e ".[dev,docs]"` (user preference: use `uv` instead of `pip`).
- Activate with `source .venv/bin/activate` (also `source $HOME/.local/bin/env` for `uv` on PATH).

### Gotchas discovered during setup

- **`tox -e lint` fails at 9.51/10** (threshold 9.99) due to pre-existing cyclic-import warnings and duplicate-code issues in the codebase. This is a known state, not a regression.
- **8 unit tests in `test_tracer_infra_environment.py` fail** in container/VM environments because cloud environment detection tests (GCP, Azure, AWS EC2) detect unexpected environment variables. These are pre-existing and environment-specific.
- **OTLP warnings** (`No valid export method: OTLP exporter is False`) appear when running with `HH_OTLP_ENABLED=false`; this is expected in test mode.
- `tox` creates its own virtualenvs under `.tox/` and installs dependencies there, so the `.venv` is primarily for IDE support and direct `make` commands (e.g., `make format`, `make typecheck`).
- Integration tests (`tox -e integration`) require real `HH_API_KEY` and optional LLM provider API keys; unit tests (`tox -e unit`) run fully offline with mocked credentials.
