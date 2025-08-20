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
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

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
        # Get association properties from context
        if parent_context is not None:
            association_properties = parent_context.get('association_properties')
            if association_properties and isinstance(association_properties, dict):
                # Set session_id and other properties as span attributes
                for key, value in association_properties.items():
                    if value is not None:
                        span.set_attribute(f"honeyhive.{key}", str(value))
    
    def on_end(self, span: ReadableSpan) -> None:
        """Called when a span ends"""
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
    
    # Static variables
    verbose = False
    _is_initialized = False
    api_key = None
    is_evaluation = False
    server_url = None
    _flush_lock = threading.RLock()
    
    # OpenTelemetry components
    tracer_provider: Optional[TracerProvider] = None
    meter_provider: Optional[MeterProvider] = None
    propagator: Optional[CompositePropagator] = None
    tracer: Optional[trace.Tracer] = None
    meter: Optional[Any] = None
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
        link_carrier=None
    ):
        
        # Get association properties from context if available
        ctx: Context = context.get_current()
        association_properties = ctx.get('association_properties') if ctx is not None else None
        if association_properties is not None:
            session_id = association_properties.get('session_id')
            project = association_properties.get('project')
            source = association_properties.get('source')
            disable_http_tracing = association_properties.get('disable_http_tracing') or False
            run_id = association_properties.get('run_id')
            dataset_id = association_properties.get('dataset_id')
            datapoint_id = association_properties.get('datapoint_id')

        try:
            # Initialize API key
            if HoneyHiveOTelTracer.api_key is None:
                if api_key is None:
                    env_api_key = os.getenv("HH_API_KEY")
                    if not HoneyHiveOTelTracer._validate_api_key(env_api_key):
                        raise Exception("api_key must be specified or set in environment variable HH_API_KEY.")
                    api_key = env_api_key
                else:
                    if not HoneyHiveOTelTracer._validate_api_key(api_key):
                        raise Exception("api_key must be a string.")
                HoneyHiveOTelTracer.api_key = api_key
            
            # Initialize server URL
            if HoneyHiveOTelTracer.server_url is None:
                if server_url is None:
                    env_server_url = os.getenv("HH_API_URL", DEFAULT_API_URL)
                    if not HoneyHiveOTelTracer._validate_server_url(env_server_url):
                        raise Exception("Invalid server URL in environment variable HH_API_URL.")
                    server_url = env_server_url
                else:
                    if not HoneyHiveOTelTracer._validate_server_url(server_url):
                        raise Exception("server_url must be a valid URL string.")
                HoneyHiveOTelTracer.server_url = server_url
            
            # Initialize project
            if project is None:
                project = os.getenv("HH_PROJECT")
                if project is None:
                    raise Exception("project must be specified or set in environment variable HH_PROJECT.")
            
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
            
            # Set verbose flag
            HoneyHiveOTelTracer.verbose = verbose
            
            # Initialize session
            if session_id is None:
                git_info = HoneyHiveOTelTracer._get_git_info()
                metadata = git_info if "error" not in git_info else None
                
                self.session_name = session_name
                self.inputs = inputs
                self.metadata = metadata
                self.project = project
                self.source = source
                
                self.session_start()
            else:
                try:
                    uuid.UUID(session_id)
                    self.session_id = session_id.lower()
                    self.project = project
                    self.source = source
                except (ValueError, AttributeError, TypeError):
                    raise errors.SDKError("session_id must be a valid UUID string.")

            # Initialize baggage
            self.baggage = BaggageDict().update({
                "session_id": self.session_id,
                "project": project,
                "source": source,
                "disable_http_tracing": str(disable_http_tracing).lower(),
            })

            if is_evaluation:
                self.baggage.update({
                    "run_id": run_id,
                    "dataset_id": dataset_id,
                    "datapoint_id": datapoint_id,
                })

            # Initialize OpenTelemetry components
            HoneyHiveOTelTracer._initialize_otel(disable_batch)

            # Handle link carrier
            if link_carrier is not None:
                self.link(link_carrier)
            else:
                ctx = context.get_current()
                ctx = self.baggage.set_all_baggage(ctx)
                context.attach(ctx)
            
            # Print initialization message
            if not HoneyHiveOTelTracer.is_evaluation:
                print("\033[38;5;208mHoneyHive is initialized\033[0m")
                
        except errors.SDKError as e:
            print(f"\033[91mHoneyHive SDK Error: {str(e)}\033[0m")
        except Exception as e:
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
            
            # Configure span exporters
            if HoneyHiveOTelTracer.verbose:
                console_exporter = ConsoleSpanExporter()
                HoneyHiveOTelTracer.tracer_provider.add_span_processor(
                    BatchSpanProcessor(console_exporter)
                )
            
            # Add OTLP exporter for HoneyHive
            otlp_exporter = OTLPSpanExporter(
                endpoint=f"{HoneyHiveOTelTracer.server_url}/opentelemetry/v1/traces",
                headers={"Authorization": f"Bearer {HoneyHiveOTelTracer.api_key}"}
            )
            
            if disable_batch:
                HoneyHiveOTelTracer.tracer_provider.add_span_processor(
                    BatchSpanProcessor(otlp_exporter, max_queue_size=1, max_export_batch_size=1)
                )
            else:
                HoneyHiveOTelTracer.tracer_provider.add_span_processor(
                    BatchSpanProcessor(otlp_exporter)
                )
            
            # Set the tracer provider
            trace.set_tracer_provider(HoneyHiveOTelTracer.tracer_provider)
            
            # Initialize meter provider
            HoneyHiveOTelTracer.meter_provider = MeterProvider()
            
            # Configure metric exporters
            if HoneyHiveOTelTracer.verbose:
                console_metric_reader = PeriodicExportingMetricReader(
                    ConsoleMetricExporter(out=open(os.devnull, "w"))
                )
                HoneyHiveOTelTracer.meter_provider.add_metric_reader(console_metric_reader)
            
            # Add OTLP metric exporter
            otlp_metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(
                    endpoint=f"{HoneyHiveOTelTracer.server_url}/opentelemetry/v1/metrics",
                    headers={"Authorization": f"Bearer {HoneyHiveOTelTracer.api_key}"}
                )
            )
            HoneyHiveOTelTracer.meter_provider.add_metric_reader(otlp_metric_reader)
            
            # Set the meter provider
            from opentelemetry.metrics import set_meter_provider
            set_meter_provider(HoneyHiveOTelTracer.meter_provider)
            
            # Get tracer and meter
            HoneyHiveOTelTracer.tracer = trace.get_tracer("honeyhive", "1.0.0")
            HoneyHiveOTelTracer.meter = HoneyHiveOTelTracer.meter_provider.get_meter("honeyhive", "1.0.0")
            
            HoneyHiveOTelTracer._is_initialized = True
            HoneyHiveOTelTracer.is_evaluation = HoneyHiveOTelTracer.is_evaluation

    @staticmethod
    def init(*args, **kwargs):
        """Legacy compatibility method"""
        return HoneyHiveOTelTracer(*args, **kwargs)
    
    @staticmethod
    def _validate_api_key(api_key):
        return api_key and type(api_key) == str
    
    @staticmethod
    def _validate_server_url(server_url):
        return server_url and type(server_url) == str
    
    @staticmethod
    def _validate_project(project):
        return project and type(project) == str
    
    @staticmethod
    def _validate_source(source):
        return source and type(source) == str
    
    @staticmethod
    def _get_validated_api_key(api_key=None):
        if api_key is None:
            api_key = os.getenv("HH_API_KEY")
        if not HoneyHiveOTelTracer._validate_api_key(api_key):
            raise Exception("api_key must be specified or set in environment variable HH_API_KEY.")
        return api_key
    
    @staticmethod
    def _get_validated_server_url(server_url=None):
        if server_url is None or server_url == 'https://api.honeyhive.ai':
            server_url = os.getenv("HH_API_URL", 'https://api.honeyhive.ai')
        if not HoneyHiveOTelTracer._validate_server_url(server_url):
            raise Exception("server_url must be a valid URL string.")
        return server_url
    
    @staticmethod
    def _get_validated_project(project=None):
        if project is None:
            project = os.getenv("HH_PROJECT")
        if not HoneyHiveOTelTracer._validate_project(project):
            raise Exception("project must be specified or set in environment variable HH_PROJECT.")
        return project
    
    @staticmethod
    def _get_validated_source(source=None):
        if source is None:
            source = os.getenv("HH_SOURCE", "dev")
        if not HoneyHiveOTelTracer._validate_source(source):
            raise Exception("source must be a non-empty string.")
        return source
    
    def session_start(self) -> str:
        """Start a session using the tracer's parameters"""
        self.session_id = HoneyHiveOTelTracer.__start_session(
            HoneyHiveOTelTracer.api_key, 
            self.project, 
            self.session_name, 
            self.source, 
            HoneyHiveOTelTracer.server_url, 
            self.inputs, 
            self.metadata
        )
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
    
    def link(self, carrier={}, getter=BaggageDict.DefaultGetter):
        """Link to a parent trace context"""
        ctx = context.get_current()
        
        carrier = HoneyHiveOTelTracer._sanitize_carrier(carrier, getter)
        ctx = HoneyHiveOTelTracer.propagator.extract(carrier, ctx, getter=getter)
        
        token = context.attach(ctx)
        
        bags = self.baggage.get_all_baggage()
        # Store association properties in context for compatibility
        ctx = context.get_current()
        ctx = context.set_value(ctx, 'association_properties', bags)
        context.attach(ctx)
        
        return token
    
    def unlink(self, token):
        """Unlink from a trace context"""
        context.detach(token)
        bags = self.baggage.get_all_baggage()
        ctx = context.get_current()
        ctx = context.set_value(ctx, 'association_properties', bags)
        context.attach(ctx)
    
    def inject(self, carrier={}, setter=BaggageDict.DefaultSetter):
        """Inject current trace and baggage context into the carrier"""
        HoneyHiveOTelTracer.propagator.inject(carrier, None, setter)
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
                HoneyHiveOTelTracer.tracer_provider.force_flush()
            if HoneyHiveOTelTracer.meter_provider:
                HoneyHiveOTelTracer.meter_provider.force_flush()
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
        if not HoneyHiveOTelTracer._is_initialized:
            print("\033[91mCould not enrich session: HoneyHiveOTelTracer not initialized successfully\033[0m")
            return
        
        session_id = session_id or self.session_id
        try:
            sdk = HoneyHive(bearer_auth=HoneyHiveOTelTracer.api_key, server_url=HoneyHiveOTelTracer.server_url)
            update_request = operations.UpdateEventRequestBody(event_id=session_id)
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
    if not HoneyHiveOTelTracer._is_initialized:
        print("\033[91mCould not enrich session: HoneyHiveOTelTracer not initialized successfully\033[0m")
        return
    try:
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
