"""
Browser automation tools for MCP server.

Provides aos_browser tool for comprehensive Playwright-based browser
automation with per-session isolation for multi-chat safety.

Architecture:
    - Consolidated tool (aos_browser) with action parameter
    - Per-session browser isolation for fault tolerance
    - 30+ actions across 6 categories

Traceability:
    FR-4 through FR-28 (all browser actions)
    NFR-6 (Graceful degradation)
    NFR-7 (Error messages with remediation)
"""

# pylint: disable=too-many-lines,unused-argument
# Justification: Comprehensive browser automation with 30+ actions requires
# 1840 lines - splitting would reduce cohesion of related browser operations
# _handle_console has page parameter for future console message collection

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: aos_browser unified interface accepts 36 parameters to support
# all browser actions (navigation, interaction, inspection, etc.) in one tool

# pylint: disable=too-many-locals
# Justification: aos_browser dispatches to 30+ action handlers, requiring
# local variables for each possible parameter type

# pylint: disable=too-many-return-statements,too-many-branches
# Justification: Action dispatcher pattern requires 26 return paths and
# branches - one for each browser automation action

# pylint: disable=broad-exception-caught
# Justification: Browser automation catches broad exceptions for robustness,
# returning structured error responses instead of crashing

import logging
import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def register_browser_tools(mcp: Any, browser_manager: Any) -> int:
    """
    Register browser automation tools with MCP server.

    Args:
        mcp (Any): FastMCP server instance
        browser_manager (BrowserManager): BrowserManager singleton

    Returns:
        int: Number of tools registered (1 - aos_browser)

    Traceability:
        FR-11 (ServerFactory integration)
        FR-12 (Conditional tool loading)
    """

    @mcp.tool()
    async def aos_browser(
        action: str,
        session_id: Optional[str] = None,
        # Navigation (FR-4)
        url: Optional[str] = None,
        wait_until: str = "load",
        timeout: int = 30000,
        # Media emulation (FR-5)
        color_scheme: Optional[str] = None,
        reduced_motion: Optional[str] = None,
        # Screenshot (FR-6)
        screenshot_full_page: bool = False,
        screenshot_path: Optional[str] = None,
        screenshot_format: str = "png",
        # Viewport (FR-7) - Using Any to work around MCP number vs integer issue
        viewport_width: Any = None,
        viewport_height: Any = None,
        # Element interaction (FR-9 through FR-12)
        selector: Optional[str] = None,
        text: Optional[str] = None,
        value: Optional[str] = None,
        button: str = "left",
        click_count: int = 1,
        modifiers: Optional[List[str]] = None,
        # Waiting/assertions (FR-13)
        wait_for_state: str = "visible",
        wait_for_timeout: int = 30000,
        # Query (FR-14)
        query_all: bool = False,
        # JavaScript (FR-15)
        script: Optional[str] = None,
        # Cookies (FR-16, FR-17)
        cookies: Optional[List[Dict[str, Any]]] = None,
        cookie_name: Optional[str] = None,
        # Storage (FR-18)
        storage_key: Optional[str] = None,
        # Test execution (FR-19)
        test_file: Optional[str] = None,
        test_config: Optional[Dict[str, Any]] = None,
        # Network interception (FR-20)
        route_pattern: Optional[str] = None,
        route_handler: Optional[str] = None,  # 'block', 'mock', or 'continue'
        mock_response: Optional[Dict[str, Any]] = None,
        # Tab management (FR-21)
        tab_id: Optional[str] = None,
        new_tab_url: Optional[str] = None,
        # File I/O (FR-22)
        file_path: Optional[str] = None,
        download_trigger_selector: Optional[str] = None,
        # Browser type (FR-23)
        browser_type: str = "chromium",
        # Headless mode (FR-24)
        headless: bool = True,
    ) -> Dict[str, Any]:
        """
        Browser automation tool with comprehensive Playwright capabilities.

        Provides browser control with persistent sessions across calls.
        Each session ID gets isolated browser process for multi-chat safety.

        Actions:
            Navigation:
                - navigate: Navigate to URL (FR-4)

            Inspection:
                - screenshot: Capture page screenshot (FR-6)
                - console: Get console messages (stub)
                - query: Query elements by selector (FR-14)
                - evaluate: Execute JavaScript (FR-15)
                - get_cookies: Get all cookies (FR-16)
                - get_local_storage: Get local storage item (FR-18)

            Interaction:
                - click: Click element (FR-9)
                - type: Type text with keyboard (FR-10)
                - fill: Fill input field (FR-11)
                - select: Select dropdown option (FR-12)

            Waiting:
                - wait: Wait for element state (FR-13)

            Context:
                - emulate_media: Set color scheme/media features (FR-5)
                - viewport: Resize browser viewport (FR-7)
                - set_cookies: Set cookies (FR-17)

            Advanced:
                - run_test: Execute Playwright test script (FR-19)
                - intercept_network: Intercept/mock network requests (FR-20)
                - new_tab: Create new tab (FR-21)
                - switch_tab: Switch to tab by ID (FR-21)
                - close_tab: Close tab by ID (FR-21)
                - list_tabs: List all tabs (FR-21)
                - upload_file: Upload file to input (FR-22)
                - download_file: Download file from page (FR-22)

            Session:
                - close: Close session and release resources (FR-3)

        Args:
            action (str): Action to perform (required)
            session_id (str, optional): Session identifier for isolation
            url (str, optional): Target URL (for navigate)
            wait_until (str): Wait condition (load/domcontentloaded/networkidle)
            timeout (int): Navigation timeout in milliseconds
            color_scheme (str, optional): Color scheme (light/dark/no-preference)
            reduced_motion (str, optional): Reduced motion (reduce/no-preference)
            screenshot_full_page (bool): Capture full scrollable page
            screenshot_path (str, optional): File path to save screenshot
            screenshot_format (str): Image format (png/jpeg)
            viewport_width (int, optional): Viewport width in pixels
            viewport_height (int, optional): Viewport height in pixels
            selector (str, optional): CSS/XPath selector
            text (str, optional): Text to type
            value (str, optional): Value to fill/select
            button (str): Mouse button (left/right/middle)
            click_count (int): Number of clicks (1-3)
            modifiers (List[str], optional): Keyboard modifiers
                (Alt, Control, Meta, Shift)
            wait_for_state (str): State to wait for
                (visible/hidden/attached/detached)
            wait_for_timeout (int): Wait timeout in milliseconds
            query_all (bool): Return all matching elements (vs first)
            script (str, optional): JavaScript to execute
            cookies (List[Dict], optional): Cookies to set
            cookie_name (str, optional): Cookie name to get
            storage_key (str, optional): Local storage key
            test_file (str, optional): Path to Playwright test file
            test_config (Dict, optional): Test configuration
            route_pattern (str, optional): URL pattern to intercept
            route_handler (str, optional): How to handle route (block/mock/continue)
            mock_response (Dict, optional): Mock response data
            tab_id (str, optional): Tab identifier
            new_tab_url (str, optional): URL for new tab
            file_path (str, optional): Path to file for upload/download
            download_trigger_selector (str, optional): Selector to trigger download
            browser_type (str): Browser type (chromium/firefox/webkit)
            headless (bool): Run browser in headless mode

        Returns:
            Dict[str, Any]: Action-specific result dictionary with status,
                           session_id, and data

        Examples:
            >>> # Navigate and test dark mode
            >>> aos_browser(action="navigate", url="http://localhost:3000",
            ...             session_id="test-1")
            >>> aos_browser(action="emulate_media", color_scheme="dark",
            ...             session_id="test-1")
            >>> aos_browser(action="screenshot",
            ...             screenshot_path="/tmp/dark.png", session_id="test-1")
            >>> aos_browser(action="close", session_id="test-1")
            >>>
            >>> # Click and type
            >>> aos_browser(action="click", selector="#login-button",
            ...             session_id="test-2")
            >>> aos_browser(action="type", selector="#username",
            ...             text="user@example.com", session_id="test-2")
            >>> aos_browser(action="fill", selector="#password",
            ...             value="secret", session_id="test-2")

        Raises:
            ValueError: If required parameters missing for action
            RuntimeError: If browser operation fails

        Traceability:
            FR-4 through FR-28 (all browser actions)
            NFR-6 (Graceful degradation)
            NFR-7 (Error messages with remediation)
        """
        try:
            sid = session_id or "default"

            # DEBUG: Log all parameters with types
            logger.debug(
                "aos_browser called: action=%s, viewport_width=%s (type=%s), "
                "viewport_height=%s (type=%s)",
                action,
                viewport_width,
                type(viewport_width).__name__,
                viewport_height,
                type(viewport_height).__name__,
            )

            # Handle close action (doesn't need session)
            if action == "close":
                await browser_manager.close_session(sid)
                return {
                    "status": "success",
                    "action": "close",
                    "session_id": sid,
                    "message": "Session closed successfully",
                }

            # Get or create session for all other actions
            # (with browser type and headless mode)
            session = await browser_manager.get_session(
                sid, browser_type=browser_type, headless=headless
            )
            page = session.page

            # ===== NAVIGATION ACTIONS =====
            if action == "navigate":
                return await _handle_navigate(page, sid, url, wait_until, timeout)

            # ===== CONTEXT ACTIONS =====
            if action == "emulate_media":
                return await _handle_emulate_media(
                    page, sid, color_scheme, reduced_motion
                )

            if action == "viewport":
                return await _handle_viewport(
                    page, sid, viewport_width, viewport_height
                )

            # ===== INSPECTION ACTIONS =====
            if action == "screenshot":
                return await _handle_screenshot(
                    page,
                    sid,
                    screenshot_full_page,
                    screenshot_path,
                    screenshot_format,
                )

            if action == "console":
                return await _handle_console(page, sid)

            if action == "query":
                return await _handle_query(page, sid, selector, query_all)

            if action == "evaluate":
                return await _handle_evaluate(page, sid, script)

            if action == "get_cookies":
                return await _handle_get_cookies(page, sid, cookie_name)

            if action == "get_local_storage":
                return await _handle_get_local_storage(page, sid, storage_key)

            # ===== INTERACTION ACTIONS =====
            if action == "click":
                return await _handle_click(
                    page, sid, selector, button, click_count, modifiers, timeout
                )

            if action == "type":
                return await _handle_type(page, sid, selector, text, timeout)

            if action == "fill":
                return await _handle_fill(page, sid, selector, value, timeout)

            if action == "select":
                return await _handle_select(page, sid, selector, value, timeout)

            # ===== WAITING ACTIONS =====
            if action == "wait":
                return await _handle_wait(
                    page, sid, selector, wait_for_state, wait_for_timeout
                )

            # ===== COOKIES/STORAGE ACTIONS =====
            if action == "set_cookies":
                return await _handle_set_cookies(page, sid, cookies)

            # ===== ADVANCED ACTIONS =====
            if action == "run_test":
                return await _handle_run_test(sid, test_file, test_config)

            if action == "intercept_network":
                return await _handle_intercept_network(
                    page, sid, route_pattern, route_handler, mock_response
                )

            if action == "new_tab":
                return await _handle_new_tab(session, sid, new_tab_url)

            if action == "switch_tab":
                return await _handle_switch_tab(session, sid, tab_id)

            if action == "close_tab":
                return await _handle_close_tab(session, sid, tab_id)

            if action == "list_tabs":
                return await _handle_list_tabs(session, sid)

            if action == "upload_file":
                return await _handle_upload_file(page, sid, selector, file_path)

            if action == "download_file":
                return await _handle_download_file(
                    page, sid, download_trigger_selector, file_path
                )

            # Unknown action
            return {
                "status": "error",
                "error": f"Unknown action: {action}",
                "valid_actions": [
                    "navigate",
                    "emulate_media",
                    "viewport",
                    "screenshot",
                    "console",
                    "query",
                    "evaluate",
                    "get_cookies",
                    "set_cookies",
                    "get_local_storage",
                    "click",
                    "type",
                    "fill",
                    "select",
                    "wait",
                    "run_test",
                    "intercept_network",
                    "new_tab",
                    "switch_tab",
                    "close_tab",
                    "list_tabs",
                    "upload_file",
                    "download_file",
                    "close",
                ],
            }

        except Exception as e:
            logger.error("aos_browser action '%s' failed: %s", action, e, exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "action": action,
                "session_id": sid if "sid" in locals() else session_id,
            }

    logger.info("✅ Registered 1 browser tool (aos_browser)")
    return 1


