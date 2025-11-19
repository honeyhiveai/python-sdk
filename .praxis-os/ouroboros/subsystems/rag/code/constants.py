"""Constants for code index file exclusion patterns.

This module contains the comprehensive default exclusion patterns used by the
code indexer when no .gitignore file is present or when respect_gitignore=False.

These patterns cover common build artifacts, dependencies, and generated files
across multiple programming languages and ecosystems.

Usage:
    >>> from ouroboros.subsystems.rag.code.constants import DEFAULT_EXCLUDE_PATTERNS
    >>> 
    >>> # Use in pattern matching
    >>> for pattern in DEFAULT_EXCLUDE_PATTERNS:
    ...     if matches_pattern(file_path, pattern):
    ...         exclude_file(file_path)

Design Principles:
    - Comprehensive: Cover common patterns across languages
    - Conservative: Prefer excluding too much over too little
    - Maintainable: Organized by language/ecosystem for easy updates
    - Documented: Each section explains what it covers

Traceability:
    - Design: .praxis-os/workspace/design/2025-11-07-code-index-gitignore-support.md
    - FR-XXX: Code indexer file exclusion system
"""

# Comprehensive default exclusion patterns for code indexer
# Used when .gitignore is not present or respect_gitignore=False
DEFAULT_EXCLUDE_PATTERNS = [
    # Python - Bytecode & Compiled
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    "*.pyo",
    "*.pyd",
    "*.so",
    ".Python",
    
    # Python - Distribution / Packaging
    "build/",
    "develop-eggs/",
    "dist/",
    "downloads/",
    "eggs/",
    ".eggs/",
    "lib/",
    "lib64/",
    "parts/",
    "sdist/",
    "var/",
    "wheels/",
    "*.egg-info/",
    ".installed.cfg",
    "*.egg",
    "MANIFEST",
    
    # Python - Virtual Environments
    ".venv/",
    "venv/",
    "ENV/",
    "env/",
    ".virtualenv/",
    "virtualenv/",
    
    # Python - Testing & Coverage
    ".tox/",
    ".nox/",
    ".pytest_cache/",
    ".coverage",
    ".coverage.*",
    "htmlcov/",
    ".nyc_output/",
    "coverage.xml",
    "*.cover",
    ".hypothesis/",
    
    # Python - Type Checking & Linting
    ".mypy_cache/",
    ".dmypy.json",
    "dmypy.json",
    ".pyre/",
    ".pytype/",
    "cython_debug/",
    
    # Python - Jupyter Notebooks
    ".ipynb_checkpoints/",
    "*.ipynb_checkpoints",
    
    # JavaScript/Node - Dependencies
    "node_modules/",
    "npm-debug.log*",
    "yarn-debug.log*",
    "yarn-error.log*",
    "lerna-debug.log*",
    ".pnpm-debug.log*",
    
    # JavaScript/Node - Build Output
    "dist/",
    "build/",
    ".next/",
    ".nuxt/",
    ".output/",
    "out/",
    ".cache/",
    ".parcel-cache/",
    ".turbo/",
    
    # JavaScript/Node - Testing & Coverage
    ".nyc_output/",
    "coverage/",
    "*.lcov",
    ".jest/",
    ".vitest/",
    
    # JavaScript/Node - Package Managers
    ".yarn/",
    ".yarn/cache",
    ".yarn/unplugged",
    ".yarn/build-state.yml",
    ".yarn/install-state.gz",
    ".pnp.*",
    ".yarn-integrity",
    
    # TypeScript
    "*.tsbuildinfo",
    ".tsbuildinfo",
    
    # Rust
    "target/",
    "Cargo.lock",
    "**/*.rs.bk",
    
    # Go
    "vendor/",
    "*.exe",
    "*.exe~",
    "*.dll",
    "*.so",
    "*.dylib",
    "*.test",
    "*.out",
    "go.work",
    "go.work.sum",
    
    # Java
    "*.class",
    "*.log",
    "*.jar",
    "*.war",
    "*.nar",
    "*.ear",
    "*.zip",
    "*.tar.gz",
    "*.rar",
    "hs_err_pid*",
    ".gradle/",
    "build/",
    "out/",
    ".idea/",
    "*.iml",
    ".settings/",
    ".classpath",
    ".project",
    
    # C/C++
    "*.o",
    "*.a",
    "*.so",
    "*.dylib",
    "*.dll",
    "*.exe",
    "*.out",
    "*.obj",
    "*.pdb",
    "*.ilk",
    "*.exp",
    "*.lib",
    "*.dll.a",
    "CMakeFiles/",
    "CMakeCache.txt",
    "cmake_install.cmake",
    "Makefile",
    "*.cmake",
    "!CMakeLists.txt",
    ".cmake/",
    
    # C# / .NET
    "bin/",
    "obj/",
    "*.user",
    "*.suo",
    "*.userosscache",
    "*.sln.docstates",
    "[Bb]in/",
    "[Oo]bj/",
    "[Ll]og/",
    "[Ll]ogs/",
    ".vs/",
    "*.dll",
    "*.exe",
    "*.pdb",
    "*.cache",
    
    # Ruby
    "*.gem",
    "*.rbc",
    ".bundle/",
    ".config/",
    "coverage/",
    "InstalledFiles",
    "lib/bundler/man/",
    "pkg/",
    "rdoc/",
    "tmp/",
    "vendor/bundle/",
    "vendor/cache/",
    "vendor/gems/",
    "vendor/ruby/",
    
    # PHP
    "vendor/",
    "composer.lock",
    "*.cache",
    ".phpunit.result.cache",
    
    # Swift
    ".build/",
    "*.xcodeproj",
    "*.xcworkspace",
    "DerivedData/",
    ".swiftpm/",
    "Package.resolved",
    
    # Kotlin
    "*.iml",
    ".gradle/",
    "build/",
    "out/",
    ".idea/",
    
    # Scala
    "*.class",
    "*.log",
    "target/",
    ".idea/",
    "*.iml",
    
    # Dart/Flutter
    ".dart_tool/",
    ".flutter-plugins",
    ".flutter-plugins-dependencies",
    ".packages",
    ".pub-cache/",
    ".pub/",
    "build/",
    "*.g.dart",
    "*.freezed.dart",
    
    # IDEs & Editors
    ".vscode/",
    ".idea/",
    "*.swp",
    "*.swo",
    "*~",
    "*.sublime-project",
    "*.sublime-workspace",
    ".vs/",
    ".fleet/",
    ".cursor/",
    
    # Version Control
    ".git/",
    ".svn/",
    ".hg/",
    ".bzr/",
    ".gitignore",
    ".gitattributes",
    
    # OS Files
    ".DS_Store",
    ".DS_Store?",
    "._*",
    ".Spotlight-V100",
    ".Trashes",
    "ehthumbs.db",
    "Thumbs.db",
    "Desktop.ini",
    "$RECYCLE.BIN/",
    "*.lnk",
    
    # Temporary Files
    "*.tmp",
    "*.temp",
    "*.bak",
    "*.backup",
    "*.swp",
    "*.swo",
    "*~",
    ".#*",
    "#*#",
    
    # Logs
    "*.log",
    "logs/",
    "*.log.*",
    
    # Database Files
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "*.db-shm",
    "*.db-wal",
    
    # Environment & Secrets
    ".env",
    ".env.local",
    ".env.*.local",
    "*.key",
    "*.pem",
    "*.cert",
    "*.crt",
    "secrets/",
    
    # Documentation Builds
    "docs/_build/",
    "docs/build/",
    "site/",
    ".doctrees/",
    
    # Miscellaneous
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".benchmarks/",
    "*.prof",
    "*.lprof",
]

__all__ = ["DEFAULT_EXCLUDE_PATTERNS"]

