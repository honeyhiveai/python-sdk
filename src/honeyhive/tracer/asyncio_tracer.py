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

# TODO: this instrumentor does not work as expected

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
        """
        Wrap and trace the specified asyncio method.
        """

        def wrapper(wrapped, instance, args, kwargs):
            start_time = default_timer()
            span = self._tracer.start_span(f"{ASYNCIO_PREFIX}.{method_name}")

            try:
                result = wrapped(*args, **kwargs)
                # If the result is a coroutine or future, attach a callback to trace its completion
                if asyncio.iscoroutine(result) or futures.isfuture(result):
                    self._attach_callback(result, span, start_time)
                return result
            except Exception as exc:
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise
            finally:
                span.end()

        _wrap(asyncio, method_name, wrapper)

    def _instrument_gather(self):
        """
        Wrap and trace asyncio.gather with a separate span that acts as the parent for all gathered coroutines.
        """

        original_gather = asyncio.gather

        async def gather_wrapper(*args, **kwargs):
            with self._tracer.start_as_current_span(
                f"{ASYNCIO_PREFIX}.gather"
            ) as span:
                start_time = default_timer()
                try:
                    result = await original_gather(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as exc:
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    raise
                finally:
                    duration = max(default_timer() - start_time, 0)
                    self.process_duration_histogram.record(
                        duration, {"operation": ASYNCIO_PREFIX}
                    )
                    self.process_created_counter.add(
                        1, {"operation": ASYNCIO_PREFIX}
                    )

        # Replace asyncio.gather with the gather_wrapper
        _wrap(
            asyncio, 
            "gather", 
            lambda wrapped, instance, args, kwargs: \
                gather_wrapper(*args, **kwargs)
        )

    def _attach_callback(self, obj, span, start_time):
        """
        Attach a callback to the coroutine or future to record metrics upon completion.
        """

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

        if asyncio.iscoroutine(obj):
            obj = asyncio.ensure_future(obj)
        obj.add_done_callback(callback)

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


instrumentor = AsyncioInstrumentor()
instrumentor.instrument()
