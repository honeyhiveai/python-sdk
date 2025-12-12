# Backwards compatibility shim - preserves `from honeyhive.api.configurations import ...`
from honeyhive._v0.api.configurations import *  # noqa: F401, F403
