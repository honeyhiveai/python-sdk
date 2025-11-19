"""
Ouroboros Foundation Layer.

Low-level utilities and infrastructure:
- SessionMapper: Generic session state persistence with status-based organization
- SessionStateHelper: Type-safe wrapper for SessionMapper with Pydantic models
- ProjectInfoDiscovery: Dynamic project metadata discovery
- PortManager: Dynamic port allocation for dual-transport
- TransportManager: Transport mode orchestration (dual/stdio/http)

Dependencies: None (foundation layer has no internal dependencies)

Traceability:
    Foundation layer components used by all other layers
"""

from ouroboros.foundation.init_lock import InitLock
from ouroboros.foundation.port_manager import PortManager
from ouroboros.foundation.project_info import ProjectInfoDiscovery
from ouroboros.foundation.session_mapper import SessionMapper
from ouroboros.foundation.session_state_helper import SessionStateHelper
from ouroboros.foundation.transport_manager import TransportManager

__all__ = [
    "InitLock",
    "SessionMapper",
    "SessionStateHelper",
    "ProjectInfoDiscovery",
    "PortManager",
    "TransportManager",
]

