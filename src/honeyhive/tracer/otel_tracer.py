import uuid
import os
import sys
import threading
import io
import subprocess
from contextlib import redirect_stdout
from typing import Optional, Dict, Any, Callable

from opentelemetry import context, baggage, trace
from opentelemetry.context import Context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from honeyhive.utils.baggage_dict import BaggageDict
from honeyhive.models import operations, components, errors
from honeyhive.sdk import HoneyHive

DEFAULT_API_URL = "https://api.honeyhive.ai"


class HoneyHiveSpanProcessor(SpanProcessor):
    """
    Custom span processor that automatically adds session_id and other association properties
    as attributes to every span.
    """
    
    def on_start(self, span: ReadableSpan, parent_context: Optional[Context] = None) -> None:
        """Called when a span starts"""
        if HoneyHiveOTelTracer.verbose:
            print(f"🚀 Span started: {span.name}")
        
        # Get association properties from context
        if parent_context is not None:
            association_properties = parent_context.get('association_properties')
            if association_properties and isinstance(association_properties, dict):
                # Set session_id and other properties as span attributes
                for key, value in association_properties.items():
                    if value is not None:
                        span.set_attribute(f"honeyhive.{key}", str(value))
                        if HoneyHiveOTelTracer.verbose:
                            print(f"🔍 Set attribute: honeyhive.{key} = {value}")
        else:
            if HoneyHiveOTelTracer.verbose:
                print(f"⚠️ No parent context for span: {span.name}")
    
    def on_end(self, span: ReadableSpan) -> None:
        """Called when a span ends"""
        try:
            if HoneyHiveOTelTracer.verbose:
                print(f"🔍 Span ended: {span.name} with attributes: {dict(span.attributes) if span.attributes else {}}")
            
            # Convert OpenTelemetry span to HoneyHive event
            if HoneyHiveOTelTracer.api_key and HoneyHiveOTelTracer.server_url:
                # Extract span attributes
                span_attributes = dict(span.attributes) if span.attributes else {}
                
                # Get session_id from span attributes or context
                session_id = span_attributes.get("honeyhive.session_id")
                if not session_id:
                    # Try to get from context baggage
                    ctx = context.get_current()
                    if ctx is not None:
                        # Try to get from baggage
                        from opentelemetry import baggage
                        session_id = baggage.get_baggage('session_id', ctx)
                        
                        if not session_id:
                            # Try to get from association_properties (legacy)
                            association_properties = ctx.get('association_properties')
                            if association_properties and isinstance(association_properties, dict):
                                session_id = association_properties.get('session_id')
                
                if HoneyHiveOTelTracer.verbose:
                    print(f"🔍 Session ID: {session_id}")
                
                if session_id:
                    # Create event via HoneyHive API
                    try:
                        from honeyhive.sdk import HoneyHive
                        from honeyhive.models import operations, components
                        
                        sdk = HoneyHive(
                            bearer_auth=HoneyHiveOTelTracer.api_key, 
                            server_url=HoneyHiveOTelTracer.server_url
                        )
                        
                        # Determine event type from span attributes
                        raw_event_type = span_attributes.get("honeyhive_event_type", "tool")
                        
                        # Map session_start to a valid event type
                        if raw_event_type == "session_start":
                            event_type = "tool"  # Use 'tool' as the default for session events
                        else:
                            event_type = raw_event_type
                        
                        if HoneyHiveOTelTracer.verbose:
                            print(f"🔍 Creating event: {span.name} of type {event_type}")
                        
                        # Create event request
                        from honeyhive.models.components.createeventrequest import CreateEventRequest
                        
                        # Calculate duration from span start/end time (timestamps are in nanoseconds)
                        duration = None
                        if hasattr(span, 'start_time') and hasattr(span, 'end_time'):
                            # Convert nanoseconds to milliseconds
                            duration = (span.end_time - span.start_time) / 1_000_000
                        
                        # Extract and structure metadata from span attributes
                        metadata = {}
                        inputs = {}
                        outputs = {}
                        feedback = {}
                        metrics = {}
                        config = {}
                        user_properties = {}
                        
                        for key, value in span_attributes.items():
                            if key.startswith("honeyhive_metadata."):
                                # Extract metadata key (remove prefix)
                                meta_key = key.replace("honeyhive_metadata.", "")
                                metadata[meta_key] = value
                            elif key.startswith("honeyhive_inputs."):
                                # Extract inputs key
                                input_key = key.replace("honeyhive_inputs.", "")
                                inputs[input_key] = value
                            elif key.startswith("honeyhive_outputs."):
                                # Extract outputs key
                                output_key = key.replace("honeyhive_outputs.", "")
                                outputs[output_key] = value
                            elif key.startswith("honeyhive_feedback."):
                                # Extract feedback key
                                feedback_key = key.replace("honeyhive_feedback.", "")
                                feedback[feedback_key] = value
                            elif key.startswith("honeyhive_metrics."):
                                # Extract metrics key
                                metric_key = key.replace("honeyhive_metrics.", "")
                                metrics[metric_key] = value
                            elif key.startswith("honeyhive_config."):
                                # Extract config key
                                config_key = key.replace("honeyhive_config.", "")
                                config[config_key] = value
                            elif key.startswith("honeyhive_user_properties."):
                                # Extract user properties key
                                prop_key = key.replace("honeyhive_user_properties.", "")
                                user_properties[prop_key] = value
                        
                        # Also check for direct attributes and JSON attributes
                        if not metadata:
                            if "honeyhive_metadata" in span_attributes:
                                metadata = span_attributes.get("honeyhive_metadata") or {}
                            elif "honeyhive_metadata_json" in span_attributes:
                                # Parse JSON metadata
                                try:
                                    import json
                                    metadata = json.loads(span_attributes.get("honeyhive_metadata_json", "{}"))
                                except (json.JSONDecodeError, TypeError):
                                    metadata = {}
                        
                        if not inputs:
                            if "honeyhive_inputs" in span_attributes:
                                inputs = span_attributes.get("honeyhive_inputs") or {}
                            elif "honeyhive_inputs_json" in span_attributes:
                                # Parse JSON inputs
                                try:
                                    import json
                                    inputs = json.loads(span_attributes.get("honeyhive_inputs_json", "{}"))
                                except (json.JSONDecodeError, TypeError):
                                    inputs = {}
                        
                        if not outputs and "honeyhive_outputs" in span_attributes:
                            outputs = span_attributes.get("honeyhive_outputs") or {}
                        
                        event_request = operations.CreateEventRequestBody(
                            event=CreateEventRequest(
                                project=span_attributes.get("honeyhive.project", "unknown"),
                                session_id=session_id,
                                event_name=span.name,
                                event_type=event_type,
                                source=span_attributes.get("honeyhive.source", "unknown"),
                                metadata=metadata,
                                inputs=inputs,
                                outputs=outputs,
                                feedback=feedback,
                                metrics=metrics,
                                config=config,
                                user_properties=user_properties,
                                duration=duration or 0
                            )
                        )
                        
                        # Send event to HoneyHive
                        response = sdk.events.create_event(request=event_request)
                        if response.status_code != 200:
                            if HoneyHiveOTelTracer.verbose:
                                print(f"❌ Failed to create event: {response.raw_response.text}")
                        else:
                            if HoneyHiveOTelTracer.verbose:
                                print(f"✅ Event created successfully: {span.name}")
                    except Exception as e:
                        if HoneyHiveOTelTracer.verbose:
                            print(f"❌ Error creating HoneyHive event: {e}")
                else:
                    if HoneyHiveOTelTracer.verbose:
                        print(f"⚠️ No session_id found for span: {span.name}")
        except Exception as e:
            # Silently fail to avoid breaking OpenTelemetry
            if HoneyHiveOTelTracer.verbose:
                print(f"❌ Error in HoneyHiveSpanProcessor.on_end: {e}")
            pass
    
    def shutdown(self) -> None:
        """Called when the span processor is shut down"""
        pass
    
    def force_flush(self, timeout_millis: float = 30000) -> bool:
        """Force flush any pending spans"""
        return True


