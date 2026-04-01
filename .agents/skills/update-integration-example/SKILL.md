---
name: update-integration-example
description: Build or update SDK integration examples for AI frameworks. Use when asked to update, create, or review a framework example in python-sdk/examples/integrations/. Covers framework API research, example writing, smoke testing, span capture, tracing sanity checks, and creating/updating the corresponding integration doc in honeyhive-ai-docs.
metadata:
  author: sanjeed5
  version: "2.6"
---

# Update Integration Example

Build or update the SDK example for a framework integration, then create or update the corresponding integration doc in `honeyhiveai/honeyhive-ai-docs`. The example is a public-facing reference that shows how to use HoneyHive with the framework. It must be correct, comprehensive, and follow the framework's current recommended APIs. The integration doc is the user-facing documentation page derived from the example.

This skill does NOT do deep tracing validation — only a sanity check.

## Integration Type: Model Provider vs Agent Framework

Before writing any example, determine the integration type:

### Model Provider Integrations (OpenAI, Anthropic, Azure OpenAI, AWS Bedrock, Gemini, etc.)

**Simple LLM call examples only.** These demonstrate basic tracing setup with the provider's SDK.
- Init tracer → init instrumentor → make 2-3 simple API calls → cleanup
- No tools, no agents, no multi-turn orchestration
- Show the provider's simplest chat/completion API
- Keep it concise
- Example pattern: `openinference_openai_example.py`

### Agent Framework Integrations (ADK, PydanticAI, CrewAI, LangGraph, etc.)

**Comprehensive agent examples with tools.** These demonstrate the framework's agent patterns.
- Agent names/hierarchy, system instructions, tool calls, session continuity
- Use the shared customer support domain (order status/policy lookup mock tools)
- Follow the full checklist in Step 2 below

If the integration is a model provider, skip the agent-specific checklist items in Step 2 (tool calls, agent hierarchy, session continuity) and write a simple example instead.

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

> Use web search to find the framework's official docs, then fetch and read the relevant docs pages directly. For exact imports, method names, and parameters, verify against the docs page and the installed package or source code instead of relying on summaries alone.

Checklist:
- [ ] Current stable version on PyPI (we last tested `{{version}}`) and any recent breaking changes
- [ ] Major patterns: agent types, orchestration, tools, callbacks/state, runtime/session
- [ ] Current recommended API surface (not deprecated methods)
- [ ] Tracing path: native OTel vs OpenInference instrumentor vs other. Prefer the simplest setup that yields complete spans without duplicates or conflicting instrumentation.
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

### Must showcase (agent framework integrations only)

- [ ] Agent names and hierarchy
- [ ] System instructions
- [ ] User input and model output
- [ ] Tool calls (arguments and results)
- [ ] Session continuity across turns
- [ ] `@trace` decorator for custom business logic (see below)

### `@trace` Decorator Pattern

Every agent framework example should include a scenario demonstrating the `@trace` decorator wrapping custom business logic around framework calls. This creates a parent span that groups the agent invocation and any surrounding business logic (validation, post-processing) into a single trace node in HoneyHive.

**Import:**
```python
from honeyhive import HoneyHiveTracer, enrich_span, trace
```

**Usage:**
```python
@trace(event_type="chain")
def handle_workflow(input_data: str) -> dict:
    # Framework calls inside become child spans
    result = framework_module(input=input_data)

    enrich_span(
        metadata={"key": "value"},  # Custom metadata
    )
    enrich_span(
        metrics={"steps_completed": 1},  # Custom metrics
    )
    return {"output": result}
```

**Requirements:**
- Use `event_type="chain"` for orchestration/workflow spans, `"tool"` for tool-like operations
- Use a descriptive `event_name` matching the function's purpose (optional — defaults to the function name)
- Works with both sync and async functions
- Add a dedicated scenario (e.g., "escalation workflow") that wraps agent calls with pre/post-processing to demonstrate the pattern clearly

**When to use `@trace` vs instrumentor-only:**
- Instrumentor alone is sufficient for tracing agent/LLM/tool spans automatically
- Use `@trace` when you want a **parent span** grouping multiple operations (e.g., agent call + validation + response formatting) into one logical unit

