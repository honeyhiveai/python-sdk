"""Provider-level span interception for HoneyHive tracer.

This module implements span interception at the TracerProvider level to ensure
semantic convention processing happens for ALL spans created by ANY tracer
from our provider, including third-party instrumentors like OpenInference and Traceloop.

This is the correct architectural solution for the BYOI multi-instance design.
"""

import functools
import inspect
import json
import threading
from typing import Any, Callable, Dict, List, Optional

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import Span, Tracer

from ...utils.logger import safe_log

# Import Universal LLM Discovery Engine v4.0
from .semantic_conventions.universal_processor import UniversalSemanticConventionProcessor


class InterceptedTracer:
    """Wrapper around OpenTelemetry Tracer that intercepts span creation.

    This class wraps any tracer obtained from our TracerProvider to ensure
    that ALL spans (including those from instrumentors) get pre-end processing.
    """

    def __init__(
        self, original_tracer: Tracer, pre_end_processors: List[Callable[[Span], None]]
    ):
        """Initialize intercepted tracer.

        Args:
            original_tracer: The original OpenTelemetry tracer to wrap
            pre_end_processors: List of functions to call before span ends
        """
        self._original_tracer = original_tracer
        self._pre_end_processors = pre_end_processors
        self._interception_count = 0

        # Forward all attributes to the original tracer
        self.__dict__.update(original_tracer.__dict__)

    def start_span(
        self,
        name: str,
        *,
        context: Optional[Any] = None,
        kind: Optional[Any] = None,
        attributes: Optional[Dict[str, Any]] = None,
        links: Optional[Any] = None,
        start_time: Optional[Any] = None,
        record_exception: bool = True,
        set_status_on_exception: bool = True,
    ) -> Any:
        """Intercept span creation to add pre-end processing.

        Args:
            name: Span name
            context: Optional context
            kind: Span kind
            attributes: Initial attributes
            links: Span links
            start_time: Start time
            record_exception: Whether to record exceptions
            set_status_on_exception: Whether to set status on exception

        Returns:
            Span with pre-end interception setup
        """
        # Create span normally using original tracer
        span_kwargs = {
            "context": context,
            "attributes": attributes,
            "links": links,
            "start_time": start_time,
            "record_exception": record_exception,
            "set_status_on_exception": set_status_on_exception,
        }

        # Only add kind if it's not None
        if kind is not None:
            span_kwargs["kind"] = kind

        span = self._original_tracer.start_span(name, **span_kwargs)  # type: ignore

        # Apply pre-end interception to the span
        self._setup_span_interception(span)

        self._interception_count += 1

        safe_log(
            None,
            "debug",
            (
                "🔍 PROVIDER INTERCEPTION: Intercepted span creation - "
                "tracer: %s, span: %s (total: %d)"
            ),
            getattr(self._original_tracer, "_instrument_module_name", "unknown"),
            name,
            self._interception_count,
        )

        return span

    def _setup_span_interception(self, span: Span) -> None:
        """Setup pre-end interception on a span with comprehensive mitigations.

        This method implements several mitigations for prototype mismatch risks:
        1. Signature validation for defensive programming
        2. Future-compatible parameter forwarding with *args, **kwargs
        3. Method metadata preservation with functools.wraps
        4. Proper type annotations matching OpenTelemetry specifications

        Args:
            span: Span to intercept
        """
        if not hasattr(span, "end") or not self._pre_end_processors:
            return

        # Store original end method
        original_end = span.end

        # Mitigation 2: Add signature validation for defensive programming
        try:
            sig = inspect.signature(original_end)
            expected_params = ["end_time"]
            actual_params = [
                name for name, param in sig.parameters.items()
                if param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
            ]
            
            if actual_params and actual_params != expected_params:
                safe_log(
                    None,
                    "warning",
                    "🔍 SPAN END INTERCEPTION: Signature mismatch detected - "
                    "expected %s, got %s. Using flexible forwarding.",
                    expected_params,
                    actual_params,
                )
        except (ValueError, TypeError) as e:
            safe_log(
                None,
                "debug",
                "🔍 SPAN END INTERCEPTION: Could not inspect signature: %s. "
                "Proceeding with flexible forwarding.",
                str(e),
            )

        # Mitigation 3 & 4: Create intercepted end method with proper signature and metadata
        @functools.wraps(original_end)
        def intercepted_end(*args, **kwargs) -> None:
            """Intercepted end method that processes span before ending.
            
            This method preserves the original span.end() signature and forwards
            all arguments to maintain compatibility with current and future
            OpenTelemetry versions.
            
            Args:
                *args: Positional arguments forwarded to original end method
                **kwargs: Keyword arguments forwarded to original end method
            """
            safe_log(
                None,
                "debug",
                "🔍 SPAN END INTERCEPTION: Processing span %s before ending",
                getattr(span, "name", "unknown"),
            )

            # Execute pre-end processors while span is still mutable
            for processor in self._pre_end_processors:
                try:
                    processor(span)
                except Exception as e:
                    safe_log(
                        None,
                        "error",
                        "Pre-end processor failed for span %s: %s",
                        getattr(span, "name", "unknown"),
                        str(e),
                    )

            # Call original end method with all arguments preserved
            try:
                return original_end(*args, **kwargs)
            except Exception as e:
                safe_log(
                    None,
                    "error",
                    "Original span.end() failed for span %s: %s",
                    getattr(span, "name", "unknown"),
                    str(e),
                )
                # Re-raise the exception to maintain original behavior
                raise

        # Replace span's end method with improved intercepted version
        span.end = intercepted_end

    def __getattr__(self, name: str) -> Any:
        """Forward all other attributes to the original tracer."""
        safe_log(
            None,
            "debug",
            "🔍 INTERCEPTED TRACER: Method %s called on intercepted tracer",
            name,
        )
        return getattr(self._original_tracer, name)

    def __repr__(self) -> str:
        return f"InterceptedTracer(original={self._original_tracer})"


