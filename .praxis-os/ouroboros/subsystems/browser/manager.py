"""
Browser automation manager for Ouroboros MCP server.

Provides Playwright-based browser automation with per-session isolation
for multi-chat safety. Each session gets its own browser process for
complete fault isolation and simplified cleanup.

Architecture:
    Per-Session Browsers (Fully Isolated)
    - Each session has own Playwright + Chromium process
    - No shared browser state between sessions
    - Simpler cleanup (kill process)
    - Better fault isolation (crash doesn't affect other sessions)
    - Developer experience > memory efficiency

Usage:
    >>> from ouroboros.config.schemas.browser import BrowserConfig
    >>> config = BrowserConfig()
    >>> manager = BrowserManager(config)
    >>> session = await manager.get_session("browser_chat_123")
    >>> await session.page.goto("https://example.com")
    >>> await manager.close_session("browser_chat_123")

Concurrency:
    - Thread-safe via asyncio.Lock on session dict
    - Each session operates independently
    - No shared browser process

Traceability:
    FR-021: Isolated Playwright Sessions
    FR-022: Browser Actions
    NFR-M4: Subsystem Isolation
"""

# pylint: disable=too-many-instance-attributes
# Justification: BrowserSession dataclass needs 8 attributes for complete session
# state (playwright instance, browser, page, tabs, metadata, timestamps)

# pylint: disable=broad-exception-caught
# Justification: Browser automation must be robust - catches broad exceptions
# during Playwright operations to provide graceful error handling and cleanup

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Literal, Optional

from playwright.async_api import Browser, Page, async_playwright

from ouroboros.config.schemas.browser import BrowserConfig
from ouroboros.foundation.session_mapper import SessionMapper
from ouroboros.foundation.session_state_helper import SessionStateHelper
from ouroboros.subsystems.browser.models import BrowserSessionState
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


@dataclass
class BrowserSession:
    """
    Fully isolated browser session for a single conversation/workflow.

    Each session maintains its own Playwright instance and browser process,
    providing complete isolation from other concurrent sessions.

    Architecture:
        Per-session browser (not shared):
        - Each session has own Playwright + Chromium process
        - Simpler cleanup (kill process)
        - Better fault isolation (crash doesn't affect other sessions)
        - Developer experience > memory efficiency (~100MB per session)

    Attributes:
        playwright (Any): Playwright instance (per session)
        browser (Browser): Chromium browser process (per session)
        page (Page): Primary page within the browser
        created_at (float): Unix timestamp of session creation
        last_access (float): Unix timestamp of last activity (auto-updated)
        browser_type (str): Browser type (chromium/firefox/webkit)
        headless (bool): Whether browser is running in headless mode
        tabs (Dict[str, Page]): Additional tabs/pages by ID

    Example:
        >>> session = BrowserSession(
        ...     playwright=pw,
        ...     browser=browser,
        ...     page=page,
        ...     created_at=time.time(),
        ...     browser_type="chromium",
        ...     headless=True
        ... )
        >>> await session.page.goto("https://example.com")
        >>> await session.cleanup()

    Traceability:
        FR-021: Isolated Playwright Sessions (per-session isolation)
        FR-022: Browser Actions (tab management)
        NFR-M4: Subsystem Isolation (fault isolation)
    """

    playwright: Any  # Playwright instance (per session)
    browser: Browser  # Chromium process (per session)
    page: Page  # Primary page within browser
    created_at: float
    last_access: float = field(default_factory=time.time)
    browser_type: str = "chromium"  # Browser type (chromium/firefox/webkit)
    headless: bool = True  # Headless mode
    tabs: Dict[str, Page] = field(default_factory=dict)  # Additional tabs by ID

    async def cleanup(self) -> None:
        """
        Release all resources and terminate browser process.

        Closes page, all tabs, browser, and stops Playwright instance. This method
        is best-effort and will not raise exceptions on cleanup failures.

        Cleanup order:
            1. Close all tabs (additional pages)
            2. Close primary page (DOM cleanup)
            3. Close browser (process termination)
            4. Stop Playwright (API cleanup)

        Raises:
            No exceptions - logs warnings on cleanup errors

        Traceability:
            FR-022: Browser Actions (resource cleanup)
            NFR-M4: Subsystem Isolation (no zombie processes)
        """
        # Close all tabs first
        for tab_id, tab_page in list(self.tabs.items()):
            try:
                await tab_page.close()
                logger.debug("Tab %s closed successfully", tab_id)
            except Exception as e:
                logger.warning("Tab %s close error: %s", tab_id, e)
        self.tabs.clear()

        # Close primary page
        try:
            await self.page.close()
            logger.debug("Primary page closed successfully")
        except Exception as e:
            logger.warning("Primary page close error: %s", e)

        # Close browser process
        try:
            await self.browser.close()
            logger.debug("Browser process terminated")
        except Exception as e:
            logger.warning("Browser close error: %s", e)

        # Stop Playwright instance
        try:
            await self.playwright.stop()
            logger.debug("Playwright instance stopped")
        except Exception as e:
            logger.warning("Playwright stop error: %s", e)


