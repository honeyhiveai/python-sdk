"""Core experiment functionality.

This module provides the core experiment execution functionality including:
- ExperimentContext for organizing experiment metadata
- run_experiment() with tracer multi-instance pattern
- Integration with backend result endpoints
"""

# pylint: disable=too-many-lines
import asyncio
import functools
import inspect
import os
import threading
import uuid
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from uuid import UUID

import httpx

from honeyhive._generated.api_config import HTTPException
from honeyhive.api.client import HoneyHive
from honeyhive.experiments.evaluators import evaluator as evaluator_class
from honeyhive.experiments.results import get_run_result
from honeyhive.experiments.utils import (
    prepare_external_dataset,
    prepare_run_request_data,
)
from honeyhive.models import (
    PostExperimentRunRequest,
    PutExperimentRunRequest,
    UpdateEventRequest,
)
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.tracer.instrumentation.decorators import trace
from honeyhive.tracer.lifecycle.flush import force_flush_tracer
from honeyhive.utils.git_context import get_git_context
from honeyhive.utils.logger import get_logger, safe_log

# Module-level logger for orchestration code (no tracer instance yet)
logger = get_logger("honeyhive.experiments.core")

# Process-wide lock guarding the instrumentor lifecycle in run_experiment.
# Serializes concurrent evaluate() calls in the same interpreter against
# BaseInstrumentor's non-atomic check-then-set in instrument().
_INSTRUMENTOR_LIFECYCLE_LOCK = threading.Lock()


# Acceptable scalar score types. Mirrors the server-side evaluator contract
# (see services/data_plane/dp_evaluation_service/app/services/metric_update_service.js
# castResultToReturnType): scores must be bool | float | str so that
# compareRunMetrics — which only diffs typeof === 'number' | 'boolean' — can
# pair them across runs.
ScalarScore = Union[bool, int, float, str]


def _is_scalar_metric_value(value: Any) -> bool:
    """Return True if `value` is safe to drop into `event.metrics` as-is.

    The backend's metrics field is `Record<string, unknown>` (no validation),
    but compareRunMetrics ignores everything that isn't bool/number, so
    non-scalar values are silently lost during run comparison. We refuse to
    write them.
    """
    if isinstance(value, bool):  # bool is a subclass of int — check first.
        return True
    if isinstance(value, (int, float, str)):
        return True
    return False


@dataclass
class EvaluatorMetricResult:
    """One evaluator's verdict for one datapoint, normalized.

    Score is the bare ``metrics[eval_name]`` value. ``explanation`` becomes
    ``metrics[f"{eval_name}_explanation"]``. Each ``extras`` entry becomes
    ``metrics[f"{eval_name}_{key}"]``.
    """

    eval_name: str
    score: Optional[ScalarScore] = None
    explanation: Optional[str] = None
    extras: Dict[str, ScalarScore] = field(default_factory=dict)

    def to_metric_attrs(self) -> Dict[str, Any]:
        """Flatten into the dict shape expected by ``enrich_span(metrics=…)``."""
        attrs: Dict[str, Any] = {}
        if self.score is not None:
            attrs[self.eval_name] = self.score
        if self.explanation is not None:
            attrs[f"{self.eval_name}_explanation"] = self.explanation
        for key, value in self.extras.items():
            attrs[f"{self.eval_name}_{key}"] = value
        return attrs

    @classmethod
    def from_raw(cls, eval_name: str, raw: Any) -> "EvaluatorMetricResult":
        """Parse an evaluator's raw return value into the canonical metrics shape.

        Accepts:
          * scalar (bool/int/float/str) → ``score``
          * 1-element list/tuple → element coerced to scalar (legacy behavior)
          * dict → ``score`` + optional ``explanation`` + scalar extras flattened
          * None → score stays None (failed evaluator path)

        Non-scalar score values are rejected with a warning; non-scalar
        extras are dropped with a warning. Score-less dicts log a warning
        but still surface their scalar entries as extras so the data
        isn't lost outright.
        """
        # Legacy coercion: list/tuple of length 1 unwrapped to its element.
        if isinstance(raw, (list, tuple)) and len(raw) == 1:
            raw = raw[0]

        if raw is None:
            return cls(eval_name=eval_name)

        if _is_scalar_metric_value(raw):
            return cls(eval_name=eval_name, score=raw)

        if isinstance(raw, dict):
            return cls._from_dict(eval_name, raw)

        # Unknown return shape — refuse to invent semantics.
        logger.warning(
            "Evaluator %s returned an unsupported value type %s; dropping its metric for this datapoint.",
            eval_name,
            type(raw).__name__,
        )
        return cls(eval_name=eval_name)

    @classmethod
    def _from_dict(cls, eval_name: str, raw: Dict[str, Any]) -> "EvaluatorMetricResult":
        """Dict-shape branch of ``from_raw``, split out to keep nesting shallow."""
        score: Optional[ScalarScore] = None
        explanation: Optional[str] = None
        extras: Dict[str, ScalarScore] = {}

        if "score" in raw:
            raw_score = raw["score"]
            if _is_scalar_metric_value(raw_score):
                score = raw_score
            else:
                logger.warning(
                    "Evaluator %s returned a non-scalar 'score' value (%s); "
                    "dropping the score (compareRunMetrics only diffs scalar "
                    "metrics, so a nested value would be silently lost "
                    "during comparison).",
                    eval_name,
                    type(raw_score).__name__,
                )
        else:
            logger.warning(
                "Evaluator %s returned a dict missing 'score' key; the bare "
                "metrics[%s] entry won't be written, but scalar dict "
                "entries will surface as %s_<key> for diagnostics.",
                eval_name,
                eval_name,
                eval_name,
            )

        if "explanation" in raw:
            raw_expl = raw["explanation"]
            if isinstance(raw_expl, str):
                explanation = raw_expl
            elif raw_expl is not None:
                # Coerce non-string explanations to str rather than dropping —
                # they're informational and the UI just renders the value.
                explanation = str(raw_expl)

        for key, value in raw.items():
            if key in ("score", "explanation"):
                continue
            if _is_scalar_metric_value(value):
                extras[key] = value
            else:
                logger.warning(
                    "Evaluator %s returned a non-scalar extra '%s' (%s); dropping it from event.metrics.",
                    eval_name,
                    key,
                    type(value).__name__,
                )

        return cls(
            eval_name=eval_name,
            score=score,
            explanation=explanation,
            extras=extras,
        )


