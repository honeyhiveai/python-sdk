"""
Browser automation manager for Agent OS MCP server.

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
    >>> manager = BrowserManager()
    >>> session = await manager.get_session("chat-123")
    >>> await session.page.goto("https://example.com")
    >>> await manager.close_session("chat-123")

Concurrency:
    - Thread-safe via asyncio.Lock on session dict
    - Each session operates independently
    - No shared browser process

Traceability:
    FR-1, FR-2, NFR-1, NFR-4, NFR-5 (per-session isolation)
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
from typing import Any, Dict, Literal

from playwright.async_api import Browser, Page, async_playwright

logger = logging.getLogger(__name__)


@dataclass
class BrowserSession:
    """
    Fully isolated browser session for a single chat/workflow.

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
        FR-2 (Multi-session support)
        FR-21 (Tab management)
        FR-23 (Cross-browser support)
        FR-24 (Headful mode)
        NFR-5 (Session isolation for AI agent UX)
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
            FR-3 (Resource cleanup)
            FR-21 (Tab cleanup)
            NFR-3 (No zombie processes)
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
    Singleton manager for per-session browser processes.

    Manages multiple isolated browser sessions, one per chat/workflow.
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
        2. Sessions auto-cleanup after timeout (default: 3600s)
        3. Explicit cleanup via close_session()
        4. Graceful shutdown via shutdown()

    Attributes:
        _sessions (Dict[str, BrowserSession]): Active sessions by ID
        _lock (asyncio.Lock): Protects session dict operations
        _session_timeout (int): Idle timeout in seconds (default: 3600)

    Example:
        >>> manager = BrowserManager(session_timeout=3600)
        >>> session = await manager.get_session("chat-123")
        >>> await session.page.goto("https://example.com")
        >>> await manager.close_session("chat-123")
        >>> await manager.shutdown()

    Traceability:
        FR-1 (Browser lifecycle management)
        FR-2 (Multi-session support)
        NFR-1 (Fast startup - no shared browser to initialize)
        NFR-4 (Thread safety)
        NFR-5 (Session isolation)
    """

    def __init__(self, session_timeout: int = 3600):
        """
        Initialize browser manager (no browser launched yet).

        Args:
            session_timeout (int): Session idle timeout in seconds.
                                   Default: 3600 (1 hour).

        Note:
            No browser is launched during initialization (lazy per-session).
            Each session will launch its own browser on first access.

        Traceability:
            NFR-1 (Fast startup)
        """
        self._sessions: Dict[str, BrowserSession] = {}
        self._lock = asyncio.Lock()
        self._session_timeout = session_timeout
        logger.info(
            "BrowserManager initialized (per-session architecture, timeout: %ss)",
            session_timeout,
        )

    async def get_session(
        self,
        session_id: str = "default",
        browser_type: Literal["chromium", "firefox", "webkit"] = "chromium",
        headless: bool = True,
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
            session_id (str): Unique session identifier. Default: "default".
            browser_type (str): Browser type (chromium/firefox/webkit).
                Default: "chromium".
            headless (bool): Run browser in headless mode. Default: True.

        Returns:
            BrowserSession: Isolated session with own browser process.

        Raises:
            RuntimeError: If browser launch fails. Includes remediation message.
            ValueError: If invalid browser_type specified (not chromium/firefox/webkit).

        Example:
            >>> session = await manager.get_session("chat-123")
            >>> await session.page.goto("https://example.com")
            >>> # Later, reuse same session
            >>> session2 = await manager.get_session("chat-123")
            >>> assert session.page is session2.page  # Same page
            >>>
            >>> # Cross-browser testing
            >>> firefox_session = await manager.get_session(
            ...     "test-ff", browser_type="firefox"
            ... )

        Concurrency:
            Thread-safe via asyncio.Lock. Multiple calls can run concurrently,
            but only one will create a new session at a time.

        Traceability:
            FR-2 (Multi-session support)
            FR-23 (Cross-browser support)
            FR-24 (Headful mode)
            NFR-1 (Lazy initialization per session)
            NFR-2 (Session reuse)
            NFR-4 (Thread safety)
            NFR-5 (Full session isolation)
        """
        async with self._lock:
            # Cleanup stale sessions first
            await self._cleanup_stale_sessions()

            # Reuse existing session
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.last_access = time.time()
                logger.debug(
                    "Reusing existing session: %s (%s, headless=%s, "
                    "total sessions: %s)",
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
                    raise ValueError(
                        f"Invalid browser_type: {browser_type}. "
                        f"Must be chromium, firefox, or webkit"
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
                logger.info(
                    "✅ Session created: %s with new %s process (total sessions: %s)",
                    session_id,
                    browser_type,
                    len(self._sessions),
                )

                return session

            except Exception as e:
                error_msg = f"Browser launch failed for session {session_id}: {e}"
                logger.error(error_msg, exc_info=True)
                raise RuntimeError(
                    f"{error_msg}\n"
                    f"Remediation:\n"
                    f"1. Ensure Playwright installed: pip install playwright\n"
                    f"2. Install {browser_type}: playwright install {browser_type}\n"
                    f"3. Check system resources (disk space, memory)\n"
                    f"4. Check network connectivity if downloading browser\n"
                    f"5. For webkit on Linux, install dependencies: "
                    f"playwright install-deps webkit"
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
            FR-3 (Resource cleanup)
            NFR-3 (No zombie processes)
        """
        now = time.time()
        stale_sessions = []

        # Identify stale sessions
        for session_id, session in self._sessions.items():
            idle_time = now - session.last_access
            if idle_time > self._session_timeout:
                stale_sessions.append((session_id, idle_time))

        # Cleanup stale sessions
        for session_id, idle_time in stale_sessions:
            try:
                session = self._sessions[session_id]
                await session.cleanup()
                del self._sessions[session_id]
                logger.info(
                    "Cleaned up stale session: %s (idle for %.1fs)",
                    session_id,
                    idle_time,
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
            >>> await manager.close_session("chat-123")
            >>> # Session is gone, resources released

        Concurrency:
            Thread-safe via asyncio.Lock.

        Traceability:
            FR-3 (Explicit resource cleanup)
            NFR-3 (No zombie processes)
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
                logger.info(
                    "Session closed: %s (remaining sessions: %s)",
                    session_id,
                    len(self._sessions),
                )
            except Exception as e:
                logger.error(
                    "Error closing session %s: %s", session_id, e, exc_info=True
                )
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
            FR-3 (Graceful shutdown)
            NFR-3 (No zombie processes)
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
