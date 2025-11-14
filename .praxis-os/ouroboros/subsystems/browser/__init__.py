"""
Browser Subsystem: Playwright-based browser automation with isolated sessions.

Components:
- BrowserManager: Manages per-session browser processes
- BrowserSession: Isolated browser session (Playwright + browser + page)

Architecture:
- Per-session isolation (each conversation gets own browser process)
- Lazy initialization (browsers launch on first use)
- Auto-cleanup (idle session timeout)
- Thread-safe session management
- Config-driven (browser type, headless mode, max sessions, timeout)

Integration:
- SessionMapper (middleware) maps conversation_id → browser_session_id
- Tools layer wraps browser actions (pos_browser)
- No cross-subsystem dependencies (isolated)

Example:
    >>> from ouroboros.config.schemas.browser import BrowserConfig
    >>> from ouroboros.subsystems.browser import BrowserManager
    >>> 
    >>> config = BrowserConfig(
    ...     browser_type="chromium",
    ...     headless=True,
    ...     max_sessions=10,
    ...     session_timeout_minutes=30
    ... )
    >>> manager = BrowserManager(config)
    >>> 
    >>> # Get session (auto-creates if new)
    >>> session = await manager.get_session("browser_client_abc_s0")
    >>> await session.page.goto("https://example.com")
    >>> 
    >>> # Close when done
    >>> await manager.close_session("browser_client_abc_s0")

Traceability:
    FR-021: Isolated Playwright Sessions
    FR-022: Browser Actions
    NFR-M4: Subsystem Isolation
"""

from ouroboros.subsystems.browser.manager import BrowserManager, BrowserSession

__all__ = [
    "BrowserManager",
    "BrowserSession",
]

