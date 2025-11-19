# Documentation Utilities

This directory contains tools for validating and maintaining documentation quality.

## Navigation Validation

### Overview

The navigation validation system automatically discovers and validates all documentation pages, ensuring:

- All `.rst` files are accessible as `.html` pages
- Navigation links work correctly
- Cross-references between pages are valid
- Search functionality is available
- New documentation integrates properly

### Self-Updating Design

The validation system **automatically adapts** as documentation grows:

- **Auto-Discovery**: Scans `docs/` directory for all `.rst` files
- **Dynamic Validation**: No manual updates to validation lists required
- **Comprehensive Coverage**: Tests every documentation page automatically
- **Integration Checking**: Validates toctree and navigation structure

### Usage

#### Local Validation (Recommended)

```bash
# Install dependencies
pip install -r docs/utils/requirements.txt

# Build documentation locally
tox -e docs

# Validate navigation
python docs/utils/validate_navigation.py --local
```

#### Production Validation

```bash
# Validate live documentation site
python docs/utils/validate_navigation.py \
  --base-url https://honeyhiveai.github.io/python-sdk/
```

#### Custom URL Validation

```bash
# Validate any deployment
python docs/utils/validate_navigation.py \
  --base-url https://your-docs-site.com \
  --timeout 30
```

### Validation Scope

The system validates:

1. **Page Accessibility**: All discovered `.rst` → `.html` pages exist
2. **Navigation Structure**: Main navigation and toctree links work
3. **Cross-References**: Internal links between documentation sections
4. **Search Functionality**: Sphinx search files and functionality
5. **Structural Integrity**: Overall documentation organization

### Integration with Development Workflow

#### Pre-Commit Validation

Add to your development workflow:

```bash
# Before committing documentation changes
python docs/utils/validate_navigation.py --local
```

#### CI/CD Integration

The validation runs automatically via GitHub Actions:

- **After Deployment**: Validates navigation after docs are deployed
- **Weekly Monitoring**: Catches issues that develop over time
- **Manual Triggers**: On-demand validation for specific testing

### Common Issues Detected

- New `.rst` files not added to toctree
- Broken cross-references after restructuring
- Missing index pages for new sections
- Orphaned documentation files
- Invalid internal link targets
- Navigation integration problems

### Extending Validation

To add new validation checks:

1. Edit `validate_navigation.py`
2. Add new validation methods to `NavigationValidator` class
3. Call new methods in `run_full_validation()`
4. Update this README with new capabilities

### Requirements

- Python 3.11+
- requests
- beautifulsoup4
- lxml

See `requirements.txt` for specific versions.

## Agent OS Integration

This validation system is integrated with Agent OS standards:

- **Mandatory for all new documentation**
- **Self-updating as documentation grows** 
- **Quality gate for documentation deployments**
- **Prevents broken navigation in production**

For details, see `.agent-os/standards/best-practices.md` section on "Documentation Navigation Validation".
