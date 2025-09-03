# Documentation Hosting Strategy for HoneyHive Python SDK

## Recommended Solution: GitHub Pages + Netlify/Vercel

### Primary Documentation (Main Branch) - GitHub Pages
- **Host**: GitHub Pages
- **URL**: `https://honeyhiveai.github.io/python-sdk/`
- **Branch**: `gh-pages` or dedicated docs branch
- **Version**: Latest stable from `main`

### PR Preview Documentation - Netlify or Vercel
- **Host**: Netlify (recommended) or Vercel
- **URL**: Dynamic preview URLs per PR
- **Example**: `https://pr-123--honeyhive-docs.netlify.app`
- **Automatic**: Deploy on every PR

## Implementation Options

## Option 1: GitHub Pages + Netlify (Recommended)

### Advantages:
- GitHub Pages for stable docs (free for public repos)
- Netlify for PR previews (free tier sufficient)
- Automatic PR comments with preview links
- Version switcher support
- Search functionality

### Setup:
1. Main docs on GitHub Pages
2. PR previews on Netlify
3. sphinx-multiversion for version management

## Option 2: Read the Docs (Simplest)

### Advantages:
- Built specifically for Sphinx
- Automatic versioning
- PR preview builds
- Built-in search
- No configuration needed

### Limitations:
- Ads on free tier
- Less customization
- Single domain for all versions

## Option 3: GitHub Pages with Mike (Versioning)

### Advantages:
- All on GitHub (no external services)
- Mike handles versioning elegantly
- Clean URLs
- Version aliases (latest, stable, dev)

### Limitations:
- No automatic PR previews
- Manual version management

## Option 4: Self-Hosted (Maximum Control)

### Advantages:
- Complete control
- Custom domain
- Advanced features
- No limitations

### Limitations:
- Requires infrastructure
- Maintenance overhead
- Cost

## Recommended Implementation

### 1. GitHub Pages for Main Documentation

```yaml
# .github/workflows/docs-main.yml
name: Deploy Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for versioning

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
          pip install sphinx-multiversion myst-parser

      - name: Build documentation
        run: |
          cd docs
          make html
          touch _build/html/.nojekyll

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
          cname: docs.honeyhive.ai  # Optional custom domain
```

### 2. Netlify for PR Previews

```yaml
# .github/workflows/docs-preview.yml
name: PR Documentation Preview

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  build-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
          pip install myst-parser

      - name: Build documentation
        run: |
          cd docs
          make html
          touch _build/html/.nojekyll

      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v2.0
        with:
          publish-dir: './docs/_build/html'
          production-deploy: false
          github-token: ${{ secrets.GITHUB_TOKEN }}
          deploy-message: "PR #${{ github.event.pull_request.number }}"
          enable-pull-request-comment: true
          enable-commit-comment: false
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

### 3. Sphinx Configuration for Versioning

```python
# docs/conf.py
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'HoneyHive Python SDK'
copyright = '2024, HoneyHive'
author = 'HoneyHive Team'

# Version info
from honeyhive import __version__
release = __version__
version = __version__

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
    'myst_parser',
    'sphinx_autodoc_typehints',
    'sphinx_multiversion',  # For version support
]

# Version switcher configuration
html_theme_options = {
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

# Multiversion settings
smv_branch_whitelist = r'^(main|master|v\d+\.\d+\.x)$'
smv_tag_whitelist = r'^v\d+\.\d+\.\d+$'
smv_remote_whitelist = r'^origin$'
smv_released_pattern = r'^tags/v\d+\.\d+\.\d+$'
```

### 4. Netlify Configuration

```toml
# netlify.toml
[build]
  publish = "docs/_build/html"
  command = """
    pip install -e . && \
    pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints myst-parser && \
    cd docs && \
    make html
  """

[build.environment]
  PYTHON_VERSION = "3.11"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "SAMEORIGIN"
    X-Content-Type-Options = "nosniff"
    X-XSS-Protection = "1; mode=block"

[[redirects]]
  from = "/"
  to = "/en/latest/"
  status = 302
  force = false
```

### 5. Documentation Structure

```
docs/
├── _static/           # Static files (CSS, JS)
├── _templates/        # Custom templates
├── api/              # API documentation
│   ├── client.rst
│   ├── tracer.rst
│   └── evaluation.rst
├── guides/           # User guides
│   ├── quickstart.rst
│   ├── installation.rst
│   └── configuration.rst
├── examples/         # Example code
├── conf.py          # Sphinx configuration
├── index.rst        # Main index
├── Makefile         # Build commands
└── requirements.txt # Doc dependencies
```

### 6. Version Switcher Template

```html
<!-- docs/_templates/versions.html -->
<div class="version-switcher">
  <select id="version-select" onchange="switchVersion(this.value)">
    <option value="latest">Latest ({{ version }})</option>
    <option value="stable">Stable</option>
    <option value="v0.1.0">v0.1.0</option>
    <option value="dev">Development</option>
  </select>
</div>

<script>
function switchVersion(version) {
  const currentPath = window.location.pathname;
  const newPath = currentPath.replace(/\/[^\/]+\//, `/${version}/`);
  window.location.pathname = newPath;
}
</script>
```

## Alternative: Read the Docs Setup

If you prefer simplicity over customization:

```yaml
# .readthedocs.yml
version: 2

sphinx:
  configuration: docs/conf.py
  fail_on_warning: true

python:
  version: "3.11"
  install:
    - method: pip
      path: .
      extra_requirements:
        - docs

build:
  os: ubuntu-22.04
  tools:
    python: "3.11"
  jobs:
    post_create_environment:
      - pip install -e .

formats:
  - pdf
  - epub
  - htmlzip
```

## Best Practices

### 1. Documentation Versioning
- Tag releases properly: `v0.1.0`, `v0.2.0`
- Maintain stable branch for latest release
- Keep dev/main for ongoing development

### 2. PR Preview Comments
```yaml
- name: Comment PR with preview link
  uses: actions/github-script@v6
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: `📚 Documentation preview: ${preview_url}`
      })
```

### 3. Search Integration
```python
# conf.py - Enable search
extensions.append('sphinx.ext.githubpages')
html_theme_options['search_bar_position'] = 'navbar'
```

### 4. API Documentation
```python
# Auto-generate from docstrings
extensions.append('sphinx.ext.autodoc')
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
```

## Recommended: GitHub Pages + Netlify

This combination provides:
- ✅ Free hosting for public repos
- ✅ Automatic PR previews
- ✅ Version management
- ✅ Custom domains
- ✅ No ads
- ✅ Fast builds
- ✅ Good SEO

## Setup Steps:

1. **GitHub Pages**: Enable in repo settings
2. **Netlify Account**: Create and link to repo
3. **Secrets**: Add `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID`
4. **Workflows**: Add the YAML files above
5. **DNS**: Point docs subdomain to GitHub Pages

This gives you professional documentation with both stable releases and PR previews!
