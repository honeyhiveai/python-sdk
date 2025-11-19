"""
Environment Variable Enforcement for Local Development

This module provides programmatic enforcement for detecting and sourcing
.env files in local development environments, following Agent OS standards.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv


class EnvFileNotFoundError(Exception):
    """Raised when required .env file is not found in local development."""


class MissingCredentialsError(Exception):
    """Raised when required credentials are missing from environment."""


class EnvironmentEnforcer:
    """Enforces .env file loading and credential validation for local development."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the environment enforcer.

        Args:
            project_root: Path to project root. If None, auto-detects from current file.
        """
        if project_root is None:
            # Auto-detect project root (look for pyproject.toml)
            current_path = Path(__file__).resolve()
            for parent in current_path.parents:
                if (parent / "pyproject.toml").exists():
                    project_root = parent
                    break
            else:
                raise RuntimeError(
                    "Could not find project root (no pyproject.toml found)"
                )

        self.project_root = project_root
        self.env_files = [
            self.project_root / ".env.integration",  # Integration-specific
            self.project_root / ".env",  # General project
        ]
        self.loaded_env_file: Optional[Path] = None

    def is_local_development(self) -> bool:
        """Detect if we're running in local development environment.

        Returns:
            True if running locally, False if in CI/production.
        """
        # CI environment indicators
        ci_indicators = [
            "CI",
            "GITHUB_ACTIONS",
            "GITLAB_CI",
            "JENKINS_URL",
            "TRAVIS",
            "CIRCLECI",
            "BUILDKITE",
            "AZURE_PIPELINES",
        ]

        # Check if any CI indicator is present
        if any(os.getenv(indicator) for indicator in ci_indicators):
            return False

        # Check if HH_SOURCE indicates CI environment
        hh_source = os.getenv("HH_SOURCE", "")
        if hh_source.startswith(("github-actions", "ci-", "pipeline-")):
            return False

        # Check if we're in a tox environment (but still local)
        if os.getenv("TOX_ENV_NAME"):
            # Tox is local development, but check if it's CI-triggered
            return not any(os.getenv(indicator) for indicator in ci_indicators)

        return True

    def detect_and_load_env_file(self) -> bool:
        """Detect and load .env file for local development.

        Returns:
            True if .env file was found and loaded, False otherwise.

        Raises:
            EnvFileNotFoundError: If no .env file found in local development.
        """
        if not self.is_local_development():
            # In CI/production, don't require .env files
            return False

        # Try to load .env files in priority order
        for env_file in self.env_files:
            if env_file.exists():
                load_dotenv(env_file, override=True)
                self.loaded_env_file = env_file
                print(f"✅ Loaded environment from: {env_file}")
                return True

        # No .env file found in local development - this is an error
        env_file_paths = "\n".join(f"  - {path}" for path in self.env_files)
        example_file = self.project_root / "env.integration.example"

        error_msg = f"""
🚨 LOCAL DEVELOPMENT ERROR: No .env file found!

According to Agent OS standards, local development MUST use .env files for credentials.

Expected .env file locations:
{env_file_paths}

To fix this:
1. Copy the example file:
   cp {example_file} {self.env_files[0]}

2. Edit {self.env_files[0]} with your real credentials:
   HH_API_KEY=your_honeyhive_api_key_here
   HH_PROJECT=your_project_name_here
   OPENAI_API_KEY=your_openai_key_here  # (optional, for LLM tests)

