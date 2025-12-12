# Backwards compatibility shim - preserves `from honeyhive.api.base import ...`
# Import utils that tests may patch at this path
from honeyhive.utils.error_handler import get_error_handler  # noqa: F401

from honeyhive._v0.api.base import *  # noqa: F401, F403
