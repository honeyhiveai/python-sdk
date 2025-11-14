# pos_browser Usage Guide

**Keywords for search**: pos_browser, browser automation, Playwright automation, web testing, browser sessions, screenshot capture, element interaction, form filling, tab management, browser viewport, emulate media, cookies, JavaScript execution, DOM query, web scraping, browser tool, automated testing, web automation, headless browser, how to use browser, browser tool reference

**This standard defines how to use the `pos_browser` tool for comprehensive browser automation, web testing, and page interaction.**

---

## 🚨 TL;DR - pos_browser Quick Reference

**Core Principle:** `pos_browser` provides unified browser automation with isolated sessions. Each conversation gets its own browser session that persists across tool calls.

**24 Actions Available:**

**Navigation:**
- `navigate` - Navigate to URL

**Inspection:**
- `screenshot` - Capture page screenshot (viewport or full page)
- `console` - Get console messages (stub)
- `query` - Query elements by CSS/XPath selector
- `evaluate` - Execute JavaScript and get result
- `get_cookies` - Get all cookies
- `get_local_storage` - Get local storage item

**Interaction:**
- `click` - Click element
- `type` - Type text into element
- `fill` - Fill input field
- `select` - Select dropdown option

**Waiting:**
- `wait` - Wait for element state

**Context:**
- `emulate_media` - Set color scheme/media features
- `viewport` - Resize browser viewport
- `set_cookies` - Set cookies

**Advanced:**
- `run_test` - Execute Playwright test script (stub)
- `intercept_network` - Intercept/mock network requests (stub)
- `new_tab` - Create new tab
- `switch_tab` - Switch to tab by ID
- `close_tab` - Close tab by ID
- `list_tabs` - List all tabs
- `upload_file` - Upload file to input (stub)
- `download_file` - Download file from page (stub)

**Session:**
- `close` - Close session and release resources

**Quick Start:**
```python
# 1. Navigate (auto-creates session)
result = pos_browser(action="navigate", url="https://example.com")
session_id = result["session_id"]  # Save this!

# 2. Take screenshot
pos_browser(
    action="screenshot",
    session_id=session_id,
    screenshot_path="/tmp/page.png",
    screenshot_full_page=True  # Capture entire scrollable page
)

# 3. Interact with page
pos_browser(action="click", session_id=session_id, selector="button#submit")
pos_browser(action="type", session_id=session_id, selector="input[name='email']", text="test@example.com")

# 4. Get data
result = pos_browser(action="evaluate", session_id=session_id, script="document.title")
title = result["result"]

# 5. Clean up
pos_browser(action="close", session_id=session_id)
```

**Critical Rules:**
- ✅ **Sessions auto-created** - First call without `session_id` creates new session
- ✅ **Session IDs persist** - Save `session_id` to reuse browser state across calls
- ✅ **Selectors are CSS/XPath** - Use standard web selectors
- ✅ **Screenshots support full page** - Set `screenshot_full_page=true`
- ✅ **Multiple tabs supported** - Use tab management actions
- ❌ **Don't forget to close** - Sessions consume resources, close when done

**Common Mistakes:**
- ❌ Not saving `session_id` from first call
- ❌ Using invalid CSS selectors (causes timeout)
- ❌ Forgetting to wait for elements before interaction
- ❌ Not closing sessions when done (resource leak)
- ❌ Using action="console" (stub, not yet implemented)

---

## ❓ Questions This Answers

1. "How do I automate browser interactions?"
2. "How to take screenshots with the browser tool?"
3. "How to click elements on a web page?"
4. "How to fill forms programmatically?"
5. "How to execute JavaScript in the browser?"
6. "How to manage multiple browser tabs?"
7. "How to get cookies from a page?"
8. "How to set browser viewport size?"
9. "How to wait for elements to load?"
10. "How to query DOM elements?"
11. "What is browser session management?"
12. "How to capture full page screenshots?"
13. "How to type text into input fields?"
14. "How to select dropdown options?"
15. "How to emulate dark mode in browser?"

---

## 🎯 Purpose

This standard provides comprehensive reference documentation for the `pos_browser` MCP tool, enabling automated browser control, web testing, and page interaction.

