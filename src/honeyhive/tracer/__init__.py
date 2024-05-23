import honeyhive
import os
from honeyhive.models import components, operations
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from traceloop.sdk import Traceloop


class HoneyHiveTracer:
    @staticmethod
    def init(
        api_key,
        project,
        session_name,
        source,
        server_url="https://api.honeyhive.ai",
    ):
        try:
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
            session_id = res.object.session_id
            Traceloop.init(
                api_endpoint=f"{server_url}/opentelemetry",
                app_name=session_id,
                metrics_exporter=ConsoleMetricExporter(out=open(os.devnull, "w")),
                headers={"Authorization": f"Bearer {api_key}"},
            )
        except:
            pass
