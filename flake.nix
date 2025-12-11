{
  description = "HoneyHive Python SDK Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        # Python with required version (3.11+)
        python = pkgs.python312;
        
        # Python development dependencies
        pythonEnv = python.withPackages (ps: with ps; [
          pip
          setuptools
          wheel
          virtualenv
          requests
          beautifulsoup4
          pyyaml
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            # Python environment
            pythonEnv
            
            # Development tools
            pkgs.git
            
            # For documentation building
            pkgs.gnumake
            
            # Useful utilities
            pkgs.which
            pkgs.curl
            pkgs.jq
          ];

          shellHook = ''
            # Set up color output
            export TERM=xterm-256color
            
            # Create virtual environment if it doesn't exist
            if [ ! -d .venv ]; then
              echo "🔧 Creating virtual environment..."
              ${pythonEnv}/bin/python -m venv .venv
            fi
            
            # Activate virtual environment
            source .venv/bin/activate
            
            # Upgrade pip (silent)
            pip install --upgrade pip > /dev/null 2>&1
            
            # Install package in editable mode with dev dependencies
            if [ ! -f .venv/.installed ]; then
              echo "📦 Installing dependencies (first run)..."
              pip install -e ".[dev,docs]" > /dev/null 2>&1
              pip install pre-commit>=3.6.0 tox>=4.0.0 > /dev/null 2>&1
              touch .venv/.installed
              echo "✨ Environment ready!"
              echo ""
              echo "📋 Available commands:"
              echo "  pytest              - Run tests"
              echo "  tox -e lint         - Run linting"
              echo "  tox -e format       - Check formatting"
              echo "  black src tests     - Format code"
              echo "  isort src tests     - Sort imports"
              echo "  pre-commit run -a   - Run all pre-commit hooks"
              echo ""
              echo "📚 Documentation:"
              echo "  cd docs && make html  - Build documentation"
              echo ""
            fi
            
            # Install pre-commit hooks if not already installed
            if [ ! -f .git/hooks/pre-commit ]; then
              pre-commit install > /dev/null 2>&1
            fi
          '';

          # Environment variables
          PYTHONPATH = ".";
          
          # Prevent Python from writing bytecode
          PYTHONDONTWRITEBYTECODE = "1";
          
          # Force Python to use UTF-8
          PYTHONIOENCODING = "UTF-8";
          
          # Enable Python development mode
          PYTHONDEVMODE = "1";
        };
      }
    );
}