# ===== ACTION HANDLERS =====


async def _handle_navigate(
    page: Any, session_id: str, url: Optional[str], wait_until: str, timeout: int
) -> Dict[str, Any]:
    """
    Handle navigate action (FR-4).

    Args:
        page: Playwright Page
        session_id: Session ID
        url: Target URL
        wait_until: Wait condition
        timeout: Timeout in milliseconds

    Returns:
        Dict with status and page metadata

    Traceability:
        FR-4 (Page navigation)
    """
    if not url:
        return {
            "status": "error",
            "error": "Missing required parameter: url",
            "action": "navigate",
            "session_id": session_id,
            "remediation": (
                "Provide url parameter, e.g., "
                "aos_browser(action='navigate', url='https://example.com')"
            ),
        }

    try:
        response = await page.goto(url, wait_until=wait_until, timeout=timeout)
        title = await page.title()
        current_url = page.url

        return {
            "status": "success",
            "action": "navigate",
            "session_id": session_id,
            "url": current_url,
            "title": title,
            "status_code": response.status if response else None,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Navigation failed: {e}",
            "action": "navigate",
            "session_id": session_id,
            "url": url,
            "remediation": (
                "Check URL is valid, increase timeout parameter, "
                "or check network connectivity"
            ),
        }


async def _handle_emulate_media(
    page: Any,
    session_id: str,
    color_scheme: Optional[str],
    reduced_motion: Optional[str],
) -> Dict[str, Any]:
    """
    Handle emulate_media action (FR-5).

    Args:
        page: Playwright Page
        session_id: Session ID
        color_scheme: Color scheme (light/dark/no-preference)
        reduced_motion: Reduced motion (reduce/no-preference)

    Returns:
        Dict with status and applied settings

    Traceability:
        FR-5 (Media emulation for dark mode testing)
    """
    if not color_scheme and not reduced_motion:
        return {
            "status": "error",
            "error": "Missing required parameter: color_scheme or reduced_motion",
            "action": "emulate_media",
            "session_id": session_id,
            "remediation": (
                "Provide at least one of: color_scheme='dark', "
                "reduced_motion='reduce'"
            ),
        }

    try:
        await page.emulate_media(
            color_scheme=color_scheme, reduced_motion=reduced_motion
        )
        return {
            "status": "success",
            "action": "emulate_media",
            "session_id": session_id,
            "color_scheme": color_scheme,
            "reduced_motion": reduced_motion,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Media emulation failed: {e}",
            "action": "emulate_media",
            "session_id": session_id,
            "remediation": "Check color_scheme is 'light', 'dark', or 'no-preference'",
        }


