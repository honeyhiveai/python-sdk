# README Templates - Universal Documentation Practice

**Timeless patterns for effective project README files.**

## What is a README?

A README is the first document developers see when discovering your project. It answers: "What is this? Should I use it? How do I get started?"

**Key principle:** A great README gets developers from zero to productive in 5 minutes.

---

## Universal README Structure

```markdown
# Project Name

Brief one-sentence description

[Badges: Build Status, Coverage, Version, License]

## What is this?
Brief explanation (2-3 sentences)

## Why use this?
Key benefits/features

## Quick Start
Get running in 5 minutes

## Installation
Detailed install instructions

## Usage
Examples and code

## Documentation
Link to full docs

## Contributing
How to contribute

## License
License information
```

---

## Section 1: Project Title and Description

### Pattern: Clear, Concise, Compelling

```markdown
# FastAPI

FastAPI is a modern, fast (high-performance) web framework for building 
APIs with Python 3.7+ based on standard Python type hints.

Key features:
- **Fast**: Very high performance, on par with NodeJS and Go
- **Fast to code**: Increase development speed by 200-300%
- **Fewer bugs**: Reduce human-induced errors by 40%
- **Intuitive**: Great editor support with autocompletion
- **Easy**: Designed to be easy to use and learn
- **Short**: Minimize code duplication
```

**Template:**
```markdown
# [Project Name]

[Project Name] is a [category] for [target audience] that [key value proposition].

Key features:
- **[Benefit 1]**: [Explanation]
- **[Benefit 2]**: [Explanation]
- **[Benefit 3]**: [Explanation]
```

---

## Section 2: Badges

### Pattern: Status at a Glance

```markdown
[![Build Status](https://github.com/user/repo/workflows/CI/badge.svg)](https://github.com/user/repo/actions)
[![Coverage](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/user/repo)
[![Version](https://img.shields.io/pypi/v/package.svg)](https://pypi.org/project/package/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Downloads](https://pepy.tech/badge/package)](https://pepy.tech/project/package)
```

**Common badges:**
- Build status (CI/CD passing)
- Test coverage (>80% good)
- Version (latest release)
- License (MIT, Apache, GPL)
- Downloads (popularity)
- Documentation (link)
- Dependencies (up-to-date)

---

## Section 3: Quick Start

### Pattern: Working Example in 5 Minutes

```markdown
## Quick Start

### Install
```bash
pip install fastapi uvicorn
```

### Create `main.py`
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

### Run
```bash
uvicorn main:app --reload
```

### Test
Open http://localhost:8000 in your browser.

**That's it!** See [Documentation](link) for more.
```

**Template:**
```markdown
## Quick Start

### Install
[One command to install]

### Create [filename]
[Minimal working example]

### Run
[One command to run]

### Test
[How to verify it works]

**That's it!** See [link to full docs] for more.
```

---

## Section 4: Installation

### Pattern: Support All Common Scenarios

```markdown
## Installation

### Using pip (recommended)
```bash
pip install package-name
```

### Using conda
```bash
conda install -c conda-forge package-name
```

### From source
```bash
git clone https://github.com/user/repo.git
cd repo
pip install -e .
```

### Requirements
- Python 3.7+
- pip 20.0+
- OS: Linux, macOS, Windows

### Optional Dependencies
```bash
# For database support
pip install package-name[database]

# For async support
pip install package-name[async]

# Install all optional dependencies
pip install package-name[all]
```
```

---

## Section 5: Usage Examples

### Pattern: Simple to Complex

```markdown
## Usage

### Basic Example
```python
from package import Client

client = Client(api_key="your_key")
result = client.do_something()
print(result)
```

### With Configuration
```python
client = Client(
    api_key="your_key",
    timeout=30,
    retry_count=3
)
```

### Advanced: Custom Handler
```python
from package import Client, CustomHandler

handler = CustomHandler(
    on_success=lambda x: print(f"Success: {x}"),
    on_error=lambda e: print(f"Error: {e}")
)

client = Client(api_key="your_key", handler=handler)
```

### Complete Example
See [examples/](examples/) directory for complete working examples.
```

---

## Section 6: Features

### Pattern: What It Can Do

```markdown
## Features

### Core Features
- ✅ Fast JSON serialization (10x faster than standard library)
- ✅ Automatic input validation
- ✅ Interactive API documentation (Swagger UI)
- ✅ OAuth2 authentication support
- ✅ WebSocket support

### Advanced Features
- 🚀 Background tasks
- 🚀 Database integration (SQLAlchemy, MongoDB)
- 🚀 Rate limiting
- 🚀 CORS middleware

### Coming Soon
- 🔜 GraphQL support (planned for v2.0)
- 🔜 gRPC integration
```

---

## Section 7: Documentation

