"""
Browser subsystem models.

Separates runtime state (BrowserSession with Playwright objects) from
persistable state (BrowserSessionState as Pydantic model for SessionMapper).

Architecture:
    - BrowserSession: @dataclass with runtime objects (browser, page)
      → In-memory only, not serializable
    
    - BrowserSessionState: Pydantic BaseModel with metadata only
      → Persisted via SessionStateHelper for timeout cleanup

Traceability:
    Design Decision: Separate runtime vs persistable state models
    Reason: Playwright objects (Browser, Page) are not JSON-serializable
"""

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, Field


class BrowserSessionState(BaseModel):
    """
    Persistable browser session metadata (no runtime objects).
    
    Used by SessionStateHelper for timeout-based cleanup. Does NOT contain
    Playwright runtime objects (browser, page) as they cannot be serialized.
    
    Attributes:
        session_id: Unique session identifier
        browser_type: Browser type (chromium/firefox/webkit)
        headless: Whether running in headless mode
        created_at: Session creation timestamp
        last_access: Last activity timestamp (updated on each get_session call)
        tab_ids: List of tab IDs (for tracking, actual Page objects not serializable)
    """
    
    model_config = {"extra": "forbid"}
    
    session_id: str = Field(..., min_length=1, description="Unique session identifier")
    browser_type: str = Field(..., description="Browser type (chromium/firefox/webkit)")
    headless: bool = Field(..., description="Headless mode flag")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_access: datetime = Field(..., description="Last activity timestamp")
    tab_ids: Dict[str, str] = Field(
        default_factory=dict, 
        description="Tab ID to URL mapping (for tracking only, Page objects not serializable)"
    )