class ExperimentContext:  # pylint: disable=too-few-public-methods
    """
    Lightweight experiment context for metadata linking.

    NOTE: This is NOT a replacement for tracer config. This is just
    a convenience class for organizing experiment metadata that gets
    passed to the tracer.

    The tracer handles actual metadata propagation when is_evaluation=True.

    Attributes:
        run_id: Experiment run identifier
        dataset_id: Dataset identifier (may have EXT- prefix)
        source: Source identifier (default: "evaluation")
        metadata: Additional metadata dictionary

    Example:
        >>> context = ExperimentContext(
        ...     run_id="run-123",
        ...     dataset_id="EXT-abc",
        ... )
        >>> tracer_config = context.to_tracer_config("dp-1")
        >>> tracer_config["is_evaluation"]
        True
    """

    def __init__(
        self,
        run_id: str,
        dataset_id: str,
        *,
        run_name: Optional[str] = None,
        source: str = "evaluation",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize experiment context.

        Args:
            run_id: Experiment run identifier
            dataset_id: Dataset identifier
            run_name: Experiment run name (used for session naming)
            source: Source identifier (default: "evaluation")
            metadata: Additional metadata
        """
        self.run_id = run_id
        self.dataset_id = dataset_id
        self.run_name = run_name
        self.source = source
        self.metadata = metadata or {}

    def to_tracer_config(self, datapoint_id: str) -> Dict[str, Any]:
        """
        Convert to tracer initialization config.

        This returns kwargs for HoneyHiveTracer(...) initialization.
        The tracer will automatically propagate all metadata to spans
        when is_evaluation=True.

        Args:
            datapoint_id: Datapoint identifier for this execution

        Returns:
            Dictionary of tracer initialization kwargs

        Example:
            >>> config = context.to_tracer_config("dp-1")
            >>> config
            {
                'is_evaluation': True,
                'run_id': 'run-123',
                'dataset_id': 'EXT-abc',
                'datapoint_id': 'dp-1',
                'source': 'evaluation'
            }
        """
        return {
            "is_evaluation": True,
            "run_id": self.run_id,
            "dataset_id": self.dataset_id,
            "datapoint_id": datapoint_id,
            "source": self.source,
        }


def run_experiment(
    function: Callable,
    dataset: List[Dict[str, Any]],
    datapoint_ids: List[str],
    *,
    server_url: Optional[str] = None,
    experiment_context: ExperimentContext,
    api_key: Optional[str] = None,
    max_workers: int = 10,
    verbose: bool = False,
    instrumentors: Optional[List[Callable[[], Any]]] = None,
    evaluators: Optional[List[Callable]] = None,
) -> List[Dict[str, Any]]:
    """
    Run experiment with tracer multi-instance pattern.

    CRITICAL: Each datapoint gets its OWN tracer instance for isolation.
    This prevents:
    - Metadata contamination between datapoints
    - Race conditions in concurrent execution
    - Session ID collisions

    Threading Model:
    - Uses ThreadPoolExecutor (not multiprocessing)
    - I/O-bound operations (LLM calls, API requests)
    - Each tracer instance is completely isolated
    - Python 3.11+ GIL improvements for I/O

    Args:
        function: User function to execute against each datapoint. Can be either
            a synchronous function or an async function. Async functions are
            automatically detected and executed with asyncio.run().
        dataset: List of datapoint dictionaries
        datapoint_ids: List of datapoint IDs (parallel to dataset)
        experiment_context: ExperimentContext with run metadata
        api_key: HoneyHive API key for tracer (or set HONEYHIVE_API_KEY env var)
        max_workers: ThreadPool size (default: 10)
        verbose: Enable verbose logging
        instrumentors: List of instrumentor factory functions. Each factory should
            return a new instrumentor instance when called. This ensures each
            datapoint gets its own instrumentor instance for proper trace routing.
            Example: [lambda: OpenAIInstrumentor(), lambda: AnthropicInstrumentor()]
        evaluators: Optional list of evaluator callables. When set, each
            evaluator runs inline on the user function's outputs inside
            the per-datapoint chain span; their normalized scores attach
            to the chain span via ``enrich_span`` before the span closes.

    Returns:
        List of execution results (one per datapoint)

    Examples:
        >>> def my_function(inputs, ground_truth):
        ...     return {"output": "test"}
        >>>
        >>> # Async functions are also supported
        >>> async def my_async_function(inputs, ground_truth):
        ...     result = await some_async_call()
        ...     return {"output": result}
        >>>
        >>> context = ExperimentContext(
        ...     run_id="run-123",
        ...     dataset_id="ds-456",
        ... )
        >>>
        >>> results = run_experiment(
        ...     function=my_function,  # or my_async_function
        ...     dataset=[{"inputs": {}, "ground_truth": {}}],
        ...     datapoint_ids=["dp-1"],
        ...     experiment_context=context,
        ...     api_key="hh_...",
        ...     max_workers=10,
        ...     instrumentors=[lambda: OpenAIInstrumentor()]
        ... )
    """
    is_async = asyncio.iscoroutinefunction(function)
    user_fn_accepts_tracer = "tracer" in inspect.signature(function).parameters

    # Whole-experiment instrumentor lifecycle. The first datapoint into the
    # pool acquires _INSTRUMENTOR_LIFECYCLE_LOCK, binds each instrumentor to
    # its tracer.provider, and records that tracer in binding_tracer. Later
    # datapoints find active_instrumentors populated and skip. Cleanup runs
    # once after the pool drains.
    #
    # binding_tracer is the transport path for every wrapped call across the
    # experiment — all such spans flow through its provider's
    # BatchSpanProcessor, so it gets one more force_flush at teardown to
    # catch anything emitted after its own datapoint's flush ran.
    active_instrumentors: List[Any] = []
    binding_tracer: List[Any] = []  # singleton container so the closure can mutate it

    def process_datapoint(
        datapoint: Dict[str, Any], datapoint_id: str
    ) -> Dict[str, Any]:
        """
        Process single datapoint with isolated tracer and instrumentors.

        This function:
        1. Creates a NEW tracer instance for this datapoint
        2. Creates NEW instrumentor instances and sets tracer provider on them
        3. Executes the user function with tracer active
        4. Uninstruments all instrumentors
        5. Flushes the tracer to ensure all spans sent
        6. Returns result with status
        """
        # Extract inputs and ground truths from datapoint
        inputs = datapoint.get("inputs", {})
        ground_truth = datapoint.get("ground_truth")

        # Create tracer config for this datapoint with inputs
        tracer_config = experiment_context.to_tracer_config(datapoint_id)
        tracer_config["inputs"] = inputs  # Set session inputs

        if experiment_context.run_name:
            tracer_config["session_name"] = experiment_context.run_name

        # Create NEW tracer instance for this datapoint
        # Each tracer is completely isolated (own API client, logger, state)
        tracer = HoneyHiveTracer(
            api_key=api_key, server_url=server_url, verbose=verbose, **tracer_config
        )

        # Instrument once for the whole experiment under the module lock.
        # An instrumentor that raises here stays uninstrumented for the rest
        # of the experiment — install failures are deterministic (missing
        # dep, version mismatch), not transient.
        if instrumentors:
            with _INSTRUMENTOR_LIFECYCLE_LOCK:
                if not active_instrumentors:
                    binding_tracer.append(tracer)
                    for instrumentor_factory in instrumentors:
                        try:
                            instrumentor = instrumentor_factory()
                            instrumentor.instrument(tracer_provider=tracer.provider)
                            active_instrumentors.append(instrumentor)
                            if verbose:
                                safe_log(
                                    tracer,
                                    "info",
                                    "Initialized instrumentor %s for experiment",
                                    type(instrumentor).__name__,
                                )
                        except Exception as e:
                            safe_log(
                                tracer,
                                "warning",
                                "Failed to initialize instrumentor: %s",
                                str(e),
                            )

        try:
            # Execute function with tracer active
            # Tracer automatically adds all experiment metadata to spans!
            if verbose:
                # Use safe_log with tracer instance (multi-instance safety)
                safe_log(
                    tracer,
                    "info",
                    "Processing datapoint %s (run: %s)",
                    datapoint_id,
                    experiment_context.run_id,
                )

            # Wrap the user function so evaluators run before the chain span
            # closes — their scores attach to the still-recording span via
            # enrich_span(metrics=…) and ride out on the OTLP export.
            #
            # Sync and async user fns take separate paths so async evaluators
            # under an async user fn can be awaited directly; spinning up a
            # nested loop in the same thread that's already running one (via
            # asyncio.run below) would raise.

            def function_with_inline_evals(dp: Dict[str, Any]) -> Any:
                fn_outputs = (
                    function(dp, tracer=tracer)
                    if user_fn_accepts_tracer
                    else function(dp)
                )
                if evaluators:
                    _apply_inline_evaluators(
                        evaluators,
                        inputs=dp.get("inputs", {}),
                        outputs=fn_outputs,
                        ground_truth=dp.get("ground_truth"),
                        tracer=tracer,
                        max_workers=max_workers,
                        verbose=verbose,
                    )
                return fn_outputs

            async def afunction_with_inline_evals(dp: Dict[str, Any]) -> Any:
                fn_outputs = await (
                    function(dp, tracer=tracer)
                    if user_fn_accepts_tracer
                    else function(dp)
                )
                if evaluators:
                    await _aapply_inline_evaluators(
                        evaluators,
                        inputs=dp.get("inputs", {}),
                        outputs=fn_outputs,
                        ground_truth=dp.get("ground_truth"),
                        tracer=tracer,
                        verbose=verbose,
                    )
                return fn_outputs

            wrapped_for_trace = (
                afunction_with_inline_evals if is_async else function_with_inline_evals
            )
            functools.update_wrapper(wrapped_for_trace, function)
            # Drop __wrapped__ so inspect.signature(..., follow_wrapped=True) —
            # used by trace's input-capture path — stops at the closure's
            # (dp,) signature instead of walking back to the user fn's
            # (dp, tracer) and failing sig.bind(datapoint).
            try:
                del wrapped_for_trace.__wrapped__
            except AttributeError:
                pass

            traced_function = trace(
                event_type="chain",
                event_name=function.__name__,
                tracer=tracer,
            )(wrapped_for_trace)

            if verbose:
                safe_log(
                    tracer,
                    "info",
                    "Calling function (async=%s, accepts_tracer=%s, evaluators=%d)",
                    is_async,
                    user_fn_accepts_tracer,
                    len(evaluators or []),
                )
            if is_async:
                outputs = asyncio.run(traced_function(datapoint))
            else:
                outputs = traced_function(datapoint)

            # Capture session ID from tracer for linking to run
            # Outputs will be enriched later via UpdateEventRequest after tracer flush
            session_id = getattr(tracer, "session_id", None)

            return {
                "datapoint_id": datapoint_id,
                "inputs": inputs,
                "outputs": outputs,
                "ground_truth": ground_truth,
                "status": "success",
                "error": None,
                "session_id": session_id,  # Include session ID for run linkage
            }

        except Exception as e:
            # Use safe_log with tracer instance for error logging
            safe_log(
                tracer,
                "error",
                "Function execution failed for datapoint %s: %s",
                datapoint_id,
                str(e),
            )

            # Capture session ID even on failure
            session_id = getattr(tracer, "session_id", None)

            return {
                "datapoint_id": datapoint_id,
                "inputs": datapoint.get("inputs", {}),
                "outputs": None,
                "ground_truth": datapoint.get("ground_truth"),
                "status": "failed",
                "error": str(e),
                "session_id": session_id,  # Include session ID for run linkage
            }

        finally:
            # CRITICAL: Flush tracer to ensure all spans sent. Instrumentor
            # teardown happens once after the pool drains (in run_experiment)
            # so an early-finishing datapoint doesn't unwrap the client out
            # from under a sibling that's still mid-call.
            try:
                force_flush_tracer(tracer)
            except Exception as e:
                # Use safe_log for flush errors (tracer may be shutting down)
                safe_log(
                    tracer,
                    "warning",
                    "Failed to flush tracer for datapoint %s: %s",
                    datapoint_id,
                    str(e),
                )

    # Validate inputs
    if len(dataset) != len(datapoint_ids):
        raise ValueError(
            f"Dataset length ({len(dataset)}) does not match datapoint_ids length ({len(datapoint_ids)})"
        )

    if verbose:
        # Module-level orchestration logging (no tracer instance)
        logger.info(
            "Executing function against %d datapoints with %d workers",
            len(dataset),
            max_workers,
        )

    # Use ThreadPoolExecutor for I/O-bound concurrent execution
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all datapoint executions
        future_to_datapoint = {}
        for datapoint, datapoint_id in zip(dataset, datapoint_ids):
            future = executor.submit(process_datapoint, datapoint, datapoint_id)
            future_to_datapoint[future] = datapoint_id

        # Collect results as they complete
        for future in as_completed(future_to_datapoint):
            datapoint_id = future_to_datapoint[future]
            try:
                result = future.result()
                results.append(result)

                if verbose:
                    status = result.get("status", "unknown")
                    # Module-level logging (tracer already flushed)
                    logger.info("Completed datapoint %s: %s", datapoint_id, status)

            except Exception as e:
                # Module-level error logging (tracer context lost)
                logger.error(
                    "Unexpected error processing datapoint %s: %s",
                    datapoint_id,
                    str(e),
                    exc_info=True,
                )
                results.append(
                    {
                        "datapoint_id": datapoint_id,
                        "status": "failed",
                        "error": str(e),
                    }
                )

    # Flush the binding tracer. Every wrapped span across the experiment
    # was emitted through its provider, and short scripts / container
    # exits can race the BatchSpanProcessor's 5 s tick and atexit hook.
    if binding_tracer:
        try:
            force_flush_tracer(binding_tracer[0])
        except Exception as e:
            logger.warning("Failed to flush binding tracer for experiment: %s", str(e))

    # Uninstrument once every datapoint has finished — unwrapping the
    # wrapped client while a sibling is still mid-call would silently drop
    # its spans.
    for instrumentor in active_instrumentors:
        try:
            instrumentor.uninstrument()
            if verbose:
                logger.info(
                    "Uninstrumented %s for experiment",
                    type(instrumentor).__name__,
                )
        except Exception as e:
            logger.warning(
                "Failed to uninstrument %s: %s",
                type(instrumentor).__name__,
                str(e),
            )

    # Log summary
    success_count = sum(1 for r in results if r.get("status") == "success")
    failed_count = sum(1 for r in results if r.get("status") == "failed")

    if verbose:
        # Module-level summary logging
        logger.info(
            "Experiment execution complete: %d succeeded, %d failed",
            success_count,
            failed_count,
        )

    return results


def _update_run_with_results(  # pylint: disable=too-many-branches
    run_id: str,
    *,
    run_name: str,
    execution_results: List[Dict[str, Any]],
    external_dataset_id: str,
    client: Any,
    verbose: bool,
) -> None:
    """Update run with session IDs and final status."""
    # Collect session IDs from execution results
    session_ids = []
    for result in execution_results:
        session_id = result.get("session_id")
        if session_id:
            try:
                UUID(session_id)  # Validate UUID format
                session_ids.append(session_id)
            except (ValueError, TypeError) as e:
                if verbose:
                    logger.warning(
                        "Invalid session ID format: %s (%s)", session_id, str(e)
                    )

    if verbose:
        logger.info(
            "Updating run with results and status (%d sessions linked)",
            len(session_ids),
        )

    try:
        update_data: Dict[str, Any] = {
            "status": "completed",
            "name": run_name,
        }

        if session_ids:
            update_data["event_ids"] = session_ids

        # Build metadata
        update_metadata: Dict[str, Any] = {}

        if external_dataset_id and external_dataset_id.startswith("EXT-"):
            update_metadata["offline_dataset_id"] = external_dataset_id

        if update_metadata:
            update_data["metadata"] = update_metadata

        if verbose:
            logger.info(
                "Updating run %s with data: status=%s, name=%s, event_ids=%d, metadata_keys=%s",
                run_id,
                update_data.get("status"),
                update_data.get("name"),
                len(update_data.get("event_ids", [])),
                list(update_metadata.keys()) if update_metadata else [],
            )

        # Use experiments API with PutExperimentRunRequest
        update_request = PutExperimentRunRequest(**update_data)
        client.experiments.update_run(run_id, update_request)

        if verbose and session_ids:
            logger.info("Linked %d sessions to run %s", len(session_ids), run_id)
    except Exception as e:
        # Enhanced error logging for 400 errors
        error_msg = str(e)
        error_type = type(e).__name__

        # Try to extract response details from different exception types
        response_details = {}

        # Check if it's a HoneyHiveError with error_response
        # pylint: disable=no-member
        if hasattr(e, "error_response") and e.error_response:
            error_resp = e.error_response
            response_details = {
                "status_code": getattr(error_resp, "status_code", None),
                "error_code": getattr(error_resp, "error_code", None),
                "error_type": getattr(error_resp, "error_type", None),
                "details": getattr(error_resp, "details", {}),
            }
        # Check if it has a response attribute (HTTPStatusError)
        elif hasattr(e, "response"):
            try:
                response = e.response
                response_details = {
                    "status_code": getattr(response, "status_code", None),
                    "reason": getattr(response, "reason_phrase", None),
                }
                # Try to get error response body
                try:
                    if hasattr(response, "json"):
                        response_details["error_body"] = response.json()
                except Exception:
                    try:
                        if hasattr(response, "text"):
                            response_details["error_text"] = response.text[:500]
                    except Exception:
                        pass
            except Exception:
                pass
        # Check if it has details attribute (custom exceptions)
        elif hasattr(e, "details"):
            response_details = {"details": e.details}
        elif hasattr(e, "status_code"):
            response_details = {"status_code": e.status_code}

        # Log error details only in verbose mode
        if verbose:
            logger.warning(
                "Failed to update run %s: %s (%s). Update data: status=%s, "
                "name=%s, event_ids_count=%d, has_metadata=%s, "
                "metadata_keys=%s. Response: %s",
                run_id,
                error_msg,
                error_type,
                update_data.get("status"),
                update_data.get("name"),
                len(update_data.get("event_ids", [])),
                bool(update_data.get("metadata")),
                list(update_metadata.keys()) if update_metadata else [],
                (
                    response_details
                    if response_details
                    else "No response details available"
                ),
            )
        else:
            # Minimal error logging when not verbose
            logger.warning("Failed to update run %s: %s", run_id, error_msg)

        # Print warning for authentication exceptions per memory
        status_code = response_details.get("status_code")
        if (
            status_code in (401, 403)
            or "401" in error_msg
            or "403" in error_msg
            or "Authentication" in error_type
        ):
            logger.warning(
                "⚠️  AUTHENTICATION EXCEPTION: Failed to update run %s due to "
                "authentication error. Please check your API key and permissions.",
                run_id,
            )


def _enrich_session_with_results(
    session_id: str,
    *,
    outputs: Any,
    ground_truth: Any,
    client: Any,
    verbose: bool,
) -> None:
    """Enrich a session event with the user-function outputs and ground_truth."""
    try:
        update_data: Dict[str, Any] = {}

        if outputs is not None:
            update_data["outputs"] = outputs

        if ground_truth is not None:
            update_data["feedback"] = {"ground_truth": ground_truth}

        if update_data:
            client.events.update(
                data=UpdateEventRequest(
                    event_id=session_id,
                    feedback=update_data.get("feedback"),
                    outputs=update_data.get("outputs"),
                )
            )

            if verbose:
                logger.info(
                    "Enriched session %s with: %s",
                    session_id,
                    list(update_data.keys()),
                )
    except Exception as e:
        logger.warning("Failed to enrich session %s: %s", session_id, str(e))


def _resolve_eval_name(eval_func: Callable) -> str:
    """Resolve an evaluator's display name (handles ``@evaluator`` instances)."""
    if isinstance(eval_func, evaluator_class):
        return eval_func.name
    return getattr(eval_func, "__name__", str(eval_func))


def _eval_call_args(
    inputs: Dict[str, Any], outputs: Any, ground_truth: Optional[Any]
) -> Tuple[Any, ...]:
    """Build positional args for an evaluator, dropping ``ground_truth`` when None.

    Mirrors the legacy two-arg ``evaluator(outputs, inputs)`` signature so
    evaluators that don't accept ``ground_truth`` still work on datapoints
    without one.

    Caveat: an evaluator declared as ``def f(outputs, inputs, ground_truth)``
    (third arg required, no default) will raise ``TypeError`` on datapoints
    where ``ground_truth`` is absent. Declare ``ground_truth=None`` if the
    evaluator should run on unlabeled datapoints.
    """
    if ground_truth is not None:
        return (outputs, inputs, ground_truth)
    return (outputs, inputs)


def _log_eval_failure(eval_name: str, exc: Exception, verbose: bool) -> None:
    if verbose:
        logger.warning("Evaluator %s failed: %s", eval_name, str(exc))


def _run_single_evaluator(
    eval_func: Callable,
    inputs: Dict[str, Any],
    outputs: Any,
    ground_truth: Optional[Any],
    *,
    verbose: bool,
) -> EvaluatorMetricResult:
    """Run one evaluator synchronously and normalize the return.

    Must be invoked from a thread with no running event loop — async
    evaluators are dispatched via ``asyncio.run`` which would otherwise
    raise. The async-user-function path uses
    ``_arun_single_evaluator`` instead. Catches evaluator exceptions and
    surfaces them as ``EvaluatorMetricResult(score=None)`` so aggregation
    sees "ran but returned nothing" rather than dropping the evaluator.
    """
    eval_name = _resolve_eval_name(eval_func)
    args = _eval_call_args(inputs, outputs, ground_truth)
    try:
        if asyncio.iscoroutinefunction(eval_func):
            raw = asyncio.run(eval_func(*args))
        else:
            raw = eval_func(*args)
        return EvaluatorMetricResult.from_raw(eval_name, raw)
    except Exception as e:  # pylint: disable=broad-except
        _log_eval_failure(eval_name, e, verbose)
        return EvaluatorMetricResult(eval_name=eval_name)


async def _arun_single_evaluator(
    eval_func: Callable,
    inputs: Dict[str, Any],
    outputs: Any,
    ground_truth: Optional[Any],
    *,
    verbose: bool,
) -> EvaluatorMetricResult:
    """Async sibling of ``_run_single_evaluator``.

    Awaits async evaluators directly (so we never start a nested loop in
    a thread that's already running one — the bug fixed by routing the
    async-user-function path through here). Sync evaluators are
    dispatched to a worker thread via ``asyncio.to_thread`` to avoid
    blocking the loop on slow CPU-bound work.
    """
    eval_name = _resolve_eval_name(eval_func)
    args = _eval_call_args(inputs, outputs, ground_truth)
    try:
        if asyncio.iscoroutinefunction(eval_func):
            raw = await eval_func(*args)
        else:
            raw = await asyncio.to_thread(eval_func, *args)
        return EvaluatorMetricResult.from_raw(eval_name, raw)
    except Exception as e:  # pylint: disable=broad-except
        _log_eval_failure(eval_name, e, verbose)
        return EvaluatorMetricResult(eval_name=eval_name)


def _run_evaluators_for_datapoint(
    evaluators: List[Callable],
    inputs: Dict[str, Any],
    outputs: Any,
    ground_truth: Optional[Any],
    *,
    max_workers: int = 10,
    verbose: bool = False,
) -> List[EvaluatorMetricResult]:
    """Run every evaluator on one datapoint's outputs in parallel.

    Evaluator function signature::

        evaluator(outputs, inputs, ground_truth) -> scalar | dict

    See ``EvaluatorMetricResult.from_raw`` for accepted return shapes.
    """
    if not evaluators:
        return []

    if len(evaluators) == 1:
        # Skip the thread-pool overhead for the common single-evaluator case.
        return [
            _run_single_evaluator(
                evaluators[0], inputs, outputs, ground_truth, verbose=verbose
            )
        ]

    results: List[EvaluatorMetricResult] = []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(evaluators))) as executor:
        futures = [
            executor.submit(
                _run_single_evaluator,
                eval_func,
                inputs,
                outputs,
                ground_truth,
                verbose=verbose,
            )
            for eval_func in evaluators
        ]
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:  # pylint: disable=broad-except
                if verbose:
                    logger.warning("Failed to collect evaluator result: %s", str(e))
    return results


