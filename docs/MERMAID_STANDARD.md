# Mermaid Diagram Standard Configuration

## Standard Dual-Theme Configuration

All Mermaid diagrams in the HoneyHive Python SDK documentation use this standardized configuration that works in both light and dark themes:

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#333333', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
```

## Key Features

- **Reliable Rendering**: Uses stable base theme that renders consistently
- **Transparent Backgrounds**: No forced background colors that conflict with themes
- **Dark Gray Text/Borders**: High contrast dark gray text and borders for visibility in both light and dark themes
- **HoneyHive Branding**: Uses HoneyHive blue (#4F81BD) for primary elements
- **No Background Conflicts**: Transparent backgrounds work in both light/dark themes

## Color Palette

- **Primary Color**: `#4F81BD` (HoneyHive Blue)
- **Text/Border Colors**: `#333333` (Dark gray for high contrast in both themes)
- **All Backgrounds**: `transparent` (No forced backgrounds)
- **Links**: `#333333` (Dark gray links)
- **Cluster Borders**: `#333333` (Dark gray borders)

## Usage

Copy this configuration block for any new Mermaid diagrams in the documentation:

```rst
.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#333333', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph TB
       // Your diagram content here
```

## Applied To

This configuration is currently applied to:

- `docs/development/testing/lambda-testing.rst` - Lambda Testing Architecture (5 diagrams)
- `docs/explanation/concepts/tracing-fundamentals.rst` - Tracing Concepts
- `docs/explanation/architecture/overview.rst` - System Architecture Overview