class HoneyHiveOTelTracer:
    """
    OpenTelemetry-based tracer implementation for HoneyHive using wrapt for instrumentation.
    Replaces the traceloop dependency with native OpenTelemetry.
    """
    
    # Static variables for OpenTelemetry components
    api_key = None
    server_url = None
    _is_initialized = False
    _is_traceloop_initialized = False
    verbose = False
    is_evaluation = False
    tracer_provider = None
    meter_provider = None
    propagator = None
    tracer = None
    meter = None
    span_processor = None
    
    # OTLP exporter configuration
    otlp_enabled = False  # Disable by default to prevent export warnings
    otlp_endpoint = None
    otlp_headers = None
    
    # Internal locks
    _flush_lock = threading.RLock()
    
    # Traceloop compatibility attributes
    _is_traceloop_initialized = False
    
    # OpenTelemetry components
    tracer_provider: Optional[TracerProvider] = None
    propagator: Optional[CompositePropagator] = None
    tracer: Optional[trace.Tracer] = None
    span_processor: Optional[HoneyHiveSpanProcessor] = None

    def __init__(
        self,
        api_key=None,
        project=None,
        session_name=None,
        source=None,
        server_url=None,
        session_id=None,
        disable_http_tracing=False,
        disable_batch=False,
        verbose=False,
        inputs=None,
        is_evaluation=False,
        run_id=None,
        dataset_id=None,
        datapoint_id=None,
        link_carrier=None,
        test_mode=False
    ):
        
        # Get association properties from context if available
        ctx: Context = context.get_current()
        association_properties = ctx.get('association_properties') if ctx is not None else None
        
        # Only use context values if explicit parameters are not provided
        # This prevents context inheritance from overriding explicit test parameters
        if association_properties is not None:
            if session_id is None:
                session_id = association_properties.get('session_id')
            if project is None:
                project = association_properties.get('project')
            if source is None:
                source = association_properties.get('source')
            if disable_http_tracing is None:
                disable_http_tracing = association_properties.get('disable_http_tracing') or False
            if run_id is None:
                run_id = association_properties.get('run_id')
            if dataset_id is None:
                dataset_id = association_properties.get('dataset_id')
            if datapoint_id is None:
                datapoint_id = association_properties.get('datapoint_id')

        try:
            # Initialize API key
            if HoneyHiveOTelTracer.api_key is None:
                if api_key is None:
                    env_api_key = os.getenv("HH_API_KEY")
                    HoneyHiveOTelTracer._validate_api_key(env_api_key)
                    api_key = env_api_key
                else:
                    HoneyHiveOTelTracer._validate_api_key(api_key)
                HoneyHiveOTelTracer.api_key = api_key
            
            # Store api_key as instance attribute for property access
            self._api_key = HoneyHiveOTelTracer.api_key
            
            # Initialize server URL
            if HoneyHiveOTelTracer.server_url is None:
                if server_url is None:
                    env_server_url = os.getenv("HH_API_URL", DEFAULT_API_URL)
                    HoneyHiveOTelTracer._validate_server_url(env_server_url)
                    server_url = env_server_url
                else:
                    HoneyHiveOTelTracer._validate_server_url(server_url)
                HoneyHiveOTelTracer.server_url = server_url
            
            # Initialize project
            if project is None:
                project = os.getenv("HH_PROJECT")
                if project is None:
                    raise Exception("project must be specified or set in environment variable HH_PROJECT.")
            else:
                HoneyHiveOTelTracer._validate_project(project)
            
            # Initialize session name
            if session_name is None:
                try:
                    session_name = os.path.basename(sys.argv[0])
                except Exception as e:
                    if HoneyHiveOTelTracer.verbose:
                        print(f"Error setting session_name: {e}")
                    session_name = "unknown"

            # Initialize source
            if source is None:
                source = os.getenv("HH_SOURCE", "dev")
            
            # Set instance attributes for API compatibility
            self.project = project
            self.source = source
            
            # Store test mode flag
            self._test_mode = test_mode
            
            # Set verbose flag
            HoneyHiveOTelTracer.verbose = verbose
            
            # Initialize OpenTelemetry components FIRST
            if test_mode:
                # In test mode, use a simplified initialization
                HoneyHiveOTelTracer._initialize_otel_test_mode()
            else:
                HoneyHiveOTelTracer._initialize_otel(disable_batch)

            # Initialize session
            if session_id is None:
                git_info = HoneyHiveOTelTracer._get_git_info()
                metadata = git_info if "error" not in git_info else None
                
                self.session_name = session_name
                self.inputs = inputs
                self.metadata = metadata
                # Note: self.project and self.source already set above
                
                if test_mode:
                    # In test mode, generate a fake session ID
                    self.session_id = str(uuid.uuid4())
                    
                    # Set up baggage context in test mode too
                    test_baggage = BaggageDict().update({
                        "session_id": self.session_id,
                        "project": project,
                        "source": source,
                        "disable_http_tracing": str(disable_http_tracing).lower(),
                    })
                    
                    # Attach baggage context
                    ctx = context.get_current()
                    ctx = test_baggage.set_all_baggage(ctx)
                    context.attach(ctx)
                else:
                    # Create a temporary session ID for the span context
                    temp_session_id = str(uuid.uuid4())
                    
                    # Set up baggage context BEFORE session start
                    temp_baggage = BaggageDict().update({
                        "session_id": temp_session_id,
                        "project": project,
                        "source": source,
                        "disable_http_tracing": str(disable_http_tracing).lower(),
                    })
                    
                    # Attach baggage context
                    ctx = context.get_current()
                    ctx = temp_baggage.set_all_baggage(ctx)
                    context.attach(ctx)
                    
                    # Now start the session (this will update the session_id)
                    self.session_start()
                    
                    # Update baggage with the real session_id
                    self.baggage = BaggageDict().update({
                        "session_id": self.session_id,
                        "project": project,
                        "source": source,
                        "disable_http_tracing": str(disable_http_tracing).lower(),
                    })
            else:
                try:
                    uuid.UUID(session_id)
                    self.session_id = session_id.lower()
                    # Note: self.project and self.source already set above
                except (ValueError, AttributeError, TypeError):
                    raise errors.SDKError("session_id must be a valid UUID string.")

            # Initialize baggage (if not already done)
            if not hasattr(self, 'baggage') or self.baggage is None:
                self.baggage = BaggageDict().update({
                    "session_id": self.session_id,
                    "project": project,
                    "source": source,
                    "disable_http_tracing": str(disable_http_tracing).lower(),
                })
                
                # Also ensure the baggage is attached to the context
                ctx = context.get_current()
                ctx = self.baggage.set_all_baggage(ctx)
                context.attach(ctx)

            if is_evaluation:
                self.baggage.update({
                    "run_id": run_id,
                    "dataset_id": dataset_id,
                    "datapoint_id": datapoint_id,
                })

            # Handle link carrier
            if link_carrier is not None:
                self.link(link_carrier)
            else:
                ctx = context.get_current()
                if self.verbose:
                    print(f"🔍 Current context before baggage: {ctx}")
                ctx = self.baggage.set_all_baggage(ctx)
                if self.verbose:
                    print(f"🔍 Context after baggage: {ctx}")
                    print(f"🔍 Baggage contents: {self.baggage}")
                context.attach(ctx)
                if self.verbose:
                    print(f"🔍 Context attached: {context.get_current()}")
            
            # Print initialization message
            if not HoneyHiveOTelTracer.is_evaluation:
                print("\033[38;5;208mHoneyHive is initialized\033[0m")
                
        except errors.SDKError as e:
            print(f"\033[91mHoneyHive SDK Error: {str(e)}\033[0m")
        except Exception as e:
            # Re-raise validation exceptions so they can be caught by tests
            if "must be" in str(e) or "must be specified" in str(e):
                raise
            if HoneyHiveOTelTracer.verbose:
                import traceback
                traceback.print_exc()
            else:
                pass

    @staticmethod
    def _initialize_otel(disable_batch=False):
        """Initialize OpenTelemetry components"""
        if HoneyHiveOTelTracer._is_initialized:
            return
            
        with threading.Lock():
            if HoneyHiveOTelTracer._is_initialized:
                return
                
            # Initialize propagator
            HoneyHiveOTelTracer.propagator = CompositePropagator([
                TraceContextTextMapPropagator(),
                W3CBaggagePropagator()
            ])
            
            # Initialize tracer provider
            HoneyHiveOTelTracer.tracer_provider = TracerProvider()
            
            # Add custom span processor for session_id and association properties
            HoneyHiveOTelTracer.span_processor = HoneyHiveSpanProcessor()
            HoneyHiveOTelTracer.tracer_provider.add_span_processor(HoneyHiveOTelTracer.span_processor)
            
            # Add OTLP span exporter for external observability backends
            if HoneyHiveOTelTracer.otlp_enabled:
                try:
                    # Use configured endpoint or default to HoneyHive API
                    endpoint = HoneyHiveOTelTracer.otlp_endpoint or f"{HoneyHiveOTelTracer.server_url}/opentelemetry/v1/traces"
                    headers = HoneyHiveOTelTracer.otlp_headers or {"Authorization": f"Bearer {HoneyHiveOTelTracer.api_key}"}
                    
                    # Validate endpoint before creating exporter
                    if not endpoint or endpoint == f"{HoneyHiveOTelTracer.server_url}/opentelemetry/v1/traces":
                        if HoneyHiveOTelTracer.verbose:
                            print(f"🔍 Skipping OTLP exporter: HoneyHive API doesn't support OTLP format")
                        HoneyHiveOTelTracer.otlp_enabled = False
                    else:
                        otlp_span_exporter = OTLPSpanExporter(
                            endpoint=endpoint,
                            headers=headers
                        )
                        # Configure BatchSpanProcessor with shorter timeout for better shutdown handling
                        otlp_processor = BatchSpanProcessor(
                            otlp_span_exporter,
                            max_queue_size=2048,
                            max_export_batch_size=512,
                            schedule_delay_millis=5000,  # 5 seconds
                            export_timeout_millis=30000  # 30 seconds
                        )
                        HoneyHiveOTelTracer.tracer_provider.add_span_processor(otlp_processor)
                        if HoneyHiveOTelTracer.verbose:
                            print(f"🔍 Added OTLP span exporter to: {endpoint}")
                except Exception as e:
                    if HoneyHiveOTelTracer.verbose:
                        print(f"Warning: Could not add OTLP span exporter: {e}")
                    # Disable OTLP if there's an error
                    HoneyHiveOTelTracer.otlp_enabled = False
            
            # Configure span exporters
            if HoneyHiveOTelTracer.verbose:
                console_exporter = ConsoleSpanExporter()
                # Configure console processor with shorter timeout
                console_processor = BatchSpanProcessor(
                    console_exporter,
                    max_queue_size=1024,
                    max_export_batch_size=256,
                    schedule_delay_millis=1000,  # 1 second
                    export_timeout_millis=5000   # 5 seconds
                )
                HoneyHiveOTelTracer.tracer_provider.add_span_processor(console_processor)
            
            # Note: We handle span-to-event conversion via HoneyHiveSpanProcessor
            # No need for OTLP trace exporter since we're using custom event creation
            if HoneyHiveOTelTracer.verbose:
                print("🔍 Using HoneyHiveSpanProcessor for event creation instead of OTLP exporter")
            
            # Set the tracer provider
            trace.set_tracer_provider(HoneyHiveOTelTracer.tracer_provider)
            
            # Get tracer (no metrics endpoint, so no meter provider)
            HoneyHiveOTelTracer.tracer = trace.get_tracer("honeyhive", "1.0.0")
            
            HoneyHiveOTelTracer._is_initialized = True
            HoneyHiveOTelTracer._is_traceloop_initialized = True
            HoneyHiveOTelTracer.is_evaluation = HoneyHiveOTelTracer.is_evaluation

    @staticmethod
    def _initialize_otel_test_mode():
        """Initialize OpenTelemetry components in test mode (no external dependencies)"""
        with threading.Lock():
            # Disable OTLP exporter in test mode by default to avoid HTTP errors
            HoneyHiveOTelTracer.otlp_enabled = False
            
            # Initialize propagator
            HoneyHiveOTelTracer.propagator = CompositePropagator([
                TraceContextTextMapPropagator(),
                W3CBaggagePropagator()
            ])
            
            # Check if tracer provider is already set
            try:
                existing_provider = trace.get_tracer_provider()
                if existing_provider is not None:
                    # Use existing provider
                    HoneyHiveOTelTracer.tracer_provider = existing_provider
                else:
                    # Create new provider
                    HoneyHiveOTelTracer.tracer_provider = TracerProvider()
                    trace.set_tracer_provider(HoneyHiveOTelTracer.tracer_provider)
            except Exception:
                # Create new provider if there's an issue
                HoneyHiveOTelTracer.tracer_provider = TracerProvider()
                trace.set_tracer_provider(HoneyHiveOTelTracer.tracer_provider)
            
            # Add custom span processor for session_id and association properties
            HoneyHiveOTelTracer.span_processor = HoneyHiveSpanProcessor()
            # Only add span processor if the tracer provider supports it
            if hasattr(HoneyHiveOTelTracer.tracer_provider, 'add_span_processor'):
                HoneyHiveOTelTracer.tracer_provider.add_span_processor(HoneyHiveOTelTracer.span_processor)
            
            # Add console exporter for testing
            console_exporter = ConsoleSpanExporter()
            # Only add span processor if the tracer provider supports it
            if hasattr(HoneyHiveOTelTracer.tracer_provider, 'add_span_processor'):
                # Configure console processor with shorter timeout for testing
                console_processor = BatchSpanProcessor(
                    console_exporter,
                    max_queue_size=512,
                    max_export_batch_size=128,
                    schedule_delay_millis=500,   # 0.5 seconds
                    export_timeout_millis=2000   # 2 seconds
                )
                HoneyHiveOTelTracer.tracer_provider.add_span_processor(console_processor)
            
            # Add OTLP span exporter for testing (with null endpoint to avoid external calls)
            if HoneyHiveOTelTracer.otlp_enabled:
                try:
                    # In test mode, use a local endpoint to avoid external API calls
                    endpoint = HoneyHiveOTelTracer.otlp_endpoint or "http://localhost:4318/v1/traces"
                    headers = HoneyHiveOTelTracer.otlp_headers or {"Authorization": f"Bearer test-api-key"}
                    
                    # Skip OTLP in test mode unless explicitly configured with a valid endpoint
                    if endpoint == "http://localhost:4318/v1/traces" and not HoneyHiveOTelTracer.otlp_endpoint:
                        if HoneyHiveOTelTracer.verbose:
                            print(f"🔍 Skipping OTLP exporter in test mode: no valid endpoint configured")
                        HoneyHiveOTelTracer.otlp_enabled = False
                    else:
                        otlp_span_exporter = OTLPSpanExporter(
                            endpoint=endpoint,
                            headers=headers
                        )
                        # Only add span processor if the tracer provider supports it
                        if hasattr(HoneyHiveOTelTracer.tracer_provider, 'add_span_processor'):
                            # Configure OTLP processor with shorter timeout for testing
                            otlp_processor = BatchSpanProcessor(
                                otlp_span_exporter,
                                max_queue_size=512,
                                max_export_batch_size=128,
                                schedule_delay_millis=500,   # 0.5 seconds
                                export_timeout_millis=2000   # 2 seconds
                            )
                            HoneyHiveOTelTracer.tracer_provider.add_span_processor(otlp_processor)
                except Exception as e:
                    # Silently fail in test mode and disable OTLP
                    HoneyHiveOTelTracer.otlp_enabled = False
            
            # Get tracer (no metrics endpoint, so no meter provider)
            HoneyHiveOTelTracer.tracer = trace.get_tracer("honeyhive", "1.0.0")
            
            HoneyHiveOTelTracer._is_initialized = True
            HoneyHiveOTelTracer._is_traceloop_initialized = True

    @staticmethod
    def init(*args, **kwargs):
        """Legacy compatibility method"""
        return HoneyHiveOTelTracer(*args, **kwargs)
    
    @staticmethod
    def configure_otlp_exporter(enabled=True, endpoint=None, headers=None):
        """Configure OTLP span exporter settings"""
        HoneyHiveOTelTracer.otlp_enabled = enabled
        if endpoint is not None:
            HoneyHiveOTelTracer.otlp_endpoint = endpoint
        if headers is not None:
            HoneyHiveOTelTracer.otlp_headers = headers
        
        if HoneyHiveOTelTracer.verbose:
            print(f"🔍 OTLP exporter configured: enabled={enabled}, endpoint={endpoint}")
    
    @staticmethod
    def shutdown():
        """Properly shutdown OpenTelemetry components and flush remaining spans"""
        try:
            if HoneyHiveOTelTracer.tracer_provider is not None:
                # Force flush any remaining spans before shutdown
                if hasattr(HoneyHiveOTelTracer.tracer_provider, 'force_flush'):
                    HoneyHiveOTelTracer.tracer_provider.force_flush()
                
                # Shutdown the tracer provider
                if hasattr(HoneyHiveOTelTracer.tracer_provider, 'shutdown'):
                    HoneyHiveOTelTracer.tracer_provider.shutdown()
            

            
            if HoneyHiveOTelTracer.verbose:
                print("🔍 OpenTelemetry components shut down successfully")
                
        except Exception as e:
            if HoneyHiveOTelTracer.verbose:
                print(f"Warning: Error during OpenTelemetry shutdown: {e}")
    
    @staticmethod
    def _validate_api_key(api_key):
        if not api_key or not isinstance(api_key, str) or api_key.strip() == "":
            raise Exception("api_key must be a non-empty string")
    
    @staticmethod
    def _validate_server_url(server_url):
        if not server_url or not isinstance(server_url, str) or server_url.strip() == "":
            raise Exception("server_url must be a non-empty string")
        # Basic URL validation
        if not server_url.startswith(('http://', 'https://')):
            raise Exception("server_url must be a valid HTTP/HTTPS URL")
    
    @staticmethod
    def _validate_project(project):
        if not project or not isinstance(project, str) or project.strip() == "":
            raise Exception("project must be a non-empty string")
    
    @staticmethod
    def _validate_source(source):
        if not source or not isinstance(source, str) or source.strip() == "":
            raise Exception("source must be a non-empty string")
    
    @staticmethod
    def _get_validated_api_key(api_key=None):
        if api_key is None:
            api_key = os.getenv("HH_API_KEY")
        HoneyHiveOTelTracer._validate_api_key(api_key)
        return api_key
    
    @staticmethod
    def _get_validated_server_url(server_url=None):
        if server_url is None or server_url == 'https://api.honeyhive.ai':
            server_url = os.getenv("HH_API_URL", 'https://api.honeyhive.ai')
        HoneyHiveOTelTracer._validate_server_url(server_url)
        return server_url
    
    @staticmethod
    def _get_validated_project(project=None):
        if project is None:
            project = os.getenv("HH_PROJECT")
        HoneyHiveOTelTracer._validate_project(project)
        return project
    
    @staticmethod
    def _get_validated_source(source=None):
        if source is None:
            source = os.getenv("HH_SOURCE", "dev")
        HoneyHiveOTelTracer._validate_source(source)
        return source
    
    @staticmethod
    def _reset_static_state():
        """Reset static state for testing purposes"""
        # First, properly shutdown OpenTelemetry components
        HoneyHiveOTelTracer.shutdown()
        
        # Reset HoneyHive tracer static variables
        HoneyHiveOTelTracer.api_key = None
        HoneyHiveOTelTracer.server_url = None
        HoneyHiveOTelTracer._is_initialized = False
        HoneyHiveOTelTracer._is_traceloop_initialized = False
        HoneyHiveOTelTracer.verbose = False
        HoneyHiveOTelTracer.is_evaluation = False
        HoneyHiveOTelTracer.tracer_provider = None
        HoneyHiveOTelTracer.propagator = None
        HoneyHiveOTelTracer.tracer = None
        HoneyHiveOTelTracer.span_processor = None
        
        # Reset OTLP exporter configuration
        HoneyHiveOTelTracer.otlp_enabled = False
        HoneyHiveOTelTracer.otlp_endpoint = None
        HoneyHiveOTelTracer.otlp_headers = None
        
        # Reset OpenTelemetry global state - ALL LAYERS
        try:
            from opentelemetry import trace, metrics, context
            from opentelemetry.sdk.trace import TracerProvider

            from opentelemetry.sdk.trace.export import ConsoleSpanExporter

            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            
            # 1. Reset trace provider with clean state
            new_trace_provider = TracerProvider()
            trace.set_tracer_provider(new_trace_provider)
            

            
            # 3. Clear ALL existing contexts (not just detach current)
            # This is crucial for complete isolation
            while context.get_current() != context.INVALID_CONTEXT:
                context.detach()
            
            # 4. Clear any global baggage
            try:
                from opentelemetry import baggage
                # Clear all baggage keys
                baggage.set_baggage("session_id", None)
                baggage.set_baggage("project", None)
                baggage.set_baggage("source", None)
                baggage.set_baggage("run_id", None)
                baggage.set_baggage("dataset_id", None)
                baggage.set_baggage("datapoint_id", None)
                baggage.set_baggage("metadata", None)
                baggage.set_baggage("feedback", None)
                baggage.set_baggage("metrics", None)
            except Exception:
                # Silently fail if baggage operations fail
                pass
            
            # 5. Clear association properties from context
            try:
                from opentelemetry import context
                # Get current context and clear association_properties
                current_ctx = context.get_current()
                if current_ctx is not None and current_ctx != context.INVALID_CONTEXT:
                    # Create a new context without association_properties
                    new_ctx = context.Context()
                    # Set the new context as current
                    context.attach(new_ctx)
                    
                    # Also clear any custom context keys that might persist
                    # This is crucial for test isolation
                    if hasattr(current_ctx, '_context'):
                        # Clear any custom keys in the context
                        for key in list(current_ctx._context.keys()):
                            if key != 'baggage':  # Keep baggage, clear everything else
                                del current_ctx._context[key]
            except Exception:
                # Silently fail if context operations fail
                pass
            
            # 6. Force flush any remaining spans/metrics
            try:
                if hasattr(new_trace_provider, 'force_flush'):
                    new_trace_provider.force_flush()

            except Exception:
                # Silently fail if flush operations fail
                pass
            
            # 7. Clear any global trace context
            try:
                from opentelemetry.trace import get_current_span
                # Clear current span context
                while get_current_span() != trace.INVALID_SPAN:
                    context.detach()
            except Exception:
                # Silently fail if span context operations fail
                pass
                
        except Exception as e:
            # Silently fail if OpenTelemetry reset fails
            pass
    
    def session_start(self) -> str:
        """Start a session using the tracer's parameters"""
        # Start the session via API
        self.session_id = HoneyHiveOTelTracer.__start_session(
            HoneyHiveOTelTracer.api_key, 
            self.project, 
            self.session_name, 
            self.source, 
            HoneyHiveOTelTracer.server_url, 
            self.inputs, 
            self.metadata
        )
        
        # Create an OpenTelemetry span for session start
        if HoneyHiveOTelTracer.tracer is not None:
            if HoneyHiveOTelTracer.verbose:
                print(f"🔍 Creating session start span for session: {self.session_id}")
            
            with HoneyHiveOTelTracer.tracer.start_as_current_span("session_start") as span:
                span.set_attribute("honeyhive_event_type", "session_start")
                span.set_attribute("honeyhive_session_id", self.session_id)
                span.set_attribute("honeyhive_project", self.project)
                span.set_attribute("honeyhive_source", self.source)
                if self.inputs:
                    # Convert dict to JSON string for span attributes
                    if isinstance(self.inputs, dict):
                        import json
                        span.set_attribute("honeyhive_inputs_json", json.dumps(self.inputs))
                    else:
                        span.set_attribute("honeyhive_inputs", str(self.inputs))
                if self.metadata:
                    # Convert dict to JSON string for span attributes
                    if isinstance(self.metadata, dict):
                        import json
                        span.set_attribute("honeyhive_metadata_json", json.dumps(self.metadata))
                    else:
                        span.set_attribute("honeyhive_metadata", str(self.metadata))
                
                if HoneyHiveOTelTracer.verbose:
                    print(f"🔍 Session start span created with attributes: {dict(span.attributes)}")
        else:
            if HoneyHiveOTelTracer.verbose:
                print(f"⚠️ No tracer available for session start span")
        
        return self.session_id
    
    @staticmethod
    def _get_git_info():
        """Get git information for metadata"""
        try:
            telemetry_disabled = os.getenv("HONEYHIVE_TELEMETRY", "true").lower() in ["false", "0", "f", "no", "n"]
            if telemetry_disabled:
                if HoneyHiveOTelTracer.verbose:
                    print("Telemetry disabled. Skipping git information collection.")
                return {"error": "Telemetry disabled"}
                
            cwd = os.getcwd()
            
            is_git_repo = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=cwd, capture_output=True, text=True, check=False
            )
            
            if is_git_repo.returncode != 0:
                if HoneyHiveOTelTracer.verbose:
                    print("Not a git repository. Skipping git information collection.")
                return {"error": "Not a git repository"}
                
            commit_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=cwd, capture_output=True, text=True, check=True
            ).stdout.strip()

            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=cwd, capture_output=True, text=True, check=True
            ).stdout.strip()

            repo_url = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=cwd, capture_output=True, text=True, check=True
            ).stdout.strip().rstrip('.git')

            commit_link = f"{repo_url}/commit/{commit_hash}" if "github.com" in repo_url else repo_url

            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=cwd, capture_output=True, text=True, check=True
            ).stdout.strip()

            has_uncommitted_changes = bool(status)

            repo_root = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=cwd, capture_output=True, text=True, check=True
            ).stdout.strip()
            
            main_module = sys.modules.get('__main__')
            relative_path = None
            if main_module and hasattr(main_module, '__file__'):
                absolute_path = os.path.abspath(main_module.__file__)
                relative_path = os.path.relpath(absolute_path, repo_root)

            return {
                "commit_hash": commit_hash,
                "branch": branch,
                "repo_url": repo_url,
                "commit_link": commit_link,
                "uncommitted_changes": has_uncommitted_changes,
                "relative_path": relative_path
            }
        except subprocess.CalledProcessError:
            if HoneyHiveOTelTracer.verbose:
                print("Failed to retrieve Git info. Is this a valid repo?")
            return {"error": "Failed to retrieve Git info. Is this a valid repo?"}
        except FileNotFoundError:
            if HoneyHiveOTelTracer.verbose:
                print("Git is not installed or not in PATH.")
            return {"error": "Git is not installed or not in PATH."}
        except Exception as e:
            if HoneyHiveOTelTracer.verbose:
                print(f"Error getting git info: {e}")
            return {"error": f"Error getting git info: {e}"}
    
    @staticmethod
    def __start_session(api_key, project, session_name, source, server_url, inputs=None, metadata=None):
        """Start a session with the HoneyHive API"""
        sdk = HoneyHive(bearer_auth=api_key, server_url=server_url)
        res = sdk.session.start_session(
            request=operations.StartSessionRequestBody(
                session=components.SessionStartRequest(
                    project=project,
                    session_name=session_name,
                    source=source,
                    inputs=inputs or {},
                    metadata=metadata or {}
                )
            )
        )
        assert res.status_code == 200, f"Failed to start session: {res.raw_response.text}"
        assert res.object.session_id is not None, "Failure initializing session"
        return res.object.session_id
    
    def _sanitize_carrier(carrier, getter):
        """Sanitize carrier for propagation"""
        _propagation_carrier = {}
        for key in ['baggage', 'traceparent']:
            carrier_value = \
                getter.get(carrier, key.lower()) or \
                getter.get(carrier, key.capitalize()) or \
                getter.get(carrier, key.upper())
            if carrier_value is not None:
                _propagation_carrier[key] = [carrier_value]
        return _propagation_carrier
    
    def link(self, carrier=None, getter=BaggageDict.DefaultGetter):
        """Link to a parent trace context"""
        if carrier is None:
            carrier = {}
        
        ctx = context.get_current()
        
        # Handle case where carrier is a string (session_id)
        if isinstance(carrier, str):
            # If carrier is a session_id string, create a proper carrier
            carrier = {"session_id": carrier}
        
        carrier = HoneyHiveOTelTracer._sanitize_carrier(carrier, getter)
        ctx = HoneyHiveOTelTracer.propagator.extract(carrier, ctx, getter=getter)
        
        token = context.attach(ctx)
        
        bags = self.baggage.get_all_baggage()
        # Store association properties in context for compatibility
        ctx = context.get_current()
        ctx = context.set_value('association_properties', bags, ctx)
        context.attach(ctx)
        
        return token
    
    def unlink(self, token):
        """Unlink from a trace context"""
        context.detach(token)
        bags = self.baggage.get_all_baggage()
        ctx = context.get_current()
        ctx = context.set_value('association_properties', bags, ctx)
        context.attach(ctx)
    
    def inject(self, carrier={}, setter=BaggageDict.DefaultSetter):
        """Inject current trace and baggage context into the carrier"""
        ctx = context.get_current()
        if HoneyHiveOTelTracer.propagator:
            HoneyHiveOTelTracer.propagator.inject(carrier, ctx, setter)
        return carrier

    @staticmethod
    def flush():
        """Flush the tracer"""
        if not HoneyHiveOTelTracer._is_initialized:
            print("\033[91mCould not flush: HoneyHiveOTelTracer not initialized successfully\033[0m")
            return
        
        if not HoneyHiveOTelTracer._flush_lock.acquire(blocking=False):
            return
        
        try:
            if HoneyHiveOTelTracer.tracer_provider:
                # Check if the tracer provider supports force_flush
                if hasattr(HoneyHiveOTelTracer.tracer_provider, 'force_flush'):
                    HoneyHiveOTelTracer.tracer_provider.force_flush()

        finally:
            HoneyHiveOTelTracer._flush_lock.release()

    def enrich_session(
        self,
        session_id=None,
        metadata=None, 
        feedback=None, 
        metrics=None, 
        config=None, 
        inputs=None, 
        outputs=None, 
        user_properties=None
    ):
        """Enrich a session with additional data"""
        try:
            # Store values in baggage for context propagation
            if metadata is not None:
                self.baggage['metadata'] = metadata
            if feedback is not None:
                self.baggage['feedback'] = feedback
            if metrics is not None:
                self.baggage['metrics'] = metrics
            
            # In test mode, skip API calls
            if hasattr(self, '_test_mode') and self._test_mode:
                return
                
            if not HoneyHiveOTelTracer._is_initialized:
                if HoneyHiveOTelTracer.verbose:
                    print("Warning: HoneyHiveOTelTracer not initialized, skipping API call")
                return
            
            # Use current session_id if not provided
            if session_id is None:
                session_id = self.session_id
            
            # Make API call to update session
            sdk = HoneyHive(
                bearer_auth=HoneyHiveOTelTracer.api_key,
                server_url=HoneyHiveOTelTracer.server_url
            )
            
            update_request = operations.UpdateEventRequestBody(event_id=session_id.lower())
            if feedback is not None:
                update_request.feedback = feedback
            if metrics is not None:
                update_request.metrics = metrics
            if metadata is not None:
                update_request.metadata = metadata
            if config is not None:
                update_request.config = config
            if inputs is not None:
                print('inputs are not supported in enrich_session')
            if outputs is not None:
                update_request.outputs = outputs
            if user_properties is not None:
                update_request.user_properties = user_properties
            response: operations.UpdateEventResponse = sdk.events.update_event(request=update_request)
            
            if response.status_code != 200:
                raise Exception(f"Failed to enrich session: {response.raw_response.text}")
                
        except Exception as e:
            if HoneyHiveOTelTracer.verbose:
                import traceback
                traceback.print_exc()
            else:
                pass



    # Note: api_key is accessed as HoneyHiveOTelTracer.api_key (class attribute)
    # No property needed since tests can access the class attribute directly

    @property
    def session_id(self) -> Optional[str]:
        """Get the current session ID"""
        if hasattr(self, '_session_id'):
            return self._session_id
        return None

    @session_id.setter
    def session_id(self, value: str) -> None:
        """Set the session ID"""
        self._session_id = value
        if hasattr(self, 'baggage') and self.baggage:
            self.baggage['session_id'] = value

    @property
    def baggage(self) -> 'BaggageDict':
        """Get the baggage dictionary"""
        if not hasattr(self, '_baggage'):
            self._baggage = BaggageDict()
        return self._baggage

    @baggage.setter
    def baggage(self, value: 'BaggageDict') -> None:
        """Set the baggage dictionary"""
        self._baggage = value