class BrowserManager:
    """
    Manager for per-session browser processes.

    Manages multiple isolated browser sessions, one per conversation/workflow.
    Each session gets its own Playwright + Chromium process for complete
    fault isolation and simplified cleanup.

    Architecture:
        Per-Session Browsers (Fully Isolated)
        - Manager only tracks sessions dict
        - NO shared browser process
        - Each session creates own browser on first access
        - Lock only protects dict operations (not browser state)

    Concurrency:
        Thread-safe via asyncio.Lock:
        - Lock protects _sessions dict (read/write)
        - No lock on browser operations (isolated per session)
        - Multiple sessions operate independently

    Lifecycle:
        1. Lazy per-session initialization (browser launches on first call)
        2. Sessions auto-cleanup after timeout (from config)
        3. Explicit cleanup via close_session()
        4. Graceful shutdown via shutdown()

    Attributes:
        config: BrowserConfig with settings (timeout, max sessions, browser type)
        _sessions (Dict[str, BrowserSession]): Active sessions by ID
        _lock (asyncio.Lock): Protects session dict operations

    Example:
        >>> config = BrowserConfig(session_timeout_minutes=30)
        >>> manager = BrowserManager(config)
        >>> session = await manager.get_session("browser_chat_123")
        >>> await session.page.goto("https://example.com")
        >>> await manager.close_session("browser_chat_123")
        >>> await manager.shutdown()

    Traceability:
        FR-021: Isolated Playwright Sessions (lifecycle management)
        FR-022: Browser Actions (multi-session support)
        NFR-P1: Cold Start <30s (lazy initialization)
        NFR-M4: Subsystem Isolation (thread safety)
    """

    def __init__(self, config: BrowserConfig, session_mapper: SessionMapper):
        """
        Initialize browser manager with config (no browser launched yet).

        Args:
            config: BrowserConfig with timeout, max sessions, browser type, headless
            session_mapper: SessionMapper for state persistence

        Note:
            No browser is launched during initialization (lazy per-session).
            Each session will launch its own browser on first access.
            SessionMapper persists metadata (last_access for timeout cleanup).

        Traceability:
            NFR-P1: Cold Start <30s (lazy initialization)
        """
        self.config = config
        self._sessions: Dict[str, BrowserSession] = {}  # In-memory browser instances
        self._lock = asyncio.Lock()
        
        # Session state helper (typed persistence for timeout cleanup)
        self._state_helper = SessionStateHelper(
            session_mapper=session_mapper,
            invoker="browser",
            state_model=BrowserSessionState
        )
        
        logger.info(
            "BrowserManager initialized (per-session architecture, "
            "browser=%s, headless=%s, max_sessions=%d, timeout=%dm)",
            config.browser_type,
            config.headless,
            config.max_sessions,
            config.session_timeout_minutes,
        )

    async def get_session(
        self,
        session_id: str,
        browser_type: Optional[str] = None,
        headless: Optional[bool] = None,
    ) -> BrowserSession:
        """
        Get or create isolated browser session (thread-safe).

        Creates new session with own Playwright + browser process if doesn't
        exist. Reuses existing session and updates last_access timestamp if exists.

        Architecture:
            Per-session browser creation:
            - Each new session launches async_playwright().start()
            - Each new session launches playwright.[browser_type].launch()
            - Each session has own browser process (isolated)
            - No shared browser to manage - simpler!

        Args:
            session_id (str): Unique session identifier (from SessionMapper)
            browser_type (str, optional): Browser type override (chromium/firefox/webkit).
                If None, uses config.browser_type.
            headless (bool, optional): Headless mode override.
                If None, uses config.headless.

        Returns:
            BrowserSession: Isolated session with own browser process.

        Raises:
            ActionableError: If browser launch fails or max sessions exceeded.

        Example:
            >>> # Default config settings:
            >>> session = await manager.get_session("browser_client_abc_s0")
            >>> await session.page.goto("https://example.com")
            >>> 
            >>> # Override for cross-browser testing:
            >>> firefox_session = await manager.get_session(
            ...     "browser_client_abc_s1",
            ...     browser_type="firefox"
            ... )

        Concurrency:
            Thread-safe via asyncio.Lock. Multiple calls can run concurrently,
            but only one will create a new session at a time.

        Traceability:
            FR-021: Isolated Playwright Sessions (isolation + reuse)
            FR-022: Browser Actions (cross-browser support)
            NFR-P1: Cold Start (lazy initialization)
            NFR-M4: Subsystem Isolation (thread safety)
        """
        # Use config defaults if not overridden
        browser_type = browser_type or self.config.browser_type
        headless = headless if headless is not None else self.config.headless

        async with self._lock:
            # Cleanup stale sessions first
            await self._cleanup_stale_sessions()

            # Check max sessions limit
            if session_id not in self._sessions and len(self._sessions) >= self.config.max_sessions:
                raise ActionableError(
                    what_failed="Browser session creation",
                    why_failed=f"Maximum concurrent sessions reached ({self.config.max_sessions})",
                    how_to_fix=(
                        "Close unused browser sessions with pos_browser(action='close', session_id='...') "
                        f"or increase max_sessions in config (current: {self.config.max_sessions})"
                    ),
                )

            # Reuse existing session
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.last_access = time.time()
                
                # Update last_access via helper (for timeout cleanup)
                state = BrowserSessionState(
                    session_id=session_id,
                    browser_type=session.browser_type,
                    headless=session.headless,
                    created_at=datetime.fromtimestamp(session.created_at),
                    last_access=datetime.fromtimestamp(session.last_access),
                    tab_ids={tab_id: "active" for tab_id in session.tabs.keys()}
                )
                self._state_helper.save(state, status="active")
                
                logger.debug(
                    "Reusing existing session: %s (%s, headless=%s, total sessions: %s)",
                    session_id,
                    session.browser_type,
                    session.headless,
                    len(self._sessions),
                )
                return session

            # Create new session with own browser process
            try:
                logger.info(
                    "Creating new session: %s (browser=%s, headless=%s)...",
                    session_id,
                    browser_type,
                    headless,
                )

                # Launch Playwright (per session)
                playwright = await async_playwright().start()
                logger.debug("Playwright instance started for %s", session_id)

                # Get browser launcher based on type
                if browser_type == "chromium":
                    launcher = playwright.chromium
                elif browser_type == "firefox":
                    launcher = playwright.firefox
                elif browser_type == "webkit":
                    launcher = playwright.webkit
                else:
                    raise ActionableError(
                        what_failed="Browser type selection",
                        why_failed=f"Invalid browser_type: {browser_type}",
                        how_to_fix="Use 'chromium', 'firefox', or 'webkit' in config or parameter",
                    )

                # Launch browser (per session)
                browser = await launcher.launch(headless=headless)
                logger.debug(
                    "%s browser launched for %s (pid: %s, headless=%s)",
                    browser_type.capitalize(),
                    session_id,
                    browser.process.pid if hasattr(browser, "process") else "unknown",
                    headless,
                )

                if not headless:
                    logger.warning(
                        "⚠️  Session %s running in headful mode. "
                        "Performance may be impacted. Use for debugging only.",
                        session_id,
                    )

                # Create new page
                page = await browser.new_page()
                logger.debug("New page created for %s", session_id)

                # Create session object
                # Note: First tab gets stable UUID like all other tabs
                first_tab_id = f"tab-{uuid.uuid4().hex[:8]}"
                session = BrowserSession(
                    playwright=playwright,
                    browser=browser,
                    page=page,  # session.page tracks the currently active tab
                    created_at=time.time(),
                    browser_type=browser_type,
                    headless=headless,
                    tabs={first_tab_id: page},  # First tab has stable UUID
                )

                # Store session
                self._sessions[session_id] = session
                
                # Persist state via helper (for timeout cleanup)
                state = BrowserSessionState(
                    session_id=session_id,
                    browser_type=browser_type,
                    headless=headless,
                    created_at=datetime.fromtimestamp(session.created_at),
                    last_access=datetime.fromtimestamp(session.created_at),
                    tab_ids={first_tab_id: "initial"}
                )
                self._state_helper.save(state, status="active")
                
                logger.info(
                    "✅ Session created: %s with new %s process (total sessions: %s)",
                    session_id,
                    browser_type,
                    len(self._sessions),
                )

                return session

            except ActionableError:
                # Re-raise our own errors
                raise
            except Exception as e:
                # Wrap other exceptions in ActionableError
                raise ActionableError(
                    what_failed=f"Browser launch for session {session_id}",
                    why_failed=str(e),
                    how_to_fix=(
                        "1. Ensure Playwright installed: pip install playwright\n"
                        f"2. Install {browser_type}: playwright install {browser_type}\n"
                        "3. Check system resources (disk space, memory)\n"
                        "4. Check network connectivity if downloading browser\n"
                        "5. For webkit on Linux: playwright install-deps webkit"
                    ),
                ) from e

    async def _cleanup_stale_sessions(self) -> None:
        """
        Auto-cleanup sessions idle beyond timeout (internal).

        Called automatically by get_session() before creating new sessions.
        Removes and cleans up sessions where (now - last_access) > timeout.

        Note:
            This method must be called within _lock context.
            Cleanup errors are logged but don't stop the cleanup process.

        Traceability:
            FR-022: Browser Actions (resource cleanup)
            NFR-M4: Subsystem Isolation (no zombie processes)
        """
        now = time.time()
        stale_sessions = []
        timeout_seconds = self.config.session_timeout_seconds

        # Identify stale sessions
        for session_id, session in self._sessions.items():
            idle_time = now - session.last_access
            if idle_time > timeout_seconds:
                stale_sessions.append((session_id, idle_time))

        # Cleanup stale sessions
        for session_id, idle_time in stale_sessions:
            try:
                session = self._sessions[session_id]
                await session.cleanup()
                del self._sessions[session_id]
                logger.info(
                    "Cleaned up stale session: %s (idle for %.1fs, timeout: %ds)",
                    session_id,
                    idle_time,
                    timeout_seconds,
                )
            except Exception as e:
                logger.error(
                    "Error cleaning up stale session %s: %s",
                    session_id,
                    e,
                    exc_info=True,
                )
                # Continue cleanup even if one fails
                continue

    async def close_session(self, session_id: str) -> None:
        """
        Explicitly close a session and release resources (thread-safe).

        Closes page, browser, stops Playwright, and removes session from dict.
        Safe to call on non-existent sessions (logs warning, no error).

        Args:
            session_id (str): Session ID to close.

        Example:
            >>> await manager.close_session("browser_chat_123")
            >>> # Session is gone, resources released

        Concurrency:
            Thread-safe via asyncio.Lock.

        Traceability:
            FR-022: Browser Actions (explicit resource cleanup)
            NFR-M4: Subsystem Isolation (no zombie processes)
        """
        async with self._lock:
            if session_id not in self._sessions:
                logger.warning(
                    "close_session called on non-existent session: %s", session_id
                )
                return

            try:
                session = self._sessions[session_id]
                await session.cleanup()
                del self._sessions[session_id]
                
                # Mark as completed via helper
                state = BrowserSessionState(
                    session_id=session_id,
                    browser_type=session.browser_type,
                    headless=session.headless,
                    created_at=datetime.fromtimestamp(session.created_at),
                    last_access=datetime.now(),
                )
                self._state_helper.save(state, status="completed")
                
                logger.info(
                    "Session closed: %s (remaining sessions: %s)",
                    session_id,
                    len(self._sessions),
                )
            except Exception as e:
                logger.error(
                    "Error closing session %s: %s", session_id, e, exc_info=True
                )
                
                # Mark as error via helper (if state exists)
                try:
                    existing_state = self._state_helper.load(session_id)
                    if existing_state:
                        # Add error reason to existing state
                        state_data = existing_state.model_dump()
                        state_data["error_reason"] = f"Cleanup failed: {e}"
                        self._state_helper.session_mapper.save_state(
                            invoker="browser",
                            session_id=session_id,
                            state_data=state_data,
                            status="error"
                        )
                except Exception as save_error:
                    logger.warning("Failed to save error state: %s", save_error)
                
                # Still remove from dict even if cleanup failed
                if session_id in self._sessions:
                    del self._sessions[session_id]
                raise

    async def shutdown(self) -> None:
        """
        Shutdown all sessions and release all resources (graceful).

        Closes all active sessions, releases all browser processes.
        Call on MCP server shutdown or application exit.

        Example:
            >>> await manager.shutdown()
            >>> # All sessions closed, all browsers terminated

        Concurrency:
            Thread-safe via asyncio.Lock.

        Traceability:
            FR-022: Browser Actions (graceful shutdown)
            NFR-M4: Subsystem Isolation (no zombie processes)
        """
        async with self._lock:
            session_count = len(self._sessions)
            logger.info("Shutting down BrowserManager (%s sessions)...", session_count)

            # Close all sessions
            for session_id in list(self._sessions.keys()):
                try:
                    session = self._sessions[session_id]
                    await session.cleanup()
                    logger.debug("Session shut down: %s", session_id)
                except Exception as e:
                    logger.error(
                        "Error shutting down session %s: %s",
                        session_id,
                        e,
                        exc_info=True,
                    )
                    # Continue shutdown even if one fails

            # Clear session dict
            self._sessions.clear()
            logger.info(
                "✅ BrowserManager shutdown complete (%s sessions closed)",
                session_count,
            )
    
    # ========================================================================
    # Playwright Action Methods (FR-022: Browser Actions)
    # ========================================================================
    
    async def navigate(
        self,
        session_id: str,
        url: str,
        wait_until: str = "load",
        timeout: int = 30000,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Navigate to URL."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            await session.page.goto(url, wait_until=wait_until, timeout=timeout)  # type: ignore[arg-type]
            return {"status": "success", "url": url}
        except Exception as e:
            logger.error("Navigation failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def screenshot(
        self,
        session_id: str,
        full_page: bool = False,
        path: Optional[str] = None,
        format: str = "png",
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Take screenshot."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            screenshot_bytes = await session.page.screenshot(
                full_page=full_page,
                path=path,
                type=format  # type: ignore[arg-type]
            )
            
            result: Dict[str, Any] = {"status": "success"}
            if path:
                result["path"] = path
            else:
                result["data"] = screenshot_bytes.decode("latin1") if isinstance(screenshot_bytes, bytes) else screenshot_bytes
            
            return result
        except Exception as e:
            logger.error("Screenshot failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def list_tabs(
        self,
        session_id: str,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """List all tabs in session."""
        session = await self.get_session(session_id, browser_type, headless)
        
        tabs = [
            {"tab_id": "main", "url": session.page.url, "title": await session.page.title()}
        ]
        
        for tab_id, page in session.tabs.items():
            tabs.append({
                "tab_id": tab_id,
                "url": page.url,
                "title": await page.title()
            })
        
        return {"status": "success", "tabs": tabs, "count": len(tabs)}
    
    async def click(
        self,
        session_id: str,
        selector: str,
        button: str = "left",
        click_count: int = 1,
        modifiers: Optional[list] = None,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Click element."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            await session.page.click(
                selector,
                button=button,  # type: ignore[arg-type]
                click_count=click_count,
                modifiers=modifiers or []
            )
            return {"status": "success", "selector": selector}
        except Exception as e:
            logger.error("Click failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def type(
        self,
        session_id: str,
        selector: str,
        text: str,
        modifiers: Optional[list] = None,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Type text into element."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            await session.page.type(selector, text)
            return {"status": "success", "selector": selector, "text": text}
        except Exception as e:
            logger.error("Type failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def fill(
        self,
        session_id: str,
        selector: str,
        value: str,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Fill input field."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            await session.page.fill(selector, value)
            return {"status": "success", "selector": selector, "value": value}
        except Exception as e:
            logger.error("Fill failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def select(
        self,
        session_id: str,
        selector: str,
        value: str,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Select dropdown option."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            await session.page.select_option(selector, value)
            return {"status": "success", "selector": selector, "value": value}
        except Exception as e:
            logger.error("Select failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def wait(
        self,
        session_id: str,
        selector: str,
        state: str = "visible",
        timeout: int = 30000,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Wait for element state."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            await session.page.wait_for_selector(selector, state=state, timeout=timeout)  # type: ignore[arg-type]
            return {"status": "success", "selector": selector, "state": state}
        except Exception as e:
            logger.error("Wait failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def query(
        self,
        session_id: str,
        selector: str,
        query_all: bool = False,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Query elements by selector."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            if query_all:
                elements = await session.page.query_selector_all(selector)
                count = len(elements)
                return {"status": "success", "selector": selector, "count": count}
            else:
                element = await session.page.query_selector(selector)
                found = element is not None
                return {"status": "success", "selector": selector, "found": found}
        except Exception as e:
            logger.error("Query failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def evaluate(
        self,
        session_id: str,
        script: str,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Execute JavaScript."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            result = await session.page.evaluate(script)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error("Evaluate failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def get_cookies(
        self,
        session_id: str,
        cookie_name: Optional[str] = None,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Get cookies."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            cookies = await session.page.context.cookies()
            
            if cookie_name:
                filtered = [c for c in cookies if c["name"] == cookie_name]
                return {"status": "success", "cookies": filtered}
            else:
                return {"status": "success", "cookies": cookies}
        except Exception as e:
            logger.error("Get cookies failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def set_cookies(
        self,
        session_id: str,
        cookies: list,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Set cookies."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            await session.page.context.add_cookies(cookies)
            return {"status": "success", "count": len(cookies)}
        except Exception as e:
            logger.error("Set cookies failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def get_local_storage(
        self,
        session_id: str,
        key: str,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Get local storage item."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            value = await session.page.evaluate(f"localStorage.getItem('{key}')")
            return {"status": "success", "key": key, "value": value}
        except Exception as e:
            logger.error("Get local storage failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def emulate_media(
        self,
        session_id: str,
        color_scheme: Optional[str] = None,
        reduced_motion: Optional[str] = None,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Emulate media features."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            await session.page.emulate_media(
                color_scheme=color_scheme,  # type: ignore[arg-type]
                reduced_motion=reduced_motion  # type: ignore[arg-type]
            )
            return {"status": "success"}
        except Exception as e:
            logger.error("Emulate media failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def set_viewport(
        self,
        session_id: str,
        width: int,
        height: int,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Set viewport size."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            await session.page.set_viewport_size({"width": width, "height": height})
            return {"status": "success", "width": width, "height": height}
        except Exception as e:
            logger.error("Set viewport failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def get_console_messages(
        self,
        session_id: str,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Get console messages (stub)."""
        return {"status": "success", "messages": [], "note": "Console logging not yet implemented"}
    
    async def run_test(
        self,
        session_id: str,
        test_file: str,
        config: Optional[Dict] = None,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Run Playwright test (stub)."""
        return {"status": "error", "error": "run_test not yet implemented"}
    
    async def intercept_network(
        self,
        session_id: str,
        pattern: str,
        handler: Optional[str] = None,
        mock_response: Optional[Dict] = None,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Intercept network requests (stub)."""
        return {"status": "error", "error": "intercept_network not yet implemented"}
    
    async def new_tab(
        self,
        session_id: str,
        url: Optional[str] = None,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Create new tab."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            page = await session.browser.new_page()
            tab_id = f"tab_{len(session.tabs) + 1}"
            session.tabs[tab_id] = page
            
            if url:
                await page.goto(url)
            
            return {"status": "success", "tab_id": tab_id, "url": url}
        except Exception as e:
            logger.error("New tab failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def switch_tab(
        self,
        session_id: str,
        tab_id: str,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Switch to tab."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            if tab_id == "main":
                # Already on main page
                return {"status": "success", "tab_id": tab_id}
            elif tab_id in session.tabs:
                # Switch by making this page the active one
                session.page = session.tabs[tab_id]
                return {"status": "success", "tab_id": tab_id}
            else:
                return {"status": "error", "error": f"Tab not found: {tab_id}"}
        except Exception as e:
            logger.error("Switch tab failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def close_tab(
        self,
        session_id: str,
        tab_id: Optional[str] = None,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Close tab."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            if not tab_id:
                # Close current page
                await session.page.close()
                return {"status": "success", "tab_id": "current"}
            elif tab_id in session.tabs:
                page = session.tabs.pop(tab_id)
                await page.close()
                return {"status": "success", "tab_id": tab_id}
            else:
                return {"status": "error", "error": f"Tab not found: {tab_id}"}
        except Exception as e:
            logger.error("Close tab failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def upload_file(
        self,
        session_id: str,
        selector: str,
        file_path: str,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Upload file to input."""
        session = await self.get_session(session_id, browser_type, headless)
        
        try:
            await session.page.set_input_files(selector, file_path)
            return {"status": "success", "selector": selector, "file_path": file_path}
        except Exception as e:
            logger.error("Upload file failed: %s", e)
            return {"status": "error", "error": str(e)}
    
    async def download_file(
        self,
        session_id: str,
        trigger_selector: str,
        download_path: Optional[str] = None,
        browser_type: str = "chromium",
        headless: bool = True
    ) -> Dict[str, Any]:
        """Download file (stub)."""
        return {"status": "error", "error": "download_file not yet implemented"}


__all__ = ["BrowserSession", "BrowserManager"]