async def _handle_screenshot(
    page: Any,
    session_id: str,
    full_page: bool,
    path: Optional[str],
    img_format: str,
) -> Dict[str, Any]:
    """
    Handle screenshot action (FR-6).

    Args:
        page: Playwright Page
        session_id: Session ID
        full_page: Capture full scrollable page
        path: File path to save screenshot
        img_format: Image format (png/jpeg)

    Returns:
        Dict with status and screenshot metadata

    Traceability:
        FR-6 (Screenshot capture for visual validation)
    """
    try:
        # Validate path if provided
        if path:
            screenshot_path = Path(path)
            # Ensure parent directory exists
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)

        screenshot_bytes = await page.screenshot(
            full_page=full_page, path=path, type=img_format
        )

        return {
            "status": "success",
            "action": "screenshot",
            "session_id": session_id,
            "path": path,
            "format": img_format,
            "full_page": full_page,
            "size_bytes": len(screenshot_bytes),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Screenshot failed: {e}",
            "action": "screenshot",
            "session_id": session_id,
            "remediation": (
                "Check path is writable, format is 'png' or 'jpeg', "
                "and page is loaded"
            ),
        }


async def _handle_viewport(
    page: Any, session_id: str, width: Any, height: Any
) -> Dict[str, Any]:
    """
    Handle viewport action (FR-7).

    Args:
        page: Playwright Page
        session_id: Session ID
        width: Viewport width in pixels
        height: Viewport height in pixels

    Returns:
        Dict with status and viewport dimensions

    Traceability:
        FR-7 (Viewport control for responsive testing)
    """
    # Convert to int (handles both int and float from JSON)
    try:
        width_int = int(width) if width is not None else None
        height_int = int(height) if height is not None else None
    except (ValueError, TypeError):
        return {
            "status": "error",
            "error": f"Invalid viewport dimensions: width={width}, height={height}",
            "action": "viewport",
            "session_id": session_id,
            "remediation": (
                "Provide numeric viewport_width and viewport_height in pixels"
            ),
        }

    if not width_int or not height_int:
        return {
            "status": "error",
            "error": "Missing required parameters: viewport_width and viewport_height",
            "action": "viewport",
            "session_id": session_id,
            "remediation": (
                "Provide both viewport_width and viewport_height in pixels, "
                "e.g., viewport_width=1920, viewport_height=1080"
            ),
        }

    try:
        await page.set_viewport_size({"width": width_int, "height": height_int})
        return {
            "status": "success",
            "action": "viewport",
            "session_id": session_id,
            "width": width_int,
            "height": height_int,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Viewport resize failed: {e}",
            "action": "viewport",
            "session_id": session_id,
            "remediation": "Check width and height are positive integers",
        }


