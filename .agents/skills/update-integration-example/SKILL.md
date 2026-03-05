---
name: update-integration-example
description: Build or update SDK integration examples for AI frameworks. Use when asked to update, create, or review a framework example in python-sdk/examples/integrations/. Covers framework API research, example writing, smoke testing, span capture, and tracing sanity checks.
metadata:
  author: sanjeed5
  version: "2.1"
---

# Update Integration Example

Build or update the SDK example for a framework integration. The example is a public-facing reference that shows how to use HoneyHive with the framework. It must be correct, comprehensive, and follow the framework's current recommended APIs.

This skill does NOT do deep tracing validation — only a sanity check.

## Inputs

These variables are provided when the skill is invoked:

- `{{package}}` — PyPI package name (e.g., `pydantic-ai`)
- `{{version}}` — Last-tested version
- `{{framework}}` — Framework identifier for file paths (e.g., `pydantic_ai`)

## Before You Start

Read:
- `AGENTS.md` — env setup, branch conventions, run instructions
- Existing examples in `python-sdk/examples/integrations/` for this framework and others (match style and conventions)
- Use code as source of truth for exact behavior (do not assume docs are up to date)

`HH_API_KEY`, `HH_API_URL`, and `HH_PROJECT` are expected to be in the environment (via direnv or repo-level config). No manual env setup needed.

---

## Step 1: Framework API Research

Framework APIs change quickly. Research the current state before writing code.

> **Sub-agent opportunity**: Launch an explore sub-agent to research the framework's latest docs and changelog while you read the existing example.

> **Context7 MCP**: Use the Context7 MCP (`resolve-library-id` then `get-library-docs`) to look up the framework's official docs. Research sub-agents give good high-level patterns but sometimes get import paths, method names, or parameter names wrong. Context7 is the fastest way to verify exact API signatures before writing code.

Checklist:
- [ ] Current stable version on PyPI (we last tested `{{version}}`) and any recent breaking changes
- [ ] Major patterns: agent types, orchestration, tools, callbacks/state, runtime/session
- [ ] Current recommended API surface (not deprecated methods)
- [ ] Tracing path: native OTel vs OpenInference instrumentor vs other (some frameworks support both — e.g., Semantic Kernel has native OTel diagnostics AND you can layer an `OpenAIInstrumentor` to capture underlying API calls; use both when available for richer traces)
- [ ] **All documented multi-agent patterns** (delegation, hand-off, graphs, etc.) — check the framework's multi-agent docs page specifically
- [ ] Patterns that a good example should demonstrate

Output:
- "Latest stable version: X"
- "Breaking changes since `{{version}}`: [none | list]"
- "Tracing approach: native OTel | OpenInference instrumentor | other"
- "Patterns to cover: [...]"

If the framework has fundamentally changed (dropped OTel support, total API redesign), note it in the report and rewrite the example from scratch in Step 2.

---

## Step 2: Build/Update the Example

Target: `python-sdk/examples/integrations/{{framework}}_example.py`

### Gate: Check if update is needed

Compare the existing example against Step 1 research:
- Does it already cover all required patterns?
- Is it using the current stable framework APIs (not deprecated ones)?
- Does the framework version match?

If the example is already current, skip to Step 3 and note "already current." Do not make changes for the sake of changes.

### Rules (if updating)

- One comprehensive example covering major agent patterns for the framework
- Stay close to official framework style and current APIs
- HoneyHive integration should be minimal and obvious (init tracer + instrumentor)
- Readable by external SDK users, not internal test code
- **Never use HoneyHive-specific themes** (ingestion, traces, dashboards). Use generic relatable scenarios
- **Never copy themes/scenarios from the framework's official docs** 
- **Share the same domain across examples**: customer support with order status/policy lookup mock tools, order IDs ORD-1001 through ORD-1003 (match existing examples like `openinference_google_adk_example.py` and `pydantic_ai_integration.py`). Reuse this domain unless the framework doesn't fit it
- Include install instructions with explicit packages (`uv` and/or `pip`)

### Must showcase

- [ ] Agent names and hierarchy
- [ ] System instructions
- [ ] User input and model output
- [ ] Tool calls (arguments and results)
- [ ] Session continuity across turns

Verify: No syntax errors. Style matches existing examples in `examples/integrations/`.

---

## Step 3: Smoke Run

Run the example against the testing environment to confirm it executes without errors. Load any environment variables and then:

```bash
cd python-sdk && uv run python examples/integrations/{{framework}}_example.py
```