### Pattern: Organized by User Journey

```markdown
## Documentation

### Getting Started
- [Installation Guide](docs/installation.md)
- [Quick Start Tutorial](docs/quickstart.md)
- [Configuration](docs/configuration.md)

### Guides
- [Authentication](docs/guides/authentication.md)
- [Database Integration](docs/guides/database.md)
- [Deployment](docs/guides/deployment.md)

### API Reference
- [Client API](docs/api/client.md)
- [Models](docs/api/models.md)
- [Exceptions](docs/api/exceptions.md)

### Advanced
- [Custom Plugins](docs/advanced/plugins.md)
- [Performance Tuning](docs/advanced/performance.md)

📚 **Full documentation:** https://docs.example.com
```

---

## Section 8: Contributing

### Pattern: Welcome and Guide Contributors

```markdown
## Contributing

We love contributions! 🎉

### How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/repo.git
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow our [Code Style Guide](CONTRIBUTING.md#code-style)
   - Add tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   pytest
   ```

5. **Submit a pull request**

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
flake8

# Run type checker
mypy src/
```

### Code of Conduct
Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

### Need Help?
- 💬 [Discord](https://discord.gg/example)
- 💬 [GitHub Discussions](https://github.com/user/repo/discussions)
- 📧 Email: contributors@example.com
```

---

## Section 9: License

### Pattern: Clear and Visible

```markdown
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
This project uses the following open-source packages:
- [Package 1](link) - MIT License
- [Package 2](link) - Apache 2.0 License
```

---

## README Templates by Project Type

### Template 1: Library/SDK

```markdown
# Library Name

One-sentence description of what it does.

[![Build](badge)] [![Coverage](badge)] [![Version](badge)]

## What is this?
2-3 sentence explanation

## Installation
```bash
pip install library-name
```

## Quick Start
```python
from library import Thing

thing = Thing()
result = thing.do_something()
```

## Features
- Feature 1
- Feature 2
- Feature 3

## Documentation
Full docs at https://docs.example.com

## Examples
See [examples/](examples/) directory

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md)

## License
MIT License
```

---

### Template 2: Web Application

```markdown
# App Name

One-sentence description

[![Build](badge)] [![Demo](badge)]

## Demo
🚀 **Live demo:** https://demo.example.com

![Screenshot](screenshot.png)

## Features
- Feature 1 with screenshot
- Feature 2 with screenshot
- Feature 3 with screenshot

## Quick Start

### Prerequisites
- Node.js 16+
- PostgreSQL 14+

### Install
```bash
git clone https://github.com/user/repo.git
cd repo
npm install
```

### Configure
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### Run
```bash
npm run dev
```

Open http://localhost:3000

## Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.

## Tech Stack
- Frontend: React, TypeScript, Tailwind CSS
- Backend: Node.js, Express, PostgreSQL
- Infrastructure: Docker, Kubernetes

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md)

## License
MIT License
```

---

### Template 3: CLI Tool

```markdown
# CLI Tool Name

One-sentence description

[![Build](badge)] [![Version](badge)]

## Installation
```bash
npm install -g cli-tool-name
# or
brew install cli-tool-name
```

## Usage

### Basic Usage
```bash
cli-tool-name [options] <arguments>
```

### Examples

**Example 1: Simple command**
```bash
$ cli-tool-name --input file.txt
Processing file.txt... Done!
```

**Example 2: With options**
```bash
$ cli-tool-name --input file.txt --output result.txt --verbose
Reading file.txt...
Processing...
Writing result.txt...
Done!
```

### Options
```
-i, --input <file>     Input file
-o, --output <file>    Output file
-v, --verbose          Verbose output
-h, --help             Show help
```

## Configuration
Create `.cli-tool-config` in your home directory:
```json
{
  "default_output": "output.txt",
  "verbose": false
}
```

## Examples
See [examples/](examples/) directory

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md)

## License
MIT License
```

---

### Template 4: Data Science Project

```markdown
# Project Name

Brief description of analysis/model

## Overview
This project analyzes [dataset] to [goal]. We use [methods] to achieve [results].

## Data
- **Source:** [Link or description]
- **Size:** X samples, Y features
- **License:** [Data license]

## Results
- **Accuracy:** 95%
- **Key findings:**
  1. Finding 1
  2. Finding 2
  3. Finding 3

## Visualizations
![Chart 1](images/chart1.png)
![Chart 2](images/chart2.png)

## Reproduce Results

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Download Data
```bash
python scripts/download_data.py
```

### Run Analysis
```bash
# Data preprocessing
python src/preprocess.py

# Train model
python src/train.py

