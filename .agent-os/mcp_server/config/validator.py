"""
Configuration validation with clear error messages.

Validates configuration paths and settings before server creation.
"""

import logging
from typing import List

from ..models.config import ServerConfig

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validate configuration paths and settings."""

    @staticmethod
    def validate(config: ServerConfig) -> List[str]:
        """
        Validate configuration against requirements.

        :param config: ServerConfig to validate
        :return: List of error messages (empty if valid)
        """
        errors = []
        paths = config.resolved_paths

        # Validate source paths exist
        for name in ["standards_path", "usage_path", "workflows_path"]:
            path = paths[name]
            if not path.exists():
                errors.append(f"❌ {name} does not exist: {path}")
            elif not path.is_dir():
                errors.append(f"❌ {name} is not a directory: {path}")

        # Index path created on demand, just check parent
        index_path = paths["index_path"]
        if not index_path.parent.exists():
            errors.append(f"❌ Index parent directory missing: {index_path.parent}")

        # Validate embedding provider
        valid_providers = ["local", "openai"]
        if config.rag.embedding_provider not in valid_providers:
            errors.append(
                f"❌ Invalid embedding_provider: {config.rag.embedding_provider}. "
                f"Must be one of: {valid_providers}"
            )

        # Validate MCP config
        if config.mcp.max_tools_warning < 1:
            errors.append(
                f"❌ max_tools_warning must be >= 1: {config.mcp.max_tools_warning}"
            )

        if not config.mcp.enabled_tool_groups:
            errors.append("❌ At least one tool group must be enabled")

        # Validate HTTP transport configuration
        if not 1024 <= config.mcp.http_port <= 65535:
            errors.append(
                f"❌ http_port must be between 1024-65535: {config.mcp.http_port}"
            )

        if config.mcp.http_host != "127.0.0.1":
            errors.append(
                f"❌ http_host must be '127.0.0.1' for security: {config.mcp.http_host}"
            )

        if not config.mcp.http_path.startswith("/"):
            errors.append(f"❌ http_path must start with '/': {config.mcp.http_path}")

        return errors


__all__ = ["ConfigValidator"]