See `dspy_integration.py` Scenario 4 for a complete implementation.

For **model provider** integrations, only showcase:
- [ ] Tracer + instrumentor initialization
- [ ] 2-3 simple API calls (basic chat completions / message creation)
- [ ] Proper cleanup (flush + uninstrument)

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

When docs, release notes, or search results disagree with runtime behavior, use the installed package or source code to resolve the mismatch, then rerun until the example matches reality.

---

## Step 4: Capture Spans & Session Dump

After the smoke run, capture raw spans and the ingested session for a tracing sanity check.

Store temporary artifacts in a gitignored scratch directory such as `.tmp/integration-example-dumps/{{framework}}/`. Keep raw dumps and session dumps there rather than in tracked paths.

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

Verify: Raw span dump exists in `.tmp/integration-example-dumps/{{framework}}/`.

### Session dump

Wait ~10s for ingestion propagation, then retrieve the ingested session:

```python
import json, os, time
from pathlib import Path
from honeyhive import HoneyHive

time.sleep(10)
dump_dir = Path(".tmp/integration-example-dumps/{{framework}}")
dump_dir.mkdir(parents=True, exist_ok=True)
client = HoneyHive(api_key=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"])
resp = client.events.get_by_session_id(session_id="<session_id>")
with open(dump_dir / "{{framework}}_session.json", "w") as f:
    json.dump(resp.events, f, indent=2, default=str)
```

Save the session dump in the same gitignored dump directory as the raw spans. Keep both artifacts during comparison, then remove them in Step 7.

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

Open the testing UI for the current environment, find the session, and take screenshots of different event types.

Verify: Trace is visible with events rendering correctly. Inputs and outputs should be cleanly visible for model events and tool calls. Share screenshots for these if possible.

---

## Step 7: Clean Up

Remove debug scaffolding before committing:
- Remove `setup_span_capture` import and call
- Remove `verbose=True` from tracer init (unless it was already there)
- Revert `session_name` if you changed it
- Remove temporary artifacts from `.tmp/integration-example-dumps/{{framework}}/` when you no longer need them

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

## Step 10: Create/Update Integration Doc in honeyhive-ai-docs

After the SDK example is complete and verified, create or update the corresponding integration doc in `honeyhiveai/honeyhive-ai-docs`.

> **File naming**: Replace underscores with hyphens for doc filenames (e.g., `pydantic_ai` -> `pydantic-ai.mdx`).

1. Clone or navigate to `honeyhive-ai-docs`. Branch off the base branch documented in that repo's `AGENTS.md`.
2. Read that repo's `AGENTS.md` for writing guidelines, versioning rules, and navigation config.
3. Use existing beta integration docs in `beta/integrations/` as templates (e.g., `pydantic-ai.mdx`, `google-adk.mdx`, `strands.mdx`).
4. Create or update `beta/integrations/{{framework}}.mdx`. Simplify code from the SDK example - focus on the integration pattern, not every feature. Include screenshots from Step 6 if available.
   - **"What Gets Traced" should only list what the instrumentor captures** — do not include SDK-level features (e.g., session continuity) that aren't instrumentor-related.
5. If this is a new page, add it to the navigation config as documented in `AGENTS.md`.
6. Open a PR following that repo's PR conventions.

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
- @trace decorator pattern: [yes/no]
- [any additional framework-specific patterns]

### Changes Made
- [list of what changed and why, or "No changes — example already current"]

### Tracing Issues Found
- [numbered list with category and severity, or "None found"]

### Integration Doc
- **File:** honeyhive-ai-docs/beta/integrations/{{framework}}.mdx
- **Status:** New | Updated | Already current | Skipped
- **Docs PR:** [link, or "No changes"]

### Links
- UI trace: [link]
- SDK PR: [link, or "No changes"]
- Docs PR: [link, or "No changes"]
```

## Skill Notes

- Keep durable, framework-specific notes in `references/` under this skill directory (Agent Skills optional dir), and keep `SKILL.md` focused on workflow/checklists.
