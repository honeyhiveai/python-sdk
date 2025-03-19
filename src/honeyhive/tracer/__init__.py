import uuid
from traceback import print_exc
import os
import sys
import threading
import io
from contextlib import redirect_stdout

from honeyhive.utils.telemetry import Telemetry
from honeyhive.utils.baggage_dict import BaggageDict
from honeyhive.models import operations, components, errors
from honeyhive.sdk import HoneyHive

from traceloop.sdk import Traceloop
from traceloop.sdk.tracing.tracing import TracerWrapper

from opentelemetry import context, baggage
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator

DEFAULT_SERVER_URL = "https://api.honeyhive.ai"

class HoneyHiveTracer:
    
    # static variables
    verbose = False
    _is_traceloop_initialized = False
    api_key = None
    is_evaluation = False
    instrumentation_id = None
    instance = None
    server_url = None

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
        try:
            # is_evaluation
            if HoneyHiveTracer.is_evaluation:
                # If we're in an evaluation, only new evaluate sessions are allowed
                if not is_evaluation:
                    raise Exception("Evaluation sessions can only be started by the evaluate function.")
            
            # api_key
            if HoneyHiveTracer.api_key is None:
                if api_key is None:
                    # get and validate api key from os env
                    env_api_key = os.getenv("HH_API_KEY")
                    if not HoneyHiveTracer._validate_api_key(env_api_key):
                        raise Exception("api_key must be specified or set in environment variable HH_API_KEY.")
                    api_key = env_api_key
                else:
                    # validate user-provided api key
                    if not HoneyHiveTracer._validate_api_key(api_key):
                        raise Exception("api_key must be a string.")
                    
                # set api key
                HoneyHiveTracer.api_key = api_key
            
            # server_url
            if HoneyHiveTracer.server_url is None:
                if server_url is None:
                    # get server url from os env with default
                    env_server_url = os.getenv("HH_API_URL", DEFAULT_SERVER_URL)
                    if not HoneyHiveTracer._validate_server_url(env_server_url):
                        raise Exception("Invalid server URL in environment variable HH_API_URL.")
                    server_url = env_server_url
                else:
                    # validate user-provided server url
                    if not HoneyHiveTracer._validate_server_url(server_url):
                        raise Exception("server_url must be a valid URL string.")
                # set server url
                HoneyHiveTracer.server_url = server_url
            
            # project
            if project is None:
                project = os.getenv("HH_PROJECT")
                if project is None:
                    raise Exception("project must be specified or set in environment variable HH_PROJECT.")
            
            # session_name
            if session_name is None:
                try:
                    session_name = os.path.basename(sys.argv[0])
                except Exception as e:
                    if HoneyHiveTracer.verbose:
                        print(f"Error setting session_name: {e}")
                    session_name = "unknown"

            # source
            if source is None:
                source = os.getenv("HH_SOURCE", "dev")
            
            # verbose
            HoneyHiveTracer.verbose = verbose
            
            # TODO: migrate to log-based session initialization
            # self.session_id = str(uuid.uuid4()).upper()
            if session_id is None:
                self.session_id = HoneyHiveTracer.__start_session(
                    api_key, project, session_name, source, server_url, inputs
                )
            else:
                # Validate that session_id is a valid UUID
                try:
                    uuid.UUID(session_id)
                    self.session_id = session_id.lower()
                except (ValueError, AttributeError, TypeError):
                    raise errors.SDKError("session_id must be a valid UUID string.")

            # baggage
            self.baggage = BaggageDict().update({
                "session_id": self.session_id,
                "project": project,
                "source": source,
                "disable_http_tracing": str(disable_http_tracing).lower(),
            })

            # evaluation
            if is_evaluation:
                self.baggage.update({
                    "run_id": run_id,
                    "dataset_id": dataset_id,
                    "datapoint_id": datapoint_id,
                })

            # Initialize the Composite Propagator
            HoneyHiveTracer.propagator = CompositePropagator(
                propagators=[
                    TraceContextTextMapPropagator(),
                    W3CBaggagePropagator()
                ]
            )

            # instrument tracer with lock
            with threading.Lock():
                # Initialize Traceloop with CompositePropagator
                if not HoneyHiveTracer._is_traceloop_initialized:
                    # Temporarily redirect stdout to suppress Traceloop init messages
                    with redirect_stdout(io.StringIO()):
                        Traceloop.init(
                            api_endpoint=f"{HoneyHiveTracer.server_url}/opentelemetry",
                            api_key=HoneyHiveTracer.api_key,
                            metrics_exporter=ConsoleMetricExporter(out=open(os.devnull, "w")),
                            disable_batch=disable_batch,
                            propagator=HoneyHiveTracer.propagator
                        )
                    # Print initialization message in orange color (works in both bash and Windows)
                    print("\033[38;5;208mHoneyHive is initialized\033[0m")
                    HoneyHiveTracer._is_traceloop_initialized = True
                    HoneyHiveTracer.instrumentation_id = str(uuid.uuid4()).upper()
                    HoneyHiveTracer.is_evaluation = is_evaluation
                Telemetry().capture("tracer_init", {"hhai_session_id": self.session_id, "hhai_project": project})
                    
            # link_carrier
            if link_carrier is not None:
                self.link(link_carrier)
            else:
                # attach baggage to the current context
                ctx = context.get_current() # deep copy of the current context
                ctx = self.baggage.set_all_baggage(ctx)
                context.attach(ctx)
            
            # traceloop sets "association_properties" in the context
            # however it is not propagated since it doesn't follow the W3C spec for Baggage
            # since traceloop stamps "association_properties" from the context into every span when it starts, 
            # we must attach the baggage in traceloop format as well
            # Traceloop.set_baggage_properties(self.baggage)
            Traceloop.set_association_properties(self.baggage)

            # save the instance
            HoneyHiveTracer.instance = self
            
            # ------------------------------------------------------------
            # TODO: log-based session initialization
            # ------------------------------------------------------------
            # save the init metadata
            # self._init_metadata = {
            #     "project": project,
            #     "session_name": session_name,
            #     "source": source,
            #     "server_url": server_url,
            #     "verbose": verbose,
            #     "disable_batch": disable_batch,
            #     "link_carrier_provided": link_carrier is not None,
            #     "instrumentation_id": HoneyHiveTracer.instrumentation_id,
            # }
            
            # # log the session initialization
            # @trace
            # def __session_init():
            #     enrich_span(metadata={
            #         '_init_metadata': self._init_metadata
            #     })
            # __session_init()
            # ------------------------------------------------------------
        except errors.SDKError as e:
            # Raise SDK exceptions as-is but without traceback
            print(f"\033[91mHoneyHive SDK Error: {str(e)}\033[0m")
        except:
            # Log other exceptions if verbose is enabled
            if HoneyHiveTracer.verbose:
                print_exc()
            else:
                pass


    # TODO: remove this, legacy DX
    @staticmethod
    def init(*args, **kwargs):
        HoneyHiveTracer.instance = HoneyHiveTracer(*args, **kwargs)
        return HoneyHiveTracer.instance
    
    @staticmethod
    def _validate_api_key(api_key):
        return api_key and type(api_key) == str
    
    @staticmethod
    def _validate_server_url(server_url):
        return server_url and type(server_url) == str
    
    @staticmethod
    def __start_session(api_key, project, session_name, source, server_url, inputs=None):
        sdk = HoneyHive(bearer_auth=api_key, server_url=server_url)
        res = sdk.session.start_session(
            request=operations.StartSessionRequestBody(
                session=components.SessionStartRequest(
                    project=project,
                    session_name=session_name,
                    source=source,
                    inputs=inputs or {},
                )
            )
        )
        assert res.status_code == 200, f"Failed to start session: {res.raw_response.text}"
        assert res.object.session_id is not None, "Failure initializing session"
        return res.object.session_id
    
    def _sanitize_carrier(carrier, getter):
        # check for baggage in the headers, potentially re-cased
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
        ctx = context.get_current() # deep copy of the current context
        
        # extract baggage from the carrier
        carrier = HoneyHiveTracer._sanitize_carrier(carrier, getter)
        ctx = HoneyHiveTracer.propagator.extract(carrier, ctx, getter=getter)
        
        # attach the baggage to the current context
        token = context.attach(ctx)
        
        # current context should now have baggage and span context from the carrier
        # it has been fully linked to the parent context
        
        # update the Traceloop baggage in the current context
        # this will be stamped on every span in this context
        bags = self.baggage.get_all_baggage()
        Traceloop.set_association_properties(bags)
        
        return token
    
    def unlink(self, token):
        # included for completeness, but not necessary
        context.detach(token)
        bags = self.baggage.get_all_baggage()
        Traceloop.set_association_properties(bags)
    
    def inject(self, carrier={}, setter=BaggageDict.DefaultSetter):
        # inject current trace and baggage context into the carrier
        HoneyHiveTracer.propagator.inject(carrier, None, setter)
        return carrier

    @staticmethod
    def flush():
        if HoneyHiveTracer._is_traceloop_initialized:
            TracerWrapper().flush()
        else:
            print("\033[91mCould not flush: HoneyHiveTracer not initialized successfully\033[0m")

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
        # TODO: migrate to log-based session enrichments
        # @trace
        # def __enrich_session():
        #     _enrichments = {}
        #     if metadata is not None:
        #         _enrichments["metadata"] = metadata
        #     if feedback is not None:
        #         _enrichments["feedback"] = feedback
        #     if metrics is not None:
        #         _enrichments["metrics"] = metrics
        #     if config is not None:
        #         _enrichments["config"] = config
        #     if inputs is not None:
        #         _enrichments["inputs"] = inputs
        #     if outputs is not None:
        #         _enrichments["outputs"] = outputs
        #     if user_properties is not None:
        #         _enrichments["user_properties"] = user_properties
        #     enrich_span(metadata={
        #         '_enrichments': _enrichments,
        #         '_init_metadata': self._init_metadata
        #     })
        # __enrich_session()
        if not HoneyHiveTracer._is_traceloop_initialized:
            print("\033[91mCould not enrich session: HoneyHiveTracer not initialized successfully\033[0m")
            return
        
        session_id = session_id or self.session_id
        try:
            sdk = HoneyHive(bearer_auth=HoneyHiveTracer.api_key, server_url=HoneyHiveTracer.server_url)
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
            response: operations.UpdateEventResponse = sdk.events.update_event(request=update_request)
            if response.status_code != 200:
                raise Exception(f"Failed to enrich session: {response.raw_response.text}")
        except:
            if HoneyHiveTracer.verbose:
                print_exc()
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
    if not HoneyHiveTracer._is_traceloop_initialized:
        print("\033[91mCould not enrich session: HoneyHiveTracer not initialized successfully\033[0m")
        return
    try:
        sdk = HoneyHive(bearer_auth=HoneyHiveTracer.api_key, server_url=HoneyHiveTracer.instance.server_url)
        if session_id is None and HoneyHiveTracer.instance is None:
            raise Exception("Please initialize HoneyHiveTracer before calling enrich_session")
        session_id = session_id or HoneyHiveTracer.instance.session_id
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
        response: operations.UpdateEventResponse = sdk.events.update_event(request=update_request)
        if response.status_code != 200:
            raise Exception(f"Failed to enrich session: {response.raw_response.text}")
    except:
        if HoneyHiveTracer.verbose:
            print_exc()
        else:
            pass
