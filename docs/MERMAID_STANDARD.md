# Mermaid Diagram Standard Configuration

## Standard Dual-Theme Configuration

All Mermaid diagrams in the HoneyHive Python SDK documentation use standardized configurations that provide optimal contrast in both light and dark themes:

### Flowchart/Graph Diagrams

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'nodeBkg': '#1565c0', 'nodeBorder': '#333333', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'defaultLinkColor': '#333333', 'titleColor': '#333333', 'edgeLabelBackground': 'transparent', 'nodeTextColor': '#ffffff'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
```

### Sequence Diagrams

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'actorBkg': '#1565c0', 'actorBorder': '#333333', 'actorTextColor': '#ffffff', 'actorLineColor': '#333333', 'signalColor': '#333333', 'signalTextColor': '#333333', 'activationBorderColor': '#333333', 'activationBkgColor': '#2e7d32', 'sequenceNumberColor': '#333333', 'sectionBkgColor': 'transparent', 'altSectionBkgColor': 'transparent', 'gridColor': '#333333', 'gridTextColor': '#333333', 'taskBkgColor': '#1565c0', 'taskTextColor': '#ffffff', 'taskTextLightColor': '#ffffff', 'taskTextOutsideColor': '#333333', 'taskTextClickableColor': '#333333', 'activeTaskBkgColor': '#2e7d32', 'activeTaskBorderColor': '#333333', 'gridTextSize': '11px', 'taskTextSize': '11px'}}}%%
```

## Key Features

- **Reliable Rendering**: Uses stable base theme that renders consistently
- **Transparent Backgrounds**: No forced background colors that conflict with themes
- **High Contrast Text**: Uses white (#ffffff) text on colored backgrounds for maximum visibility
- **HoneyHive Branding**: Uses HoneyHive professional color palette
- **True Dual-Theme Compatibility**: Optimized configurations for both light and dark documentation themes
- **Explicit Node Styling**: Ensures consistent node backgrounds and text colors across all themes
- **Natural Spacing**: Sequence diagrams use Mermaid's default spacing for reliable content display
- **Responsive Design**: Diagrams scale appropriately with container width

## Color Palette

- **Primary Color**: `#4F81BD` (HoneyHive Blue)
- **Text/Border Colors**: `#ffffff` (White for maximum contrast in both themes)
- **All Backgrounds**: `transparent` (No forced backgrounds)
- **Links**: `#333333` (Dark gray links visible in both themes)
- **Cluster Borders**: `#333333` (Dark gray borders visible in both themes)

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

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#1565c0', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'secondaryColor': '#2e7d32', 'tertiaryColor': '#ef6c00', 'background': 'transparent', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'actorBkg': '#1565c0', 'actorBorder': '#333333', 'actorTextColor': '#ffffff', 'actorLineColor': '#333333', 'signalColor': '#333333', 'signalTextColor': '#333333', 'activationBorderColor': '#333333', 'activationBkgColor': '#2e7d32', 'sequenceNumberColor': '#333333', 'sectionBkgColor': 'transparent', 'altSectionBkgColor': 'transparent', 'gridColor': '#333333', 'gridTextColor': '#333333', 'taskBkgColor': '#1565c0', 'taskTextColor': '#ffffff', 'taskTextLightColor': '#ffffff', 'taskTextOutsideColor': '#333333', 'taskTextClickableColor': '#333333', 'activeTaskBkgColor': '#2e7d32', 'activeTaskBorderColor': '#333333', 'gridTextSize': '11px', 'taskTextSize': '11px'}}}%%
   sequenceDiagram
       // Your sequence diagram content here
```

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

This configuration is currently applied to:

- `docs/development/testing/lambda-testing.rst` - Lambda Testing Architecture (5 diagrams)
- `docs/explanation/architecture/overview.rst` - High-Level Architecture (1 diagram)
- `docs/explanation/architecture/diagrams.rst` - Comprehensive Architecture Diagrams (15 diagrams)
- `docs/explanation/concepts/tracing-fundamentals.rst` - Tracing Concepts
- `docs/explanation/architecture/overview.rst` - System Architecture Overview
