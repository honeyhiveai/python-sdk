"""Threading utilities for OpenTelemetry context propagation.

This module provides utilities for propagating OpenTelemetry trace context
across thread boundaries, which is essential for maintaining parent-child
relationships when using ThreadPoolExecutor or other threading constructs.

The core issue: OpenTelemetry context is thread-local by design. When you spawn
a new thread (e.g., via ThreadPoolExecutor), the new thread starts with an empty
context, causing spans created in that thread to become orphaned (no parent).

This module provides three solutions:

1. `with_trace_context(func)` - Wrap a function to capture and propagate context
2. `TracedThreadPoolExecutor` - A drop-in replacement for ThreadPoolExecutor
3. `instrument_threading()` - Monkey-patch ThreadPoolExecutor globally

Example:
    Using with_trace_context explicitly::

        from honeyhive import trace
        from honeyhive.tracer.utils.threading import with_trace_context
        from concurrent.futures import ThreadPoolExecutor

        @trace()
        def child_task():
            # This span will now be properly parented
            pass

        @trace()
        def parent_task():
            with ThreadPoolExecutor() as executor:
                # Wrap the function to propagate context
                executor.submit(with_trace_context(child_task))

    Using TracedThreadPoolExecutor::

        from honeyhive import trace
        from honeyhive.tracer.utils.threading import TracedThreadPoolExecutor

        @trace()
        def child_task():
            pass

        @trace()
        def parent_task():
            with TracedThreadPoolExecutor() as executor:
                # Context is automatically propagated
                executor.submit(child_task)

    Using global instrumentation::

        from honeyhive.tracer.utils.threading import instrument_threading
        from concurrent.futures import ThreadPoolExecutor

        # Call once at startup
        instrument_threading()

        # Now all ThreadPoolExecutor usage propagates context automatically
        with ThreadPoolExecutor() as executor:
            executor.submit(child_task)
"""

from concurrent.futures import Future, ThreadPoolExecutor
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from opentelemetry import context as otel_context
from opentelemetry.context import Context

T = TypeVar("T")

# Track whether we've already instrumented ThreadPoolExecutor
_threading_instrumented = False
_original_submit: Optional[Callable] = None


def with_trace_context(func: Callable[..., T]) -> Callable[..., T]:
    """Wrap a function to capture and propagate OpenTelemetry context.

    This wrapper captures the current OpenTelemetry context at the time
    the wrapper is called (typically when passed to executor.submit()),
    and attaches that context when the function actually executes in
    the worker thread.

    Args:
        func: The function to wrap

    Returns:
        A wrapped function that propagates trace context

    Example:
        >>> from concurrent.futures import ThreadPoolExecutor
        >>> from honeyhive import trace
        >>> from honeyhive.tracer.utils.threading import with_trace_context
        >>>
        >>> @trace()
        ... def my_task():
        ...     pass
        >>>
        >>> with ThreadPoolExecutor() as executor:
        ...     # Context is captured here and propagated to worker thread
        ...     future = executor.submit(with_trace_context(my_task))
    """
    # Capture the current context NOW (in the calling thread)
    captured_context: Context = otel_context.get_current()

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Attach the captured context in the worker thread
        token = otel_context.attach(captured_context)
        try:
            return func(*args, **kwargs)
        finally:
            otel_context.detach(token)

    return wrapper