**Core Principle**: One tool, multiple actions. All browser operations (navigation, inspection, interaction, tab management) use `pos_browser` with different `action` parameters.

---

## What is pos_browser?

`pos_browser` is a unified browser automation tool built on **Playwright**, providing:

- **Isolated browser sessions** - Each conversation gets own browser process
- **Persistent state** - Sessions survive across multiple tool calls
- **Full Playwright capabilities** - Navigation, interaction, JavaScript execution
- **Multi-tab support** - Create, switch, close tabs within session
- **Screenshot capture** - Viewport or full scrollable page
- **Context emulation** - Dark mode, mobile viewport, cookies
- **Element interaction** - Click, type, fill, select
- **JavaScript execution** - Run arbitrary JS, get return values

**Architecture:**
```
AI Agent → pos_browser (Tools Layer)
    ↓
BrowserManager (Subsystems Layer)
    ↓
Playwright (each session = own browser process)
```

---

## Action Reference

### Navigation Actions

#### navigate

Navigate browser to URL.

**Parameters:**
- `action`: "navigate" (required)
- `url`: Target URL (required)
- `session_id`: Session identifier (optional, auto-creates if omitted)
- `wait_until`: Wait condition - "load", "domcontentloaded", "networkidle" (default: "load")
- `timeout`: Navigation timeout in milliseconds (default: 30000)

**Returns:**
- `status`: "success" or "error"
- `action`: "navigate"
- `url`: URL navigated to
- `session_id`: Browser session identifier

**Example:**
```python
# Basic navigation (auto-creates session)
result = pos_browser(action="navigate", url="https://example.com")
session_id = result["session_id"]

# Navigation with options
pos_browser(
    action="navigate",
    session_id=session_id,
    url="https://example.com/api",
    wait_until="networkidle",  # Wait for network to be idle
    timeout=60000  # 60 second timeout
)
```

---

### Inspection Actions

#### screenshot

Capture page screenshot.

**Parameters:**
- `action`: "screenshot" (required)
- `session_id`: Session identifier (required)
- `screenshot_path`: File path to save screenshot (optional)
- `screenshot_full_page`: Capture full scrollable page (default: false)
- `screenshot_format`: Image format - "png", "jpeg" (default: "png")

**Returns:**
- `status`: "success" or "error"
- `action`: "screenshot"
- `path`: File path where screenshot was saved
- `session_id`: Browser session identifier

**Example:**
```python
# Viewport screenshot
pos_browser(
    action="screenshot",
    session_id=session_id,
    screenshot_path="/tmp/viewport.png"
)

# Full page screenshot
pos_browser(
    action="screenshot",
    session_id=session_id,
    screenshot_path="/tmp/fullpage.png",
    screenshot_full_page=True  # Captures entire scrollable page
)
```

---

#### query

Query DOM elements by CSS/XPath selector.

**Parameters:**
- `action`: "query" (required)
- `session_id`: Session identifier (required)
- `selector`: CSS or XPath selector (required)
- `query_all`: Return all matching elements vs first (default: false)

**Returns:**
- `status`: "success" or "error"
- `action`: "query"
- `selector`: Selector used
- `found`: Boolean - whether element(s) found (query_all=false)
- `count`: Number of elements found (query_all=true)
- `session_id`: Browser session identifier

**Example:**
```python
# Find single element
result = pos_browser(
    action="query",
    session_id=session_id,
    selector="h1"
)
if result["found"]:
    print("H1 element exists")

# Find all matching elements
result = pos_browser(
    action="query",
    session_id=session_id,
    selector="a",
    query_all=True
)
print(f"Found {result['count']} links")
```

---

#### evaluate

Execute JavaScript code and get result.

**Parameters:**
- `action`: "evaluate" (required)
- `session_id`: Session identifier (required)
- `script`: JavaScript code to execute (required)

**Returns:**
- `status`: "success" or "error"
- `action`: "evaluate"
- `result`: Return value from JavaScript
- `session_id`: Browser session identifier

**Example:**
```python
# Get page title
result = pos_browser(
    action="evaluate",
    session_id=session_id,
    script="document.title"
)
title = result["result"]

# Get custom data
result = pos_browser(
    action="evaluate",
    session_id=session_id,
    script="({ url: window.location.href, userAgent: navigator.userAgent })"
)
data = result["result"]
```

