"""
Browser configuration schema.

Defines Pydantic v2 configuration for the Browser subsystem (Playwright integration).

Features:
- Browser type selection (chromium, firefox, webkit)
- Headless/headful mode
- Max concurrent sessions (resource management)
- Session timeout (auto-cleanup)
"""

from pydantic import BaseModel, Field


class BrowserConfig(BaseModel):
    """
    Configuration for browser subsystem (Playwright).
    
    Controls browser automation behavior, session management, and resource limits.
    
    Attributes:
        browser_type: Default browser type (chromium, firefox, webkit)
        headless: Run browser in headless mode (default: True)
        max_sessions: Maximum concurrent browser sessions (default: 10)
        session_timeout_minutes: Minutes before idle session cleanup (default: 30)
    
    Example YAML:
        ```yaml
        browser:
          browser_type: chromium
          headless: true
          max_sessions: 10
          session_timeout_minutes: 30
        ```
    
    Validation:
        - browser_type must be chromium, firefox, or webkit
        - max_sessions: 1-50 (resource constraints)
        - session_timeout_minutes: 5-120 (reasonable bounds)
    """
    
    model_config = {"frozen": True, "extra": "forbid"}
    
    browser_type: str = Field(
        default="chromium",
        pattern="^(chromium|firefox|webkit)$",
        description="Browser type for Playwright (chromium, firefox, webkit)"
    )
    
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode (no UI)"
    )
    
    max_sessions: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum concurrent browser sessions (resource management)"
    )
    
    session_timeout_minutes: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Minutes before idle session auto-cleanup"
    )
    
    @property
    def session_timeout_seconds(self) -> int:
        """
        Get session timeout in seconds (for BrowserManager compatibility).
        
        Returns:
            int: Timeout in seconds
        
        Example:
            >>> config = BrowserConfig(session_timeout_minutes=30)
            >>> config.session_timeout_seconds
            1800
        """
        return self.session_timeout_minutes * 60


__all__ = ["BrowserConfig"]
