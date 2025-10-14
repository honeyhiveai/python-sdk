"""
Configuration loader with graceful fallback to defaults.

Loads configuration from config.json with safe error handling.
Single source of truth for configuration loading.
"""

# pylint: disable=broad-exception-caught
# Justification: Config loader must be robust - catches broad exceptions to
# provide graceful fallback to defaults when config files are missing or invalid

import json
import logging
from pathlib import Path

from ..models.config import MCPConfig, RAGConfig, ServerConfig

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load configuration from config.json with graceful fallback."""

    @staticmethod
    def load(base_path: Path, config_filename: str = "config.json") -> ServerConfig:
        """
        Load server configuration from file or use defaults.

        :param base_path: Path to .agent-os/ directory
        :param config_filename: Name of config file (default: config.json)
        :return: Fully configured ServerConfig
        :raises ValueError: If base_path invalid
        """
        if not base_path.exists():
            raise ValueError(f"Base path does not exist: {base_path}")

        if not base_path.is_dir():
            raise ValueError(f"Base path is not a directory: {base_path}")

        rag_config = ConfigLoader._load_rag_config(base_path, config_filename)
        mcp_config = ConfigLoader._load_mcp_config(base_path, config_filename)

        return ServerConfig(base_path=base_path, rag=rag_config, mcp=mcp_config)

    @staticmethod
    def _load_rag_config(base_path: Path, config_filename: str) -> RAGConfig:
        """
        Load RAG configuration from config.json.

        Falls back to defaults if:
        - config.json doesn't exist
        - JSON parse fails
        - rag section missing

        :param base_path: Path to .agent-os/
        :param config_filename: Config file name
        :return: RAGConfig with overrides or defaults
        """
        config_path = base_path / config_filename

        if not config_path.exists():
            logger.info(
                "No %s found at %s, using defaults", config_filename, config_path
            )
            return RAGConfig()

        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)

            rag_section = data.get("rag", {})

            # Use .get() with class defaults as fallback
            return RAGConfig(
                standards_path=rag_section.get(
                    "standards_path", RAGConfig.standards_path
                ),
                usage_path=rag_section.get("usage_path", RAGConfig.usage_path),
                workflows_path=rag_section.get(
                    "workflows_path", RAGConfig.workflows_path
                ),
                index_path=rag_section.get("index_path", RAGConfig.index_path),
                embedding_provider=rag_section.get(
                    "embedding_provider", RAGConfig.embedding_provider
                ),
            )
        except json.JSONDecodeError as e:
            logger.warning(
                "Failed to parse %s: %s. Using defaults.", config_filename, e
            )
            return RAGConfig()
        except Exception as e:
            logger.warning("Unexpected error loading config: %s. Using defaults.", e)
            return RAGConfig()

    @staticmethod
    def _load_mcp_config(base_path: Path, config_filename: str) -> MCPConfig:
        """
        Load MCP configuration from config.json.

        Falls back to defaults if config missing or invalid.

        :param base_path: Path to .agent-os/
        :param config_filename: Config file name
        :return: MCPConfig with overrides or defaults
        """
        config_path = base_path / config_filename

        if not config_path.exists():
            return MCPConfig()

        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)

            mcp_section = data.get("mcp", {})

            return MCPConfig(
                enabled_tool_groups=mcp_section.get(
                    "enabled_tool_groups", MCPConfig().enabled_tool_groups
                ),
                max_tools_warning=mcp_section.get(
                    "max_tools_warning", MCPConfig().max_tools_warning
                ),
            )
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Error loading MCP config: %s. Using defaults.", e)
            return MCPConfig()


__all__ = ["ConfigLoader"]
