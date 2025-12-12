# Backwards compatibility shim - preserves `from honeyhive.models.tracing import ...`
from honeyhive._v0.models.tracing import *  # noqa: F401, F403