This is a functional check, not a tracing validation. Confirm:
- [ ] No import errors or missing dependencies
- [ ] Agent runs and produces output
- [ ] No crashes or unhandled exceptions
- [ ] HoneyHive tracer initializes without errors

If the example fails, fix it before proceeding.

> **Common failure**: Import paths. Research may report a class lives in one module when it actually lives in another (e.g., `ChatHistoryAgentThread` is in `semantic_kernel.agents`, not `semantic_kernel.contents.chat_history`). When the smoke run hits an `ImportError`, check the installed package directly (`uv run python -c "from <module> import <class>"`) rather than guessing at alternative paths.

---

## Step 4: Capture Spans & Session Dump

After the smoke run, capture raw spans and the ingested session for a tracing sanity check.

### Span capture

Add span capture after tracer init (before instrumentor):
```python
from capture_spans import setup_span_capture
setup_span_capture("{{framework}}", tracer)
```

Use `session_name="{{framework}}-example-update"` and `verbose=True` on the tracer so the run is easy to find.

Run with `CAPTURE_SPANS=true`:
```bash
cd python-sdk && CAPTURE_SPANS=true uv run python examples/integrations/{{framework}}_example.py
```

Verify: Raw span dump exists in `span_dumps/`.

### Session dump

Wait ~10s for ingestion propagation, then retrieve the ingested session:

```python
import json, os, time
from honeyhive import HoneyHive

time.sleep(10)
client = HoneyHive(api_key=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
resp = client.events.get_by_session_id(session_id="<session_id>", project=os.environ["HH_PROJECT"])
with open("span_dumps/{{framework}}_session.json", "w") as f:
    json.dump([vars(e) for e in resp.events], f, indent=2, default=str)
```

> **API gotchas**: The `HoneyHive` client uses `api_key=` (not `bearer_token=`). The `get_by_session_id` method uses `project=` (not `project_name=`). The response is an `EventExportResponse` object — access `.events` for the list, and use `vars(e)` for serialization (events don't have `.to_dict()`).

Save to `span_dumps/` alongside the raw span dump. Leave both dump files in place during the testing cycle — they get cleaned up in Step 7.

---

## Step 5: Tracing Sanity Check

Quick sanity check across the span dump, session dump, and UI.

**Trace Structure:**
- [ ] All expected spans present (none dropped)
- [ ] No duplicate spans from multiple instrumentation scopes
- [ ] Parent-child nesting matches execution flow

**Event Type Classification:**
- [ ] LLM calls are `model` events, tool calls are `tool` events, agent/orchestration spans are `chain` events

**Attribute Completeness:**
- [ ] System prompts, conversation history, tool args/results present
- [ ] Token counts and model name present

**UI Cleanliness:**
- [ ] Inputs and outputs are clean in session dump - this will be shown in UI to user finally

**Session Context:**
- [ ] Session groups turns correctly

If issues are found, list them in the report.

---

## Step 6: Verify in UI

Open https://fe.testing-cp-1.honeyhive.ai, find the session, and take screenshots of different event types.

Session link: `https://fe.testing-cp-1.honeyhive.ai/datastore/sessions/<session_id>/<project_id>`

Verify: Trace is visible with events rendering correctly. Inputs and outputs should be cleanly visible for model events and tool calls. Share screenshots for these if possible.

---

## Step 7: Clean Up

Remove debug scaffolding before committing:
- Remove `setup_span_capture` import and call
- Remove `verbose=True` from tracer init (unless it was already there)
- Revert `session_name` if you changed it

Examples are public-facing SDK code — no debug instrumentation should be committed.

---

## Step 8: Generate & Format

```bash
cd python-sdk && make generate && make format
```

`make generate` regenerates the client from the OpenAPI spec. CI will block the PR if generated code is stale. Both commands must exit 0.

---

## Step 9: Open PR (only if changes were made)

If you updated the example, open a PR in `honeyhiveai/python-sdk`. Include the report below in the PR description. If no changes were made, skip.

---

## Report

```
## Example Update: {{package}}

**File:** python-sdk/examples/integrations/{{framework}}_example.py
**Framework version:** [version]
**Status:** New | Updated | Already current | Blocked

### Patterns Covered
- Agent names/hierarchy: [yes/no]
- System instructions: [yes/no]
- User input/model output: [yes/no]
- Tool calls (args + results): [yes/no]
- Session continuity: [yes/no]
- [any additional framework-specific patterns]

### Changes Made
- [list of what changed and why, or "No changes — example already current"]

### Tracing Issues Found
- [numbered list with category and severity, or "None found"]

### Links
- UI trace: [link]
- PR: [link, or "No changes"]
```
