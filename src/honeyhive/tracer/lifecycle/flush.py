"""Force flush operations for tracer lifecycle management.

This module handles all force flush operations including tracer providers,
span processors, and batch processors with comprehensive error handling
and timeout management.
"""

# pylint: disable=cyclic-import
# Justification: This module participates in a necessary architectural cycle.
# flush.py depends on core.py for shared infrastructure (safe_log, locking),
# while core.py imports flush operations for coordinated shutdown sequences.
# The cycle ensures that flush operations can be properly coordinated with
# shutdown while maintaining modular separation of flush-specific logic.

from typing import Any, List, Tuple

from ...utils.logger import safe_log
from .core import acquire_lifecycle_lock_optimized


def force_flush_tracer(tracer_instance: Any, timeout_millis: float = 30000) -> bool:
    """Force flush any pending spans and data for a tracer instance.

    This function ensures that all pending spans and telemetry data are
    immediately sent to their destinations, rather than waiting for
    automatic batching/flushing. It handles multiple flush targets and
    provides comprehensive error handling.

    :param tracer_instance: The tracer instance to flush
    :type tracer_instance: HoneyHiveTracer
    :param timeout_millis: Maximum time to wait for flush completion in milliseconds
    :type timeout_millis: float
    :return: True if flush completed successfully within timeout, False otherwise
    :rtype: bool

    **Example:**

    .. code-block:: python

        # Flush with default timeout (30 seconds)
        success = force_flush_tracer(tracer)

        # Flush with custom timeout (5 seconds)
        success = force_flush_tracer(tracer, timeout_millis=5000)

        # Use before critical sections
        if force_flush_tracer(tracer):
            print("All spans flushed successfully")
        else:
            print("Flush timeout or error occurred")

    **Note:**

    This function attempts to flush multiple components in sequence:
    the tracer provider, custom span processors, and batch processors.
    It returns True only if all components flush successfully.
    """
    safe_log(tracer_instance, "debug", "Force flush requested")

    flush_results: List[Tuple[str, bool]] = []

    safe_log(
        tracer_instance,
        "debug",
        f"force_flush_tracer: Acquiring _lifecycle_lock (timeout: {timeout_millis}ms)",
    )

    try:
        safe_log(
            tracer_instance,
            "debug",
            "force_flush_tracer: Attempting to acquire _lifecycle_lock...",
        )
        # Use environment-optimized flush timeout
        flush_timeout_seconds = timeout_millis / 1000.0
        with acquire_lifecycle_lock_optimized(
            "flush", custom_timeout=flush_timeout_seconds
        ) as acquired:
            if not acquired:
                safe_log(
                    tracer_instance,
                    "warning",
                    f"Failed to acquire _lifecycle_lock ({flush_timeout_seconds}s)",
                )
                return False
            safe_log(
                tracer_instance,
                "debug",
                "force_flush_tracer: Successfully acquired _lifecycle_lock",
            )
            # 1. Flush the tracer provider if available and supports it
            _flush_tracer_provider(tracer_instance, timeout_millis, flush_results)

            # 2. Flush our custom span processor if available
            _flush_span_processor(tracer_instance, timeout_millis, flush_results)

            # 3. Flush any batch span processors attached to the provider
            _flush_batch_processors(tracer_instance, timeout_millis, flush_results)

        # Calculate overall result
        overall_success = all(result for _, result in flush_results)

        _log_flush_results(tracer_instance, overall_success, flush_results)

        return overall_success

    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "error",
            "Force flush failed",
            honeyhive_data={
                "error": str(e),
                "error_type": type(e).__name__,
                "operation": "force_flush_tracer",
            },
        )
        return False


def _flush_tracer_provider(
    tracer_instance: Any, timeout_millis: float, flush_results: List[Tuple[str, bool]]
) -> None:
    """Flush the tracer provider component.

    :param tracer_instance: The tracer instance
    :type tracer_instance: HoneyHiveTracer
    :param timeout_millis: Timeout in milliseconds
    :type timeout_millis: float
    :param flush_results: List to append results to
    :type flush_results: List[Tuple[str, bool]]
    """
    if tracer_instance.provider and hasattr(tracer_instance.provider, "force_flush"):
        try:
            provider_result = tracer_instance.provider.force_flush(
                timeout_millis=int(timeout_millis)
            )
            flush_results.append(("provider", provider_result))
            safe_log(
                tracer_instance,
                "debug",
                "Provider force_flush completed",
                honeyhive_data={
                    "success": provider_result,
                    "operation": "provider_flush",
                },
            )
        except Exception as e:
            flush_results.append(("provider", False))
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(
                tracer_instance,
                "error",
                "Provider force_flush error",
                honeyhive_data={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "operation": "provider_flush",
                },
            )
    else:
        safe_log(
            tracer_instance,
            "debug",
            "Provider does not support force_flush",
            honeyhive_data={"operation": "provider_flush"},
        )
        flush_results.append(("provider", True))  # Consider successful if not supported


