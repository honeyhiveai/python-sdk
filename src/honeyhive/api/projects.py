# Backwards compatibility shim - preserves `from honeyhive.api.projects import ...`
from honeyhive._v0.api.projects import *  # noqa: F401, F403