def _apply_inline_evaluators(
    evaluators: List[Callable],
    inputs: Dict[str, Any],
    outputs: Any,
    ground_truth: Optional[Any],
    tracer: Any,
    *,
    max_workers: int,
    verbose: bool,
) -> List[EvaluatorMetricResult]:
    """Run evaluators inline and attach their metrics to the active chain span.

    Called from inside the user-function wrapper while the
    ``@trace(event_type="chain", event_name=function.__name__)`` span is
    still recording. The flattened metric dict is written via
    ``enrich_span(metrics=…)`` — same path the docs document for
    span-level metrics — so the metrics ride out with the span on its
    OTLP export. No post-hoc lookup, no writer race.

    Returns the rich results for callers that want to inspect them
    (currently just tests).
    """
    results = _run_evaluators_for_datapoint(
        evaluators,
        inputs,
        outputs,
        ground_truth,
        max_workers=max_workers,
        verbose=verbose,
    )
    _attach_metrics_to_span(results, tracer)
    return results


async def _arun_evaluators_for_datapoint(
    evaluators: List[Callable],
    inputs: Dict[str, Any],
    outputs: Any,
    ground_truth: Optional[Any],
    *,
    verbose: bool = False,
) -> List[EvaluatorMetricResult]:
    """Async sibling of ``_run_evaluators_for_datapoint``.

    Used when the user function is async — running on a thread that
    already has a live event loop. ``asyncio.gather`` fans out the
    evaluators concurrently; ``_arun_single_evaluator`` handles
    sync-vs-async dispatch per evaluator.
    """
    if not evaluators:
        return []
    return list(
        await asyncio.gather(
            *(
                _arun_single_evaluator(
                    eval_func, inputs, outputs, ground_truth, verbose=verbose
                )
                for eval_func in evaluators
            )
        )
    )