# Generate visualizations
python src/visualize.py
```

## Project Structure
```
├── data/               # Data files (not in git)
├── notebooks/          # Jupyter notebooks
├── src/                # Source code
│   ├── preprocess.py
│   ├── train.py
│   └── visualize.py
├── models/             # Trained models
├── results/            # Output files
└── requirements.txt
```

## Requirements
- Python 3.8+
- pandas
- scikit-learn
- matplotlib

## Citation
If you use this work, please cite:
```bibtex
@misc{author2025project,
  title={Project Name},
  author={Author Name},
  year={2025},
  url={https://github.com/user/repo}
}
```

## License
MIT License (Code) / CC-BY-4.0 (Data)
```

---

## Anti-Patterns

### Anti-Pattern 1: No README

❌ Project with no README at all.

**Impact:** No one understands what it does. No adoption.

---

### Anti-Pattern 2: "See Wiki for Instructions"

❌ Empty README that redirects to wiki.

**Problem:** Extra click, wiki might be outdated, reduces visibility.

**Fix:** Put quick start in README, link to wiki for details.

---

### Anti-Pattern 3: Outdated Examples

❌ Examples that don't work with current version.

```markdown
## Example
```python
from oldpackage import OldClass  # This class was removed in v2.0!
```
```

**Fix:** Test examples in CI/CD, update regularly.

---

### Anti-Pattern 4: Installation Instructions Don't Work

❌ Missing dependencies, wrong commands, platform-specific issues not mentioned.

**Fix:** Test installation on clean machine, document all prerequisites.

---

### Anti-Pattern 5: Wall of Text

❌ Massive paragraph with no structure.

**Fix:** Use headers, bullet points, code blocks, images.

---

### Anti-Pattern 6: No Quick Start

❌ Only linking to 50-page documentation.

**Fix:** 5-minute quick start in README, link to full docs.

---

## Best Practices

### 1. Lead with Value

```markdown
# Project Name

[One sentence: what it does, who it's for, why it's better]

NOT: "This is a project I created for fun"
YES: "A fast, type-safe HTTP client for Python with async support"
```

---

### 2. Show, Don't Tell

```markdown
# BAD
This library is fast and easy to use.

# GOOD
```python
# Just 3 lines to make an authenticated API call
client = APIClient(api_key="...")
response = client.users.get(123)
print(response.name)
```
```

---

### 3. Progressive Disclosure

```
README (high-level) → Quick Start (5 min) → Tutorials (1 hour) → Reference (complete)
```

Don't dump everything in README. Link to detailed docs.

---

### 4. Visual Elements

- Screenshots for UIs
- Architecture diagrams for systems
- Performance charts for benchmarks
- GIFs for workflows

```markdown
![Demo](demo.gif)
```

---

### 5. Keep It Updated

- Update README with each release
- Test examples in CI/CD
- Review annually for outdated info

---

### 6. Accessibility

- Use meaningful link text (not "click here")
- Provide alt text for images
- Use semantic headers (h1, h2, h3)
- High contrast for badges

---

## Checklist for Great README

- [ ] Clear project name
- [ ] One-sentence description
- [ ] Badges (build, coverage, version)
- [ ] "What is this?" section
- [ ] "Why use this?" (key features/benefits)
- [ ] Quick start (5 minutes to working example)
- [ ] Installation instructions
- [ ] Usage examples (simple → complex)
- [ ] Link to full documentation
- [ ] Contributing guidelines
- [ ] License information
- [ ] Contact/support information
- [ ] All examples work with current version
- [ ] Screenshots/visuals (if applicable)
- [ ] No dead links
- [ ] Clear call to action (install, try demo, read docs)

---

## Tools for README

### Badges
- [Shields.io](https://shields.io/) - Badge service
- [Badgen](https://badgen.net/) - Alternative badge service

### Formatting
- [Markdown Guide](https://www.markdownguide.org/)
- [CommonMark](https://commonmark.org/) - Standard markdown spec

### Screenshots/GIFs
- [Carbon](https://carbon.now.sh/) - Beautiful code screenshots
- [Terminalizer](https://terminalizer.com/) - Record terminal
- [LICEcap](https://www.cockos.com/licecap/) - Screen to GIF

### Linting
- [markdownlint](https://github.com/DavidAnson/markdownlint) - Markdown linter
- [awesome-readme](https://github.com/matiassingers/awesome-readme) - Examples

---

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/development/python-documentation.md` (Python: PyPI requirements)
- See `.agent-os/standards/development/js-documentation.md` (JavaScript: npm package.json)
- See `.agent-os/standards/development/rust-documentation.md` (Rust: Cargo.toml)
- Etc.

---

**Your README is your project's first impression. Make it count. Get developers productive in 5 minutes. Show value immediately. Link to detailed docs. Keep it updated. A great README is the difference between "I'll try this" and "I'll keep looking."**
