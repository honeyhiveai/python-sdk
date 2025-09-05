# Mermaid Diagram Standard Configuration

## Standard Dual-Theme Configuration

All Mermaid diagrams in the HoneyHive Python SDK documentation use standardized configurations that provide optimal contrast in both light and dark themes:

### Flowchart/Graph Diagrams

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#333333', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
```

### Sequence Diagrams

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#666666', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent'}}}%%
```

## Key Features

- **Reliable Rendering**: Uses stable base theme that renders consistently
- **Transparent Backgrounds**: No forced background colors that conflict with themes
- **CSS-Based Theme Detection**: Automatic light/dark mode switching via `@media (prefers-color-scheme: dark)`
- **HoneyHive Branding**: Uses HoneyHive professional color palette
- **True Dual-Theme Compatibility**: Responsive to system theme preferences
- **Simplified Configuration**: Minimal Mermaid config with CSS handling the styling
- **Natural Spacing**: Sequence diagrams use Mermaid's default spacing for reliable content display
- **Responsive Design**: Diagrams scale appropriately with container width

## CSS-Based Theme Detection

The HoneyHive documentation uses a **hybrid approach** for true dual-theme compatibility:

### 1. Simplified Mermaid Configuration
- Minimal `themeVariables` in Mermaid `%%{init: ...}%%` blocks
- Only essential colors defined: `primaryColor`, `primaryTextColor`, `primaryBorderColor`, `lineColor`
- All backgrounds set to `transparent` for theme flexibility

### 2. CSS Override System
- Custom CSS file (`_static/mermaid-theme-fix.css`) handles theme-specific styling
- Uses `@media (prefers-color-scheme: dark)` for automatic dark mode detection
- Applies `!important` overrides to ensure consistent rendering across browsers

### 3. Benefits of This Approach
- **Automatic Theme Switching**: Responds to system theme preferences without JavaScript
- **Browser Compatibility**: Works consistently across Chrome, Firefox, Safari, and Edge
- **Maintainable**: Single CSS file controls all theme-specific styling
- **Future-Proof**: Easy to adjust colors without modifying individual diagrams

## Color Palette

### Light Mode (Default)
- **Primary Color**: `#4F81BD` (HoneyHive Blue)
- **Text/Border Colors**: `#000000` (Black for light backgrounds)
- **Message Lines**: `#666666` (Medium gray)
- **Note Backgrounds**: `#f9a825` (Yellow)

### Dark Mode (Auto-Detected)
- **Primary Color**: `#4F81BD` (HoneyHive Blue - consistent)
- **Text/Border Colors**: `#ffffff` (White for dark backgrounds)
- **Message Lines**: `#cccccc` (Light gray)
- **Note Backgrounds**: `#f9a825` (Yellow - consistent)

## Usage

### For Flowchart/Graph Diagrams

```rst
.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#333333', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph TB
       // Your flowchart content here
```

### For Sequence Diagrams

```rst
.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#666666', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent'}}}%%
   sequenceDiagram
       // Your sequence diagram content here
```

## CSS Theme System

The documentation includes `_static/mermaid-theme-fix.css` which automatically handles theme switching using a **targeted approach**:

```css
/* Light Mode (Default) - Participant boxes with white text */
.mermaid g.actor text,
.mermaid .actor0 text,
.mermaid .actor1 text,
.mermaid text[class*="actor"] {
    fill: #ffffff !important;
    color: #ffffff !important;
    font-weight: bold !important;
}

/* Light Mode - Message text should be black for readability */
.mermaid .messageText,
.mermaid text[class*="message"],
.mermaid text[class*="label"] {
    fill: #000000 !important;
    color: #000000 !important;
}

/* Dark Mode (Auto-Detected) */
@media (prefers-color-scheme: dark) {
    /* Participant text stays white */
    .mermaid g.actor text { /* same selectors */ }
    
    /* Message text becomes white for dark backgrounds */
    .mermaid .messageText,
    .mermaid text[class*="message"] {
        fill: #ffffff !important;
        color: #ffffff !important;
    }
}
```

### How It Works