---

#### get_cookies

Get all cookies for current page.

**Parameters:**
- `action`: "get_cookies" (required)
- `session_id`: Session identifier (required)

**Returns:**
- `status`: "success" or "error"
- `action`: "get_cookies"
- `cookies`: List of cookie objects
- `session_id`: Browser session identifier

**Example:**
```python
result = pos_browser(action="get_cookies", session_id=session_id)
cookies = result["cookies"]
for cookie in cookies:
    print(f"{cookie['name']}: {cookie['value']}")
```

---

### Interaction Actions

#### click

Click element by selector.

**Parameters:**
- `action`: "click" (required)
- `session_id`: Session identifier (required)
- `selector`: CSS/XPath selector (required)
- `button`: Mouse button - "left", "right", "middle" (default: "left")
- `click_count`: Number of clicks (1-3) (default: 1)
- `modifiers`: Keyboard modifiers - ["Alt", "Control", "Meta", "Shift"] (optional)

**Returns:**
- `status`: "success" or "error"
- `action`: "click"
- `selector`: Selector clicked
- `session_id`: Browser session identifier

**Example:**
```python
# Basic click
pos_browser(
    action="click",
    session_id=session_id,
    selector="button#submit"
)

# Double-click
pos_browser(
    action="click",
    session_id=session_id,
    selector="div.item",
    click_count=2
)

# Ctrl+click
pos_browser(
    action="click",
    session_id=session_id,
    selector="a[href*='docs']",
    modifiers=["Control"]
)
```

---

#### type

Type text using keyboard.

**Parameters:**
- `action`: "type" (required)
- `session_id`: Session identifier (required)
- `selector`: CSS/XPath selector (required)
- `text`: Text to type (required)

**Returns:**
- `status`: "success" or "error"
- `action`: "type"
- `selector`: Selector typed into
- `session_id`: Browser session identifier

**Example:**
```python
# Type into search box
pos_browser(
    action="type",
    session_id=session_id,
    selector="input[type='search']",
    text="browser automation"
)
```

---

#### fill

Fill input field (faster than type, sets value directly).

**Parameters:**
- `action`: "fill" (required)
- `session_id`: Session identifier (required)
- `selector`: CSS/XPath selector (required)
- `value`: Value to fill (required)

**Returns:**
- `status`: "success" or "error"
- `action`: "fill"
- `selector`: Selector filled
- `session_id`: Browser session identifier

**Example:**
```python
# Fill form fields
pos_browser(
    action="fill",
    session_id=session_id,
    selector="input[name='email']",
    value="user@example.com"
)

pos_browser(
    action="fill",
    session_id=session_id,
    selector="input[name='password']",
    value="secret123"
)
```

---

#### select

Select dropdown option.

**Parameters:**
- `action`: "select" (required)
- `session_id`: Session identifier (required)
- `selector`: CSS/XPath selector (required)
- `value`: Option value to select (required)

**Returns:**
- `status`: "success" or "error"
- `action`: "select"
- `selector`: Selector selected
- `session_id`: Browser session identifier

**Example:**
```python
# Select by value
pos_browser(
    action="select",
    session_id=session_id,
    selector="select[name='country']",
    value="US"
)
```

---

### Waiting Actions

#### wait

Wait for element to reach specific state.

**Parameters:**
- `action`: "wait" (required)
- `session_id`: Session identifier (required)
- `selector`: CSS/XPath selector (required)
- `wait_for_state`: State to wait for - "visible", "hidden", "attached", "detached" (default: "visible")
- `wait_for_timeout`: Timeout in milliseconds (default: 30000)

**Returns:**
- `status`: "success" or "error"
- `action`: "wait"
- `selector`: Selector waited for
- `state`: State achieved
- `session_id`: Browser session identifier

**Example:**
```python
# Wait for element to be visible
pos_browser(
    action="wait",
    session_id=session_id,
    selector="div#content",
    wait_for_state="visible",
    wait_for_timeout=5000  # 5 second timeout
)

# Wait for loading spinner to disappear
pos_browser(
    action="wait",
    session_id=session_id,
    selector="div.loading-spinner",
    wait_for_state="hidden"
)
```