async def _aapply_inline_evaluators(
    evaluators: List[Callable],
    inputs: Dict[str, Any],
    outputs: Any,
    ground_truth: Optional[Any],
    tracer: Any,
    *,
    verbose: bool,
) -> List[EvaluatorMetricResult]:
    """Async sibling of ``_apply_inline_evaluators`` for async user functions.

    Awaits each evaluator without spinning up a nested loop, then writes
    the flattened metrics onto the still-recording chain span via
    ``enrich_span``.
    """
    results = await _arun_evaluators_for_datapoint(
        evaluators, inputs, outputs, ground_truth, verbose=verbose
    )
    _attach_metrics_to_span(results, tracer)
    return results


def _attach_metrics_to_span(results: List[EvaluatorMetricResult], tracer: Any) -> None:
    """Best-effort write of flattened evaluator metrics onto the active span.

    Inline enrichment must never fail the run — scores still propagate to
    the session via the legacy enrichment path on the failure side.
    """
    # pylint: disable=import-outside-toplevel
    # Lazy import to avoid a circular import on module load.
    from honeyhive.tracer.instrumentation.enrichment import enrich_span

    metrics: Dict[str, Any] = {}
    for r in results:
        metrics.update(r.to_metric_attrs())
    if not metrics:
        return
    try:
        enrich_span(metrics=metrics, tracer=tracer)
    except Exception as e:  # pylint: disable=broad-except
        logger.warning("Failed to attach evaluator metrics to chain span: %s", str(e))


