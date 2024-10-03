import honeyhive
import os
import sys
from honeyhive.models import components, operations
from honeyhive.utils.telemetry import Telemetry
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from traceloop.sdk import Traceloop
from traceloop.sdk.tracing.tracing import TracerWrapper
from traceback import print_exc


class HoneyHiveTracer:
    _is_traceloop_initialized = False
    session_id = None
    api_key = None

    @staticmethod
    def init(
        api_key,
        project,
        session_name=None,
        source='dev',
        server_url="https://api.honeyhive.ai",
        disable_batch=False,
        verbose=False,
    ):
        try:
            HoneyHiveTracer.verbose = verbose
            
            # Set session_name to the main module name if not provided
            if session_name is None:
                try:
                    session_name = os.path.basename(sys.argv[0])
                except Exception as e:
                    if HoneyHiveTracer.verbose:
                        print(f"Error setting session_name: {e}")
                    session_name = "unknown"
            
            session_id = HoneyHiveTracer.__start_session(
                api_key, project, session_name, source, server_url
            )
            Telemetry().capture("tracer_init", {"hhai_session_id": session_id})
            if not HoneyHiveTracer._is_traceloop_initialized:
                Traceloop.init(
                    api_endpoint=f"{server_url}/opentelemetry",
                    api_key=api_key,
                    metrics_exporter=ConsoleMetricExporter(out=open(os.devnull, "w")),
                    disable_batch=disable_batch,
                )
                HoneyHiveTracer._is_traceloop_initialized = True
            Traceloop.set_association_properties({"session_id": session_id})
            HoneyHiveTracer.session_id = session_id
            HoneyHiveTracer.api_key = api_key
        except:
            if HoneyHiveTracer.verbose:
                print_exc()
            else:
                pass

    @staticmethod
    def init_from_session_id(
        api_key,
        session_id,
        server_url="https://api.honeyhive.ai",
        disable_batch=False,
        verbose=False,
    ):
        try:
            HoneyHiveTracer.verbose = verbose
            
            if not HoneyHiveTracer._is_traceloop_initialized:
                Traceloop.init(
                    api_endpoint=f"{server_url}/opentelemetry",
                    api_key=api_key,
                    metrics_exporter=ConsoleMetricExporter(out=open(os.devnull, "w")),
                    disable_batch=disable_batch,
                )
                HoneyHiveTracer._is_traceloop_initialized = True
            Traceloop.set_association_properties({"session_id": session_id})
            HoneyHiveTracer.session_id = session_id
            HoneyHiveTracer.api_key = api_key
        except:
            if HoneyHiveTracer.verbose:
                print_exc()
            else:
                pass

    @staticmethod
    def __start_session(api_key, project, session_name, source, server_url):
        sdk = honeyhive.HoneyHive(bearer_auth=api_key, server_url=server_url)
        res = sdk.session.start_session(
            request=operations.StartSessionRequestBody(
                session=components.SessionStartRequest(
                    project=project,
                    session_name=session_name,
                    source=source,
                )
            )
        )
        assert res.object.session_id is not None
        return res.object.session_id

    @staticmethod
    def flush():
        TracerWrapper().flush()

def enrich_session(
    metadata=None, 
    feedback=None, 
    metrics=None, 
    config=None, 
    inputs=None, 
    outputs=None, 
    user_properties=None
):
    if HoneyHiveTracer.session_id is None:
        raise Exception("HoneyHiveTracer is not initialized")
    session_id = HoneyHiveTracer.session_id
    try:
        sdk = honeyhive.HoneyHive(HoneyHiveTracer.api_key)
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
            print('inputs are not supported in enrich_session') # TODO: add support for inputs (type change)
        if outputs is not None:
            update_request.outputs = outputs
        if user_properties is not None:
            update_request.user_properties = user_properties
        sdk.events.update_event(request=update_request)
    except:
        if HoneyHiveTracer.verbose:
            print_exc()
        else:
            pass