3. Never commit .env files to git (they're in .gitignore)

For CI/production environments, set environment variables directly.
"""
        raise EnvFileNotFoundError(error_msg.strip())

    def validate_required_credentials(self, required_vars: List[str]) -> Dict[str, str]:
        """Validate that required environment variables are present.

        Args:
            required_vars: List of required environment variable names.

        Returns:
            Dictionary of variable names to values.

        Raises:
            MissingCredentialsError: If required variables are missing.
        """
        missing_vars = []
        credentials = {}

        for var_name in required_vars:
            value = os.getenv(var_name)
            if not value:
                missing_vars.append(var_name)
            else:
                credentials[var_name] = value

        if missing_vars:
            env_file_info = ""
            if self.loaded_env_file:
                env_file_info = f"\nLoaded from: {self.loaded_env_file}"
            elif self.is_local_development():
                env_file_info = (
                    "\nNo .env file was loaded (see detect_and_load_env_file())"
                )

            missing_list = "\n".join(f"  - {var}" for var in missing_vars)
            error_msg = f"""
🚨 MISSING REQUIRED CREDENTIALS:

The following environment variables are required:
{missing_list}
{env_file_info}

For local development, add these to your .env file:
{chr(10).join(f'{var}=your_{var.lower()}_here' for var in missing_vars)}

For CI/production, set these environment variables directly.
"""
            raise MissingCredentialsError(error_msg.strip())

        return credentials

    def enforce_integration_test_credentials(self) -> Dict[str, str]:
        """Enforce credentials required for integration tests.

        Returns:
            Dictionary of validated credentials.

        Raises:
            EnvFileNotFoundError: If .env file missing in local development.
            MissingCredentialsError: If required credentials are missing.
        """
        # Always try to load .env file in local development
        self.detect_and_load_env_file()

        # Core required credentials for integration tests
        required_vars = ["HH_API_KEY"]

        # Validate and return credentials
        return self.validate_required_credentials(required_vars)

    def get_optional_llm_credentials(self) -> Dict[str, Optional[str]]:
        """Get optional LLM provider credentials for instrumentor tests.

        Returns:
            Dictionary of LLM provider credentials (may contain None values).
        """
        llm_vars = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AZURE_OPENAI_API_KEY",
        ]

        return {var: os.getenv(var) for var in llm_vars}

    def print_environment_status(self) -> None:
        """Print current environment status for debugging."""
        print("\n" + "=" * 60)
        print("🔍 ENVIRONMENT STATUS")
        print("=" * 60)

        print(f"Local Development: {self.is_local_development()}")
        print(f"Project Root: {self.project_root}")

        if self.loaded_env_file:
            print(f"Loaded .env file: {self.loaded_env_file}")
        else:
            print("No .env file loaded")

        # Show key environment variables (without exposing secrets)
        key_vars = ["HH_API_KEY", "HH_PROJECT", "HH_SOURCE", "OPENAI_API_KEY"]
        print("\nKey Environment Variables:")
        for var in key_vars:
            value = os.getenv(var)
            if value:
                # Show first 8 chars + "..." for security
                masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
                print(f"  {var}: {masked_value}")
            else:
                print(f"  {var}: (not set)")

        print("=" * 60 + "\n")


# Global instance for easy access
_enforcer = EnvironmentEnforcer()


def enforce_local_env_file() -> bool:
    """Convenience function to enforce .env file loading in local development.

    Returns:
        True if .env file was loaded, False if not needed (CI/production).

    Raises:
        EnvFileNotFoundError: If .env file missing in local development.
    """
    return _enforcer.detect_and_load_env_file()


def enforce_integration_credentials() -> Dict[str, str]:
    """Convenience function to enforce integration test credentials.

    Returns:
        Dictionary of validated credentials.

    Raises:
        EnvFileNotFoundError: If .env file missing in local development.
        MissingCredentialsError: If required credentials are missing.
    """
    return _enforcer.enforce_integration_test_credentials()


def get_llm_credentials() -> Dict[str, Optional[str]]:
    """Convenience function to get optional LLM credentials.

    Returns:
        Dictionary of LLM provider credentials (may contain None values).
    """
    return _enforcer.get_optional_llm_credentials()


def print_env_status() -> None:
    """Convenience function to print environment status."""
    _enforcer.print_environment_status()


if __name__ == "__main__":
    try:
        print("Testing Environment Enforcement...")
        print_env_status()

        print("Enforcing .env file loading...")
        enforce_local_env_file()

        print("Enforcing integration credentials...")
        creds = enforce_integration_credentials()
        print(f"✅ Found {len(creds)} required credentials")

        print("Checking optional LLM credentials...")
        llm_creds = get_llm_credentials()
        available_llm = [k for k, v in llm_creds.items() if v]
        print(
            f"✅ Found {len(available_llm)} LLM provider credentials: {available_llm}"
        )

    except (EnvFileNotFoundError, MissingCredentialsError) as e:
        print(f"❌ {e}")
        sys.exit(1)
