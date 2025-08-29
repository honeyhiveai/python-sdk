# HoneyHive Python SDK Documentation

This directory contains the Sphinx documentation for the HoneyHive Python SDK.

## Building the Documentation

### Using Tox (Recommended)

```bash
# Build the documentation
tox -e docs

# The built HTML files will be in docs/_build/html/
```

### Manual Build

```bash
# Install dependencies
pip install sphinx sphinx-rtd-theme myst-parser

# Build the documentation
sphinx-build -b html docs docs/_build/html
```

## Viewing the Documentation

### Local HTTP Server

After building, you can serve the documentation locally:

```bash
# Using the provided script
python docs/serve.py

# Or manually
cd docs/_build/html
python -m http.server 8000
```

Then open your browser to `http://localhost:8000`

### Direct File Access

You can also open `docs/_build/html/index.html` directly in your browser.

## Documentation Structure

- **Main Documentation**: `index.rst` - Entry point and overview
- **API Reference**: `api/index.rst` - Complete API documentation
- **Tracing**: `tracer/index.rst` - OpenTelemetry integration
- **Evaluation**: `evaluation/index.rst` - AI evaluation framework
- **Utilities**: `utils/index.rst` - Helper modules
- **Examples**: `examples/` - Usage examples and patterns

## Configuration

The documentation is configured in `conf.py` with:

- **Theme**: Read the Docs theme for professional appearance
- **Extensions**: autodoc, napoleon, viewcode, intersphinx, todo, myst-parser
- **Markdown Support**: Full support for .md files via MyST parser
- **Auto-documentation**: Automatic extraction of docstrings from Python code

## Adding New Documentation

### Python Modules

Documentation for Python modules is automatically generated from docstrings. Just add proper docstrings to your code and they'll appear in the docs.

### New Pages

1. Create a new `.rst` or `.md` file
2. Add it to the appropriate `toctree` in the main `index.rst`
3. Rebuild the documentation

### API Documentation

The API documentation is automatically generated from the source code using Sphinx's autodoc extension. Make sure your classes and methods have proper docstrings.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the Python path includes the `src/` directory
2. **Missing Dependencies**: Install required packages with `pip install -r requirements.txt`
3. **Build Failures**: Check that all referenced files exist and are properly formatted

### Warnings

The build may show warnings about:
- Documents not included in toctrees (normal for standalone files)
- Cross-reference targets not found (check your links)
- Title underlines too short (make them longer than the title)

Most warnings don't prevent the build from succeeding.

## Deployment

The built documentation can be deployed to any static hosting service:

- **GitHub Pages**: Push the `_build/html/` contents to a `gh-pages` branch
- **Read the Docs**: Connect your repository for automatic builds
- **Netlify/Vercel**: Deploy the `_build/html/` directory

## Contributing

When adding new features or APIs:

1. Update the relevant documentation files
2. Add proper docstrings to your code
3. Update examples if needed
4. Rebuild and test the documentation
5. Ensure all links and references work correctly
