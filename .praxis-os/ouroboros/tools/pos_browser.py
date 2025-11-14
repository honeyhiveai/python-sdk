"""
pos_browser: Unified browser automation tool.

Provides a single consolidated tool for all browser operations with Playwright:
- Navigation: navigate
- Inspection: screenshot, console, query, evaluate, get_cookies, get_local_storage
- Interaction: click, type, fill, select
- Waiting: wait
- Context: emulate_media, viewport, set_cookies
- Advanced: run_test, intercept_network, new_tab, switch_tab, close_tab, list_tabs, upload_file, download_file
- Session: close

Architecture:
    AI Agent → pos_browser (Tools Layer)
        ↓
    SessionMapper (Middleware) - Maps conversation_id → browser_session_id
        ↓
    BrowserManager (Browser Subsystem)
        ↓
    Playwright (isolated sessions)

Traceability:
    FR-007: pos_browser - Browser Automation Tool
    FR-021: Isolated Playwright Sessions
    FR-022: Browser Actions (24 actions)
"""

import logging
from typing import Any, Dict, List, Literal, Optional

from ouroboros.tools.base import ActionDispatchMixin

logger = logging.getLogger(__name__)


class BrowserTool(ActionDispatchMixin):
    """
    Unified browser automation tool using ActionDispatchMixin pattern.
    
    Provides comprehensive Playwright operations through a single tool interface.
    """
    
    def __init__(self, mcp: Any, browser_manager: Any, session_mapper: Any):
        """Initialize with browser manager and session mapper."""
        super().__init__(mcp)
        self.browser_manager = browser_manager
        self.session_mapper = session_mapper
        
        # Define action handlers
        self.handlers = {
            # Navigation
            "navigate": self._handle_navigate,
            # Inspection
            "screenshot": self._handle_screenshot,
            "console": self._handle_console,
            "query": self._handle_query,
            "evaluate": self._handle_evaluate,
            "get_cookies": self._handle_get_cookies,
            "get_local_storage": self._handle_get_local_storage,
            # Interaction
            "click": self._handle_click,
            "type": self._handle_type,
            "fill": self._handle_fill,
            "select": self._handle_select,
            # Waiting
            "wait": self._handle_wait,
            # Context
            "emulate_media": self._handle_emulate_media,
            "viewport": self._handle_viewport,
            "set_cookies": self._handle_set_cookies,
            # Advanced
            "run_test": self._handle_run_test,
            "intercept_network": self._handle_intercept_network,
            "new_tab": self._handle_new_tab,
            "switch_tab": self._handle_switch_tab,
            "close_tab": self._handle_close_tab,
            "list_tabs": self._handle_list_tabs,
            "upload_file": self._handle_upload_file,
            "download_file": self._handle_download_file,
            # Session
            "close": self._handle_close,
        }
    
    @property
    def tool(self):
        """Return the MCP tool decorator wrapper."""
        @self.mcp.tool()
        async def pos_browser(
            action: Literal[
                # Navigation
                "navigate",
                # Inspection
                "screenshot",
                "console",
                "query",
                "evaluate",
                "get_cookies",
                "get_local_storage",
                # Interaction
                "click",
                "type",
                "fill",
                "select",
                # Waiting
                "wait",
                # Context
                "emulate_media",
                "viewport",
                "set_cookies",
                # Advanced
                "run_test",
                "intercept_network",
                "new_tab",
                "switch_tab",
                "close_tab",
                "list_tabs",
                "upload_file",
                "download_file",
                # Session
                "close",
            ],
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
            # Viewport (FR-7)
            viewport_width: Optional[int] = None,
            viewport_height: Optional[int] = None,
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
            Each conversation gets isolated browser session via SessionMapper middleware.
            
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
                action: Browser operation to perform (required)
                session_id: Optional session identifier (auto-mapped if not provided)
                url: Target URL (for navigate)
                wait_until: Wait condition (load/domcontentloaded/networkidle)
                timeout: Navigation timeout in milliseconds
                color_scheme: Color scheme (light/dark/no-preference)
                reduced_motion: Reduced motion (reduce/no-preference)
                screenshot_full_page: Capture full scrollable page
                screenshot_path: File path to save screenshot
                screenshot_format: Image format (png/jpeg)
                viewport_width: Viewport width in pixels
                viewport_height: Viewport height in pixels
                selector: CSS/XPath selector
                text: Text to type
                value: Value to fill/select
                button: Mouse button (left/right/middle)
                click_count: Number of clicks (1-3)
                modifiers: Keyboard modifiers (Alt, Control, Meta, Shift)
                wait_for_state: State to wait for (visible/hidden/attached/detached)
                wait_for_timeout: Wait timeout in milliseconds
                query_all: Return all matching elements (vs first)
                script: JavaScript to execute
                cookies: Cookies to set
                cookie_name: Cookie name to get
                storage_key: Local storage key
                test_file: Path to Playwright test file
                test_config: Test configuration
                route_pattern: URL pattern to intercept
                route_handler: How to handle route (block/mock/continue)
                mock_response: Mock response data
                tab_id: Tab identifier
                new_tab_url: URL for new tab
                file_path: Path to file for upload/download
                download_trigger_selector: Selector to trigger download
                browser_type: Browser type (chromium/firefox/webkit)
                headless: Run browser in headless mode
                
            Returns:
                Dictionary with:
                - status: "success" or "error"
                - action: Echoed action parameter
                - session_id: Browser session identifier
                - data: Action-specific result data
                
            Examples:
                >>> # Navigate to URL
                >>> pos_browser(
                ...     action="navigate",
                ...     url="https://example.com"
                ... )
                
                >>> # Take screenshot
                >>> pos_browser(
                ...     action="screenshot",
                ...     session_id="browser_client_abc_s0",
                ...     screenshot_path="/tmp/page.png"
                ... )
                
                >>> # Click element
                >>> pos_browser(
                ...     action="click",
                ...     session_id="browser_client_abc_s0",
                ...     selector="#submit-button"
                ... )
            
            Raises:
                ValueError: If action is invalid or required parameters missing
                
            Traceability:
                FR-007: pos_browser - Browser Automation Tool
                FR-021: Isolated Playwright Sessions
                FR-022: Browser Actions
            """
            # Middleware Integration: SessionMapper
            # Map conversation context → browser_session_id for session isolation
            if not session_id:
                # SessionMapper creates generic session_id for browser subsystem
                browser_session_id = self.session_mapper.create_session_id("browser", conversation_id=None)
                logger.debug(
                    "SessionMapper auto-created browser_session_id: %s",
                    browser_session_id
                )
            else:
                # Use provided session_id (allows explicit session management)
                browser_session_id = session_id
            
            # Dispatch to handler
            result = await self.dispatch(
                action,
                self.handlers,  # type: ignore[arg-type]
                browser_session_id=browser_session_id,
                browser_type=browser_type,
                headless=headless,
                url=url,
                wait_until=wait_until,
                timeout=timeout,
                color_scheme=color_scheme,
                reduced_motion=reduced_motion,
                screenshot_full_page=screenshot_full_page,
                screenshot_path=screenshot_path,
                screenshot_format=screenshot_format,
                viewport_width=viewport_width,
                viewport_height=viewport_height,
                selector=selector,
                text=text,
                value=value,
                button=button,
                click_count=click_count,
                modifiers=modifiers,
                wait_for_state=wait_for_state,
                wait_for_timeout=wait_for_timeout,
                query_all=query_all,
                script=script,
                cookies=cookies,
                cookie_name=cookie_name,
                storage_key=storage_key,
                test_file=test_file,
                test_config=test_config,
                route_pattern=route_pattern,
                route_handler=route_handler,
                mock_response=mock_response,
                tab_id=tab_id,
                new_tab_url=new_tab_url,
                file_path=file_path,
                download_trigger_selector=download_trigger_selector,
            )
            
            # Add session_id to result
            if "session_id" not in result:
                result["session_id"] = browser_session_id
            
            return result
        
        return pos_browser
    
    # ========================================================================
    # Navigation Handlers
    # ========================================================================
    
    async def _handle_navigate(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        url: Optional[str] = None,
        wait_until: str = "load",
        timeout: int = 30000,
        **kwargs
    ) -> Dict[str, Any]:
        """Navigate to URL."""
        if not url:
            raise ValueError("navigate action requires url parameter")
        
        return await self.browser_manager.navigate(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            url=url,
            wait_until=wait_until,
            timeout=timeout,
        )
    
    # ========================================================================
    # Inspection Handlers
    # ========================================================================
    
    async def _handle_screenshot(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        screenshot_full_page: bool = False,
        screenshot_path: Optional[str] = None,
        screenshot_format: str = "png",
        **kwargs
    ) -> Dict[str, Any]:
        """Capture page screenshot."""
        return await self.browser_manager.screenshot(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            full_page=screenshot_full_page,
            path=screenshot_path,
            format=screenshot_format,
        )
    
    async def _handle_console(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        **kwargs
    ) -> Dict[str, Any]:
        """Get console messages."""
        return await self.browser_manager.get_console_messages(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
        )
    
    async def _handle_query(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        selector: Optional[str] = None,
        query_all: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Query elements by selector."""
        if not selector:
            raise ValueError("query action requires selector parameter")
        
        return await self.browser_manager.query(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            selector=selector,
            query_all=query_all,
        )
    
    async def _handle_evaluate(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        script: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute JavaScript."""
        if not script:
            raise ValueError("evaluate action requires script parameter")
        
        return await self.browser_manager.evaluate(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            script=script,
        )
    
    async def _handle_get_cookies(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        cookie_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get all cookies."""
        return await self.browser_manager.get_cookies(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            cookie_name=cookie_name,
        )
    
    async def _handle_get_local_storage(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        storage_key: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get local storage item."""
        if not storage_key:
            raise ValueError("get_local_storage action requires storage_key parameter")
        
        return await self.browser_manager.get_local_storage(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            key=storage_key,
        )
    
    # ========================================================================
    # Interaction Handlers
    # ========================================================================
    
    async def _handle_click(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        selector: Optional[str] = None,
        button: str = "left",
        click_count: int = 1,
        modifiers: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Click element."""
        if not selector:
            raise ValueError("click action requires selector parameter")
        
        return await self.browser_manager.click(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            selector=selector,
            button=button,
            click_count=click_count,
            modifiers=modifiers,
        )
    
    async def _handle_type(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        selector: Optional[str] = None,
        text: Optional[str] = None,
        modifiers: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Type text with keyboard."""
        if not selector:
            raise ValueError("type action requires selector parameter")
        if not text:
            raise ValueError("type action requires text parameter")
        
        return await self.browser_manager.type(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            selector=selector,
            text=text,
            modifiers=modifiers,
        )
    
    async def _handle_fill(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        selector: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Fill input field."""
        if not selector:
            raise ValueError("fill action requires selector parameter")
        if not value:
            raise ValueError("fill action requires value parameter")
        
        return await self.browser_manager.fill(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            selector=selector,
            value=value,
        )
    
    async def _handle_select(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        selector: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Select dropdown option."""
        if not selector:
            raise ValueError("select action requires selector parameter")
        if not value:
            raise ValueError("select action requires value parameter")
        
        return await self.browser_manager.select(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            selector=selector,
            value=value,
        )
    
    # ========================================================================
    # Waiting Handlers
    # ========================================================================
    
    async def _handle_wait(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        selector: Optional[str] = None,
        wait_for_state: str = "visible",
        wait_for_timeout: int = 30000,
        **kwargs
    ) -> Dict[str, Any]:
        """Wait for element state."""
        if not selector:
            raise ValueError("wait action requires selector parameter")
        
        return await self.browser_manager.wait(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            selector=selector,
            state=wait_for_state,
            timeout=wait_for_timeout,
        )
    
    # ========================================================================
    # Context Handlers
    # ========================================================================
    
    async def _handle_emulate_media(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        color_scheme: Optional[str] = None,
        reduced_motion: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Set color scheme/media features."""
        return await self.browser_manager.emulate_media(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            color_scheme=color_scheme,
            reduced_motion=reduced_motion,
        )
    
    async def _handle_viewport(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        viewport_width: Optional[int] = None,
        viewport_height: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Resize browser viewport."""
        if viewport_width is None or viewport_height is None:
            raise ValueError("viewport action requires viewport_width and viewport_height parameters")
        
        return await self.browser_manager.set_viewport(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            width=viewport_width,
            height=viewport_height,
        )
    
    async def _handle_set_cookies(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        cookies: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Set cookies."""
        if not cookies:
            raise ValueError("set_cookies action requires cookies parameter")
        
        return await self.browser_manager.set_cookies(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            cookies=cookies,
        )
    
    # ========================================================================
    # Advanced Handlers
    # ========================================================================
    
    async def _handle_run_test(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        test_file: Optional[str] = None,
        test_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute Playwright test script."""
        if not test_file:
            raise ValueError("run_test action requires test_file parameter")
        
        return await self.browser_manager.run_test(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            test_file=test_file,
            config=test_config,
        )
    
    async def _handle_intercept_network(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        route_pattern: Optional[str] = None,
        route_handler: Optional[str] = None,
        mock_response: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Intercept/mock network requests."""
        if not route_pattern:
            raise ValueError("intercept_network action requires route_pattern parameter")
        
        return await self.browser_manager.intercept_network(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            pattern=route_pattern,
            handler=route_handler,
            mock_response=mock_response,
        )
    
    async def _handle_new_tab(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        new_tab_url: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create new tab."""
        return await self.browser_manager.new_tab(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            url=new_tab_url,
        )
    
    async def _handle_switch_tab(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        tab_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Switch to tab by ID."""
        if not tab_id:
            raise ValueError("switch_tab action requires tab_id parameter")
        
        return await self.browser_manager.switch_tab(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            tab_id=tab_id,
        )
    
    async def _handle_close_tab(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        tab_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Close tab by ID."""
        return await self.browser_manager.close_tab(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            tab_id=tab_id,
        )
    
    async def _handle_list_tabs(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        **kwargs
    ) -> Dict[str, Any]:
        """List all tabs."""
        return await self.browser_manager.list_tabs(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
        )
    
    async def _handle_upload_file(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        selector: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Upload file to input."""
        if not selector:
            raise ValueError("upload_file action requires selector parameter")
        if not file_path:
            raise ValueError("upload_file action requires file_path parameter")
        
        return await self.browser_manager.upload_file(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            selector=selector,
            file_path=file_path,
        )
    
    async def _handle_download_file(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        download_trigger_selector: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Download file from page."""
        if not download_trigger_selector:
            raise ValueError("download_file action requires download_trigger_selector parameter")
        
        return await self.browser_manager.download_file(  # type: ignore[no-any-return]
            session_id=browser_session_id,
            browser_type=browser_type,
            headless=headless,
            trigger_selector=download_trigger_selector,
            download_path=file_path,
        )
    
    # ========================================================================
    # Session Handlers
    # ========================================================================
    
    async def _handle_close(
        self,
        browser_session_id: str,
        browser_type: str,
        headless: bool,
        **kwargs
    ) -> Dict[str, Any]:
        """Close session and release resources."""
        # BrowserManager.close_session() only needs session_id
        # browser_type and headless are stored in the session already
        await self.browser_manager.close_session(session_id=browser_session_id)
        
        return {
            "status": "success",
            "message": "Browser session closed successfully"
        }


def register_browser_tool(mcp: Any, browser_manager: Any, session_mapper: Any) -> int:
    """
    Register pos_browser tool with MCP server.
    
    Args:
        mcp: FastMCP server instance
        browser_manager: BrowserManager instance for Playwright automation
        session_mapper: SessionMapper instance for conversation → browser session mapping
        
    Returns:
        int: Number of tools registered (always 1)
        
    Traceability:
        FR-007: pos_browser tool registration
        FR-021: Isolated Playwright sessions via SessionMapper
    """
    # Create tool instance
    tool_instance = BrowserTool(
        mcp=mcp,
        browser_manager=browser_manager,
        session_mapper=session_mapper
    )
    
    # Register the tool (accessing the @mcp.tool() decorated function)
    _ = tool_instance.tool
    
    logger.info("✅ Registered pos_browser tool (24 actions) using ActionDispatchMixin")
    return 1  # One tool registered


__all__ = ["register_browser_tool", "BrowserTool"]

