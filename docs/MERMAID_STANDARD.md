# Mermaid Diagram Standard Configuration

## Standard Dual-Theme Configuration

All Mermaid diagrams in the HoneyHive Python SDK documentation use this standardized configuration that provides optimal contrast in both light and dark themes:

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#ffffff', 'lineColor': '#ffffff', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#ffffff', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#ffffff', 'linkWidth': 2}}}%%
```

## Key Features

- **Reliable Rendering**: Uses stable base theme that renders consistently
- **Transparent Backgrounds**: No forced background colors that conflict with themes
- **High Contrast Text**: Uses white (#ffffff) text and borders for maximum visibility
- **HoneyHive Branding**: Uses HoneyHive blue (#4F81BD) for primary elements
- **Dual-Theme Compatibility**: White text provides excellent contrast on both light and dark backgrounds

## Color Palette

- **Primary Color**: `#4F81BD` (HoneyHive Blue)
- **Text/Border Colors**: `#ffffff` (White for maximum contrast in both themes)
- **All Backgrounds**: `transparent` (No forced backgrounds)
- **Links**: `#ffffff` (White links for visibility)
- **Cluster Borders**: `#ffffff` (White borders for definition)

## Usage

Copy this configuration block for any new Mermaid diagrams in the documentation:

```rst
.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#ffffff', 'lineColor': '#ffffff', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#ffffff', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#ffffff', 'linkWidth': 2}}}%%
   graph TB
       // Your diagram content here
```

## Applied To

This configuration is currently applied to:

- `docs/development/testing/lambda-testing.rst` - Lambda Testing Architecture (5 diagrams)
- `docs/explanation/concepts/tracing-fundamentals.rst` - Tracing Concepts
- `docs/explanation/architecture/overview.rst` - System Architecture Overview
