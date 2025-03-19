#!/usr/bin/env bash

export POETRY_PYPI_TOKEN_PYPI=${PYPI_TOKEN}

# Get the current version
current_version=$(poetry version -s)
echo "Current version: $current_version"

# Calculate the new patch version
major=$(echo $current_version | cut -d. -f1)
minor=$(echo $current_version | cut -d. -f2)
patch=$(echo $current_version | cut -d. -f3)
new_patch=$((patch + 1))
new_version="$major.$minor.$new_patch"

# Update the version in pyproject.toml
poetry version $new_version
echo "Version bumped to: $new_version"

# Prepare the README for PyPI
poetry run python scripts/prepare-readme.py

# Build and publish
poetry publish --build --skip-existing
