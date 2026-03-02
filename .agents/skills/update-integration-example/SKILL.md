---
name: update-integration-example
description: Update or create SDK integration examples for AI frameworks. Use when asked to update, create, or review a framework example in honeyhiveai/python-sdk. Covers framework API research, example writing, smoke testing, span capture, and tracing sanity checks.
metadata:
  author: sanjeed5
  version: "1.0"
---

# Update Integration Example

Update the SDK example for a framework integration. The example is a public-facing reference showing how to use HoneyHive with the framework. It must be correct, comprehensive, and use the framework's current APIs.

This skill does NOT do deep tracing validation. 

## Inputs

These variables are provided when the skill is invoked:

- `{{package}}` — PyPI package name (e.g., `pydantic-ai`)
- `{{version}}` — Last-tested version
- `{{framework}}` — Framework identifier for file paths (e.g., `pydantic_ai`)

## Setup

- The `honeyhiveai/python-sdk` repo has testing env credentials configured — no extra env setup needed.
- Initialize HoneyHive tracer with `source=integrations_checker`.
- Read existing examples in `python-sdk/examples/integrations/` to match style and conventions.

## Step 1: Research Framework

Framework APIs change quickly. Research the current state before touching code.

Checklist:
- Current stable version on PyPI (we last tested `{{version}}`) and any breaking changes
- Major patterns: agent types, orchestration, tools, callbacks/state, sessions
- Current recommended API surface (not deprecated methods)
- Tracing path: native OTel vs OpenInference instrumentor vs other
- All documented multi-agent patterns (delegation, hand-off, graphs, etc.)

Output (post as thread update):
- Latest stable version
- Breaking changes since `{{version}}`: [none | list]
- Tracing approach: native OTel | OpenInference instrumentor | other
- Patterns to cover: [list]

If the framework fundamentally changed (dropped OTel, total API redesign), report that to user. 

## Step 2: Update Example (only if needed)

Target: `python-sdk/examples/integrations/{{framework}}_example.py`

**Gate:** Compare existing example against Step 1 research. If it already uses current APIs, covers all required patterns, and has no deprecated methods — skip to Step 3 and note "already current."

**Rules (if updating):**
- One comprehensive example covering major agent patterns
- Use official framework style and current APIs
- HoneyHive integration should be minimal: init tracer + instrumentor
- Domain: customer support with order status/policy lookup mock tools, order IDs ORD-1001 to ORD-1003 (match existing examples like `openinference_google_adk_example.py` and `pydantic_ai_integration.py`)
- Never use HoneyHive-specific themes. Never copy scenarios from the framework's official docs
- Include install instructions with explicit packages (uv and/or pip)

**Must exercise:**
- Agent names and hierarchy
- System instructions
- User input and model output
- Tool calls (arguments and results)
- Session continuity across turns

Verify: No syntax errors. Style matches existing examples.

## Step 3: Run Against Testing Environment

Add span capture after tracer init:
```python
from capture_spans import setup_span_capture
setup_span_capture("{{framework}}", tracer)
```

Use `session_name="{{framework}}-example-update"` and `verbose=True` on the tracer.

```bash
cd python-sdk && CAPTURE_SPANS=true uv run python examples/integrations/{{framework}}_example.py
```

Verify: No import errors, agent runs to completion, tracer initializes, raw span dump exists in `span_dumps/`.

## Step 4: Retrieve Session Dump

Wait ~10s for ingestion propagation, then retrieve the ingested session:

```python
import json, os, time
from honeyhive import HoneyHive

time.sleep(10)
client = HoneyHive(bearer_token=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
result = client.events.get_by_session_id(session_id="<session_id>", project_name=os.environ["HH_PROJECT"])
with open("span_dumps/{{framework}}_session.json", "w") as f:
    json.dump([e.to_dict() for e in result], f, indent=2, default=str)
```

Verify: Session dump file exists in `span_dumps/`.
Post thread update with session ID and link: 
https://<frontend-host>/datastore/sessions/<session_id>/<project_id>

## Step 5: Tracing Sanity Check

Quick check (not a full validation). For every raw span, find its ingested event and check:

- **Trace Structure:** All spans present, no duplicates, meaningful names, correct nesting
- **Event Types:** LLM calls are model events, tool calls are tool events, agent spans are agent events
- **Attributes:** System prompts, conversation history, tool I/O, token counts, model name captured
- **UI Cleanliness:** Inputs/outputs render cleanly — no empty objects, no raw attribute dumps
- **Session Context:** Session groups turns correctly

If issues found, list them in the report. 

## Step 6: Verify in UI

Open https://fe.testing-cp.honeyhive.ai, find the session ( https://fe.testing-cp.honeyhive.ai/datastore/sessions/<session_id>/<project_id>) , take screenshots of different event types.
Verify: Trace visible with events rendering correctly. Especially input and output should be cleanly visible for model events and tool calls. 

## Step 7: Format

```bash
cd python-sdk && make format
```

Verify: Exits 0.

## Step 8: Open PR (only if changes were made)

If you updated the example, open a PR in `honeyhiveai/python-sdk`. Include the report below in the PR description. If no changes, skip.

## Report

Post in the Slack thread:

```
## Example Update: {{package}}

**File:** python-sdk/examples/integrations/{{framework}}_example.py
**Framework version:** [version]
**Status:** Updated | Already current | Blocked

### Patterns Covered
- Agent names/hierarchy: [yes/no]
- System instructions: [yes/no]
- User input/model output: [yes/no]
- Tool calls (args + results): [yes/no]
- Session continuity: [yes/no]

### Changes Made
- [list, or "No changes"]

### Tracing Issues Found
- [numbered list with severity, or "None"]

### Links
- UI trace: [link]
- PR: [link, or "No changes"]
```
