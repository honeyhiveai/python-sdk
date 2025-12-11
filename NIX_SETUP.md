# Nix Development Environment Setup

This project uses Nix flakes and direnv for a reproducible development environment that handles all dependencies automatically.

## Prerequisites

1. **Nix with flakes enabled** (already installed ✅)
2. **direnv** (already installed ✅)

If you need to install these on a new system:
```bash
# Install Nix with flakes
sh <(curl -L https://nixos.org/nix/install) --daemon

# Enable flakes (add to ~/.config/nix/nix.conf)
experimental-features = nix-command flakes

# Install direnv
nix profile install nixpkgs#direnv
```

## Quick Start

### Option 1: Automatic Setup with direnv (Recommended)

Simply navigate to the project directory:

```bash
cd /Users/skylar/workspace/python-sdk
# direnv will automatically activate the environment
```

If this is your first time, you'll need to allow direnv:
```bash
direnv allow
```

That's it! The environment will:
- ✅ Install Python 3.12
- ✅ Create a virtual environment (`.venv`)
- ✅ Install all dev dependencies
- ✅ Set up pre-commit hooks
- ✅ Configure environment variables

### Option 2: Manual Nix Shell

If you prefer not to use direnv:

```bash
nix develop
```

## What You Get

- **Python 3.12** (meets the >=3.11 requirement)
- **Virtual environment** (`.venv`) with all dependencies
- **Development tools** installed via pip:
  - pytest, pytest-asyncio, pytest-cov, pytest-mock
  - black, isort, flake8, mypy
  - tox, pre-commit
  - sphinx (for documentation)
- **Pre-commit hooks** automatically installed
- **Consistent environment** across all developers

## Development Workflow

Once the environment is active, you can use all standard commands:

```bash
# Run tests
pytest

# Run linting
tox -e lint

# Check formatting
tox -e format

# Format code
black src tests
isort src tests

# Run pre-commit hooks manually
pre-commit run --all-files

# Build documentation
cd docs && make html
```

## How It Works

1. **flake.nix** - Defines the development environment with Python 3.12 and system dependencies
2. **.envrc** - Tells direnv to load the Nix flake automatically
3. **.venv/** - Python virtual environment created automatically (gitignored)
4. **Pre-commit hooks** - Installed automatically on first activation

## Troubleshooting

### Environment not activating

```bash
# Make sure direnv is hooked into your shell
# Add to ~/.zshrc or ~/.bashrc:
eval "$(direnv hook zsh)"  # or bash
```

### Need to reinstall dependencies

```bash
# Remove the marker file and reactivate
rm .venv/.installed
direnv reload
```

### Clean slate

```bash
# Remove virtual environment and start fresh
rm -rf .venv
direnv reload
```

## Benefits Over Traditional Setup

✅ **No global Python version conflicts** - Nix provides Python 3.12 isolated from your system  
✅ **Reproducible** - Same environment for all developers  
✅ **Automatic** - direnv activates/deactivates as you enter/leave the directory  
✅ **Fast** - Nix caches everything, subsequent activations are instant  
✅ **Clean** - Everything is contained, easy to remove  

## Files

- `flake.nix` - Nix flake definition
- `flake.lock` - Locked dependencies (commit this)
- `.envrc` - direnv configuration
- `.venv/` - Python virtual environment (gitignored)
- `.direnv/` - direnv cache (gitignored)

## Migration from Traditional Setup

If you previously used the manual setup with `python-sdk` venv:

```bash
# Remove old virtual environment
rm -rf python-sdk

# Use Nix setup instead
direnv allow
```

The Nix setup uses `.venv` as the virtual environment name instead of `python-sdk`.