class InterceptingTracerProvider:
    """TracerProvider wrapper that creates intercepted tracers.

    This class wraps a TracerProvider to ensure that ALL tracers obtained
    from it (including by instrumentors) create spans with pre-end processing.
    """

    def __init__(
        self, original_provider: TracerProvider, tracer_instance: Optional[Any] = None
    ):
        """Initialize intercepting tracer provider.

        Args:
            original_provider: The original TracerProvider to wrap
            tracer_instance: HoneyHive tracer instance for logging context
        """
        self._original_provider = original_provider
        self._tracer_instance = tracer_instance
        self._pre_end_processors: List[Callable[[Span], None]] = []
        self._processors_lock = threading.RLock()
        self._created_tracers: Dict[str, InterceptedTracer] = {}
        self._tracers_lock = threading.RLock()

        # Register default semantic convention processor
        self._register_default_processors()

        safe_log(
            tracer_instance,
            "info",
            "🔍 PROVIDER INTERCEPTION: Initialized intercepting provider wrapper",
        )

    def _register_default_processors(self) -> None:
        """Register default pre-end processors."""
        self.register_pre_end_processor(self._semantic_convention_processor)

    def register_pre_end_processor(self, processor: Callable[[Span], None]) -> None:
        """Register a pre-end processor for all spans.

        Args:
            processor: Function to call before any span ends
        """
        with self._processors_lock:
            self._pre_end_processors.append(processor)

        safe_log(
            self._tracer_instance,
            "debug",
            "🔍 PROVIDER INTERCEPTION: Registered pre-end processor: %s",
            getattr(processor, "__name__", "anonymous"),
        )

    def get_tracer(
        self,
        instrumenting_module_name: str,
        instrumenting_library_version: Optional[str] = None,
        schema_url: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Get an intercepted tracer.

        This method is called by instrumentors to get their tracer. We return
        an InterceptedTracer that will apply pre-end processing to all spans.

        Args:
            instrumenting_module_name: Name of the instrumenting module
            instrumenting_library_version: Version of the instrumenting library
            schema_url: Schema URL
            attributes: Optional attributes for the tracer

        Returns:
            InterceptedTracer that will process all spans before they end
        """
        safe_log(
            self._tracer_instance,
            "info",
            "🔍 PROVIDER INTERCEPTION: get_tracer called for %s (version: %s)",
            instrumenting_module_name,
            instrumenting_library_version or "unknown",
        )
        tracer_key = f"{instrumenting_module_name}:{instrumenting_library_version}"

        with self._tracers_lock:
            # Check if we already created this tracer
            if tracer_key in self._created_tracers:
                return self._created_tracers[tracer_key]

            # Get original tracer from provider
            original_tracer = self._original_provider.get_tracer(
                instrumenting_module_name=instrumenting_module_name,
                instrumenting_library_version=instrumenting_library_version,
                schema_url=schema_url,
                attributes=attributes,
            )

            # Create intercepted version
            with self._processors_lock:
                intercepted_tracer = InterceptedTracer(
                    original_tracer, self._pre_end_processors.copy()
                )

            # Cache it
            self._created_tracers[tracer_key] = intercepted_tracer

            safe_log(
                self._tracer_instance,
                "info",
                "🔍 PROVIDER INTERCEPTION: Created intercepted tracer for %s "
                "(version: %s) with %d processors",
                instrumenting_module_name,
                instrumenting_library_version or "unknown",
                len(self._pre_end_processors),
            )

            safe_log(
                self._tracer_instance,
                "info",
                "🔍 PROVIDER INTERCEPTION: Returning intercepted tracer %s (type: %s)",
                id(intercepted_tracer),
                type(intercepted_tracer).__name__,
            )

            return intercepted_tracer

    def _semantic_convention_processor(self, span: Span) -> None:
        """Default semantic convention processor using Universal LLM Discovery Engine v4.0.

        Args:
            span: Span to process
        """
        safe_log(
            self._tracer_instance,
            "info",
            "🔍 SEMANTIC CONVENTION PROCESSOR: Called for span %s (Universal Engine v4.0)",
            getattr(span, "name", "unknown"),
        )
        try:
            # Initialize universal processor (singleton per provider)
            if not hasattr(self, '_universal_processor'):
                self._universal_processor = UniversalSemanticConventionProcessor(cache_manager=None)

            span_attributes = self._extract_span_attributes(span)
            if not span_attributes:
                return

            # Process semantic conventions using Universal Engine v4.0
            self._process_semantic_conventions_v4(span, span_attributes)

        except Exception as e:
            safe_log(
                self._tracer_instance,
                "error",
                "Universal Engine semantic convention processing failed for span %s: %s",
                getattr(span, "name", "unknown"),
                str(e),
            )

    def _process_semantic_conventions_v4(
        self, span: Span, span_attributes: Dict[str, Any]
    ) -> None:
        """Process semantic conventions using Universal LLM Discovery Engine v4.0."""
        # Filter out HoneyHive attributes for provider detection
        filtered_attributes = {
            k: v
            for k, v in span_attributes.items()
            if not k.startswith(("honeyhive", "traceloop.association.properties"))
        }

        if not filtered_attributes:
            return

        # Process using Universal Engine v4.0 (O(1) detection)
        event_data = self._universal_processor.processor.process_span_attributes(filtered_attributes)  # type: ignore[union-attr]

        # Check if provider was detected
        detected_provider = event_data.get("metadata", {}).get("provider", "unknown")
        
        safe_log(
            self._tracer_instance,
            "debug",
            "🔍 UNIVERSAL ENGINE: Detected %s for span %s with %d attributes",
            detected_provider,
            getattr(span, "name", "unknown"),
            len(span_attributes),
        )

        if detected_provider == "unknown":
            return

        # Apply processed data to span
        self._apply_event_data_to_span_v4(
            span, event_data, detected_provider
        )

    def _extract_span_attributes(self, span: Span) -> Dict[str, Any]:
        """Extract attributes from span."""
        return (
            dict(getattr(span, "attributes", {})) if hasattr(span, "attributes") else {}
        )

    def _apply_event_data_to_span_v4(
        self,
        span: Span,
        event_data: Dict[str, Any],
        detected_provider: str,
    ) -> None:
        """Apply Universal Engine processed event data to span attributes."""
        # Apply all sections (inputs, outputs, config, metadata)
        for section_name in ["inputs", "outputs", "config", "metadata"]:
            section_data = event_data.get(section_name)
            if section_data and isinstance(section_data, dict):
                self._apply_section_to_span(span, section_data, f"honeyhive_{section_name}")
        
        # Set provider and engine version
        span.set_attribute("honeyhive.detected_provider", detected_provider)
        span.set_attribute("honeyhive.universal_engine_version", "4.0")

        safe_log(
            self._tracer_instance,
            "info",
            "Applied %s provider conventions to span %s using Universal Engine v4.0",
            detected_provider,
            getattr(span, "name", "unknown"),
        )

    def _apply_event_data_to_span(
        self,
        span: Span,
        event_data: Dict[str, Any],
        event_type: str,
        detected_convention: str,
    ) -> None:
        """Apply processed event data to span attributes (OLD SYSTEM - DEPRECATED)."""
        # Process inputs
        self._apply_section_to_span(span, event_data.get("inputs"), "honeyhive_inputs")

        # Process outputs
        self._apply_section_to_span(
            span, event_data.get("outputs"), "honeyhive_outputs"
        )

        # Mark span as pre-processed for backend fast-path validation
        span.set_attribute("honeyhive_processed", "true")
        span.set_attribute("honeyhive_schema_version", "1.0")
        span.set_attribute("honeyhive_event_type", event_type)

        safe_log(
            self._tracer_instance,
            "info",
            "✅ SEMANTIC CONVENTIONS: Processed %s span %s - inputs: %d, outputs: %d",
            detected_convention,
            getattr(span, "name", "unknown"),
            len(event_data.get("inputs", {})),
            len(event_data.get("outputs", {})),
        )

    def _apply_section_to_span(
        self, span: Span, section_data: Any, prefix: str
    ) -> None:
        """Apply a section of event data to span attributes."""
        if not section_data or not isinstance(section_data, dict):
            return

        for key, value in section_data.items():
            if isinstance(value, (list, dict)):
                # Serialize structured data as JSON for OpenTelemetry compatibility
                span.set_attribute(f"{prefix}.{key}", json.dumps(value))
            else:
                span.set_attribute(f"{prefix}.{key}", str(value))

    def __getattr__(self, name: str) -> Any:
        """Forward all other attributes to the original provider."""
        return getattr(self._original_provider, name)

    def __repr__(self) -> str:
        return f"InterceptingTracerProvider(original={self._original_provider})"


def setup_provider_interception(tracer_instance: Any) -> None:
    """Setup provider-level span interception for a HoneyHive tracer instance.

    This function wraps the tracer's provider to ensure ALL spans created
    by ANY tracer from that provider get pre-end processing.

    Args:
        tracer_instance: HoneyHive tracer instance to setup interception for
    """
    if not hasattr(tracer_instance, "provider") or tracer_instance.provider is None:
        safe_log(
            tracer_instance,
            "warning",
            "Cannot setup provider interception - no provider available",
        )
        return

    # Check if already intercepted
    if isinstance(tracer_instance.provider, InterceptingTracerProvider):
        safe_log(tracer_instance, "debug", "Provider interception already setup")
        return

    # Wrap the provider
    original_provider = tracer_instance.provider
    intercepting_provider = InterceptingTracerProvider(
        original_provider, tracer_instance
    )

    # Replace the provider
    tracer_instance.provider = intercepting_provider

    # Update the tracer to use the new provider
    if hasattr(tracer_instance, "tracer") and tracer_instance.tracer:
        # The tracer's provider reference needs to be updated too
        tracer_instance.tracer._provider = intercepting_provider

    safe_log(
        tracer_instance,
        "info",
        "✅ PROVIDER INTERCEPTION: Setup complete - all spans from this "
        "provider will be intercepted",
    )


def is_provider_intercepted(tracer_instance: Any) -> bool:
    """Check if a tracer instance has provider interception setup.

    Args:
        tracer_instance: HoneyHive tracer instance to check

    Returns:
        True if provider interception is active
    """
    return hasattr(tracer_instance, "provider") and isinstance(
        tracer_instance.provider, InterceptingTracerProvider
    )
