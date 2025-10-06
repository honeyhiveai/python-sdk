"""Configuration file for the Sphinx documentation builder."""

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------

project = "HoneyHive Python SDK"
copyright = "2024, HoneyHive AI"
author = "HoneyHive AI"

# The full version, including alpha/beta/rc tags
release = "0.1.0"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinxcontrib.mermaid",
    "sphinx_tabs.tabs",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "python-sdk/**",  # Exclude venv site-packages
]

# Suppress warnings from external packages
suppress_warnings = [
    "ref.ref",  # Undefined label warnings
    "toc.not_included",  # Site-packages not in toctree
]

# The suffix of source filenames.
source_suffix = ".rst"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom CSS files to include
html_css_files = [
    "mermaid-theme-fix.css",
]

# -- Options for autodoc ----------------------------------------------------

# Automatically extract type hints
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_member_order = "bysource"

# -- Options for napoleon ---------------------------------------------------

# Use Google style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

# -- Options for intersphinx -------------------------------------------------

# Link to Python standard library documentation
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "opentelemetry": ("https://opentelemetry-python.readthedocs.io/en/latest/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for markdown ---------------------------------------------------

# RST-specific extensions and settings

# -- Project-specific settings -----------------------------------------------

# Add any custom settings here
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
}

# SEO and search optimization
html_meta = {
    "description": "Comprehensive Python SDK for LLM observability and evaluation with OpenTelemetry integration and BYOI architecture",
    "keywords": "LLM observability, OpenTelemetry, Python SDK, AI monitoring, machine learning, tracing, evaluation, OpenAI, Anthropic, HoneyHive",
    "author": "HoneyHive AI",
    "robots": "index,follow",
    "viewport": "width=device-width, initial-scale=1",
}

# Additional HTML context for templates
html_context = {
    "github_user": "honeyhiveai",
    "github_repo": "python-sdk",
    "github_version": "main",
    "doc_path": "docs/",
}

# Show source links
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True

# Search optimization
html_search_language = "en"
# Test comment
