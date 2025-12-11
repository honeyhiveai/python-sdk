"""Core experiment functionality.

This module provides the core experiment execution functionality including:
- ExperimentContext for organizing experiment metadata
- run_experiment() with tracer multi-instance pattern
- Integration with backend result endpoints
"""

# pylint: disable=too-many-lines
import asyncio
import inspect  # ✅ TASK 2: Needed for signature detection
import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from honeyhive.api.client import HoneyHive
from honeyhive.api.events import UpdateEventRequest
from honeyhive.experiments.evaluators import evaluator as evaluator_class
from honeyhive.experiments.results import get_run_result
from honeyhive.experiments.utils import (
    prepare_external_dataset,
    prepare_run_request_data,
)
from honeyhive.models import CreateRunRequest
from honeyhive.tracer import HoneyHiveTracer
from honeyhive.tracer.instrumentation.decorators import trace
from honeyhive.tracer.lifecycle.flush import force_flush_tracer
from honeyhive.utils.logger import get_logger, safe_log

# Module-level logger for orchestration code (no tracer instance yet)
logger = get_logger("honeyhive.experiments.core")


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
        project: Project identifier
        source: Source identifier (default: "evaluation")
        metadata: Additional metadata dictionary

    Example:
        >>> context = ExperimentContext(
        ...     run_id="run-123",
        ...     dataset_id="EXT-abc",
        ...     project="my-project"
        ... )
        >>> tracer_config = context.to_tracer_config("dp-1")
        >>> tracer_config["is_evaluation"]
        True
    """

    def __init__(
        self,
        run_id: str,
        dataset_id: str,
        project: str,
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
            project: Project identifier
            run_name: Experiment run name (used for session naming)
            source: Source identifier (default: "evaluation")
            metadata: Additional metadata
        """
        self.run_id = run_id
        self.dataset_id = dataset_id
        self.project = project
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
                'project': 'my-project',
                'is_evaluation': True,
                'run_id': 'run-123',
                'dataset_id': 'EXT-abc',
                'datapoint_id': 'dp-1',
                'source': 'evaluation'
            }
        """
        return {
            "project": self.project,
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
        ...     project="my-project"
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

        # ✅ TASK 1: Use experiment run name for session name
        if experiment_context.run_name:
            tracer_config["session_name"] = experiment_context.run_name

        # Create NEW tracer instance for this datapoint
        # Each tracer is completely isolated (own API client, logger, state)
        tracer = HoneyHiveTracer(
            api_key=api_key, server_url=server_url, verbose=verbose, **tracer_config
        )

        # Create and initialize instrumentor instances for this datapoint
        # Each datapoint gets its own instrumentor instances to ensure traces
        # are routed correctly to the right session
        active_instrumentors: List[Any] = []
        if instrumentors:
            for instrumentor_factory in instrumentors:
                try:
                    # Create new instrumentor instance from factory
                    instrumentor = instrumentor_factory()
                    # Set the tracer provider on the instrumentor
                    instrumentor.instrument(tracer_provider=tracer.provider)
                    active_instrumentors.append(instrumentor)
                    if verbose:
                        safe_log(
                            tracer,
                            "info",
                            "Initialized instrumentor %s for datapoint %s",
                            type(instrumentor).__name__,
                            datapoint_id,
                        )
                except Exception as e:
                    safe_log(
                        tracer,
                        "warning",
                        "Failed to initialize instrumentor for datapoint %s: %s",
                        datapoint_id,
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

            # ✅ TASK 2: Check if function accepts tracer parameter (signature detection)
            sig = inspect.signature(function)
            params = sig.parameters

            # ✅ Automatically wrap the function with @trace decorator
            # This creates a span for the user's function execution and
            # captures inputs/outputs
            traced_function = trace(
                event_type="chain",
                event_name=function.__name__,
                tracer=tracer,
            )(function)

            # Check if the function is async
            is_async = asyncio.iscoroutinefunction(function)

            if "tracer" in params:
                # NEW v1.0 pattern: pass tracer for enrich_span/enrich_session support
                if verbose:
                    safe_log(
                        tracer,
                        "info",
                        "Calling function with tracer parameter (v1.0 feature)",
                    )
                if is_async:
                    outputs = asyncio.run(traced_function(datapoint, tracer=tracer))
                else:
                    outputs = traced_function(datapoint, tracer=tracer)
            else:
                # MAIN BRANCH pattern: backward compatible
                if verbose:
                    safe_log(
                        tracer,
                        "info",
                        "Calling function without tracer (main branch compatible)",
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
            # Uninstrument all instrumentors for this datapoint
            for instrumentor in active_instrumentors:
                try:
                    instrumentor.uninstrument()
                    if verbose:
                        safe_log(
                            tracer,
                            "info",
                            "Uninstrumented %s for datapoint %s",
                            type(instrumentor).__name__,
                            datapoint_id,
                        )
                except Exception as e:
                    safe_log(
                        tracer,
                        "warning",
                        "Failed to uninstrument %s for datapoint %s: %s",
                        type(instrumentor).__name__,
                        datapoint_id,
                        str(e),
                    )

            # CRITICAL: Flush tracer to ensure all spans sent
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
            f"Dataset length ({len(dataset)}) does not match "
            f"datapoint_ids length ({len(datapoint_ids)})"
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
    evaluator_metrics: Optional[Dict[str, Dict[str, Any]]],
    client: Any,
    verbose: bool,
) -> None:
    """Update run with session IDs, status, and evaluator metrics."""
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

        if evaluator_metrics:
            update_metadata["evaluator_metrics"] = evaluator_metrics

        if update_metadata:
            update_data["metadata"] = update_metadata

        if verbose:
            logger.info(
                "Updating run %s with data: status=%s, name=%s, "
                "event_ids=%d, metadata_keys=%s",
                run_id,
                update_data.get("status"),
                update_data.get("name"),
                len(update_data.get("event_ids", [])),
                list(update_metadata.keys()) if update_metadata else [],
            )

        client.evaluations.update_run_from_dict(run_id, update_data)

        if verbose:
            if session_ids:
                logger.info("Linked %d sessions to run %s", len(session_ids), run_id)
            if evaluator_metrics:
                logger.info(
                    "Sent evaluator metrics for %d datapoints to backend",
                    len(evaluator_metrics),
                )
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
                "metadata_keys=%s, evaluator_metrics_count=%d. Response: %s",
                run_id,
                error_msg,
                error_type,
                update_data.get("status"),
                update_data.get("name"),
                len(update_data.get("event_ids", [])),
                bool(update_data.get("metadata")),
                list(update_metadata.keys()) if update_metadata else [],
                len(evaluator_metrics) if evaluator_metrics else 0,
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
    datapoint_id: Optional[str],
    outputs: Any,
    ground_truth: Any,  # ✅ TASK 3: Add ground_truth parameter
    evaluator_metrics: Dict[str, Dict[str, Any]],
    client: Any,
    verbose: bool,
) -> None:
    """Enrich a session with outputs, ground_truth, and evaluator metrics."""
    try:
        update_data = {}

        if outputs is not None:
            update_data["outputs"] = outputs

        # ✅ TASK 3: Add ground_truth to feedback field
        if ground_truth is not None:
            update_data["feedback"] = {"ground_truth": ground_truth}

        if datapoint_id and datapoint_id in evaluator_metrics:
            update_data["metrics"] = evaluator_metrics[datapoint_id]

        if update_data:
            update_request = UpdateEventRequest(event_id=session_id, **update_data)
            client.events.update_event(update_request)

            if verbose:
                enriched_fields = list(update_data.keys())
                logger.info("Enriched session %s with: %s", session_id, enriched_fields)
    except Exception as e:
        logger.warning("Failed to enrich session %s: %s", session_id, str(e))


def _run_evaluators(
    evaluators: List[Callable],
    execution_results: List[Dict[str, Any]],
    max_workers: int = 10,
    verbose: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    Run evaluators against execution results.

    This function executes evaluators concurrently for each datapoint's
    execution result, collecting metrics from each evaluator.

    Evaluator Function Signature:
        evaluator(outputs, inputs, ground_truth) -> float

        - outputs: The result from running the function on the datapoint
        - inputs: The original datapoint inputs
        - ground_truth: The expected output (optional)

    Args:
        evaluators: List of evaluator callables
        execution_results: List of execution results from run_experiment
        max_workers: ThreadPool size for concurrent execution
        verbose: Enable verbose logging

    Returns:
        Dictionary mapping datapoint_id to evaluator metrics

    Example:
        >>> def accuracy(outputs, inputs, ground_truth):
        ...     return 1.0 if outputs == ground_truth else 0.0
        >>>
        >>> evaluators = [accuracy, relevance]
        >>> results = [{"datapoint_id": "dp-1", "outputs": {...}, ...}]
        >>> metrics = _run_evaluators(evaluators, results)
        >>> metrics
        {
            "dp-1": {
                "accuracy": 0.95,
                "relevance": 0.87
            }
        }
    """

    def run_single_evaluator(
        eval_func: Callable,
        datapoint_id: str,
        inputs: Dict[str, Any],
        outputs: Any,
        ground_truth: Optional[Any],
    ) -> tuple[str, str, Any]:
        """Run a single evaluator and return (datapoint_id, eval_name, score)."""
        # Get evaluator name (before try block to avoid unbound variable)
        if isinstance(eval_func, evaluator_class):
            eval_name = eval_func.name
        else:
            eval_name = getattr(eval_func, "__name__", str(eval_func))

        try:
            # Execute evaluator
            # Standard signature: evaluator(outputs, inputs, ground_truth)
            # Outputs come first as they are the primary evaluation target
            if asyncio.iscoroutinefunction(eval_func):
                # Async evaluator
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    if ground_truth is not None:
                        score = loop.run_until_complete(
                            eval_func(outputs, inputs, ground_truth)
                        )
                    else:
                        score = loop.run_until_complete(eval_func(outputs, inputs))
                finally:
                    loop.close()
            else:
                # Sync evaluator
                if ground_truth is not None:
                    score = eval_func(outputs, inputs, ground_truth)
                else:
                    score = eval_func(outputs, inputs)

            return datapoint_id, eval_name, score

        except Exception as e:
            if verbose:
                logger.warning(
                    "Evaluator %s failed for datapoint %s: %s",
                    eval_name,
                    datapoint_id,
                    str(e),
                )
            return (
                datapoint_id,
                eval_name,
                None,
            )

    # Aggregate all metrics by datapoint
    all_metrics: Dict[str, Dict[str, Any]] = {}

    # Use ThreadPoolExecutor for concurrent evaluator execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all evaluator tasks
        futures = []
        for result in execution_results:
            datapoint_id = result["datapoint_id"]
            inputs = result.get("inputs", {})
            outputs = result.get("outputs")
            ground_truth = result.get("ground_truth")

            # Initialize metrics dict for this datapoint
            if datapoint_id not in all_metrics:
                all_metrics[datapoint_id] = {}

            # Submit each evaluator for this datapoint
            for eval_func in evaluators:
                future = executor.submit(
                    run_single_evaluator,
                    eval_func,
                    datapoint_id,
                    inputs,
                    outputs,
                    ground_truth,
                )
                futures.append(future)

        # Collect results
        for future in as_completed(futures):
            try:
                datapoint_id, eval_name, score = future.result()
                all_metrics[datapoint_id][eval_name] = score
            except Exception as e:
                if verbose:
                    logger.warning("Failed to collect evaluator result: %s", str(e))

    return all_metrics


