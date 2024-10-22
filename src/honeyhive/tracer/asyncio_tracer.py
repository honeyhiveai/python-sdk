import asyncio
from asyncio import futures
from timeit import default_timer
from typing import Collection

from wrapt import wrap_function_wrapper as _wrap

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.metrics import get_meter
from opentelemetry.trace import get_tracer
from opentelemetry.trace.status import Status, StatusCode


ASYNCIO_PREFIX = "asyncio"
VERSION = "1.0.0"


class AsyncioInstrumentor(BaseInstrumentor):
    """
    A simplified instrumentor for asyncio that wraps and traces all main asyncio methods.
    """

    # List of asyncio methods to instrument (excluding 'gather')
    methods_to_instrument = [
        "create_task",
        "ensure_future",
        "wait",
        "wait_for",
        "as_completed",
        "to_thread",
        "run_coroutine_threadsafe",
    ]

    # List of specific coroutines to instrument
    coroutines_to_instrument = [
        # "sleep",
    ]

    def instrumentation_dependencies(self) -> Collection[str]:
        return []

    def _instrument(self, **kwargs):
        # Initialize tracer and meter
        self._tracer = get_tracer(
            __name__, VERSION, tracer_provider=kwargs.get("tracer_provider")
        )
        self._meter = get_meter(
            __name__, VERSION, meter_provider=kwargs.get("meter_provider")
        )

        # Create metrics
        self.process_duration_histogram = self._meter.create_histogram(
            name="asyncio.process.duration",
            description="Duration of asyncio process",
            unit="ms",
        )
        self.process_created_counter = self._meter.create_counter(
            name="asyncio.process.created",
            description="Number of asyncio processes",
            unit="1",
        )

        # Instrument each specified asyncio method (excluding 'gather')
        for method in self.methods_to_instrument:
            self._instrument_method(method)

        # Instrument 'gather' with a separate wrapper
        self._instrument_gather()

        # Instrument specific coroutines
        for coro in self.coroutines_to_instrument:
            self._instrument_coroutine(coro)

    def _uninstrument(self, **kwargs):
        # Uninstrument each specified asyncio method
        for method in self.methods_to_instrument:
            unwrap(asyncio, method)

        # Uninstrument 'gather'
        unwrap(asyncio, "gather")

        # Uninstrument specific coroutines
        for coro in self.coroutines_to_instrument:
            self._uninstrument_coroutine(coro)

    def _instrument_method(self, method_name: str):
        original_method = getattr(asyncio, method_name)

        if asyncio.iscoroutinefunction(original_method):
            async def wrapper(wrapped, instance, args, kwargs):
                start_time = default_timer()
                with self._tracer.start_as_current_span(f"{ASYNCIO_PREFIX}.{method_name}") as span:
                    try:
                        result = await wrapped(*args, **kwargs)
                        if isinstance(result, futures.Future):
                            self._attach_callback(result, span, start_time)
                        else:
                            # Record metrics directly
                            duration = max(default_timer() - start_time, 0)
                            self.process_duration_histogram.record(duration, {"operation": ASYNCIO_PREFIX})
                            self.process_created_counter.add(1, {"operation": ASYNCIO_PREFIX})
                        return result
                    except Exception as exc:
                        span.set_status(Status(StatusCode.ERROR, str(exc)))
                        raise
            _wrap(asyncio, method_name, wrapper)
        else:
            def wrapper(wrapped, instance, args, kwargs):
                start_time = default_timer()
                with self._tracer.start_as_current_span(f"{ASYNCIO_PREFIX}.{method_name}") as span:
                    try:
                        result = wrapped(*args, **kwargs)
                        if isinstance(result, futures.Future):
                            self._attach_callback(result, span, start_time)
                        else:
                            # Record metrics directly
                            duration = max(default_timer() - start_time, 0)
                            self.process_duration_histogram.record(duration, {"operation": ASYNCIO_PREFIX})
                            self.process_created_counter.add(1, {"operation": ASYNCIO_PREFIX})
                        return result
                    except Exception as exc:
                        span.set_status(Status(StatusCode.ERROR, str(exc)))
                        raise
            _wrap(asyncio, method_name, wrapper)

    def _instrument_gather(self):
        async def wrapper(wrapped, instance, args, kwargs):
            with self._tracer.start_as_current_span(f"{ASYNCIO_PREFIX}.gather") as span:
                start_time = default_timer()
                try:
                    result = await wrapped(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as exc:
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    raise
                finally:
                    duration = max(default_timer() - start_time, 0)
                    self.process_duration_histogram.record(duration, {"operation": ASYNCIO_PREFIX})
                    self.process_created_counter.add(1, {"operation": ASYNCIO_PREFIX})

        _wrap(asyncio, "gather", wrapper)

    def _attach_callback(self, obj, span, start_time):
        def callback(fut):
            duration = max(default_timer() - start_time, 0)
            self.process_duration_histogram.record(duration, {"operation": ASYNCIO_PREFIX})
            self.process_created_counter.add(1, {"operation": ASYNCIO_PREFIX})

            if fut.cancelled():
                span.set_status(Status(StatusCode.ERROR, "Cancelled"))
            elif fut.exception():
                span.set_status(Status(StatusCode.ERROR, str(fut.exception())))
            else:
                span.set_status(Status(StatusCode.OK))
            span.end()

        if isinstance(obj, futures.Future):
            obj.add_done_callback(callback)
        else:
            # Not a Future; cannot attach a callback safely
            pass

    def _instrument_coroutine(self, coro_name: str):
        """
        Wrap and trace the specified asyncio coroutine.
        """

        original_coro = getattr(asyncio, coro_name, None)
        if original_coro is None or not asyncio.iscoroutinefunction(original_coro):
            # The specified coroutine does not exist or is not a coroutine function
            return

        def coro_wrapper(wrapped, instance, args, kwargs):
            async def traced_coroutine(*args, **kwargs):
                span = self._tracer.start_span(f"{ASYNCIO_PREFIX}.{coro_name}")
                start_time = default_timer()
                try:
                    result = await wrapped(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as exc:
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    raise
                finally:
                    duration = max(default_timer() - start_time, 0)
                    self.process_duration_histogram.record(
                        duration, {"operation": ASYNCIO_PREFIX, "coroutine": coro_name}
                    )
                    self.process_created_counter.add(
                        1, {"operation": ASYNCIO_PREFIX, "coroutine": coro_name}
                    )
                    span.end()

            return traced_coroutine(*args, **kwargs)

        _wrap(asyncio, coro_name, coro_wrapper)

    def _uninstrument_coroutine(self, coro_name: str):
        """
        Unwrap the specified asyncio coroutine.
        """
        original_coro = getattr(asyncio, coro_name, None)
        if original_coro is None or not asyncio.iscoroutinefunction(original_coro):
            return
        unwrap(asyncio, coro_name)

# Instrument the AsyncioInstrumentor
asyncio_instrumentor = AsyncioInstrumentor()
asyncio_instrumentor.instrument()