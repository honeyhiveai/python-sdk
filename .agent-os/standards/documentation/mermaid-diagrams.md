# Mermaid Diagram Standards

**Date**: 2025-09-04  
**Status**: Active  
**Scope**: All HoneyHive Python SDK documentation

## Overview

This document defines the mandatory standards for all Mermaid diagrams in the HoneyHive Python SDK project. These standards ensure professional appearance and excellent readability in both light and dark themes.

## 🚨 CRITICAL Requirements

### Dual-Theme Configuration

**ALL Mermaid diagrams MUST use this EXACT configuration:**

```rst
.. mermaid::

   %%{init: {'theme':'base', 'themeVariables': {'primaryColor': '#4F81BD', 'primaryTextColor': '#ffffff', 'primaryBorderColor': '#333333', 'lineColor': '#333333', 'mainBkg': 'transparent', 'secondBkg': 'transparent', 'tertiaryColor': 'transparent', 'clusterBkg': 'transparent', 'clusterBorder': '#333333', 'edgeLabelBackground': 'transparent', 'background': 'transparent'}, 'flowchart': {'linkColor': '#333333', 'linkWidth': 2}}}%%
   graph TB
       // Your diagram content here
```

### Key Configuration Elements

- **`theme: 'base'`**: Provides stable foundation for customization
- **`primaryTextColor: '#ffffff'`**: White text for maximum contrast
- **`lineColor: '#333333'`**: Dark gray lines visible in both themes
- **`linkColor: '#333333'`**: Dark gray arrows visible in both themes
- **`mainBkg: 'transparent'`**: No background conflicts with themes
- **`primaryColor: '#4F81BD'`**: HoneyHive brand blue

## 🎨 HoneyHive Color Palette

### Professional Colors (MANDATORY)

Use these colors for node fills to maintain brand consistency:

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Primary Blue | `#1565c0` | Main elements, primary actions |
| Success Green | `#2e7d32` | Success states, completed items |
| Warning Orange | `#ef6c00` | Warnings, important notices |
| Action Purple | `#7b1fa2` | Actions, tests, processes |
| Alert Yellow | `#f9a825` | Alerts, attention needed |
| Error Red | `#c62828` | Errors, failures, critical issues |

### Color Usage Guidelines

- **Primary Blue**: Use for main workflow elements, primary processes
- **Success Green**: Use for completed states, successful operations
- **Warning Orange**: Use for warnings, results, important metrics
- **Action Purple**: Use for tests, actions, user interactions
- **Alert Yellow**: Use for alerts, warnings that need attention
- **Error Red**: Use for errors, failures, critical issues

## ✅ ClassDef Requirements

### MANDATORY Pattern

**ALL classDef definitions MUST include `color:#ffffff`:**

```mermaid
classDef primary fill:#1565c0,stroke:#333333,stroke-width:2px,color:#ffffff
classDef success fill:#2e7d32,stroke:#333333,stroke-width:2px,color:#ffffff
classDef warning fill:#ef6c00,stroke:#333333,stroke-width:2px,color:#ffffff
classDef action fill:#7b1fa2,stroke:#333333,stroke-width:2px,color:#ffffff
classDef alert fill:#f9a825,stroke:#333333,stroke-width:2px,color:#ffffff
classDef error fill:#c62828,stroke:#333333,stroke-width:2px,color:#ffffff
```

### ClassDef Components

- **`fill`**: Use HoneyHive professional colors from the palette
- **`stroke:#333333`**: Dark gray borders visible in both themes
- **`stroke-width:2px`**: Consistent border width
- **`color:#ffffff`**: **CRITICAL** - White text for readability

## ❌ Prohibited Patterns

### NEVER Use These

- ❌ **Light fill colors** (`#ffcdd2`, `#e3f2fd`) - Poor contrast in dark themes
- ❌ **Missing `color:#ffffff`** in classDef - Text invisible in dark themes  
- ❌ **White arrows** (`linkColor: '#ffffff'`) - Invisible in light themes
- ❌ **Dark text** (`primaryTextColor: '#333333'`) - Invisible in dark themes
- ❌ **Non-transparent backgrounds** - Conflicts with theme switching
- ❌ **Random colors** - Must use HoneyHive palette

### Common Mistakes

1. **Forgetting `color:#ffffff`** in classDef definitions
2. **Using light pastel colors** that don't provide sufficient contrast
3. **Setting white arrow colors** that disappear in light themes
4. **Hardcoded backgrounds** that conflict with documentation themes

## 📋 Quality Checklist

Before committing ANY Mermaid diagram, verify:

- ✅ Uses exact HoneyHive dual-theme configuration
- ✅ All classDef definitions include `color:#ffffff`
- ✅ Uses only HoneyHive professional color palette
- ✅ Arrows/lines are dark gray (`#333333`) for dual-theme visibility
- ✅ Text is readable on all colored backgrounds
- ✅ No hardcoded backgrounds or theme-specific colors
- ✅ Follows semantic color usage (green=success, red=error, etc.)

## 🧪 Testing Requirements

### Visual Testing

Test ALL diagrams in both themes:

1. **Light Theme**: Verify arrows and text are clearly visible
2. **Dark Theme**: Verify arrows and text are clearly visible
3. **Color Contrast**: Ensure professional appearance
4. **Brand Consistency**: Verify colors match HoneyHive standards

### Browser Testing

Test in multiple browsers:
- ✅ Chrome/Chromium (Full support)
- ✅ Firefox (Full support - optimize node labels for best rendering)
- ✅ Edge (Full support)
- ⚠️ Safari (Limited support - borders may not be visible)
- ✅ Arc (Chromium-based - Full support)

**Firefox Optimization Tips:**
- Keep node labels concise (avoid very long text)
- Simplify multi-line text where possible
- Use hyphens for ranges (e.g., "3.11-3.13" vs "3.11/3.12/3.13")
- Test complex diagrams in Firefox during development

## 📚 Reference Files

- **Standard Definition**: `docs/MERMAID_STANDARD.md`
- **Implementation Examples**: `docs/development/testing/lambda-testing.rst`
- **Agent OS Rules**: `.cursorrules` (Mermaid Diagram Standards section)

## 🔄 Updates and Maintenance

### When to Update

- New HoneyHive brand colors are introduced
- Mermaid library updates change behavior
- Documentation theme changes affect diagram rendering
- User feedback indicates visibility issues

### Update Process

1. Update this standards document
2. Update `docs/MERMAID_STANDARD.md`
3. Update `.cursorrules` Mermaid section
4. Update all existing diagrams to new standard
5. Test in both light and dark themes
6. Commit changes with appropriate documentation

## 🎯 Success Metrics

- **100% compliance** with dual-theme configuration
- **Zero visibility issues** reported in either theme
- **Professional appearance** matching HoneyHive brand
- **Consistent color usage** across all diagrams
- **Excellent readability** in all supported browsers

---

**Compliance**: This standard is MANDATORY for all contributors and AI assistants working on the HoneyHive Python SDK project.
