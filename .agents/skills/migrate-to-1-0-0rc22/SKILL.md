---
name: migrate-to-1-0-0rc22
description: Use when upgrading customer code that imports `honeyhive` to >= 1.0.0rc22 from rc21 or earlier. Covers the typed-Pydantic-model migration on `client.events`, `client.datapoints`, `client.datasets`, and `client.metrics` (dict subscript → attribute access on nested response fields), the OpenTelemetry minimum bump (1.20 → 1.41), and the `event_type` Pydantic-required tightening on event creation.
metadata:
  version: "1.0"
---

# Migrate to HoneyHive Python SDK v1.0.0rc22

Upgrade callers of the `honeyhive` SDK from rc21 (or earlier) to **>= 1.0.0rc22**. The bulk of the migration is mechanical: nested response fields that were `Dict[str, Any]` are now typed Pydantic models, so `response.result["key"]` becomes `response.result.key`. Request-side code does not change.

## When to Use

Trigger this migration when **all** of the following are true:

- A project imports `honeyhive` and is being upgraded to `>= 1.0.0rc22`.
- The code contains any of these patterns:
  - `response.result["..."]` on a `client.datapoints.*` or `client.datasets.*` return value.
  - `m["..."]` on items from `client.metrics.list()` or `get_metric()`.
  - `event["..."]` on items in `response.events` from `client.events.export()` / `.get_by_session_id()`.
  - A pinned `opentelemetry-*` floor below `1.41.0` (or a Traceloop instrumentor floor below `0.58.0`).

If none of these patterns appear, the upgrade is drop-in — no code change needed.

## What Changed

In rc22 the SDK regenerated from a flattened OpenAPI spec. ~15 fields that were previously `Dict[str, Any]` are now concrete Pydantic models with `extra="allow"`. From the caller's perspective:

- **Responses** — read nested fields with attribute access. **This is the only required code change.**
- **Requests** — no change. Pydantic coerces raw dicts at construction time, and `extra="allow"` lets unknown fields pass through to the wire untouched.

## Quick Reference

| Wrapper | Affected field | New typed model | Example attribute |
|---|---|---|---|
| `client.events.export()` / `.get_by_session_id()` | `response.events[i]` | `LegacyEvent` | `.event_id`, `.metadata` |
| `client.datapoints.create()` (sync, async, `add_datapoint*`) | `response.result` | `CreateDatapointResponseResult` | `.insertedIds` |
| `client.datapoints.update()` (sync, async, `update_datapoint*`) | `response.result` | `UpdateDatapointResponseResult` | `.modifiedCount` |
| `client.datasets.create()` | `response.result` | `InsertResult` | `.insertedId` |
| `client.datasets.update()` | `response.result` | `Dataset` | `.name`, `.id`, etc. |
| `client.datasets.delete()` | `response.result` | `DeleteResult` | `.id` |
| `client.metrics.list()` / `get_metric()` | each list item | `MetricItem` | `.name`, `.type`, etc. |

## Migration

For each affected wrapper, replace dict subscript with attribute access on the typed model.

### `client.events.export()` / `client.events.get_by_session_id()`

```python
# before
event_id = response.events[0]["event_id"]
metadata = response.events[0].get("metadata") or {}

# after
event_id = response.events[0].event_id
metadata = response.events[0].metadata or {}
```

### `client.datapoints.create()` (sync, async, legacy `add_datapoint`)

```python
# before
new_ids = response.result["insertedIds"]

# after
new_ids = response.result.insertedIds
```

### `client.datapoints.update()` (sync, async, legacy `update_datapoint`)

```python
# before
count = response.result["modifiedCount"]

# after
count = response.result.modifiedCount
```

### `client.datasets.create()` / `.update()` / `.delete()`

```python
# before
new_id     = create_resp.result["insertedId"]
ds_name    = update_resp.result["name"]
deleted_id = delete_resp.result["id"]

# after
new_id     = create_resp.result.insertedId
ds_name    = update_resp.result.name
deleted_id = delete_resp.result.id
```

### `client.metrics.list()` / legacy `get_metric()`

```python
# before
metrics = client.metrics.list()
names = [m["name"] for m in metrics]

# after
metrics = client.metrics.list()
names = [m.name for m in metrics]
```

## Escape Hatch

If a downstream consumer truly needs the dict shape (logging, ad-hoc serialization, third-party APIs that expect dicts), call `model_dump()` on the typed model:

```python
raw = response.result.model_dump()        # nested models flattened to dicts
ev_raw = response.events[0].model_dump()
```

Prefer attribute access in new code; reserve `model_dump()` for boundary serialization.

## Stricter `event_type` Validation

`PostEventRequestEvent.event_type` is now a required Pydantic field. This is **not** a behavior change — calls that omitted `event_type` were already rejected by the HoneyHive backend with a 400. The only difference is the exception type: a Pydantic `ValidationError` raised at request-construction time instead of a server-side error after the round-trip.

If your code catches and handles invalid-event-payload errors, add `pydantic.ValidationError` to the catch:

```python
from pydantic import ValidationError

try:
    PostEventRequestEvent(inputs={...})  # missing event_type
except ValidationError as exc:
    ...
```

## Dependency Bumps

If your environment pins OpenTelemetry or Traceloop instrumentor versions, raise the floors:

| Package | rc21 floor | rc22 floor |
|---|---|---|
| `opentelemetry-api` | 1.20.0 | 1.41.0 |
| `opentelemetry-sdk` | 1.20.0 | 1.41.0 |
| `opentelemetry-exporter-otlp-proto-http` | 1.20.0 | 1.41.0 |
| `opentelemetry-instrumentation-*` (Traceloop) | 0.46.0 | 0.58.0 |

If you don't pin these, `pip install --upgrade honeyhive` resolves them automatically.

## Validation

After applying the migration:

1. **Static check** — search for remaining dict-subscript patterns:
   ```bash
   rg 'response\.result\[' .
   rg '\.events\[[0-9]+\]\[' .
   ```
   Both should return empty (or only matches inside `model_dump()` escape-hatch sites).

2. **Smoke test** — execute one representative call per affected wrapper and assert attribute access works:
   ```python
   resp = client.datapoints.create(...)
   assert hasattr(resp.result, "insertedIds")
   ```

3. **Type check** — run `mypy` or `pyright`. Type checkers now flag any leftover dict-subscript usage on typed responses, since `result` is no longer `Dict[str, Any]`.

## Common Pitfalls

- **Async + legacy aliases need migration too.** `add_datapoint`, `add_datapoint_async`, `update_datapoint`, `update_datapoint_async`, `get_metric`, etc. return the same typed responses as their canonical counterparts.
- **Don't `dict(model)` a typed response.** It iterates field names, not the wire shape. Use `model_dump()`.
- **Unknown wire fields still work.** Because every generated model sets `extra="allow"`, fields the backend adds in the future are accessible via attribute access on the typed model — no SDK upgrade needed for additive API changes.
- **Request-side nested fields are dict-coercible.** When constructing a request model, you can still pass raw dicts for *nested* fields — Pydantic coerces them into the typed sub-models (e.g. `PostEventRequest(event={...})` works; the inner dict becomes a `PostEventRequestEvent`). The top-level argument to wrapper methods like `client.events.create(...)` / `client.datapoints.create(...)` must be a constructed request model — passing a bare dict raises `AttributeError`, since the wrappers call `.model_dump()` on the input.