async def _handle_console(
    page: Any, session_id: str
) -> Dict[str, Any]:  # pylint: disable=unused-argument
    """
    Handle console action (FR-8, stub for now).

    Args:
        page: Playwright Page
        session_id: Session ID

    Returns:
        Dict with status and console messages (stub)

    Traceability:
        FR-8 (Console messages - Phase 2 feature)
    """
    return {
        "status": "success",
        "action": "console",
        "session_id": session_id,
        "messages": [],
        "note": "Console capture not yet implemented (Phase 2 feature)",
    }


async def _handle_query(
    page: Any, session_id: str, selector: Optional[str], query_all: bool
) -> Dict[str, Any]:
    """
    Handle query action (FR-14).

    Args:
        page: Playwright Page
        session_id: Session ID
        selector: CSS/XPath selector
        query_all: Return all matching elements

    Returns:
        Dict with status and element data

    Traceability:
        FR-14 (Query elements by selector)
    """
    if not selector:
        return {
            "status": "error",
            "error": "Missing required parameter: selector",
            "action": "query",
            "session_id": session_id,
            "remediation": "Provide selector parameter, e.g., selector='#login-button'",
        }

    try:
        if query_all:
            elements = await page.query_selector_all(selector)
            count = len(elements)
            texts = [await el.text_content() for el in elements]
            return {
                "status": "success",
                "action": "query",
                "session_id": session_id,
                "selector": selector,
                "count": count,
                "texts": texts,
            }

        element = await page.query_selector(selector)
        if element:
            text = await element.text_content()
            is_visible = await element.is_visible()
            return {
                "status": "success",
                "action": "query",
                "session_id": session_id,
                "selector": selector,
                "found": True,
                "text": text,
                "visible": is_visible,
            }

        return {
            "status": "success",
            "action": "query",
            "session_id": session_id,
            "selector": selector,
            "found": False,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Query failed: {e}",
            "action": "query",
            "session_id": session_id,
            "selector": selector,
            "remediation": "Check selector syntax is valid CSS or XPath",
        }


async def _handle_evaluate(
    page: Any, session_id: str, script: Optional[str]
) -> Dict[str, Any]:
    """
    Handle evaluate action (FR-15).

    Args:
        page: Playwright Page
        session_id: Session ID
        script: JavaScript to execute

    Returns:
        Dict with status and evaluation result

    Traceability:
        FR-15 (JavaScript execution)
    """
    if not script:
        return {
            "status": "error",
            "error": "Missing required parameter: script",
            "action": "evaluate",
            "session_id": session_id,
            "remediation": "Provide script parameter, e.g., script='document.title'",
        }

    try:
        result = await page.evaluate(script)
        return {
            "status": "success",
            "action": "evaluate",
            "session_id": session_id,
            "script": script,
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"JavaScript evaluation failed: {e}",
            "action": "evaluate",
            "session_id": session_id,
            "script": script,
            "remediation": "Check JavaScript syntax is valid",
        }


async def _handle_get_cookies(
    page: Any, session_id: str, cookie_name: Optional[str]
) -> Dict[str, Any]:
    """
    Handle get_cookies action (FR-16).

    Args:
        page: Playwright Page
        session_id: Session ID
        cookie_name: Specific cookie name (optional)

    Returns:
        Dict with status and cookies

    Traceability:
        FR-16 (Get cookies)
    """
    try:
        cookies = await page.context.cookies()

        if cookie_name:
            cookie = next((c for c in cookies if c["name"] == cookie_name), None)
            if cookie:
                return {
                    "status": "success",
                    "action": "get_cookies",
                    "session_id": session_id,
                    "cookie_name": cookie_name,
                    "cookie": cookie,
                }

            return {
                "status": "success",
                "action": "get_cookies",
                "session_id": session_id,
                "cookie_name": cookie_name,
                "found": False,
            }

        return {
            "status": "success",
            "action": "get_cookies",
            "session_id": session_id,
            "cookies": cookies,
            "count": len(cookies),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Get cookies failed: {e}",
            "action": "get_cookies",
            "session_id": session_id,
            "remediation": "Ensure page is loaded and context is accessible",
        }


