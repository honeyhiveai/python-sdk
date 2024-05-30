import honeyhive
import os
from honeyhive.models import components, operations
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from traceloop.sdk import Traceloop


class HoneyHiveTracer:
    _is_traceloop_initialized = False

    @staticmethod
    def init(
        api_key,
        project,
        session_name,
        source,
        server_url="https://api.honeyhive.ai",
    ):
        try:
            session_id = HoneyHiveTracer.__start_session(
                api_key, project, session_name, source, server_url
            )
            if not HoneyHiveTracer._is_traceloop_initialized:
                Traceloop.init(
                    api_endpoint=f"{server_url}/opentelemetry",
                    api_key=api_key,
                    metrics_exporter=ConsoleMetricExporter(out=open(os.devnull, "w")),
                )
                HoneyHiveTracer._is_traceloop_initialized = True
            Traceloop.set_association_properties({"session_id": session_id})
        except:
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