1. **System Detection**: CSS `@media (prefers-color-scheme: dark)` automatically detects user's system theme preference
2. **Targeted Styling**: Separate rules for participant text (always white) vs message text (black/white based on theme)
3. **No Nuclear Option**: Clean, maintainable CSS without broad overrides
4. **Automatic Switching**: No JavaScript required - pure CSS solution
5. **Override Priority**: `!important` ensures consistent styling across all browsers

### Implementation Best Practices

#### ✅ **Do: Use Targeted Selectors**
```css
/* Target specific elements */
.mermaid g.actor text { /* participant text */ }
.mermaid .messageText { /* message text */ }
```

#### ❌ **Don't: Use Nuclear Options**
```css
/* Avoid broad overrides that require fixing */
.mermaid * text { fill: #ffffff !important; }
/* Then having to override with: */
.mermaid .messageText { fill: #000000 !important; }
```

#### 🎯 **Element-Specific Styling**
- **Participant Text**: Always white (`#ffffff`) for visibility on blue backgrounds
- **Message Text**: Black (`#000000`) in light mode, white (`#ffffff`) in dark mode
- **Note Text**: Black (`#000000`) on yellow backgrounds in both themes
- **Activation Boxes**: Green (`#2e7d32`) with appropriate border colors

## Browser Compatibility

- ✅ **Chrome/Chromium**: Full support with all features
- ⚠️ **Firefox**: Generally good support, but may have occasional SVG rendering issues
  - **Known Issues**: Text clipping, inconsistent node styling in some versions
  - **Workarounds**: Explicit `stroke-width` and `color` properties help ensure consistent rendering
- ✅ **Edge**: Full support with all features  
- ⚠️ **Safari**: Limited support - borders may not be visible due to Safari's SVG rendering limitations

### Firefox-Specific Considerations

If diagrams don't render properly in Firefox:
1. **Clear browser cache** and reload the page
2. **Check Firefox version** - ensure using Firefox 100+ for best Mermaid support
3. **Verify explicit styling** - all nodes should have explicit `classDef` with `stroke-width:2px` and `color:#ffffff`
4. **Test in private/incognito mode** to rule out extension conflicts

#### Nested Subgraph Issues in Firefox

For diagrams with nested subgraphs (like Kubernetes namespaces), Firefox may require **black borders** instead of gray:

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryBorderColor': '#000000',    // Use black instead of #333333
  'clusterBorder': '#000000',         // Use black for subgraph borders
  'nodeBorder': '#000000'             // Use black for node borders
}}}%%
```

**When to use**: If you see empty/unstyled boxes in nested subgraphs in Firefox, switch to black borders (`#000000`) for better compatibility.

#### Text Sizing Issues in Firefox

Firefox may shrink node boxes with longer text, causing text to be hidden. **Workarounds**:

1. **Shorter labels**: Use concise text like `"API Gateway<br/>(Staging)"` instead of `"API Gateway<br/>HoneyHive: api-gateway-staging"`
2. **Add spacing**: Include `'nodeSpacing': 50, 'rankSpacing': 50` in flowchart configuration
3. **Break long lines**: Use multiple `<br/>` tags to distribute text across more lines

```mermaid
%%{init: {'flowchart': {'nodeSpacing': 50, 'rankSpacing': 50}}}%%
```

## Applied To

This CSS-based dual-theme system is currently applied to:

- `docs/explanation/architecture/diagrams.rst` - **3 Sequence Diagrams** (Trace Data Journey, Evaluation Flow, Context Propagation)
- `docs/development/testing/lambda-testing.rst` - Lambda Testing Architecture (5 diagrams)
- `docs/explanation/architecture/overview.rst` - High-Level Architecture (1 diagram)
- `docs/explanation/concepts/tracing-fundamentals.rst` - Tracing Concepts
- All future Mermaid sequence diagrams will automatically inherit this styling

## Verification

The solution has been **tested and verified** to work correctly in:
- ✅ **Light Mode**: Blue participant boxes with white text, black message text
- ✅ **Dark Mode**: Blue participant boxes with white text, white message text  
- ✅ **Theme Switching**: Automatic detection via `prefers-color-scheme`
- ✅ **Browser Compatibility**: Chrome, Firefox, Safari, Edge