---

### Context Actions

#### viewport

Resize browser viewport.

**Parameters:**
- `action`: "viewport" (required)
- `session_id`: Session identifier (required)
- `viewport_width`: Width in pixels (required)
- `viewport_height`: Height in pixels (required)

**Returns:**
- `status`: "success" or "error"
- `action`: "viewport"
- `width`: Viewport width set
- `height`: Viewport height set
- `session_id`: Browser session identifier

**Example:**
```python
# Desktop viewport
pos_browser(
    action="viewport",
    session_id=session_id,
    viewport_width=1920,
    viewport_height=1080
)

# Mobile viewport
pos_browser(
    action="viewport",
    session_id=session_id,
    viewport_width=375,
    viewport_height=667
)
```

---

#### emulate_media

Emulate media features (color scheme, reduced motion).

**Parameters:**
- `action`: "emulate_media" (required)
- `session_id`: Session identifier (required)
- `color_scheme`: Color scheme - "light", "dark", "no-preference" (optional)
- `reduced_motion`: Reduced motion - "reduce", "no-preference" (optional)

**Returns:**
- `status`: "success" or "error"
- `action`: "emulate_media"
- `session_id`: Browser session identifier

**Example:**
```python
# Dark mode
pos_browser(
    action="emulate_media",
    session_id=session_id,
    color_scheme="dark"
)

# Reduced motion
pos_browser(
    action="emulate_media",
    session_id=session_id,
    reduced_motion="reduce"
)
```

---

#### set_cookies

Set cookies for current page.

**Parameters:**
- `action`: "set_cookies" (required)
- `session_id`: Session identifier (required)
- `cookies`: List of cookie objects (required)

**Cookie object format:**
```python
{
    "name": "cookie_name",
    "value": "cookie_value",
    "domain": "example.com",
    "path": "/",
    "expires": -1,  # Session cookie
    "httpOnly": False,
    "secure": False,
    "sameSite": "Lax"
}
```

**Returns:**
- `status`: "success" or "error"
- `action`: "set_cookies"
- `count`: Number of cookies set
- `session_id`: Browser session identifier

**Example:**
```python
pos_browser(
    action="set_cookies",
    session_id=session_id,
    cookies=[
        {
            "name": "auth_token",
            "value": "abc123",
            "domain": "example.com",
            "path": "/"
        }
    ]
)
```

---

### Tab Management Actions

#### new_tab

Create new tab.

**Parameters:**
- `action`: "new_tab" (required)
- `session_id`: Session identifier (required)
- `new_tab_url`: URL to open in new tab (required)

**Returns:**
- `status`: "success" or "error"
- `action`: "new_tab"
- `tab_id`: New tab identifier
- `url`: URL opened
- `session_id`: Browser session identifier

**Example:**
```python
result = pos_browser(
    action="new_tab",
    session_id=session_id,
    new_tab_url="https://example.com/docs"
)
new_tab_id = result["tab_id"]
```

---

#### list_tabs

List all tabs in session.

**Parameters:**
- `action`: "list_tabs" (required)
- `session_id`: Session identifier (required)

**Returns:**
- `status`: "success" or "error"
- `action`: "list_tabs"
- `tabs`: List of tab objects with tab_id, url, title
- `count`: Number of tabs
- `session_id`: Browser session identifier

**Example:**
```python
result = pos_browser(action="list_tabs", session_id=session_id)
for tab in result["tabs"]:
    print(f"{tab['tab_id']}: {tab['title']} - {tab['url']}")
```

---

#### switch_tab

Switch to specific tab.

**Parameters:**
- `action`: "switch_tab" (required)
- `session_id`: Session identifier (required)
- `tab_id`: Tab identifier to switch to (required)

**Returns:**
- `status`: "success" or "error"
- `action`: "switch_tab"
- `tab_id`: Tab switched to
- `session_id`: Browser session identifier

**Example:**
```python
# List tabs to find ID
result = pos_browser(action="list_tabs", session_id=session_id)
tab_id = result["tabs"][1]["tab_id"]

# Switch to that tab
pos_browser(action="switch_tab", session_id=session_id, tab_id=tab_id)
```

