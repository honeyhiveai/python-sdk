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

        # Python development dependencies (minimal base)
        # All other dependencies (including requests, beautifulsoup4, pyyaml)
        # are managed via pip and pyproject.toml to avoid duplication
        pythonEnv = python.withPackages (ps: with ps; [
          pip
          setuptools
          wheel
          virtualenv
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
            buildInputs = [
            # Python environment
            pythonEnv
          ];

          shellHook = ''
            # Set up color output
            export TERM=xterm-256color

            # Fix xcrun warnings on macOS by unsetting DEVELOPER_DIR
            # See: https://github.com/NixOS/nixpkgs/issues/376958#issuecomment-3471021813
            unset DEVELOPER_DIR

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
              pip install -e ".[dev,docs]" 2>&1
              touch .venv/.installed
              echo "✨ Environment ready!"
              echo ""
              echo "Run 'make help' to see available commands"
              echo ""
            fi
          '';

          # Environment variables

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