def _flush_span_processor(
    tracer_instance: Any, timeout_millis: float, flush_results: List[Tuple[str, bool]]
) -> None:
    """Flush the custom span processor component.

    :param tracer_instance: The tracer instance
    :type tracer_instance: HoneyHiveTracer
    :param timeout_millis: Timeout in milliseconds
    :type timeout_millis: float
    :param flush_results: List to append results to
    :type flush_results: List[Tuple[str, bool]]
    """
    if tracer_instance.span_processor and hasattr(
        tracer_instance.span_processor, "force_flush"
    ):
        try:
            processor_result = tracer_instance.span_processor.force_flush(
                timeout_millis=timeout_millis
            )
            flush_results.append(("span_processor", processor_result))
            safe_log(
                tracer_instance,
                "debug",
                "Span processor force_flush completed",
                honeyhive_data={
                    "success": processor_result,
                    "operation": "span_processor_flush",
                },
            )
        except Exception as e:
            flush_results.append(("span_processor", False))
            # Graceful degradation following Agent OS standards - never crash host
            safe_log(
                tracer_instance,
                "error",
                "Span processor force_flush error",
                honeyhive_data={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "operation": "span_processor_flush",
                },
            )
    else:
        flush_results.append(
            ("span_processor", True)
        )  # Consider successful if not available


def _get_batch_processors(tracer_instance: Any) -> List[Any]:
    """Extract batch processors from tracer provider."""
    if not (
        tracer_instance.provider
        and hasattr(tracer_instance.provider, "_span_processors")
    ):
        return []

    batch_processors = []
    for processor in getattr(tracer_instance.provider, "_span_processors", []):
        if hasattr(processor, "force_flush"):
            batch_processors.append(processor)
    return batch_processors


def _flush_single_processor(
    processor: Any, timeout_millis: float, processor_index: int, tracer_instance: Any
) -> bool:
    """Flush a single batch processor."""
    try:
        result = processor.force_flush(timeout_millis=int(timeout_millis))
        safe_log(
            tracer_instance,
            "debug",
            "Batch processor force_flush completed",
            honeyhive_data={
                "processor_index": processor_index,
                "success": result,
                "operation": "batch_processor_flush",
            },
        )
        return bool(result)
    except Exception as e:
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "error",
            "Batch processor force_flush error",
            honeyhive_data={
                "processor_index": processor_index,
                "error": str(e),
                "error_type": type(e).__name__,
                "operation": "batch_processor_flush",
            },
        )
        return False


def _flush_batch_processors(
    tracer_instance: Any, timeout_millis: float, flush_results: List[Tuple[str, bool]]
) -> None:
    """Flush any batch span processors attached to the provider.

    :param tracer_instance: The tracer instance
    :type tracer_instance: HoneyHiveTracer
    :param timeout_millis: Timeout in milliseconds
    :type timeout_millis: float
    :param flush_results: List to append results to
    :type flush_results: List[Tuple[str, bool]]
    """
    try:
        batch_processors = _get_batch_processors(tracer_instance)

        if not batch_processors:
            flush_results.append(("batch_processors", True))
            return

        batch_results = []
        for i, processor in enumerate(batch_processors):
            result = _flush_single_processor(
                processor, timeout_millis, i + 1, tracer_instance
            )
            batch_results.append(result)

        flush_results.append(("batch_processors", all(batch_results)))

    except Exception as e:
        flush_results.append(("batch_processors", False))
        # Graceful degradation following Agent OS standards - never crash host
        safe_log(
            tracer_instance,
            "error",
            "Batch processors flush error",
            honeyhive_data={
                "error": str(e),
                "error_type": type(e).__name__,
                "operation": "batch_processors_flush",
            },
        )


def _log_flush_results(
    tracer_instance: Any, overall_success: bool, flush_results: List[Tuple[str, bool]]
) -> None:
    """Log the results of the flush operation.

    :param tracer_instance: The tracer instance
    :type tracer_instance: HoneyHiveTracer
    :param overall_success: Whether the overall flush was successful
    :type overall_success: bool
    :param flush_results: List of component flush results
    :type flush_results: List[Tuple[str, bool]]
    """
    if tracer_instance.test_mode:
        return

    if overall_success:
        safe_log(
            tracer_instance,
            "info",
            "Force flush completed successfully",
            honeyhive_data={
                "components_flushed": len(flush_results),
                "all_successful": True,
            },
        )
    else:
        failed_components = [name for name, result in flush_results if not result]
        total = len(flush_results)
        successful = total - len(failed_components)
        safe_log(
            tracer_instance,
            "warning",
            "Force flush completed with failures",
            honeyhive_data={
                "failed_components": failed_components,
                "total_components": total,
                "success_rate": f"{successful}/{total}",
            },
        )