def evaluate(  # pylint: disable=too-many-locals,too-many-branches
    function: Callable,
    *,
    dataset: Optional[List[Dict[str, Any]]] = None,
    dataset_id: Optional[str] = None,
    evaluators: Optional[List[Callable]] = None,
    instrumentors: Optional[List[Callable[[], Any]]] = None,
    api_key: Optional[str] = None,
    server_url: Optional[str] = None,
    project: str = "default",
    name: Optional[str] = None,
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
        project: HoneyHive project (or set HONEYHIVE_PROJECT env var)
        name: Experiment run name (auto-generated if not provided)
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
        ...     project="my-project",
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
        ...     api_key="hh_...",
        ...     project="my-project"
        ... )
        >>>
        >>> # With instrumentors for automatic LLM tracing
        >>> from openinference.instrumentation.openai import OpenAIInstrumentor
        >>> result = evaluate(
        ...     function=my_function,
        ...     dataset=dataset,
        ...     api_key="hh_...",
        ...     project="my-project",
        ...     instrumentors=[lambda: OpenAIInstrumentor()]
        ... )
    """
    # Validate inputs
    if dataset is None and dataset_id is None:
        raise ValueError("Must provide either 'dataset' or 'dataset_id'")
    if dataset is not None and dataset_id is not None:
        raise ValueError("Cannot provide both 'dataset' and 'dataset_id'")
    if project is None:
        raise ValueError("Must provide 'project' or set HONEYHIVE_PROJECT env var")

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
    client = HoneyHive(api_key=api_key, server_url=server_url, verbose=verbose)

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

        # Get dataset metadata
        ds_response = client.datasets.get_dataset(dataset_id)
        dataset_list = []
        datapoint_ids = []

        # Dataset.datapoints is List[str] (IDs only), fetch each datapoint
        if ds_response.datapoints:
            for dp_id in ds_response.datapoints:
                try:
                    dp = client.datapoints.get_datapoint(dp_id)
                    dataset_list.append(
                        {
                            "inputs": dp.inputs or {},
                            "ground_truth": dp.ground_truth,
                            "id": dp.field_id or dp_id,
                        }
                    )
                    datapoint_ids.append(dp.field_id or dp_id)
                except Exception as e:
                    logger.warning("Failed to fetch datapoint %s: %s", dp_id, str(e))

        external_dataset_id = dataset_id

        if verbose:
            logger.info(
                "Loaded %d datapoints from HoneyHive dataset", len(dataset_list)
            )
            logger.info("DEBUG - external_dataset_id set to: %s", external_dataset_id)
            logger.info("DEBUG - datapoint_ids collected: %s", datapoint_ids)

    # Step 2: Create experiment run
    run_id = str(uuid.uuid4())
    run_name = name or f"experiment-{run_id[:8]}"

    if verbose:
        logger.info("Creating experiment run: %s", run_name)
        logger.info("DEBUG - Before prepare_run_request_data:")
        logger.info("  external_dataset_id: %s", external_dataset_id)
        logger.info("  datapoint_ids: %s", datapoint_ids)

    run_data = prepare_run_request_data(
        run_id=run_id,
        name=run_name,
        project=project,
        dataset_id=external_dataset_id,
        event_ids=[],  # Empty initially
        datapoint_ids=datapoint_ids,  # Link datapoints to run
        configuration={
            "function": function.__name__,
            "evaluators": [e.__name__ for e in (evaluators or [])],
            "max_workers": max_workers,
            "aggregate_function": aggregate_function,
        },
        status="pending",
    )

    if verbose:
        logger.info("DEBUG - After prepare_run_request_data:")
        logger.info("  run_data['dataset_id']: %s", run_data.get("dataset_id"))
        logger.info("  run_data['datapoint_ids']: %s", run_data.get("datapoint_ids"))
        logger.info("  run_data['metadata']: %s", run_data.get("metadata"))

    # Create run via API
    run_request = CreateRunRequest(**run_data)
    run_response = client.evaluations.create_run(run_request)

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
        project=project,
        run_name=run_name,  # ✅ TASK 1: Pass run name for session naming
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
    )

    # Step 5: Run evaluators (if provided)
    evaluator_metrics = None
    if evaluators:
        if verbose:
            logger.info("Running %d evaluators", len(evaluators))

        # Run evaluators against execution results
        evaluator_metrics = _run_evaluators(
            evaluators=evaluators,
            execution_results=execution_results,
            max_workers=max_workers,
            verbose=verbose,
        )

        if verbose:
            logger.info(
                "Evaluators complete: %d metrics collected", len(evaluator_metrics)
            )

    # Enrich sessions with outputs and evaluator metrics
    # (always, not just when evaluators exist)
    if verbose:
        logger.info("Enriching sessions with outputs and evaluator metrics")

    for result in execution_results:
        session_id = result.get("session_id")
        if session_id:
            _enrich_session_with_results(
                session_id=session_id,
                datapoint_id=result.get("datapoint_id"),
                outputs=result.get("outputs"),
                ground_truth=result.get("ground_truth"),  # ✅ TASK 3: Pass ground_truth
                evaluator_metrics=evaluator_metrics or {},
                client=client,
                verbose=verbose,
            )

    # Step 6: Update run with results
    _update_run_with_results(
        run_id=run_id,
        run_name=run_name,
        execution_results=execution_results,
        external_dataset_id=external_dataset_id,
        evaluator_metrics=evaluator_metrics,
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
