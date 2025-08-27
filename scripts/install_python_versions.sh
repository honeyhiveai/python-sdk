#!/bin/bash
# Script to install required Python versions for tox testing
# This script helps set up the Python versions needed for the HoneyHive SDK tests

set -e

echo "Installing Python versions for HoneyHive SDK tox testing..."

# Check if pyenv is available
if command -v pyenv &> /dev/null; then
    echo "pyenv found. Installing Python versions with pyenv..."
    
    # Install Python versions
    pyenv install 3.10.13 || echo "Python 3.10.13 installation failed or already exists"
    pyenv install 3.11.7 || echo "Python 3.11.7 installation failed or already exists"
    pyenv install 3.12.1 || echo "Python 3.12.1 installation failed or already exists"
    
    echo "Python versions installed with pyenv."
    echo "Available versions:"
    pyenv versions
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS detected. Installing Python versions with Homebrew..."
    
    if command -v brew &> /dev/null; then
        brew install python@3.10 python@3.11 python@3.12
        echo "Python versions installed with Homebrew."
    else
        echo "Homebrew not found. Please install Homebrew first:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux detected. Installing Python versions with system package manager..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y python3.10 python3.11 python3.12
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y python310 python311 python312
    elif command -v dnf &> /dev/null; then
        # Fedora
        sudo dnf install -y python3.10 python3.11 python3.12
    else
        echo "Unsupported Linux distribution. Please install Python versions manually."
        exit 1
    fi
    
    echo "Python versions installed with system package manager."
    
else
    echo "Unsupported operating system: $OSTYPE"
    echo "Please install Python versions manually:"
echo "  - Python 3.10.13"
    echo "  - Python 3.11.7"
    echo "  - Python 3.12.1"
    exit 1
fi

echo ""
echo "Verifying Python versions..."

echo "Python 3.10: $(python3.10 --version 2>/dev/null || echo 'Not found')"
echo "Python 3.11: $(python3.11 --version 2>/dev/null || echo 'Not found')"
echo "Python 3.12: $(python3.12 --version 2>/dev/null || echo 'Not found')"

echo ""
echo "Next steps:"
echo "1. Install tox: pip install tox>=4.0"
echo "2. Run tests: tox"
echo "3. Or use the helper script: python scripts/run_tox.py test"
echo ""
echo "Note: Some Python versions may not be available on all systems."
echo "Tox will skip environments for unavailable Python versions."