async def _handle_set_cookies(
    page: Any, session_id: str, cookies: Optional[List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Handle set_cookies action (FR-17).

    Args:
        page: Playwright Page
        session_id: Session ID
        cookies: List of cookie dictionaries

    Returns:
        Dict with status

    Traceability:
        FR-17 (Set cookies)
    """
    if not cookies:
        return {
            "status": "error",
            "error": "Missing required parameter: cookies",
            "action": "set_cookies",
            "session_id": session_id,
            "remediation": (
                "Provide cookies parameter as list of dicts, e.g., "
                "cookies=[{'name': 'session', 'value': 'abc123', "
                "'domain': '.example.com'}]"
            ),
        }

    try:
        await page.context.add_cookies(cookies)
        return {
            "status": "success",
            "action": "set_cookies",
            "session_id": session_id,
            "cookies_set": len(cookies),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Set cookies failed: {e}",
            "action": "set_cookies",
            "session_id": session_id,
            "remediation": "Check cookie format (name, value, domain required)",
        }


async def _handle_get_local_storage(
    page: Any, session_id: str, key: Optional[str]
) -> Dict[str, Any]:
    """
    Handle get_local_storage action (FR-18).

    Args:
        page: Playwright Page
        session_id: Session ID
        key: Local storage key

    Returns:
        Dict with status and value

    Traceability:
        FR-18 (Get local storage)
    """
    if not key:
        return {
            "status": "error",
            "error": "Missing required parameter: storage_key",
            "action": "get_local_storage",
            "session_id": session_id,
            "remediation": "Provide storage_key parameter, e.g., storage_key='theme'",
        }

    try:
        value = await page.evaluate(f"localStorage.getItem('{key}')")
        return {
            "status": "success",
            "action": "get_local_storage",
            "session_id": session_id,
            "key": key,
            "value": value,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Get local storage failed: {e}",
            "action": "get_local_storage",
            "session_id": session_id,
            "key": key,
            "remediation": "Ensure page is loaded and has local storage access",
        }


async def _handle_click(
    page: Any,
    session_id: str,
    selector: Optional[str],
    button: str,
    click_count: int,
    modifiers: Optional[List[str]],
    timeout: int,
) -> Dict[str, Any]:
    """
    Handle click action (FR-9).

    Args:
        page: Playwright Page
        session_id: Session ID
        selector: CSS/XPath selector
        button: Mouse button
        click_count: Number of clicks
        modifiers: Keyboard modifiers
        timeout: Timeout in milliseconds

    Returns:
        Dict with status

    Traceability:
        FR-9 (Click element)
    """
    if not selector:
        return {
            "status": "error",
            "error": "Missing required parameter: selector",
            "action": "click",
            "session_id": session_id,
            "remediation": "Provide selector parameter, e.g., selector='#login-button'",
        }

    try:
        await page.click(
            selector,
            button=button,
            click_count=click_count,
            modifiers=modifiers or [],
            timeout=timeout,
        )
        return {
            "status": "success",
            "action": "click",
            "session_id": session_id,
            "selector": selector,
            "button": button,
            "click_count": click_count,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Click failed: {e}",
            "action": "click",
            "session_id": session_id,
            "selector": selector,
            "remediation": (
                "Check selector exists, element is visible and clickable, "
                "or increase timeout"
            ),
        }


async def _handle_type(
    page: Any,
    session_id: str,
    selector: Optional[str],
    text: Optional[str],
    timeout: int,
) -> Dict[str, Any]:
    """
    Handle type action (FR-10).

    Args:
        page: Playwright Page
        session_id: Session ID
        selector: CSS/XPath selector
        text: Text to type
        timeout: Timeout in milliseconds

    Returns:
        Dict with status

    Traceability:
        FR-10 (Type text)
    """
    if not selector:
        return {
            "status": "error",
            "error": "Missing required parameter: selector",
            "action": "type",
            "session_id": session_id,
            "remediation": "Provide selector parameter, e.g., selector='#username'",
        }

    if not text:
        return {
            "status": "error",
            "error": "Missing required parameter: text",
            "action": "type",
            "session_id": session_id,
            "remediation": "Provide text parameter, e.g., text='user@example.com'",
        }

    try:
        await page.type(selector, text, timeout=timeout)
        return {
            "status": "success",
            "action": "type",
            "session_id": session_id,
            "selector": selector,
            "text": text,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Type failed: {e}",
            "action": "type",
            "session_id": session_id,
            "selector": selector,
            "remediation": (
                "Check selector exists, element is visible and focused, "
                "or increase timeout"
            ),
        }


async def _handle_fill(
    page: Any,
    session_id: str,
    selector: Optional[str],
    value: Optional[str],
    timeout: int,
) -> Dict[str, Any]:
    """
    Handle fill action (FR-11).

    Args:
        page: Playwright Page
        session_id: Session ID
        selector: CSS/XPath selector
        value: Value to fill
        timeout: Timeout in milliseconds

    Returns:
        Dict with status

    Traceability:
        FR-11 (Fill input)
    """
    if not selector:
        return {
            "status": "error",
            "error": "Missing required parameter: selector",
            "action": "fill",
            "session_id": session_id,
            "remediation": "Provide selector parameter, e.g., selector='#password'",
        }

    if not value:
        return {
            "status": "error",
            "error": "Missing required parameter: value",
            "action": "fill",
            "session_id": session_id,
            "remediation": "Provide value parameter, e.g., value='secret123'",
        }

    try:
        await page.fill(selector, value, timeout=timeout)
        return {
            "status": "success",
            "action": "fill",
            "session_id": session_id,
            "selector": selector,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Fill failed: {e}",
            "action": "fill",
            "session_id": session_id,
            "selector": selector,
            "remediation": (
                "Check selector exists, element is an input/textarea, "
                "or increase timeout"
            ),
        }


async def _handle_select(
    page: Any,
    session_id: str,
    selector: Optional[str],
    value: Optional[str],
    timeout: int,
) -> Dict[str, Any]:
    """
    Handle select action (FR-12).

    Args:
        page: Playwright Page
        session_id: Session ID
        selector: CSS/XPath selector
        value: Option value to select
        timeout: Timeout in milliseconds

    Returns:
        Dict with status

    Traceability:
        FR-12 (Select dropdown option)
    """
    if not selector:
        return {
            "status": "error",
            "error": "Missing required parameter: selector",
            "action": "select",
            "session_id": session_id,
            "remediation": "Provide selector parameter, e.g., selector='#country'",
        }

    if not value:
        return {
            "status": "error",
            "error": "Missing required parameter: value",
            "action": "select",
            "session_id": session_id,
            "remediation": "Provide value parameter, e.g., value='USA'",
        }

    try:
        await page.select_option(selector, value, timeout=timeout)
        return {
            "status": "success",
            "action": "select",
            "session_id": session_id,
            "selector": selector,
            "value": value,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Select failed: {e}",
            "action": "select",
            "session_id": session_id,
            "selector": selector,
            "remediation": (
                "Check selector exists, element is a <select>, "
                "option value exists, or increase timeout"
            ),
        }


async def _handle_wait(
    page: Any,
    session_id: str,
    selector: Optional[str],
    state: str,
    timeout: int,
) -> Dict[str, Any]:
    """
    Handle wait action (FR-13).

    Args:
        page: Playwright Page
        session_id: Session ID
        selector: CSS/XPath selector
        state: State to wait for (visible/hidden/attached/detached)
        timeout: Timeout in milliseconds

    Returns:
        Dict with status

    Traceability:
        FR-13 (Wait for element state)
    """
    if not selector:
        return {
            "status": "error",
            "error": "Missing required parameter: selector",
            "action": "wait",
            "session_id": session_id,
            "remediation": (
                "Provide selector parameter, e.g., selector='#loading-spinner'"
            ),
        }

    try:
        await page.wait_for_selector(selector, state=state, timeout=timeout)
        return {
            "status": "success",
            "action": "wait",
            "session_id": session_id,
            "selector": selector,
            "state": state,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Wait failed: {e}",
            "action": "wait",
            "session_id": session_id,
            "selector": selector,
            "state": state,
            "remediation": (
                "Check selector is valid, increase timeout, "
                "or verify element reaches expected state"
            ),
        }


# ===== PHASE 5: ADVANCED ACTION HANDLERS =====


async def _handle_run_test(
    session_id: str,
    test_file: Optional[str],
    test_config: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Handle run_test action (FR-19).

    Args:
        session_id: Session ID
        test_file: Path to Playwright test file
        test_config: Test configuration

    Returns:
        Dict with status and test results

    Traceability:
        FR-19 (Test script execution)
    """
    if not test_file:
        return {
            "status": "error",
            "error": "Missing required parameter: test_file",
            "action": "run_test",
            "session_id": session_id,
            "remediation": (
                "Provide test_file parameter, "
                "e.g., test_file='tests/example.spec.ts'"
            ),
        }

    try:
        # Build test command
        cmd = ["npx", "playwright", "test", test_file]

        # Add config options
        if test_config:
            if test_config.get("headed"):
                cmd.append("--headed")
            if test_config.get("project"):
                cmd.extend(["--project", test_config["project"]])
            if test_config.get("reporter"):
                cmd.extend(["--reporter", test_config["reporter"]])

        # Execute test
        logger.info("Running test: %s", " ".join(cmd))
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            check=False,
        )

        return {
            "status": "success" if result.returncode == 0 else "failed",
            "action": "run_test",
            "session_id": session_id,
            "test_file": test_file,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": "Test execution timed out (5 minutes)",
            "action": "run_test",
            "session_id": session_id,
            "test_file": test_file,
            "remediation": (
                "Check test file for infinite loops or reduce test complexity"
            ),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Test execution failed: {e}",
            "action": "run_test",
            "session_id": session_id,
            "test_file": test_file,
            "remediation": (
                "Ensure Playwright is installed "
                "(npm install -D @playwright/test) and test file exists"
            ),
        }


async def _handle_intercept_network(
    page: Any,
    session_id: str,
    pattern: Optional[str],
    handler: Optional[str],
    mock_response: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Handle intercept_network action (FR-20).

    Args:
        page: Playwright Page
        session_id: Session ID
        pattern: URL pattern to intercept
        handler: How to handle route (block/mock/continue)
        mock_response: Mock response data

    Returns:
        Dict with status and interception info

    Traceability:
        FR-20 (Network interception)
    """
    if not pattern:
        return {
            "status": "error",
            "error": "Missing required parameter: route_pattern",
            "action": "intercept_network",
            "session_id": session_id,
            "remediation": (
                "Provide route_pattern parameter, e.g., route_pattern='**/api/**'"
            ),
        }

    if not handler:
        return {
            "status": "error",
            "error": "Missing required parameter: route_handler",
            "action": "intercept_network",
            "session_id": session_id,
            "remediation": (
                "Provide route_handler parameter, "
                "e.g., route_handler='block' or 'mock'"
            ),
        }

    try:
        # Create route handler based on type
        if handler == "block":
            await page.route(pattern, lambda route: route.abort())
            return {
                "status": "success",
                "action": "intercept_network",
                "session_id": session_id,
                "pattern": pattern,
                "handler": "block",
                "message": f"Blocking all requests matching: {pattern}",
            }

        if handler == "mock":
            if not mock_response:
                return {
                    "status": "error",
                    "error": "Missing mock_response for mock handler",
                    "action": "intercept_network",
                    "session_id": session_id,
                    "remediation": (
                        "Provide mock_response parameter with status, "
                        "contentType, and body"
                    ),
                }

            async def mock_handler(route):
                await route.fulfill(
                    status=mock_response.get("status", 200),
                    content_type=mock_response.get("contentType", "application/json"),
                    body=mock_response.get("body", "{}"),
                )

            await page.route(pattern, mock_handler)
            return {
                "status": "success",
                "action": "intercept_network",
                "session_id": session_id,
                "pattern": pattern,
                "handler": "mock",
                "mock_response": mock_response,
                "message": f"Mocking requests matching: {pattern}",
            }

        if handler == "continue":
            await page.route(pattern, lambda route: route.continue_())
            return {
                "status": "success",
                "action": "intercept_network",
                "session_id": session_id,
                "pattern": pattern,
                "handler": "continue",
                "message": f"Continuing requests matching: {pattern}",
            }

        return {
            "status": "error",
            "error": f"Invalid route_handler: {handler}",
            "action": "intercept_network",
            "session_id": session_id,
            "remediation": "route_handler must be 'block', 'mock', or 'continue'",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Network interception failed: {e}",
            "action": "intercept_network",
            "session_id": session_id,
            "pattern": pattern,
            "remediation": "Check pattern syntax is valid (e.g., '**/api/**')",
        }


async def _handle_new_tab(
    session: Any, session_id: str, url: Optional[str]
) -> Dict[str, Any]:
    """
    Handle new_tab action (FR-21).

    Args:
        session: BrowserSession
        session_id: Session ID
        url: URL to load in new tab

    Returns:
        Dict with status and tab ID

    Traceability:
        FR-21 (Tab management)
    """
    try:
        # Create new page in same browser context
        new_page = await session.browser.new_page()

        # Generate unique tab ID
        tab_id = f"tab-{uuid.uuid4().hex[:8]}"

        # Store in session tabs
        session.tabs[tab_id] = new_page

        # Navigate if URL provided
        if url:
            await new_page.goto(url)
            title = await new_page.title()
        else:
            title = "about:blank"

        logger.info("Created new tab: %s (total tabs: %s)", tab_id, len(session.tabs))

        return {
            "status": "success",
            "action": "new_tab",
            "session_id": session_id,
            "tab_id": tab_id,
            "url": url or "about:blank",
            "title": title,
            "total_tabs": len(session.tabs),  # Primary is now in tabs dict
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Create tab failed: {e}",
            "action": "new_tab",
            "session_id": session_id,
            "remediation": (
                "Check browser session is active and has sufficient resources"
            ),
        }


async def _handle_switch_tab(
    session: Any, session_id: str, tab_id: Optional[str]
) -> Dict[str, Any]:
    """
    Handle switch_tab action (FR-21).

    Args:
        session: BrowserSession
        session_id: Session ID
        tab_id: Tab ID to switch to

    Returns:
        Dict with status

    Traceability:
        FR-21 (Tab management)
    """
    if not tab_id:
        return {
            "status": "error",
            "error": "Missing required parameter: tab_id",
            "action": "switch_tab",
            "session_id": session_id,
            "remediation": (
                "Provide tab_id parameter from new_tab or list_tabs response"
            ),
        }

    try:
        # Check if tab exists
        if tab_id not in session.tabs:
            return {
                "status": "error",
                "error": f"Tab not found: {tab_id}",
                "action": "switch_tab",
                "session_id": session_id,
                "available_tabs": list(session.tabs.keys()),
                "remediation": "Use list_tabs to see available tab IDs",
            }

        # Get the target tab
        target_page = session.tabs[tab_id]

        # Bring tab to front (visual focus in browser)
        await target_page.bring_to_front()

        # Update session.page to point to active tab (for subsequent operations)
        # All tabs stay in tabs dict with stable IDs - we just change which is active
        session.page = target_page

        title = await target_page.title()
        url = target_page.url

        logger.info("Switched to tab: %s", tab_id)

        return {
            "status": "success",
            "action": "switch_tab",
            "session_id": session_id,
            "tab_id": tab_id,
            "url": url,
            "title": title,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Switch tab failed: {e}",
            "action": "switch_tab",
            "session_id": session_id,
            "tab_id": tab_id,
            "remediation": ("Check tab_id is valid and tab is still open"),
        }


async def _handle_close_tab(
    session: Any, session_id: str, tab_id: Optional[str]
) -> Dict[str, Any]:
    """
    Handle close_tab action (FR-21).

    Args:
        session: BrowserSession
        session_id: Session ID
        tab_id: Tab ID to close

    Returns:
        Dict with status

    Traceability:
        FR-21 (Tab management)
    """
    if not tab_id:
        return {
            "status": "error",
            "error": "Missing required parameter: tab_id",
            "action": "close_tab",
            "session_id": session_id,
            "remediation": (
                "Provide tab_id parameter from new_tab or list_tabs response"
            ),
        }

    try:
        if tab_id not in session.tabs:
            return {
                "status": "error",
                "error": f"Tab not found: {tab_id}",
                "action": "close_tab",
                "session_id": session_id,
                "available_tabs": list(session.tabs.keys()),
                "remediation": "Use list_tabs to see available tab IDs",
            }

        # Close the tab
        tab_page = session.tabs[tab_id]
        await tab_page.close()
        del session.tabs[tab_id]

        logger.info("Closed tab: %s (remaining tabs: %s)", tab_id, len(session.tabs))

        return {
            "status": "success",
            "action": "close_tab",
            "session_id": session_id,
            "tab_id": tab_id,
            "remaining_tabs": len(session.tabs),  # Primary is now in tabs dict
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Close tab failed: {e}",
            "action": "close_tab",
            "session_id": session_id,
            "tab_id": tab_id,
            "remediation": "Check tab_id is valid and tab is still open",
        }


async def _handle_list_tabs(session: Any, session_id: str) -> Dict[str, Any]:
    """
    Handle list_tabs action (FR-21).

    Args:
        session: BrowserSession
        session_id: Session ID

    Returns:
        Dict with status and tab list

    Traceability:
        FR-21 (Tab management)
    """
    try:
        tabs = []

        # List all tabs (including primary which is now in tabs dict)
        # Primary page is the one stored in session.page
        for tab_id, tab_page in session.tabs.items():
            tabs.append(
                {
                    "tab_id": tab_id,
                    "url": tab_page.url,
                    "title": await tab_page.title(),
                    "is_primary": (
                        tab_page == session.page
                    ),  # Check if this is the active page
                }
            )

        return {
            "status": "success",
            "action": "list_tabs",
            "session_id": session_id,
            "tabs": tabs,
            "total_tabs": len(tabs),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"List tabs failed: {e}",
            "action": "list_tabs",
            "session_id": session_id,
            "remediation": "Check browser session is active",
        }


async def _handle_upload_file(
    page: Any, session_id: str, selector: Optional[str], file_path: Optional[str]
) -> Dict[str, Any]:
    """
    Handle upload_file action (FR-22).

    Args:
        page: Playwright Page
        session_id: Session ID
        selector: Input selector
        file_path: Path to file to upload

    Returns:
        Dict with status

    Traceability:
        FR-22 (File upload)
    """
    if not selector:
        return {
            "status": "error",
            "error": "Missing required parameter: selector",
            "action": "upload_file",
            "session_id": session_id,
            "remediation": (
                "Provide selector parameter for file input, "
                "e.g., selector='input[type=file]'"
            ),
        }

    if not file_path:
        return {
            "status": "error",
            "error": "Missing required parameter: file_path",
            "action": "upload_file",
            "session_id": session_id,
            "remediation": (
                "Provide file_path parameter, e.g., file_path='/path/to/file.pdf'"
            ),
        }

    try:
        # Validate file exists
        file = Path(file_path)
        if not file.exists():
            return {
                "status": "error",
                "error": f"File not found: {file_path}",
                "action": "upload_file",
                "session_id": session_id,
                "remediation": "Ensure file_path points to an existing file",
            }

        # Upload file
        await page.set_input_files(selector, str(file))

        return {
            "status": "success",
            "action": "upload_file",
            "session_id": session_id,
            "selector": selector,
            "file_path": file_path,
            "file_size": file.stat().st_size,
            "file_name": file.name,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"File upload failed: {e}",
            "action": "upload_file",
            "session_id": session_id,
            "selector": selector,
            "file_path": file_path,
            "remediation": (
                "Check selector targets a file input and file is accessible"
            ),
        }


async def _handle_download_file(
    page: Any,
    session_id: str,
    trigger_selector: Optional[str],
    save_path: Optional[str],
) -> Dict[str, Any]:
    """
    Handle download_file action (FR-22).

    Args:
        page: Playwright Page
        session_id: Session ID
        trigger_selector: Selector to trigger download
        save_path: Path to save downloaded file

    Returns:
        Dict with status and file info

    Traceability:
        FR-22 (File download)
    """
    if not trigger_selector:
        return {
            "status": "error",
            "error": "Missing required parameter: download_trigger_selector",
            "action": "download_file",
            "session_id": session_id,
            "remediation": (
                "Provide download_trigger_selector parameter, "
                "e.g., download_trigger_selector='#download-btn'"
            ),
        }

    if not save_path:
        return {
            "status": "error",
            "error": "Missing required parameter: file_path",
            "action": "download_file",
            "session_id": session_id,
            "remediation": (
                "Provide file_path parameter for save location, "
                "e.g., file_path='/tmp/download.pdf'"
            ),
        }

    try:
        # Ensure parent directory exists
        save_file = Path(save_path)
        save_file.parent.mkdir(parents=True, exist_ok=True)

        # Start download and click trigger
        async with page.expect_download(timeout=60000) as download_info:
            await page.click(trigger_selector)

        download = await download_info.value

        # Save to specified path
        await download.save_as(save_path)

        # Get file info
        file_size = save_file.stat().st_size if save_file.exists() else 0

        return {
            "status": "success",
            "action": "download_file",
            "session_id": session_id,
            "trigger_selector": trigger_selector,
            "file_path": save_path,
            "file_size": file_size,
            "suggested_filename": download.suggested_filename,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"File download failed: {e}",
            "action": "download_file",
            "session_id": session_id,
            "trigger_selector": trigger_selector,
            "remediation": (
                "Check trigger_selector initiates a download and save_path "
                "is writable. Increase timeout if download is slow."
            ),
        }