def enrich_session(
    session_id=None,
    metadata=None,
    feedback=None,
    metrics=None,
    config=None,
    inputs=None,
    outputs=None,
    user_properties=None
):
    """Global function to enrich a session"""
    # Check if tracer is initialized or if we're in test mode
    if not HoneyHiveOTelTracer._is_initialized and not HoneyHiveOTelTracer._is_traceloop_initialized:
        print("\033[91mCould not enrich session: HoneyHiveOTelTracer not initialized successfully\033[0m")
        return
    
    try:
        # In test mode or when not fully initialized, just store in context
        if HoneyHiveOTelTracer._is_traceloop_initialized and not HoneyHiveOTelTracer._is_initialized:
            # Store in OpenTelemetry context for later use
            ctx = context.get_current()
            if ctx is not None:
                # Store enrichment data in context for later processing
                if metadata:
                    context.set_value('honeyhive_metadata', metadata, ctx)
                if feedback:
                    context.set_value('honeyhive_feedback', feedback, ctx)
                if metrics:
                    context.set_value('honeyhive_metrics', metrics, ctx)
                if config:
                    context.set_value('honeyhive_config', config, ctx)
                if outputs:
                    context.set_value('honeyhive_outputs', outputs, ctx)
                if user_properties:
                    context.set_value('honeyhive_user_properties', user_properties, ctx)
            return
        
        # Full initialization path - make API calls
        sdk = HoneyHive(bearer_auth=HoneyHiveOTelTracer.api_key, server_url=HoneyHiveOTelTracer.server_url)
        if session_id is None:
            ctx: Context = context.get_current()
            association_properties = ctx.get('association_properties') if ctx is not None else None
            if association_properties is not None:
                session_id = association_properties.get('session_id')
            if session_id is None:
                raise Exception("Please initialize HoneyHiveOTelTracer before calling enrich_session")
            
        update_request = operations.UpdateEventRequestBody(event_id=session_id.lower())
        if feedback is not None:
            update_request.feedback = feedback
        if metrics is not None:
            update_request.metrics = metrics
        if metadata is not None:
            update_request.metadata = metadata
        if config is not None:
            update_request.config = config
        if inputs is not None:
            print('inputs are not supported in enrich_session')
        if outputs is not None:
            update_request.outputs = outputs
        if user_properties is not None:
            update_request.user_properties = user_properties
        response: operations.UpdateEventResponse = sdk.events.update_event(request=update_request)
        if response.status_code != 200:
            raise Exception(f"Failed to enrich session: {response.raw_response.text}")
    except Exception as e:
        if HoneyHiveOTelTracer.verbose:
            import traceback
            traceback.print_exc()
        else:
            pass