---

#### close_tab

Close specific tab.

**Parameters:**
- `action`: "close_tab" (required)
- `session_id`: Session identifier (required)
- `tab_id`: Tab identifier to close (required)

**Returns:**
- `status`: "success" or "error"
- `action`: "close_tab"
- `tab_id`: Tab closed
- `session_id`: Browser session identifier

**Example:**
```python
pos_browser(action="close_tab", session_id=session_id, tab_id="tab_2")
```

---

### Session Management

#### close

Close browser session and release resources.

**Parameters:**
- `action`: "close" (required)
- `session_id`: Session identifier (required)

**Returns:**
- `status`: "success" or "error"
- `message`: Success message

**Example:**
```python
pos_browser(action="close", session_id=session_id)
```

**Important:** Always close sessions when done to release browser processes and memory.

---

## Common Patterns

### Pattern 1: Web Scraping

```python
# 1. Navigate
result = pos_browser(action="navigate", url="https://example.com/data")
session_id = result["session_id"]

# 2. Wait for content
pos_browser(action="wait", session_id=session_id, selector="table#data")

# 3. Extract data with JavaScript
result = pos_browser(
    action="evaluate",
    session_id=session_id,
    script="""
        Array.from(document.querySelectorAll('table#data tr')).map(row => ({
            cells: Array.from(row.querySelectorAll('td')).map(cell => cell.textContent)
        }))
    """
)
data = result["result"]

# 4. Clean up
pos_browser(action="close", session_id=session_id)
```

---

### Pattern 2: Form Automation

```python
# 1. Navigate to form
result = pos_browser(action="navigate", url="https://example.com/form")
session_id = result["session_id"]

# 2. Fill form fields
pos_browser(action="fill", session_id=session_id, selector="#name", value="John Doe")
pos_browser(action="fill", session_id=session_id, selector="#email", value="john@example.com")
pos_browser(action="select", session_id=session_id, selector="#country", value="US")

# 3. Submit form
pos_browser(action="click", session_id=session_id, selector="button[type='submit']")

# 4. Wait for success message
pos_browser(action="wait", session_id=session_id, selector="div.success")

# 5. Verify
result = pos_browser(action="evaluate", session_id=session_id, script="document.querySelector('div.success').textContent")
print(result["result"])

# 6. Clean up
pos_browser(action="close", session_id=session_id)
```

---

### Pattern 3: Multi-Tab Browsing

```python
# 1. Start with main tab
result = pos_browser(action="navigate", url="https://example.com")
session_id = result["session_id"]

# 2. Open second tab
result = pos_browser(action="new_tab", session_id=session_id, new_tab_url="https://example.com/docs")
docs_tab_id = result["tab_id"]

# 3. Open third tab
result = pos_browser(action="new_tab", session_id=session_id, new_tab_url="https://example.com/api")
api_tab_id = result["tab_id"]

# 4. Switch between tabs
pos_browser(action="switch_tab", session_id=session_id, tab_id=docs_tab_id)
# Work in docs tab...

pos_browser(action="switch_tab", session_id=session_id, tab_id=api_tab_id)
# Work in API tab...

# 5. List all tabs
result = pos_browser(action="list_tabs", session_id=session_id)
print(f"Open tabs: {result['count']}")

# 6. Close specific tab
pos_browser(action="close_tab", session_id=session_id, tab_id=docs_tab_id)

# 7. Clean up session
pos_browser(action="close", session_id=session_id)
```

---

### Pattern 4: Screenshot Testing

```python
# 1. Navigate
result = pos_browser(action="navigate", url="https://example.com")
session_id = result["session_id"]

# 2. Desktop screenshot
pos_browser(action="viewport", session_id=session_id, viewport_width=1920, viewport_height=1080)
pos_browser(action="screenshot", session_id=session_id, screenshot_path="/tmp/desktop.png")

# 3. Mobile screenshot
pos_browser(action="viewport", session_id=session_id, viewport_width=375, viewport_height=667)
pos_browser(action="screenshot", session_id=session_id, screenshot_path="/tmp/mobile.png")

# 4. Dark mode screenshot
pos_browser(action="emulate_media", session_id=session_id, color_scheme="dark")
pos_browser(action="screenshot", session_id=session_id, screenshot_path="/tmp/dark.png")

# 5. Full page screenshot
pos_browser(
    action="screenshot",
    session_id=session_id,
    screenshot_path="/tmp/fullpage.png",
    screenshot_full_page=True
)

# 6. Clean up
pos_browser(action="close", session_id=session_id)
```

