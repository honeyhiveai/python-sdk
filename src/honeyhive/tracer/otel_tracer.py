"""OpenTelemetry tracer implementation for HoneyHive."""

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

    _instance: Optional["HoneyHiveTracer"] = None
    _lock = threading.Lock()
    _is_initialized = False

    # Instance attributes
    session_id: Optional[str]
    client: Optional[Any]
    session_api: Optional[Any]

    def __new__(cls, *args: Any, **kwargs: Any) -> "HoneyHiveTracer":
        """Singleton pattern for tracer."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        source: str = "production",
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

        if self._is_initialized:
            return

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
        self.session_name = session_name or f"tracer_session_{int(time.time())}"

        # Initialize OpenTelemetry components
        self._initialize_otel()

        # Initialize session management
        self._initialize_session()

        # Set up baggage context
        self._setup_baggage_context()

        # Mark as initialized
        self._is_initialized = True

        # Auto-integrate instrumentors if provided
        if instrumentors:
            self._integrate_instrumentors(instrumentors)

        print(f"✓ HoneyHiveTracer initialized for project: {self.project}")
        if disable_http_tracing:
            print("✓ HTTP tracing disabled")
        else:
            print("✓ HTTP tracing enabled")

    @classmethod
    def reset(cls) -> None:
        """Reset the tracer instance for testing purposes."""
        cls._instance = None
        cls._is_initialized = False

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
        """
        Initialize the HoneyHive tracer (official API for backwards compatibility).

        This method provides the same functionality as the constructor but follows
        the official HoneyHive SDK API pattern shown in production documentation.

        Args:
            api_key: HoneyHive API key
            project: Project name
            source: Source environment (defaults to "dev" per official docs)
            test_mode: Whether to run in test mode
            session_name: Optional session name for automatic session creation
            server_url: Optional server URL for self-hosted deployments
            instrumentors: List of OpenInference instrumentors to automatically integrate
            disable_http_tracing: Whether to disable HTTP tracing (defaults to True)

        Returns:
            HoneyHiveTracer instance

        Example:
            # Official SDK pattern from docs.honeyhive.ai
            HoneyHiveTracer.init(
                api_key="your-api-key",
                project="your-project",
                source="prod"
            )

            # With HTTP tracing enabled
            HoneyHiveTracer.init(
                api_key="your-api-key",
                project="your-project",
                source="prod",
                disable_http_tracing=False
            )

            # With test mode and instrumentors
            HoneyHiveTracer.init(
                api_key="your-api-key",
                project="your-project",
                source="prod",
                test_mode=True,
                instrumentors=[OpenAIInstrumentor()]
            )
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
        # Create tracer provider
        self.provider = TracerProvider()

        # Add span processor to enrich spans with HoneyHive attributes
        try:
            self.span_processor = HoneyHiveSpanProcessor()
            self.provider.add_span_processor(self.span_processor)
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

                # Add OTLP exporter with batch processing
                self.provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

                print(f"✓ OTLP exporter configured to send spans to: {otlp_endpoint}")

            except ImportError:
                print(
                    "⚠️  OTLP exporter not available, using console exporter for debugging"
                )
                self.provider.add_span_processor(
                    BatchSpanProcessor(ConsoleSpanExporter())
                )
        else:
            print("🔍 OTLP export disabled, using no-op exporter for tests")

            # Create a custom no-op exporter to prevent I/O errors during tests
            class NoOpExporter:
                """No-op exporter that prevents I/O errors during tests."""

                def export(self, spans: Any) -> bool:
                    """Export spans to the backend.

                    Args:
                        spans: List of spans to export

                    Returns:
                        True if export was successful, False otherwise
                    """
                    # Do nothing - prevents I/O errors during tests
                    return True

                def shutdown(self) -> None:
                    """Shutdown the exporter."""
                    # No cleanup needed for no-op exporter

                def force_flush(self, timeout_millis: float = 30000.0) -> bool:
                    """Force flush the exporter."""
                    # No flushing needed for no-op exporter
                    return True

            # Use ConsoleSpanExporter instead of NoOpExporter to avoid type issues
            self.provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        # Set up propagators
        self.propagator = CompositePropagator(
            [
                TraceContextTextMapPropagator(),
                W3CBaggagePropagator(),
            ]
        )

        # Set as global provider
        trace.set_tracer_provider(self.provider)

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
        metadata: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Enrich the current active span with additional data.

        Args:
            span_name: Name of the span to enrich (defaults to current active span)
            metadata: Span metadata
            metrics: Span metrics
            attributes: Span attributes

        Returns:
            Whether the enrichment was successful
        """
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
        if not OTEL_AVAILABLE:
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
        if not OTEL_AVAILABLE:
            return Context()

        return self.propagator.extract(carrier)

    def shutdown(self) -> None:
        """Shutdown the tracer and flush remaining spans."""
        if not OTEL_AVAILABLE:
            return

        try:
            self.provider.shutdown()
        except Exception as e:
            if not self.test_mode:
                print(f"Error shutting down tracer: {e}")

    @classmethod
    def _reset_static_state(cls) -> None:
        """Reset static state for testing."""
        cls._instance = None
        cls._is_initialized = False

    @classmethod
    def configure_otlp_exporter(
        cls,
        enabled: bool = True,
        endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Configure OTLP exporter settings.

        Args:
            enabled: Whether OTLP export is enabled
            endpoint: OTLP endpoint URL
            headers: OTLP headers
        """
        if not OTEL_AVAILABLE:
            return

        # This would be implemented to configure OTLP exporter
        # For now, we'll use the HoneyHive span processor
        # TODO: Implement OTLP exporter configuration


# Global function for session enrichment
def enrich_session(
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
    user_properties: Optional[Dict[str, Any]] = None,
) -> bool:
    """Global function to enrich a session.

    Args:
        session_id: Session ID to enrich
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
    try:
        # Get tracer instance
        tracer = HoneyHiveTracer._instance if HoneyHiveTracer._is_initialized else None
        if tracer:
            return tracer.enrich_session(
                session_id=session_id,
                metadata=metadata,
                feedback=feedback,
                metrics=metrics,
                config=config or {},  # Required field, provide default
                inputs=inputs,
                outputs=outputs,
                user_properties=user_properties,
            )

        print("Warning: Tracer not available")
        return False
    except Exception as e:
        print(f"Warning: enrich_session failed: {e}")
        return False


# Global function for span enrichment
def enrich_span(
    span_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> bool:
    """Global function to enrich the current active span.

    Args:
        span_name: Name of the span to enrich (defaults to current active span)
        metadata: Span metadata
        metrics: Span metrics
        attributes: Span attributes

    Returns:
        Whether the enrichment was successful
    """
    try:
        # Get tracer instance
        tracer = HoneyHiveTracer._instance if HoneyHiveTracer._is_initialized else None
        if tracer:
            return tracer.enrich_span(
                metadata=metadata,
                metrics=metrics,
                attributes=attributes,
            )

        print("Warning: Tracer not available")
        return False
    except Exception as e:
        print(f"Warning: enrich_span failed: {e}")
        return False


def get_tracer() -> Optional[HoneyHiveTracer]:
    """Get the global tracer instance.

    Returns:
        Global HoneyHiveTracer instance or None if not initialized
    """
    if not HoneyHiveTracer._is_initialized:
        return None

    return HoneyHiveTracer._instance