class TracedThreadPoolExecutor(ThreadPoolExecutor):
    """A ThreadPoolExecutor that automatically propagates OpenTelemetry context.

    This is a drop-in replacement for concurrent.futures.ThreadPoolExecutor
    that automatically captures and propagates the OpenTelemetry trace context
    to worker threads. Spans created in worker threads will be properly
    parented to the calling thread's active span.

    Example:
        >>> from honeyhive import trace
        >>> from honeyhive.tracer.utils.threading import TracedThreadPoolExecutor
        >>>
        >>> @trace()
        ... def my_task():
        ...     # This span will be a child of the parent_task span
        ...     pass
        >>>
        >>> @trace()
        ... def parent_task():
        ...     with TracedThreadPoolExecutor(max_workers=4) as executor:
        ...         future = executor.submit(my_task)
        ...         result = future.result()
    """

    def submit(
        self, fn: Callable[..., T], *args: Any, **kwargs: Any
    ) -> "Future[T]":
        """Submit a callable to be executed with trace context propagation.

        The current OpenTelemetry context is captured at submit time and
        attached in the worker thread before executing the callable.

        Args:
            fn: The callable to execute
            *args: Positional arguments for the callable
            **kwargs: Keyword arguments for the callable

        Returns:
            A Future representing the execution of the callable
        """
        # Capture context at submit time (in the calling thread)
        captured_context: Context = otel_context.get_current()

        def context_wrapper() -> T:
            # Attach context in the worker thread
            token = otel_context.attach(captured_context)
            try:
                return fn(*args, **kwargs)
            finally:
                otel_context.detach(token)

        return super().submit(context_wrapper)


def instrument_threading() -> bool:
    """Instrument ThreadPoolExecutor to automatically propagate trace context.

    This function monkey-patches concurrent.futures.ThreadPoolExecutor.submit
    to automatically capture and propagate OpenTelemetry context to worker
    threads. After calling this function, all ThreadPoolExecutor usage will
    propagate context automatically.

    This is idempotent - calling it multiple times has no additional effect.

    Returns:
        True if instrumentation was applied, False if already instrumented

    Example:
        >>> from honeyhive.tracer.utils.threading import instrument_threading
        >>> from concurrent.futures import ThreadPoolExecutor
        >>>
        >>> # Call once at application startup
        >>> instrument_threading()
        >>>
        >>> # Now all executor usage propagates context
        >>> with ThreadPoolExecutor() as executor:
        ...     executor.submit(my_task)  # Context automatically propagated

    Warning:
        This modifies the global ThreadPoolExecutor class. While generally
        safe, it may affect other libraries that depend on the original
        behavior. Use TracedThreadPoolExecutor for a more isolated solution.
    """
    global _threading_instrumented, _original_submit

    if _threading_instrumented:
        return False

    # Save original submit method
    _original_submit = ThreadPoolExecutor.submit

    def instrumented_submit(
        self: ThreadPoolExecutor, fn: Callable[..., T], *args: Any, **kwargs: Any
    ) -> "Future[T]":
        """Instrumented submit that propagates trace context."""
        # Capture context at submit time
        captured_context: Context = otel_context.get_current()

        def context_wrapper() -> T:
            token = otel_context.attach(captured_context)
            try:
                return fn(*args, **kwargs)
            finally:
                otel_context.detach(token)

        return _original_submit(self, context_wrapper)

    # Apply the patch
    ThreadPoolExecutor.submit = instrumented_submit  # type: ignore
    _threading_instrumented = True

    return True


def uninstrument_threading() -> bool:
    """Remove ThreadPoolExecutor instrumentation.

    Restores the original ThreadPoolExecutor.submit method.

    Returns:
        True if uninstrumentation was applied, False if not instrumented

    Example:
        >>> from honeyhive.tracer.utils.threading import (
        ...     instrument_threading,
        ...     uninstrument_threading,
        ... )
        >>>
        >>> instrument_threading()  # Enable
        >>> # ... use executors ...
        >>> uninstrument_threading()  # Disable
    """
    global _threading_instrumented, _original_submit

    if not _threading_instrumented or _original_submit is None:
        return False

    # Restore original submit method
    ThreadPoolExecutor.submit = _original_submit  # type: ignore
    _threading_instrumented = False
    _original_submit = None

    return True


def is_threading_instrumented() -> bool:
    """Check if ThreadPoolExecutor is currently instrumented.

    Returns:
        True if instrumented, False otherwise
    """
    return _threading_instrumented
