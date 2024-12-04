from honeyhive.utils.telemetry import Telemetry
from .custom import trace, enrich_span

from traceloop.sdk import Traceloop
from traceloop.sdk.tracing.tracing import TracerWrapper

from opentelemetry import context, baggage
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator

import uuid
from traceback import print_exc
import os
import sys

import honeyhive
from honeyhive import operations, components
class BaggageDict(dict):

    valid_baggage_keys = [
        'session_id', 
        # 'project',
    ]
    
    class DefaultGetter:
        @staticmethod
        def get(carrier, key):
            return carrier.get(key)
    
    class DefaultSetter:
        @staticmethod
        def set(carrier, key, value):
            carrier[key] = value

    def update(self, _dict: dict):
        _dict = {
            k: str(v) for k, v in _dict.items() 
            if v is not None and k in self.valid_baggage_keys
        }
        super().update(_dict)
        return self
    
    def __setitem__(self, key: str, value: str):
        if value is None:
            return
        super().__setitem__(key, str(value))
    
    def __getitem__(self, key: str):
        value = super().__getitem__(key)
        if value == "True":
            return True
        if value == "False":
            return False
        return value
    
    def get(self, key: str):
        return self.__getitem__(key)
    
    def set_all_baggage(self, ctx=None):
        if ctx is None:
            ctx = context.get_current()
        for key in BaggageDict.valid_baggage_keys:            
            value = self.get(key)
            if value is not None:
                ctx = baggage.set_baggage(key, value, ctx)
        return ctx

    def get_all_baggage(self, ctx=None):
        if ctx is None:
            ctx = context.get_current()
        bags = {}
        for key in BaggageDict.valid_baggage_keys:
            value = baggage.get_baggage(key, ctx)
            if value is not None:
                bags[key] = value
        return bags

class HoneyHiveTracer:
    
    verbose = False
    _is_traceloop_initialized = False
    api_key = None
    is_evaluation = False
    instrumentation_id = None
    
    def __init__(
        self,
        api_key=os.environ.get("HH_API_KEY"),
        project=os.environ.get("HH_PROJECT"),
        session_name=None,
        source='dev',
        server_url=os.environ.get("HH_SERVER_URL", "https://api.honeyhive.ai"),
        disable_batch=False,
        verbose=False,
        inputs=None,
        is_evaluation=False,
        link_carrier=None
    ):
        try:
            HoneyHiveTracer.verbose = verbose

            if HoneyHiveTracer.is_evaluation:
                # If we're in an evaluation, only new evaluate sessions are allowed
                if not is_evaluation:
                    return
            
            # Check for api_key and project in the arguments or environment variables
            if api_key is None:
                # check os env for api key
                api_key = os.getenv("HONEYHIVE_API_KEY")
                if api_key is None:
                    raise Exception("api_key must be specified or set in environment variable HH_API_KEY.")
            if project is None:
                project = os.getenv("HH_PROJECT")
                if project is None:
                    raise Exception("project must be specified or set in environment variable HH_PROJECT.")

            HoneyHiveTracer.verbose = verbose
            HoneyHiveTracer.api_key = api_key
            
            self.session_id = str(uuid.uuid4()).upper()
            self.baggage = BaggageDict().update({
                "session_id": self.session_id,
                # "project": project,
            })
            
            assert self.api_key is not None, \
                "api_key is not set. Either set a HH_API_KEY environment variable or pass an api_key to the tracer."
            
            # Initialize the Composite Propagator
            HoneyHiveTracer.propagator = CompositePropagator(
                propagators=[
                    TraceContextTextMapPropagator(),
                    W3CBaggagePropagator()
                ]
            )
            
            # Initialize Traceloop with CompositePropagator
            if not HoneyHiveTracer._is_traceloop_initialized:
                Traceloop.init(
                    api_endpoint=f"{server_url}/opentelemetry",
                    api_key=api_key,
                    metrics_exporter=ConsoleMetricExporter(out=open(os.devnull, "w")),
                    disable_batch=disable_batch,
                    propagator=HoneyHiveTracer.propagator
                )
                HoneyHiveTracer._is_traceloop_initialized = True
                HoneyHiveTracer.instrumentation_id = str(uuid.uuid4()).upper()

            Telemetry().capture("tracer_init", {"hhai_session_id": self.session_id})
            
            # Set session_name to the main module name if not provided
            if session_name is None:
                try:
                    session_name = os.path.basename(sys.argv[0])
                except Exception as e:
                    if HoneyHiveTracer.verbose:
                        print(f"Error setting session_name: {e}")
                    session_name = "unknown"
                    
            if link_carrier is not None:
                self.link(link_carrier)
            else:
                # attach baggage to the current context
                ctx = context.get_current() # deep copy of the current context
                ctx = self.baggage.set_all_baggage(ctx)
                context.attach(ctx)
            
            # traceloop sets "association_properties" in the context
            # however it is not propagated since it doesn't follow the W3C spec for Baggage
            # since traceloop stamps "association_properties" from the context into every span when it starts, we must attach the baggage in traceloop format as well
            Traceloop.set_association_properties(self.baggage)
            
            # save the init metadata
            self._init_metadata = {
                "project": project,
                "session_name": session_name,
                "source": source,
                "server_url": server_url,
                "verbose": verbose,
                "disable_batch": disable_batch,
                "link_carrier_provided": link_carrier is not None,
                "instrumentation_id": HoneyHiveTracer.instrumentation_id,
            }
            
            # log the session initialization
            @trace
            def __session_init():
                enrich_span(metadata={
                    '_init_metadata': self._init_metadata
                })
            __session_init()
            
            session_id = HoneyHiveTracer.__start_session(
                api_key, project, session_name, source, server_url, inputs
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
                HoneyHiveTracer.is_evaluation = is_evaluation
            Traceloop.set_association_properties({"session_id": session_id})
            HoneyHiveTracer.session_id = session_id
            HoneyHiveTracer.api_key = api_key
        except:
            if HoneyHiveTracer.verbose:
                print_exc()
            else:
                pass

    @staticmethod
    def init(*args, **kwargs):
        return HoneyHiveTracer(*args, **kwargs)
    
    def __start_session(self, api_key, project, session_name, source, server_url, inputs=None):
        sdk = honeyhive.HoneyHive(bearer_auth=api_key, server_url=server_url)
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
        assert res.object.session_id is not None
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
        TracerWrapper().flush()

    def enrich_session(
        self,
        metadata=None, 
        feedback=None, 
        metrics=None, 
        config=None, 
        inputs=None, 
        outputs=None, 
        user_properties=None
    ):
        # log the session-level enrichments
        @trace
        def __enrich_session():
            _enrichments = {}
            if metadata is not None:
                _enrichments["metadata"] = metadata
            if feedback is not None:
                _enrichments["feedback"] = feedback
            if metrics is not None:
                _enrichments["metrics"] = metrics
            if config is not None:
                _enrichments["config"] = config
            if inputs is not None:
                _enrichments["inputs"] = inputs
            if outputs is not None:
                _enrichments["outputs"] = outputs
            if user_properties is not None:
                _enrichments["user_properties"] = user_properties
            enrich_span(metadata={
                '_enrichments': _enrichments,
                '_init_metadata': self._init_metadata
            })
        __enrich_session()
