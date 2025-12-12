# Backwards compatibility shim - preserves `from honeyhive.models.generated import ...`
from honeyhive._v0.models.generated import *  # noqa: F401, F403
