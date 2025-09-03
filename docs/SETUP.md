# Documentation Setup Guide for HoneyHive Python SDK

This guide explains how to set up and deploy documentation with support for:
- **Production docs** from the main branch
- **PR preview docs** for pull requests
- **Versioned documentation** for releases

## Quick Start

### 1. Local Development

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build docs locally
cd docs
make clean
make html

# View docs
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
```

### 2. Enable GitHub Pages

1. Go to Settings → Pages in your GitHub repository
2. Source: Deploy from a branch
3. Branch: `gh-pages` / `root`
4. Save

### 3. Set Up Netlify for PR Previews

1. Sign up at [netlify.com](https://netlify.com)
2. Create a new site from Git
3. Connect your GitHub repository
4. Build settings:
   - Base directory: `.`
   - Build command: `pip install -e . && cd docs && make html`
   - Publish directory: `docs/_build/html`
5. Get your API token and site ID:
   - API Token: User Settings → Applications → Personal Access Tokens
   - Site ID: Site Settings → General → Site Information

### 4. Add GitHub Secrets

Add these secrets to your repository (Settings → Secrets):

```bash
NETLIFY_AUTH_TOKEN=<your-netlify-token>
NETLIFY_SITE_ID=<your-site-id>
```

## Documentation Structure

```
docs/
├── _static/              # Static files (CSS, JS, images)
├── _templates/           # Custom Sphinx templates
├── api/                  # API reference documentation
│   ├── index.rst
│   ├── client.rst       # API client docs
│   ├── tracer.rst       # Tracer docs
│   └── evaluation.rst   # Evaluation framework docs
├── guides/              # User guides
│   ├── quickstart.rst
│   ├── installation.rst
│   ├── configuration.rst
│   └── examples.rst
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation index
├── Makefile             # Build commands
├── requirements.txt     # Documentation dependencies
└── SETUP.md            # This file
```

## Deployment Workflows

### Main Branch → GitHub Pages

The `.github/workflows/docs-deploy.yml` workflow:
- Triggers on pushes to `main`
- Builds documentation with Sphinx
- Deploys to GitHub Pages
- URL: `https://<username>.github.io/<repo>/`

### Pull Requests → Netlify Previews

The `.github/workflows/docs-preview.yml` workflow:
- Triggers on PR changes
- Builds documentation
- Deploys to Netlify
- Comments on PR with preview URL
- URL: `https://pr-<number>--<site-name>.netlify.app`

### Tagged Releases → Versioned Docs

The `.github/workflows/docs-versioned.yml` workflow:
- Triggers on version tags (`v*`)
- Uses `mike` for version management
- Maintains multiple versions
- URLs:
  - Latest: `/latest/`
  - Stable: `/stable/`
  - Specific: `/0.1.0/`

## Writing Documentation

### ReStructuredText Files (.rst)

```rst
Page Title
==========

Section
-------

Subsection
~~~~~~~~~~

**Bold text**, *italic text*, ``code``

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   
   tracer = HoneyHiveTracer.init()

.. note::
   This is a note.

.. warning::
   This is a warning.
```

### Markdown Files (.md)

```markdown
# Page Title

## Section

**Bold text**, *italic text*, `code`

```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init()
```

> **Note:** This is a note.

> **Warning:** This is a warning.
```

### API Documentation

Use docstrings in your Python code:

```python
def my_function(param1: str, param2: int = 0) -> bool:
    """Brief description of the function.
    
    Longer description with more details about what
    the function does and how to use it.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        
    Example:
        >>> my_function("test", 42)
        True
    """
    pass
```

## Sphinx Configuration

Key settings in `docs/conf.py`:

```python
# Project information
project = 'HoneyHive Python SDK'
copyright = '2024, HoneyHive'
author = 'HoneyHive Team'

# Extensions
extensions = [
    'sphinx.ext.autodoc',        # Auto-generate from docstrings
    'sphinx.ext.napoleon',        # Google/NumPy docstring support
    'sphinx.ext.viewcode',        # Add source code links
    'sphinx.ext.intersphinx',     # Link to other projects
    'sphinx_rtd_theme',          # Read the Docs theme
    'myst_parser',               # Markdown support
    'sphinx_autodoc_typehints',  # Type hint support
    'sphinx_copybutton',         # Copy button for code blocks
]

# Theme
html_theme = 'sphinx_rtd_theme'

# Theme options
html_theme_options = {
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
}
```

## Version Management with Mike

### Initial Setup

```bash
# Install mike
pip install mike

# Initialize gh-pages branch
mike deploy --push --update-aliases 0.1.0 latest

# Set default version
mike set-default --push latest
```

### Deploying Versions

```bash
# Deploy a new version
mike deploy --push --update-aliases 0.2.0 latest

# Deploy development version
mike deploy --push dev

# List versions
mike list

# Delete a version
mike delete --push 0.1.0

# Retitle a version
mike retitle --push 0.2.0 "0.2.0 (Current)"
```

## Custom Domain Setup

### For GitHub Pages

1. Create `CNAME` file in `docs/` with your domain:
   ```
   docs.honeyhive.ai
   ```

2. Configure DNS:
   - CNAME record: `docs` → `<username>.github.io`

### For Netlify

1. Add custom domain in Netlify site settings
2. Configure DNS as instructed by Netlify

## Troubleshooting

### Build Failures

```bash
# Clean build artifacts
cd docs
make clean
rm -rf _build

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Build with verbose output
make html SPHINXOPTS="-v"
```

### Missing API Documentation

```bash
# Ensure package is installed
pip install -e .

# Check Python path in conf.py
sys.path.insert(0, os.path.abspath('..'))

# Force rebuild
sphinx-build -E -b html . _build/html
```

### Preview Not Working

1. Check GitHub Actions logs
2. Verify Netlify secrets are set
3. Check netlify.toml configuration
4. Ensure PR has documentation changes

## Best Practices

1. **Keep docs in sync**: Update docs with code changes
2. **Use type hints**: Improves auto-generated docs
3. **Write good docstrings**: They become your API docs
4. **Include examples**: Show real usage patterns
5. **Test locally**: Always preview before pushing
6. **Version appropriately**: Tag releases properly
7. **Cross-reference**: Link between related topics

## Automation Features

### PR Comments

The preview workflow automatically comments on PRs with:
- Preview URL (if Netlify configured)
- Build status
- Artifact download link (fallback)

### Version Aliases

Mike maintains aliases:
- `latest`: Most recent development
- `stable`: Latest release
- `dev`: Development branch
- Version numbers: `0.1.0`, `0.2.0`, etc.

### Search

Sphinx automatically generates search functionality.
Enhanced with `sphinx-search` extension.

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
- [Mike Documentation](https://github.com/jimporter/mike)
- [Netlify Documentation](https://docs.netlify.com/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)

## Support

For documentation issues:
1. Check this guide
2. Review GitHub Actions logs
3. Open an issue with details
