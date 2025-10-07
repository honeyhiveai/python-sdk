"""
Configuration validation with clear error messages.

Validates configuration paths and settings before server creation.
"""

from pathlib import Path
from typing import List
import logging

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
            errors.append(f"❌ max_tools_warning must be >= 1: {config.mcp.max_tools_warning}")
        
        if not config.mcp.enabled_tool_groups:
            errors.append("❌ At least one tool group must be enabled")
        
        return errors


__all__ = ["ConfigValidator"]