def evaluate(  # pylint: disable=too-many-locals,too-many-branches
    function: Callable,
    *,
    dataset: Optional[List[Dict[str, Any]]] = None,
    dataset_id: Optional[str] = None,
    evaluators: Optional[List[Callable]] = None,
    instrumentors: Optional[List[Callable[[], Any]]] = None,
    api_key: Optional[str] = None,
    server_url: Optional[str] = None,
    project: Optional[str] = None,
    name: Optional[str] = None,
    run_id: Optional[str] = None,
    max_workers: int = 10,
    aggregate_function: str = "average",
    verbose: bool = False,
    print_results: bool = True,
) -> Any:
    """
    Run experiment evaluation with backend aggregation.

    This is the main user-facing API for running experiments. It:
    1. Prepares dataset (external or HoneyHive)
    2. Creates experiment run via API
    3. Executes function against dataset with tracer multi-instance
    4. Runs evaluators (if provided)
    5. Retrieves aggregated results from backend

    Args:
        function: User function to execute against each datapoint. Can be either
            a synchronous function or an async function. Async functions are
            automatically detected and executed with asyncio.run().
        dataset: External dataset (list of dicts with 'inputs' and 'ground_truth')
        dataset_id: HoneyHive dataset ID (alternative to external dataset)
        evaluators: List of evaluator functions (optional)
        instrumentors: List of instrumentor factory functions. Each factory should
            return a new instrumentor instance when called. This ensures each
            datapoint gets its own tracer and instrumentor instance for proper
            trace routing. Example: [lambda: OpenAIInstrumentor()]
        api_key: HoneyHive API key (or set HONEYHIVE_API_KEY/HH_API_KEY env var)
        server_url: HoneyHive server URL (or set HONEYHIVE_SERVER_URL/
            HH_SERVER_URL/HH_API_URL env var)
        project: Deprecated and ignored. Project scope is determined by the API key.
        name: Experiment run name (auto-generated if not provided)
        run_id: Experiment run ID to send to the backend (auto-generated UUID if not
            provided). The backend's returned run_id is always honored as the final ID.
        max_workers: ThreadPool size for concurrent execution (default: 10)
        aggregate_function: Backend aggregation function
            ("average", "sum", "min", "max")
        verbose: Enable verbose logging
        print_results: Print formatted results table after evaluation
            (default: True)

    Returns:
        ExperimentResultSummary with backend-computed aggregates

    Raises:
        ValueError: If neither dataset nor dataset_id provided, or both provided

    Examples:
        >>> from honeyhive import HoneyHive
        >>> from honeyhive.experiments import evaluate
        >>>
        >>> # Define function to test (sync)
        >>> def my_function(inputs, ground_truth):
        ...     # Your LLM call or function logic
        ...     return {"output": "result"}
        >>>
        >>> # Async functions are also supported
        >>> async def my_async_function(inputs, ground_truth):
        ...     result = await some_async_llm_call()
        ...     return {"output": result}
        >>>
        >>> # External dataset
        >>> dataset = [
        ...     {"inputs": {"query": "test1"}, "ground_truth": {"answer": "a1"}},
        ...     {"inputs": {"query": "test2"}, "ground_truth": {"answer": "a2"}}
        ... ]
        >>>
        >>> result = evaluate(
        ...     function=my_function,  # or my_async_function
        ...     dataset=dataset,
        ...     api_key="hh_...",
        ...     name="My Experiment"
        ... )
        >>>
        >>> print(f"Success: {result.success}")
        >>> print(f"Passed: {len(result.passed)}")
        >>> print(f"Metrics: {result.metrics.list_metrics()}")
        >>>
        >>> # HoneyHive dataset
        >>> result = evaluate(
        ...     function=my_function,
        ...     dataset_id="ds-123",
        ...     api_key="hh_..."
        ... )
        >>>
        >>> # With instrumentors for automatic LLM tracing
        >>> from openinference.instrumentation.openai import OpenAIInstrumentor
        >>> result = evaluate(
        ...     function=my_function,
        ...     dataset=dataset,
        ...     api_key="hh_...",
        ...     instrumentors=[lambda: OpenAIInstrumentor()]
        ... )
    """
    # Validate inputs
    if dataset is None and dataset_id is None:
        raise ValueError("Must provide either 'dataset' or 'dataset_id'")
    if dataset is not None and dataset_id is not None:
        raise ValueError("Cannot provide both 'dataset' and 'dataset_id'")
    if project is not None:
        warnings.warn(
            "The 'project' argument to evaluate() is deprecated and ignored. "
            "Project scope is determined by the API key.",
            DeprecationWarning,
            stacklevel=2,
        )

    # Load from environment variables if not provided
    # Support both HONEYHIVE_* and HH_* prefixes for convenience
    # Note: HoneyHive client's config only reads HH_* prefix, so we check
    # HONEYHIVE_* first for better UX, then pass explicitly to client
    if api_key is None:
        api_key = os.getenv("HONEYHIVE_API_KEY") or os.getenv("HH_API_KEY")

    if server_url is None:
        # Check multiple variations for maximum compatibility
        server_url = (
            os.getenv("HONEYHIVE_SERVER_URL")  # Most intuitive
            or os.getenv("HH_SERVER_URL")  # Alternative shorthand
            or os.getenv("HH_API_URL")  # Client config uses this
        )

    # Initialize client - passing explicit values ensures both HONEYHIVE_* and HH_*
    # environment variables work (client's config only checks HH_* prefix)
    client_params = {"api_key": api_key}
    if server_url:
        client_params["base_url"] = server_url
    client = HoneyHive(**client_params)

    # Step 1: Prepare dataset
    if dataset is not None:
        # External dataset - generate EXT- IDs
        if verbose:
            logger.info("Preparing external dataset with %d datapoints", len(dataset))

        external_dataset_id, datapoint_ids = prepare_external_dataset(dataset)
        dataset_list = dataset

        if verbose:
            logger.info("Generated external dataset ID: %s", external_dataset_id)
    else:
        # HoneyHive dataset - fetch from API
        # At this point dataset_id is guaranteed to be str (not None)
        assert dataset_id is not None, "dataset_id must be provided"

        if verbose:
            logger.info("Fetching HoneyHive dataset: %s", dataset_id)
            logger.info("DEBUG - Input dataset_id type: %s", type(dataset_id))
            logger.info("DEBUG - Is EXT- dataset: %s", dataset_id.startswith("EXT-"))

        # Get dataset metadata - list() returns GetDatasetsResponse with datasets list
        ds_response = client.datasets.list(dataset_id=dataset_id)
        dataset_list = []
        datapoint_ids = []

        # Extract the dataset from the response
        if not ds_response.datasets:
            raise ValueError(f"Dataset not found: {dataset_id}")
        dataset_obj = ds_response.datasets[0]

        # Dataset.datapoints is List[str] (IDs only), fetch each datapoint.
        # get_datapoint returns a typed GetDatapointResponse Pydantic model
        # whose `.datapoint` field is List[Datapoint] (also Pydantic).
        #
        # Catch ONLY the exception types that represent a fetch failure
        # we can reasonably skip and keep going on (HTTP errors from the
        # generated SDK + httpx transport-level errors). Anything else
        # — AttributeError, TypeError, KeyError, etc. — indicates a real
        # bug we want to surface immediately rather than silently produce
        # an empty datapoint list.
        if dataset_obj.datapoints:
            for dp_id in dataset_obj.datapoints:
                try:
                    dp_response = client.datapoints.get_datapoint(dp_id)
                except (HTTPException, httpx.HTTPError) as e:
                    logger.warning("Failed to fetch datapoint %s: %s", dp_id, str(e))
                    continue
                dp_list = getattr(dp_response, "datapoint", []) or []
                if dp_list:
                    dp = dp_list[0]
                    dataset_list.append(
                        {
                            "inputs": getattr(dp, "inputs", None) or {},
                            "ground_truth": getattr(dp, "ground_truth", None),
                            "id": getattr(dp, "id", None) or dp_id,
                        }
                    )
                    datapoint_ids.append(getattr(dp, "id", None) or dp_id)

            # Guard against the silent-data-loss shape that the narrow
            # except above doesn't cover: every fetch logged + skipped
            # (transient HTTP failure on every datapoint), or every
            # response had an empty `.datapoint` list. In either case
            # the dataset claimed N datapoints but we collected zero —
            # better to fail loudly than to proceed with an empty
            # dataset and report passed=0.
            if not dataset_list:
                raise ValueError(
                    f"Dataset {dataset_id} listed "
                    f"{len(dataset_obj.datapoints)} datapoint(s) but every "
                    f"fetch returned no usable datapoint. Check warnings "
                    f"above for per-datapoint errors."
                )

        external_dataset_id = dataset_id

        if verbose:
            logger.info(
                "Loaded %d datapoints from HoneyHive dataset", len(dataset_list)
            )
            logger.info("DEBUG - external_dataset_id set to: %s", external_dataset_id)
            logger.info("DEBUG - datapoint_ids collected: %s", datapoint_ids)

    # Step 2: Create experiment run
    # Generate a client-side UUID if no run_id was provided. The backend also
    # generates a UUID when run_id is omitted, but we do it here so the
    # default run name ("experiment-{short_id}") is derived from the same ID
    # that will be sent in the request.
    run_id = run_id or str(uuid.uuid4())
    normalized_name = name.strip() if name else None
    run_name = normalized_name or f"experiment-{run_id[:8]}"

    if verbose:
        logger.info("Creating experiment run: %s", run_name)
        logger.info("DEBUG - Before prepare_run_request_data:")
        logger.info("  external_dataset_id: %s", external_dataset_id)
        logger.info("  datapoint_ids: %s", datapoint_ids)

    git_context = get_git_context()

    run_metadata: Dict[str, Any] = {}
    if git_context:
        run_metadata["git"] = git_context

    run_data = prepare_run_request_data(
        run_id=run_id,
        name=run_name,
        dataset_id=external_dataset_id,
        event_ids=[],  # Empty initially
        datapoint_ids=datapoint_ids,  # Link datapoints to run
        configuration={
            "function": function.__name__,
            "evaluators": [e.__name__ for e in (evaluators or [])],
            "max_workers": max_workers,
            "aggregate_function": aggregate_function,
        },
        metadata=run_metadata,
        status="pending",
    )

    if verbose:
        logger.info("DEBUG - After prepare_run_request_data:")
        logger.info("  run_data['dataset_id']: %s", run_data.get("dataset_id"))
        logger.info("  run_data['datapoint_ids']: %s", run_data.get("datapoint_ids"))
        logger.info("  run_data['metadata']: %s", run_data.get("metadata"))

    # Create run via API (experiments API handles runs)
    run_request = PostExperimentRunRequest(**run_data)
    run_response = client.experiments.create_run(run_request)

    # Use backend-generated run_id if available
    if hasattr(run_response, "run_id") and run_response.run_id:
        run_id = str(run_response.run_id)

    if verbose:
        logger.info("Created experiment run: %s", run_id)

    # Step 3: Create experiment context
    # external_dataset_id is guaranteed to be str at this point
    context = ExperimentContext(
        run_id=run_id,
        dataset_id=external_dataset_id or "",  # Type safety
        run_name=run_name,
        source="evaluation",
    )

    # Step 4: Execute experiment with tracer multi-instance
    if verbose:
        logger.info(
            "Executing function against %d datapoints with %d workers",
            len(dataset_list),
            max_workers,
        )

    execution_results = run_experiment(
        function=function,
        dataset=dataset_list,
        datapoint_ids=datapoint_ids,
        server_url=server_url,
        experiment_context=context,
        api_key=api_key,
        max_workers=max_workers,
        verbose=verbose,
        instrumentors=instrumentors,
        evaluators=evaluators,
    )

    if verbose:
        logger.info("Enriching sessions with outputs and ground_truth")

    for result in execution_results:
        session_id = result.get("session_id")
        if session_id:
            _enrich_session_with_results(
                session_id=session_id,
                outputs=result.get("outputs"),
                ground_truth=result.get("ground_truth"),
                client=client,
                verbose=verbose,
            )

    _update_run_with_results(
        run_id=run_id,
        run_name=run_name,
        execution_results=execution_results,
        external_dataset_id=external_dataset_id,
        client=client,
        verbose=verbose,
    )

    # Step 7: Retrieve aggregated results from backend
    if verbose:
        logger.info(
            "Retrieving aggregated results with %s aggregation", aggregate_function
        )

    result_summary = get_run_result(
        client=client,
        run_id=run_id,
        aggregate_function=aggregate_function,
    )

    if verbose:
        logger.info(
            "Experiment complete: %s (passed: %d, failed: %d)",
            "SUCCESS" if result_summary.success else "FAILED",
            len(result_summary.passed),
            len(result_summary.failed),
        )

    # Print formatted results table if requested
    if print_results:
        result_summary.print_table(run_name=run_name)

    return result_summary