---

## Troubleshooting

### Element Not Found

**Problem:** `error: "Timeout 30000ms exceeded"`

**Cause:** Selector doesn't match any element, or element not yet visible

**Solution:**
```python
# 1. Verify selector with query
result = pos_browser(action="query", session_id=session_id, selector="your-selector")
if not result["found"]:
    print("Selector doesn't match anything")

# 2. Wait for element first
pos_browser(action="wait", session_id=session_id, selector="your-selector", wait_for_state="visible")

# 3. Then interact
pos_browser(action="click", session_id=session_id, selector="your-selector")
```

---

### Session Already Closed

**Problem:** `error: "Session not found"`

**Cause:** Session was closed or doesn't exist

**Solution:**
```python
# Always save session_id from first call
result = pos_browser(action="navigate", url="https://example.com")
session_id = result["session_id"]  # ← SAVE THIS!

# Use saved session_id for subsequent calls
pos_browser(action="screenshot", session_id=session_id, ...)
```

---

### Resource Leaks

**Problem:** Browser processes accumulating, memory usage growing

**Cause:** Not closing sessions

**Solution:**
```python
# ALWAYS close sessions when done
try:
    # Your browser automation
    pos_browser(...)
finally:
    # Ensure cleanup even if errors occur
    pos_browser(action="close", session_id=session_id)
```

---

## Configuration

Browser behavior configured via MCP server config:

```yaml
browser:
  browser_type: "chromium"  # chromium, firefox, webkit
  headless: true  # true = no visible window, false = show browser
  max_sessions: 5  # Maximum concurrent browser sessions
  session_timeout_minutes: 30  # Auto-close idle sessions after N minutes
```

---

## Security Considerations

1. **Sensitive URLs** - Be cautious with auth tokens in URLs (logged by server)
2. **Credentials** - Don't pass credentials in screenshots that might be saved
3. **Cookie exposure** - get_cookies returns all cookies including auth tokens
4. **JavaScript execution** - evaluate runs arbitrary JS with full page access
5. **File paths** - Screenshots saved to filesystem, ensure proper permissions

---

## Performance Tips

1. **Reuse sessions** - Don't create new session for every action, reuse session_id
2. **Use fill vs type** - fill is faster than type for input fields
3. **Batch operations** - Do multiple actions in same session before closing
4. **Full page screenshots** - Only use when needed, slower than viewport screenshots
5. **Close sessions** - Don't leave sessions open indefinitely, resources add up

---

## Related Standards

**Query for related standards:**
- **MCP Tool Design** → `pos_search_project(action="search_standards", query="MCP tool design best practices")`
- **Testing Standards** → `pos_search_project(action="search_standards", query="testing strategies")`
- **Error Handling** → `pos_search_project(action="search_standards", query="error messages that enable action")`

---

## Bugs Fixed During Dogfooding

**2025-11-08:** Initial port validation found 3 bugs:

1. **Bug #1: get_browser_session_id() doesn't exist**
   - **Problem:** Called non-existent SessionMapper method
   - **Fix:** Use `session_mapper.create_session_id("browser", None)` instead
   - **Root cause:** Violated architecture - SessionMapper is generic, not browser-specific

2. **Bug #2: close_session() getting wrong parameters**
   - **Problem:** Tool passed `browser_type` and `headless` parameters that weren't accepted
   - **Fix:** Only pass `session_id` (browser_type/headless already stored in session)
   - **Root cause:** API mismatch between tool and subsystem

3. **Bug #3: close handler returns None**
   - **Problem:** BrowserManager.close_session() returns None but tool expects dict
   - **Fix:** Construct proper response dict in handler
   - **Root cause:** Missing response formatting

**Lesson:** Dogfood all tools after porting! Testing finds integration issues that specs miss.

---

**This is your complete reference for browser automation in prAxIs OS. Query liberally, automate confidently.** 🚀

