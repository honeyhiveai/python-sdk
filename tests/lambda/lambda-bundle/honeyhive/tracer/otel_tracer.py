"""OpenTelemetry tracer implementation for HoneyHive."""

import inspect
import json
import os
import threading
import time
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional

if TYPE_CHECKING:
    from opentelemetry import baggage, context, trace
    from opentelemetry.baggage.propagation import W3CBaggagePropagator
    from opentelemetry.context import Context
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.propagators.composite import CompositePropagator
    from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor, TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

try:
    from opentelemetry import baggage, context, trace
    from opentelemetry.baggage.propagation import W3CBaggagePropagator
    from opentelemetry.context import Context
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.propagators.composite import CompositePropagator
    from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor, TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

from ..api.client import HoneyHive
from ..api.events import CreateEventRequest, UpdateEventRequest
from ..api.session import SessionAPI
from ..models.generated import EventType1
from ..utils.config import config
from .span_processor import HoneyHiveSpanProcessor


class HoneyHiveTracer:
    """HoneyHive OpenTelemetry tracer implementation."""

    # Instance attributes
    session_id: Optional[str]
    client: Optional[Any]
    session_api: Optional[Any] = None
    is_main_provider: bool = False
    provider: Optional[Any] = None
    tracer: Optional[Any] = None
    span_processor: Optional[Any] = None
    propagator: Optional[Any] = None

    def __init__(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        source: str = "dev",
        test_mode: bool = False,
        session_name: Optional[str] = None,
        instrumentors: Optional[list] = None,
        disable_http_tracing: bool = True,
    ):
        """Initialize the HoneyHive tracer.

        Args:
            api_key: HoneyHive API key
            project: Project name
            source: Source environment
            test_mode: Whether to run in test mode
            session_name: Optional session name for automatic session creation
            instrumentors: List of OpenInference instrumentors to automatically integrate
            disable_http_tracing: Whether to disable HTTP tracing (defaults to True)
        """
        if not OTEL_AVAILABLE:
            raise ImportError("OpenTelemetry is required for HoneyHiveTracer")

        self.test_mode = test_mode
        self.disable_http_tracing = disable_http_tracing

        # Set HTTP tracing environment variable based on parameter
        if disable_http_tracing:
            os.environ["HH_DISABLE_HTTP_TRACING"] = "true"
        else:
            os.environ["HH_DISABLE_HTTP_TRACING"] = "false"

        # In test mode, we can proceed without an API key
        if not test_mode:
            self.api_key = api_key or config.api_key
            if not self.api_key:
                raise ValueError("API key is required for HoneyHiveTracer")
        else:
            # Use a dummy API key for test mode
            self.api_key = api_key or config.api_key or "test-api-key"

        self.project = project or config.project or "default"
        self.source = source

        # Set default session name to the calling file name if not provided
        if session_name is None:
            try:
                # Get the calling frame to find the file where tracer was initialized
                frame = inspect.currentframe()
                if frame:
                    # Go up the call stack to find the caller
                    caller_frame = frame.f_back
                    if caller_frame:
                        # Get the filename from the caller frame
                        filename = caller_frame.f_code.co_filename
                        if filename and filename != "<string>":
                            # Extract just the filename without path and extension
                            session_name = os.path.splitext(os.path.basename(filename))[
                                0
                            ]
                        else:
                            session_name = f"tracer_session_{int(time.time())}"
                    else:
                        session_name = f"tracer_session_{int(time.time())}"
                else:
                    session_name = f"tracer_session_{int(time.time())}"
            except Exception:
                # Fallback to timestamp-based name if anything goes wrong
                session_name = f"tracer_session_{int(time.time())}"

        self.session_name = session_name

        # Initialize OpenTelemetry components
        self._initialize_otel()

        # Initialize session management
        self._initialize_session()

        # Set up baggage context
        self._setup_baggage_context()

        # Auto-integrate instrumentors if provided
        if instrumentors:
            self._integrate_instrumentors(instrumentors)

        print(f"✓ HoneyHiveTracer initialized for project: {self.project}")
        print(f"✓ Session name: {self.session_name}")
        if disable_http_tracing:
            print("✓ HTTP tracing disabled")
        else:
            print("✓ HTTP tracing enabled")

    @classmethod
    def reset(cls) -> None:
        """Reset the tracer instance.

        Note: This method is no longer needed in multi-instance mode.
        Each tracer instance is independent and can be discarded when no longer needed.
        """
        # In multi-instance mode, simply log that reset is not needed
        print(
            "ℹ️  Reset not needed in multi-instance mode. Each tracer instance is independent."
        )
        print("   Discard tracer instances when no longer needed instead of resetting.")

    @classmethod
    def init(
        cls,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        source: str = "dev",
        test_mode: bool = False,
        session_name: Optional[str] = None,
        server_url: Optional[str] = None,
        instrumentors: Optional[list] = None,
        disable_http_tracing: bool = True,
    ) -> "HoneyHiveTracer":
        """Initialize the HoneyHive tracer (official API for backwards compatibility).

        This method provides the same functionality as the constructor but follows
        the official HoneyHive SDK API pattern shown in production documentation.

        Args:
            api_key: HoneyHive API key
            project: Project name
            source: Source environment (defaults to "production")
            test_mode: Whether to run in test mode
            session_name: Optional session name for automatic session creation
            server_url: Optional server URL for self-hosted deployments
            instrumentors: List of OpenInference instrumentors to automatically integrate
            disable_http_tracing: Whether to disable HTTP tracing (defaults to True)

        Returns:
            HoneyHiveTracer instance
        """
        # Handle server_url parameter (maps to api_url in our config)
        if server_url:
            # Set the server URL in environment for this initialization
            original_api_url = os.environ.get("HH_API_URL")
            os.environ["HH_API_URL"] = server_url

            try:
                # Create tracer with server URL
                tracer = cls(
                    api_key=api_key,
                    project=project,
                    source=source,
                    test_mode=test_mode,
                    session_name=session_name,
                    instrumentors=instrumentors,
                    disable_http_tracing=disable_http_tracing,
                )
                return tracer
            finally:
                # Restore original API URL
                if original_api_url is not None:
                    os.environ["HH_API_URL"] = original_api_url
                else:
                    os.environ.pop("HH_API_URL", None)
        else:
            # Standard initialization without server URL
            return cls(
                api_key=api_key,
                project=project,
                source=source,
                test_mode=test_mode,
                session_name=session_name,
                instrumentors=instrumentors,
                disable_http_tracing=disable_http_tracing,
            )

    def _initialize_otel(self) -> None:
        """Initialize OpenTelemetry components."""
        # Check if a tracer provider already exists
        existing_provider = trace.get_tracer_provider()
        is_main_provider = False

        # Check if the existing provider is a NoOp provider or None
        is_noop_provider = (
            existing_provider is None
            or str(type(existing_provider).__name__) == "NoOpTracerProvider"
            or "NoOp" in str(type(existing_provider).__name__)
        )

        if is_noop_provider:
            # No existing provider or only NoOp provider, we can be the main provider
            self.provider = TracerProvider()
            is_main_provider = True
            self.is_main_provider = True
            print("🔧 Creating new TracerProvider as main provider")
        else:
            # Use existing provider, we'll be a secondary provider
            self.provider = existing_provider
            self.is_main_provider = False
            print(
                f"🔧 Using existing TracerProvider: {type(existing_provider).__name__}"
            )
            print("   HoneyHive will add span processors to the existing provider")

        # Add span processor to enrich spans with HoneyHive attributes
        try:
            self.span_processor = HoneyHiveSpanProcessor()
            # Only add span processor if we can (i.e., if it's a TracerProvider instance)
            if hasattr(self.provider, "add_span_processor"):
                self.provider.add_span_processor(self.span_processor)
            else:
                print(
                    "⚠️  Existing provider doesn't support span processors, skipping HoneyHive integration"
                )
        except ImportError:
            print("⚠️  HoneyHiveSpanProcessor not available, skipping integration.")

        # Import required components
        try:
            from opentelemetry.sdk.trace.export import (
                BatchSpanProcessor,
                ConsoleSpanExporter,
            )
        except ImportError:
            print("⚠️  Required OpenTelemetry components not available")
            return

        # Check if OTLP export is enabled
        otlp_enabled = os.getenv("HH_OTLP_ENABLED", "true").lower() != "false"

        if otlp_enabled and not self.test_mode:
            # Add OTLP span exporter to send spans to the backend service
            # This ensures spans are sent to the standard OTLP endpoint that your backend expects
            try:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                    OTLPSpanExporter,
                )

                # Configure OTLP exporter to send to your backend service
                # Your backend service is listening on the opentelemetry/v1/traces endpoint
                otlp_endpoint = f"{config.api_url}/opentelemetry/v1/traces"

                print(f"🔍 Sending spans to OTLP endpoint: {otlp_endpoint}")

                otlp_exporter = OTLPSpanExporter(
                    endpoint=otlp_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-Project": self.project,
                        "X-Source": self.source,
                    },
                )

                # Add OTLP exporter with batch processing if provider supports it
                if hasattr(self.provider, "add_span_processor"):
                    self.provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
                    print(
                        f"✓ OTLP exporter configured to send spans to: {otlp_endpoint}"
                    )
                else:
                    print(
                        "⚠️  Existing provider doesn't support span processors, OTLP export disabled"
                    )

            except ImportError:
                print(
                    "⚠️  OTLP exporter not available, using console exporter for debugging"
                )
                if hasattr(self.provider, "add_span_processor"):
                    self.provider.add_span_processor(
                        BatchSpanProcessor(ConsoleSpanExporter())
                    )
        else:
            print("🔍 OTLP export disabled, using no-op exporter for tests")

            # NoOpExporter was removed as it's not used

            # Use ConsoleSpanExporter instead of NoOpExporter to avoid type issues
            if hasattr(self.provider, "add_span_processor"):
                self.provider.add_span_processor(
                    BatchSpanProcessor(ConsoleSpanExporter())
                )

        # Set up propagators
        self.propagator = CompositePropagator(
            [
                TraceContextTextMapPropagator(),
                W3CBaggagePropagator(),
            ]
        )

        # Only set as global provider if we're the main provider
        if is_main_provider:
            trace.set_tracer_provider(self.provider)
            print("✓ Set as global TracerProvider")
        else:
            print("✓ Added to existing TracerProvider (not overriding global)")

        # Create tracer
        self.tracer = trace.get_tracer("honeyhive", "0.1.0")

    def _initialize_session(self) -> None:
        """Initialize session management."""
        try:
            # Create client and session API
            self.client = HoneyHive(
                api_key=self.api_key, base_url=config.api_url, test_mode=self.test_mode
            )
            self.session_api = SessionAPI(self.client)

            # Create a new session automatically
            print(
                f"🔍 Creating session with project: {self.project}, source: {self.source}"
            )
            session_response = self.session_api.start_session(
                project=self.project, session_name=self.session_name, source=self.source
            )

            if hasattr(session_response, "session_id"):
                self.session_id = session_response.session_id
                print(f"✓ HoneyHive session created: {self.session_id}")
            else:
                print(f"⚠️  Session response missing session_id: {session_response}")
                self.session_id = None

        except Exception as e:
            if not self.test_mode:
                print(f"Warning: Failed to create session: {e}")
                # Log the full exception details
                print(f"Exception details: {type(e).__name__}: {e}")
            self.session_id = None
            self.client = None
            self.session_api = None

    def _setup_baggage_context(self) -> None:
        """Set up baggage with session context for OpenInference integration."""
        try:
            # Always set up baggage context, even if session creation failed
            # This ensures OpenInference spans can still access project and source
            baggage_items = {}

            if self.session_id:
                baggage_items["session_id"] = self.session_id
                print(f"✓ Session context injected: {self.session_id}")
            else:
                print("⚠️  No session ID available, using project/source only")

            # Always set project and source in baggage
            baggage_items["project"] = self.project
            baggage_items["source"] = self.source

            # Add experiment harness information to baggage if available
            if config.experiment_id:
                baggage_items["experiment_id"] = config.experiment_id
                print(f"✓ Experiment ID injected: {config.experiment_id}")

            if config.experiment_name:
                baggage_items["experiment_name"] = config.experiment_name
                print(f"✓ Experiment name injected: {config.experiment_name}")

            if config.experiment_variant:
                baggage_items["experiment_variant"] = config.experiment_variant
                print(f"✓ Experiment variant injected: {config.experiment_variant}")

            if config.experiment_group:
                baggage_items["experiment_group"] = config.experiment_group
                print(f"✓ Experiment group injected: {config.experiment_group}")

            if config.experiment_metadata:
                # Add experiment metadata as JSON string for baggage compatibility
                try:
                    baggage_items["experiment_metadata"] = json.dumps(
                        config.experiment_metadata
                    )
                    print(
                        f"✓ Experiment metadata injected: {len(config.experiment_metadata)} items"
                    )
                except Exception:
                    # Fallback to string representation
                    baggage_items["experiment_metadata"] = str(
                        config.experiment_metadata
                    )
                    print(f"✓ Experiment metadata injected (string format)")

            # Set up baggage context
            ctx = context.get_current()
            for key, value in baggage_items.items():
                if value:
                    ctx = baggage.set_baggage(key, str(value), ctx)

            # Activate the context
            context.attach(ctx)

            print(f"✓ Baggage context set up with: {baggage_items}")

        except Exception as e:
            print(f"⚠️  Warning: Failed to set up baggage context: {e}")
            # Continue without baggage context - spans will still be processed

    def _integrate_instrumentors(self, instrumentors: list) -> None:
        """Automatically integrate with provided instrumentors."""
        for instrumentor in instrumentors:
            try:
                # Check if the instrumentor has an instrument method
                if hasattr(instrumentor, "instrument") and callable(
                    getattr(instrumentor, "instrument")
                ):
                    # Get the name for logging
                    name = (
                        getattr(instrumentor, "__class__", type(instrumentor)).__name__
                        or "Unknown"
                    )
                    print(f"🔗 Integrating {name}...")
                    instrumentor.instrument()
                    print(f"✓ {name} integrated.")
                else:
                    print(
                        f"⚠️  Skipping object without instrument method: {type(instrumentor)}"
                    )
            except Exception as e:
                print(f"⚠️  Failed to integrate instrumentor {type(instrumentor)}: {e}")

    @contextmanager
    def start_span(
        self,
        name: str,
        session_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterator[Optional[Any]]:
        """Start a new span with context manager.

        Args:
            name: Span name
            session_id: Session ID for baggage (defaults to tracer's session)
            parent_id: Parent event ID for tracking relationships
            attributes: Span attributes
            **kwargs: Additional span attributes
        """
        if not OTEL_AVAILABLE:
            yield None
            return

        # Use tracer's session ID if none provided
        if session_id is None:
            session_id = self.session_id

        # Prepare attributes
        span_attributes = attributes or {}
        span_attributes.update(kwargs)

        # Add session information to attributes
        if session_id:
            span_attributes["honeyhive.session_id"] = session_id
            span_attributes["honeyhive.project"] = self.project
            span_attributes["honeyhive.source"] = self.source

        # Add experiment harness information to attributes if available
        if config.experiment_id:
            span_attributes["honeyhive.experiment_id"] = config.experiment_id

        if config.experiment_name:
            span_attributes["honeyhive.experiment_name"] = config.experiment_name

        if config.experiment_variant:
            span_attributes["honeyhive.experiment_variant"] = config.experiment_variant

        if config.experiment_group:
            span_attributes["honeyhive.experiment_group"] = config.experiment_group

        if config.experiment_metadata:
            # Add experiment metadata as individual attributes for better observability
            for key, value in config.experiment_metadata.items():
                span_attributes[f"honeyhive.experiment_metadata.{key}"] = str(value)

        # Add parent_id if provided
        if parent_id:
            span_attributes["honeyhive.parent_id"] = parent_id

        # Set up baggage
        baggage_items = {}
        if session_id:
            baggage_items["session_id"] = session_id
            baggage_items["project"] = self.project
            baggage_items["source"] = self.source

        # Add parent_id to baggage if provided
        if parent_id:
            baggage_items["parent_id"] = parent_id

        # Create span context with baggage
        ctx = context.get_current()
        if baggage_items:
            for key, value in baggage_items.items():
                if value:
                    ctx = baggage.set_baggage(key, str(value), ctx)

        # Start span with context
        with trace.get_tracer("honeyhive").start_as_current_span(
            name, context=ctx, attributes=span_attributes
        ) as span:
            yield span

    def create_event(
        self,
        event_type: str,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """Create a HoneyHive event associated with the current session.

        Args:
            event_type: Type of event
            inputs: Input data for the event
            outputs: Output data for the event
            metadata: Additional metadata
            **kwargs: Additional event attributes
        """
        if not self.session_id or not hasattr(self, "session_api"):
            if not self.test_mode:
                print("Warning: Cannot create event - no active session")
            return None

        try:
            # Create event request with all required fields
            event_request = CreateEventRequest(
                project=self.project,
                source=self.source,
                event_name=f"event_{event_type}",
                event_type=EventType1.model,  # Use valid enum value
                session_id=self.session_id,
                config={},  # Required field, provide empty dict
                inputs=inputs or {},  # Required field, provide default
                outputs=outputs or {},
                duration=0.0,  # Required field
                metadata=metadata or {},
                **kwargs,
            )

            # Create event via API
            if self.session_api and hasattr(self.session_api, "client"):
                event_response = (
                    self.session_api.client.events.create_event_from_request(
                        event_request
                    )
                )

                if not self.test_mode:
                    print(f"✓ Event created: {event_response.event_id}")

                return event_response.event_id  # type: ignore[no-any-return]

            print("Warning: Session API not available")
            return None

        except Exception as e:
            if not self.test_mode:
                print(f"Warning: Failed to create event: {e}")
            return None

    def enrich_session(
        self,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        user_properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Enrich the current session with additional data.

        Args:
            session_id: Session ID to enrich (defaults to tracer's session)
            metadata: Session metadata
            feedback: User feedback
            metrics: Computed metrics
            config: Session configuration
            inputs: Session inputs
            outputs: Session outputs
            user_properties: User properties

        Returns:
            Whether the enrichment was successful
        """
        if not self.session_id:
            if not self.test_mode:
                print("Warning: Cannot enrich session - no active session")
            return False

        try:
            # Try to get the existing event ID from baggage context
            event_id = None
            if OTEL_AVAILABLE:
                try:
                    from opentelemetry import baggage

                    ctx = context.get_current()
                    event_id = baggage.get_baggage("event_id", ctx)
                    if event_id:
                        event_id = str(event_id)  # Convert to string
                except Exception:
                    pass

            if event_id:
                # Update existing event using UpdateEventRequest
                update_request = UpdateEventRequest(
                    event_id=str(event_id),  # Ensure event_id is a string
                    metadata=metadata,
                    feedback=feedback,
                    metrics=metrics,
                    outputs=outputs,
                    config=config or {},  # Required field, provide default
                    user_properties=user_properties,
                )

                if self.test_mode:
                    print(f"🔍 UpdateEventRequest created: {update_request}")

                # Send update request via the events API
                if self.client and hasattr(self.client, "events"):
                    self.client.events.update_event(update_request)
                    return True

                print("Warning: Client or events API not available")
                return False
            else:
                # Fallback: create a new enrichment event if no event ID found
                # AND also set all fields as span attributes for the current span
                current_span = trace.get_current_span()
                if OTEL_AVAILABLE:
                    try:
                        if (
                            current_span
                            and current_span.get_span_context().span_id != 0
                        ):
                            # Set all enrichment data as span attributes
                            if metadata:
                                for key, value in metadata.items():
                                    current_span.set_attribute(
                                        f"honeyhive.session.metadata.{key}", str(value)
                                    )

                            if feedback:
                                for key, value in feedback.items():
                                    current_span.set_attribute(
                                        f"honeyhive.session.feedback.{key}", str(value)
                                    )

                            if metrics:
                                for key, value in metrics.items():
                                    current_span.set_attribute(
                                        f"honeyhive.session.metrics.{key}", str(value)
                                    )

                            if config:
                                for key, value in config.items():
                                    current_span.set_attribute(
                                        f"honeyhive.session.config.{key}", str(value)
                                    )

                            if inputs:
                                for key, value in inputs.items():
                                    current_span.set_attribute(
                                        f"honeyhive.session.inputs.{key}", str(value)
                                    )

                            if outputs:
                                for key, value in outputs.items():
                                    current_span.set_attribute(
                                        f"honeyhive.session.outputs.{key}", str(value)
                                    )

                            if user_properties:
                                for key, value in user_properties.items():
                                    current_span.set_attribute(
                                        f"honeyhive.session.user_properties.{key}",
                                        str(value),
                                    )
                    except Exception:
                        pass

                # Create enrichment event
                event = CreateEventRequest(
                    project=self.project,
                    source=self.source,
                    event_name="session_enrichment",
                    event_type=EventType1.model,  # Use valid enum value
                    session_id=session_id or self.session_id,
                    event_id=None,  # Will be auto-generated
                    parent_id=None,  # No parent
                    children_ids=None,  # No children
                    error=None,  # No error
                    start_time=None,  # Will use current time
                    end_time=None,  # Will use current time
                    duration=0.0,  # Required field
                    metadata=metadata,
                    feedback=feedback,
                    metrics=metrics,
                    config=config or {},  # Required field, provide default
                    inputs=inputs or {},  # Required field, provide default
                    outputs=outputs,
                    user_properties=user_properties,
                )

                # Send enrichment event via the events API
                if self.client and hasattr(self.client, "events"):
                    response = self.client.events.create_event(event)
                    if response.success:
                        return True
                    if not self.test_mode:
                        print(f"Failed to enrich session {session_id}: API error")
                    return False

                print("Warning: Client or events API not available")
                return False

        except Exception as e:
            if not self.test_mode:
                print(f"Failed to enrich session {session_id}: {e}")
            return False

    def enrich_span(
        self,
        *args: Any,
        metadata: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        **kwargs: Any,
    ) -> Any:
        """Enrich the current active span with additional data.

        This method supports both context manager and direct call patterns:

        1. Context manager pattern (backwards compatibility with basic_usage.py)::

            with tracer.enrich_span("session_name", {"key": "value"}):
                # code here

        2. Direct method call::

            success = tracer.enrich_span(metadata={"key": "value"})

        Args:
            *args: Positional arguments for backwards compatibility
                   - args[0]: event_type or session_name (str)
                   - args[1]: metadata (dict)
            metadata: Span metadata
            metrics: Span metrics
            attributes: Span attributes
            outputs: Output data from the operation
            error: Exception or error information
            **kwargs: Additional keyword arguments

        Returns:
            Context manager for context manager usage, bool for direct calls
        """
        # Handle backwards compatibility with positional arguments from basic_usage.py
        if args:
            # This is the pattern: tracer.enrich_span("session_name", {"key": "value"})
            # Return a context manager for backwards compatibility
            event_type = args[0] if len(args) >= 1 else None
            if len(args) >= 2 and isinstance(args[1], dict):
                metadata = args[1] if metadata is None else metadata

            return _enrich_span_context_manager(
                event_type=event_type,
                metadata=metadata,
                metrics=metrics,
                attributes=attributes,
                outputs=outputs,
                error=error,
                tracer=self,
                **kwargs,
            )

        # Direct method call - original behavior
        if not OTEL_AVAILABLE:
            return False

        try:
            # Try to get the existing event ID from baggage context first
            event_id = None
            try:
                from opentelemetry import baggage

                ctx = context.get_current()
                event_id = baggage.get_baggage("event_id", ctx)
            except Exception:
                pass

            if event_id:
                # Ensure event_id is a string
                event_id_str = str(event_id) if event_id is not None else None
                if event_id_str:
                    # Update existing event using UpdateEventRequest
                    update_request = UpdateEventRequest(
                        event_id=event_id_str,
                        metadata=metadata,
                        metrics=metrics,
                    )

                    # Send update request via the events API
                    if self.client and hasattr(self.client, "events"):
                        self.client.events.update_event(update_request)
                        return True

                    print("Warning: Client or events API not available")
                    return False

                print("Warning: Invalid event_id")
                return False

            # Fallback: enrich the current OpenTelemetry span directly
            current_span = trace.get_current_span()
            if not current_span or current_span.get_span_context().span_id == 0:
                if not self.test_mode:
                    print("Warning: No active span to enrich")
                return False

            # Set all enrichment data as span attributes with comprehensive coverage
            if metadata:
                for key, value in metadata.items():
                    current_span.set_attribute(
                        f"honeyhive.span.metadata.{key}", str(value)
                    )

            if metrics:
                for key, value in metrics.items():
                    current_span.set_attribute(
                        f"honeyhive.span.metrics.{key}", str(value)
                    )

            # Add custom attributes (these are already properly prefixed)
            if attributes:
                for key, value in attributes.items():
                    current_span.set_attribute(key, str(value))

            # Handle outputs using _set_span_attributes for proper data structure handling
            if outputs:
                _set_span_attributes(current_span, "honeyhive.span.outputs", outputs)

            # Handle error using _set_span_attributes for proper error serialization
            if error:
                _set_span_attributes(current_span, "honeyhive.span.error", error)

            return True

        except Exception as e:
            if not self.test_mode:
                print(f"Failed to enrich span: {e}")
            return False

    def get_baggage(
        self, key: str, ctx_param: Optional[Context] = None
    ) -> Optional[str]:
        """Get baggage value.

        Args:
            key: Baggage key
            ctx_param: OpenTelemetry context

        Returns:
            Baggage value or None
        """
        if not OTEL_AVAILABLE:
            return None

        ctx = ctx_param or context.get_current()
        result = baggage.get_baggage(key, ctx)
        return str(result) if result is not None else None

    def set_baggage(
        self, key: str, value: str, ctx_param: Optional[Context] = None
    ) -> Context:
        """Set baggage value.

        Args:
            key: Baggage key
            value: Baggage value
            ctx_param: OpenTelemetry context

        Returns:
            Updated context
        """
        if not OTEL_AVAILABLE:
            return ctx_param or Context()

        ctx = ctx_param or context.get_current()
        return baggage.set_baggage(key, value, ctx)

    def inject_context(self, carrier: Dict[str, str]) -> None:
        """Inject trace context into carrier.

        Args:
            carrier: Dictionary to inject context into
        """
        if not OTEL_AVAILABLE or not self.propagator:
            return

        ctx = context.get_current()
        self.propagator.inject(carrier, context=ctx)

    def extract_context(self, carrier: Dict[str, str]) -> Context:
        """Extract trace context from carrier.

        Args:
            carrier: Dictionary containing context

        Returns:
            Extracted context
        """
        if not OTEL_AVAILABLE or not self.propagator:
            # Return a default context if no propagator available
            from opentelemetry.context import Context

            return Context()

        try:
            result = self.propagator.extract(carrier)
            # Ensure we return a Context type
            from opentelemetry.context import Context

            if isinstance(result, Context):
                return result
            else:
                return Context()
        except Exception:
            # Fallback to default context if extraction fails
            from opentelemetry.context import Context

            return Context()

    def force_flush(self, timeout_millis: float = 30000) -> bool:
        """Force flush any pending spans and data.

        This method ensures that all pending spans and telemetry data are
        immediately sent to their destinations, rather than waiting for
        automatic batching/flushing.

        Args:
            timeout_millis: Maximum time to wait for flush completion in milliseconds.
                          Defaults to 30 seconds (30000ms).

        Returns:
            bool: True if flush completed successfully within timeout, False otherwise.

        Example:
            Flush with default timeout (30 seconds):

            >>> success = tracer.force_flush()

            Flush with custom timeout (5 seconds):

            >>> success = tracer.force_flush(timeout_millis=5000)

            Use before critical sections:

            >>> if tracer.force_flush():
            ...     print("All spans flushed successfully")
            ... else:
            ...     print("Flush timeout or error occurred")
        """
        if not OTEL_AVAILABLE:
            print("⚠️  OpenTelemetry not available, skipping force_flush")
            return True

        flush_results = []

        try:
            # 1. Flush the tracer provider if available and supports it
            if self.provider and hasattr(self.provider, "force_flush"):
                try:
                    provider_result = self.provider.force_flush(
                        timeout_millis=int(timeout_millis)
                    )
                    flush_results.append(("provider", provider_result))
                    if not self.test_mode:
                        print(
                            f"✓ Provider force_flush: {'success' if provider_result else 'failed'}"
                        )
                except Exception as e:
                    flush_results.append(("provider", False))
                    if not self.test_mode:
                        print(f"❌ Provider force_flush error: {e}")
            else:
                if not self.test_mode:
                    print("ℹ️  Provider does not support force_flush")
                flush_results.append(
                    ("provider", True)
                )  # Consider it successful if not supported

            # 2. Flush our custom span processor if available
            if self.span_processor and hasattr(self.span_processor, "force_flush"):
                try:
                    processor_result = self.span_processor.force_flush(
                        timeout_millis=timeout_millis
                    )
                    flush_results.append(("span_processor", processor_result))
                    if not self.test_mode:
                        print(
                            f"✓ Span processor force_flush: {'success' if processor_result else 'failed'}"
                        )
                except Exception as e:
                    flush_results.append(("span_processor", False))
                    if not self.test_mode:
                        print(f"❌ Span processor force_flush error: {e}")
            else:
                flush_results.append(
                    ("span_processor", True)
                )  # Consider successful if not available

            # 3. Flush any batch span processors that might be attached to the provider
            if self.provider and hasattr(self.provider, "_span_processors"):
                try:
                    batch_processors = []
                    for processor in getattr(self.provider, "_span_processors", []):
                        if hasattr(processor, "force_flush"):
                            batch_processors.append(processor)

                    if batch_processors:
                        batch_results = []
                        for i, processor in enumerate(batch_processors):
                            try:
                                result = processor.force_flush(
                                    timeout_millis=int(timeout_millis)
                                )
                                batch_results.append(result)
                                if not self.test_mode:
                                    print(
                                        f"✓ Batch processor {i+1} force_flush: {'success' if result else 'failed'}"
                                    )
                            except Exception as e:
                                batch_results.append(False)
                                if not self.test_mode:
                                    print(
                                        f"❌ Batch processor {i+1} force_flush error: {e}"
                                    )

                        flush_results.append(("batch_processors", all(batch_results)))
                    else:
                        flush_results.append(("batch_processors", True))
                except Exception as e:
                    flush_results.append(("batch_processors", False))
                    if not self.test_mode:
                        print(f"❌ Batch processors flush error: {e}")

            # Calculate overall result
            overall_success = all(result for _, result in flush_results)

            if not self.test_mode:
                if overall_success:
                    print("✓ Force flush completed successfully")
                else:
                    failed_components = [
                        name for name, result in flush_results if not result
                    ]
                    print(
                        f"⚠️  Force flush completed with failures: {failed_components}"
                    )

            return overall_success

        except Exception as e:
            if not self.test_mode:
                print(f"❌ Force flush failed: {e}")
            return False

    def shutdown(self) -> None:
        """Shutdown the tracer and its provider."""
        try:
            # Only shutdown if we're the main provider
            if (
                self.is_main_provider
                and self.provider
                and hasattr(self.provider, "shutdown")
            ):
                self.provider.shutdown()
                print("✓ Tracer provider shut down")
            else:
                print("✓ Tracer instance closed (not main provider)")
        except Exception as e:
            if not self.test_mode:
                print(f"Error shutting down tracer: {e}")

    @classmethod
    def _reset_static_state(cls) -> None:
        """Reset static state (no longer needed in multi-instance mode)."""
        # In multi-instance mode, this method is not needed
        print("ℹ️  Static state reset not needed in multi-instance mode.")
        print("   Each tracer instance manages its own state independently.")


# Global helper functions for backward compatibility
# Note: These functions are no longer needed in multi-instance mode.
# Users should create and manage their own tracer instances directly.


def enrich_session(
    session_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    tracer: Optional[HoneyHiveTracer] = None,
) -> None:
    """Enrich session with metadata.

    Note: This function is no longer needed in multi-instance mode.
    Users should call enrich_session() directly on their tracer instances.

    Args:
        session_id: Session ID to enrich
        metadata: Metadata to add to session
        tracer: Tracer instance to use (required in multi-instance mode)
    """
    if tracer is None:
        print("❌ Error: tracer parameter is required in multi-instance mode")
        print("   Usage: tracer.enrich_session(session_id, metadata)")
        return

    tracer.enrich_session(session_id, metadata)


def enrich_span(
    *args: Any,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    attributes: Optional[Dict[str, Any]] = None,
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    config_data: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
    event_id: Optional[str] = None,
    tracer: Optional[HoneyHiveTracer] = None,
    **kwargs: Any,
) -> Any:
    """Unified enrich_span function supporting both context manager and direct call patterns.

    This function provides backwards compatibility with existing usage patterns:

    1. Context manager pattern (from enhanced_tracing_demo.py):
        with enrich_span(event_type="demo", metadata={"key": "value"}):
            # code here

    2. Direct method call pattern (from basic_usage.py):
        with tracer.enrich_span("session_name", {"key": "value"}):
            # code here

    3. HoneyHiveTracer instance method call:
        success = tracer.enrich_span(metadata={"key": "value"})

    4. Global function call:
        success = enrich_span(metadata={"key": "value"}, tracer=my_tracer)

    Args:
        *args: Positional arguments for backwards compatibility
               - args[0]: event_type or session_name (str)
               - args[1]: metadata (dict)
        metadata: Span metadata
        metrics: Span metrics
        attributes: Span attributes
        event_type: Type of traced event
        event_name: Name of the traced event
        inputs: Input data for the event
        outputs: Output data for the event
        config_data: Configuration data
        feedback: User feedback
        error: Error information
        event_id: Unique event identifier
        tracer: HoneyHiveTracer instance (for multi-instance support)
        **kwargs: Additional attributes to set on the span

    Returns:
        Context manager for context manager usage, bool for direct calls
    """
    # Handle backwards compatibility with positional arguments
    if args:
        if len(args) >= 1:
            if isinstance(args[0], str):
                # Pattern: enrich_span("session_name", {...}) from basic_usage.py
                if event_type is None:
                    event_type = args[0]
            elif isinstance(args[0], dict):
                # Pattern: enrich_span({"key": "value"}, {...}) - first arg is metadata
                if metadata is None:
                    metadata = args[0]
        if len(args) >= 2 and isinstance(args[1], dict):
            # Second argument is metadata or metrics dict
            if metadata is None and isinstance(args[0], str):
                # Pattern: enrich_span("session_name", {"key": "value"})
                metadata = args[1]
            elif metrics is None and isinstance(args[0], dict):
                # Pattern: enrich_span({"metadata": "value"}, {"metrics": "value"})
                metrics = args[1]
        if len(args) >= 3 and isinstance(args[2], dict):
            # Third argument is attributes dict
            if attributes is None:
                attributes = args[2]

    # Check if this is being called as a context manager (look for specific context manager args)
    # Context manager usage has rich parameters like event_type, inputs, outputs, etc.
    # Direct calls typically only have metadata, metrics, attributes
    is_context_manager = (
        event_type is not None
        or event_name is not None
        or inputs is not None
        or outputs is not None
        or config_data is not None
        or feedback is not None
        or error is not None
        or event_id is not None
    )

    if is_context_manager:
        # Return context manager
        return _enrich_span_context_manager(
            event_type=event_type,
            event_name=event_name,
            inputs=inputs,
            outputs=outputs,
            metadata=metadata,
            config_data=config_data,
            metrics=metrics,
            feedback=feedback,
            error=error,
            event_id=event_id,
            attributes=attributes,
            tracer=tracer,
            **kwargs,
        )
    else:
        # Direct method call - delegate to tracer instance
        if tracer is None:
            print("❌ Error: tracer parameter is required for direct method calls")
            print("   Usage options:")
            print("   1. tracer.enrich_span(metadata={'key': 'value'})")
            print("   2. enrich_span(metadata={'key': 'value'}, tracer=my_tracer)")
            print("   3. Use context manager: with enrich_span(event_type='demo'):")
            return False

        return tracer.enrich_span(
            metadata=metadata,
            metrics=metrics,
            attributes=attributes,
            outputs=outputs,
            error=error,
        )


@contextmanager
def _enrich_span_context_manager(
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    config_data: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
    event_id: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    tracer: Optional[HoneyHiveTracer] = None,
    **kwargs: Any,
) -> Any:
    """Context manager implementation for enrich_span.

    Yields:
        None: The context manager yields control to the wrapped code block
    """
    try:
        # Get current span from OpenTelemetry context
        current_span = trace.get_current_span()

        if current_span and current_span.is_recording():
            # Set comprehensive attributes on the current span
            if event_type:
                current_span.set_attribute("honeyhive_event_type", event_type)

            if event_name:
                current_span.set_attribute("honeyhive_event_name", event_name)

            if event_id:
                current_span.set_attribute("honeyhive_event_id", event_id)

            # Set inputs if provided
            if inputs:
                _set_span_attributes(current_span, "honeyhive_inputs", inputs)

            # Set config if provided
            if config_data:
                _set_span_attributes(current_span, "honeyhive_config", config_data)

            # Set metadata if provided
            if metadata:
                _set_span_attributes(current_span, "honeyhive_metadata", metadata)

            # Set metrics if provided
            if metrics:
                _set_span_attributes(current_span, "honeyhive_metrics", metrics)

            # Set feedback if provided
            if feedback:
                _set_span_attributes(current_span, "honeyhive_feedback", feedback)

            # Set attributes if provided (for direct method call compatibility)
            if attributes:
                for key, value in attributes.items():
                    current_span.set_attribute(key, str(value))

            # Set additional kwargs as attributes
            for key, value in kwargs.items():
                current_span.set_attribute(f"honeyhive_{key}", value)

            # Add experiment harness information if available
            try:
                if config_data and config_data.get("experiment_id"):
                    current_span.set_attribute(
                        "honeyhive_experiment_id", config_data["experiment_id"]
                    )

                if config_data and config_data.get("experiment_name"):
                    current_span.set_attribute(
                        "honeyhive_experiment_name", config_data["experiment_name"]
                    )

                if config_data and config_data.get("experiment_variant"):
                    current_span.set_attribute(
                        "honeyhive_experiment_variant",
                        config_data["experiment_variant"],
                    )

                if config_data and config_data.get("experiment_group"):
                    current_span.set_attribute(
                        "honeyhive_experiment_group",
                        config_data["experiment_group"],
                    )

                if config_data and config_data.get("experiment_metadata"):
                    # Add experiment metadata as individual attributes
                    for key, value in config_data["experiment_metadata"].items():
                        current_span.set_attribute(
                            f"honeyhive_experiment_metadata_{key}", str(value)
                        )
            except Exception:
                # Silently handle any exceptions when setting experiment attributes
                pass

        yield current_span

    except Exception:
        # If enrichment fails, just yield None
        yield None


def _set_span_attributes(span: Any, prefix: str, value: Any) -> None:
    """Set span attributes with proper type handling and JSON serialization.

    Recursively sets span attributes for complex data structures, handling
    different data types appropriately for OpenTelemetry compatibility.

    Args:
        span: OpenTelemetry span object
        prefix: Attribute name prefix
        value: Value to set as attribute
    """
    if value is None:
        return

    try:
        if isinstance(value, dict):
            for key, val in value.items():
                _set_span_attributes(span, f"{prefix}.{key}", val)
        elif isinstance(value, (list, tuple)):
            for i, val in enumerate(value):
                _set_span_attributes(span, f"{prefix}.{i}", val)
        elif isinstance(value, (str, int, float, bool)):
            span.set_attribute(prefix, value)
        else:
            # For complex objects, try JSON serialization
            try:
                json_str = json.dumps(value, default=str)
                span.set_attribute(prefix, json_str)
            except (TypeError, ValueError):
                # Fallback to string representation
                span.set_attribute(prefix, str(value))
    except Exception:
        # Silently handle any exceptions during attribute setting
        pass
