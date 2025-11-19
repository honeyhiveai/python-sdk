"""Simplified configuration interface for HoneyHive tracers.

This module provides a clean, simple interface for accessing tracer configuration
values without the complexity of the underlying merging system.
"""

# pylint: disable=protected-access
# Justification: Accessing _merged_config is the established pattern for tracer config

import os
from typing import Any, Dict


class TracerConfigInterface:
    """Simple, clean interface for accessing tracer configuration.

    This class provides both attribute-style and dict-style access to
    configuration values, hiding the complexity of the underlying
    configuration merging system.

    Examples:
        >>> tracer = HoneyHiveTracer(api_key="key", project="test")
        >>>
        >>> # Attribute-style access - TracerConfig at root
        >>> print(tracer.config.api_key)
        >>> print(tracer.config.project)
        >>>
        >>> # Nested config access - other configs namespaced
        >>> print(tracer.config.otlp.batch_size)
        >>> print(tracer.config.http.timeout)
        >>> print(tracer.config.session.inputs)
        >>>
        >>> # Dict-style access with defaults for root level
        >>> api_key = tracer.config.get("api_key", "default")
        >>> project = tracer.config.get("project", "default")
        >>>
        >>> # Check if config has a value
        >>> if "custom_field" in tracer.config:
        >>>     print(tracer.config.custom_field)
    """

    def __init__(self, tracer_instance: Any) -> None:
        """Initialize config interface with reference to tracer instance.

        Args:
            tracer_instance: The HoneyHiveTracer instance this config belongs to
        """
        self._tracer = tracer_instance

    def __getattr__(self, name: str) -> Any:
        """Get configuration value using attribute access.

        Args:
            name: Configuration key name

        Returns:
            Configuration value

        Raises:
            AttributeError: If configuration key doesn't exist
        """
        # Dynamic resolution strategy - try multiple sources in order
        value = self._resolve_config_value(name)
        if value is not None:
            return value

        raise AttributeError(f"Configuration key '{name}' not found")

    def _resolve_config_value(self, name: str) -> Any:
        """Dynamically resolve configuration value from multiple sources.

        This method uses dynamic logic to search through configuration sources
        with proper precedence: config objects > env variables > tracer defaults.

        Args:
            name: Configuration key name

        Returns:
            Configuration value or None if not found
        """
        # Strategy 1: Direct config access (Pydantic models and dicts)
        # These have highest priority as they're explicitly provided
        value = self._try_direct_config_access(name)
        if value is not None:
            return value

        # Strategy 2: Nested config traversal (dynamic nested search)
        # Also high priority as these are from explicit config objects
        value = self._try_nested_config_access(name)
        if value is not None:
            return value

        # Strategy 3: Environment variable resolution (dynamic env mapping)
        # Environment variables take precedence over tracer instance defaults
        env_value = self._try_environment_variable_access(name)
        if env_value is not None:
            return env_value

        # Strategy 4: Tracer instance attributes (fallback to defaults)
        value = self._try_tracer_attribute_access(name)
        if value is not None:
            return value

        return None

    def _try_direct_config_access(self, name: str) -> Any:
        """Try direct access to merged config.

        Only returns values that are from explicit Pydantic config objects,
        not from legacy parameter defaults.
        """
        if not hasattr(self._tracer, "_merged_config"):
            return None

        config = self._tracer._merged_config

        # Check if this value came from an explicit Pydantic config object
        # vs. a legacy parameter default by examining the value
        if hasattr(config, name):
            value = getattr(config, name)
            # Skip default values - let environment variables override them
            if not self._is_default_value(name, value):
                return value

        # Dictionary key access - also check for defaults
        if isinstance(config, dict) and name in config:
            value = config[name]
            # Skip default values - let environment variables override them
            if not self._is_default_value(name, value):
                return value

        return None

    def _is_default_value(self, name: str, value: Any) -> bool:
        """Determine if a value is a default that should be overridden by env vars.

        Uses dynamic logic to identify common default values that should not
        take precedence over environment variables.
        """
        # Common default value patterns (based on original SDK defaults)
        default_patterns = {
            "source": "dev",  # Original: os.getenv("HH_SOURCE", "dev")
            "server_url": "https://api.honeyhive.ai",  # Original DEFAULT_API_URL
            "session_name": "unknown",  # Original fallback when script name fails
            "disable_http_tracing": True,  # New SDK default for performance
            "disable_batch": False,  # Original constructor default
            "verbose": False,  # Original constructor default
            "is_evaluation": False,  # Original constructor default
            "test_mode": False,  # Not in original, but logical default
            "disable_tracing": False,  # Not in original, but logical default
            "api_key": None,  # Required field
            "project": None,  # Required field
            "session_id": None,  # Generated UUID in original
            "inputs": None,  # Original constructor default
            "run_id": None,  # Original constructor default
            "dataset_id": None,  # Original constructor default
            "datapoint_id": None,  # Original constructor default
            "link_carrier": None,  # Original constructor default
        }

        # Check if this is a known default value
        if name in default_patterns:
            return bool(value == default_patterns[name])

        # Dynamic default detection for other values
        if value is None:
            return True  # None is usually a default
        if isinstance(value, bool) and value is False:
            return True  # False is often a default for boolean flags
        if isinstance(value, str) and value in ["dev", "default", "unknown"]:
            return True  # Common default string values

        return False

    def _try_nested_config_access(self, name: str) -> Any:
        """Dynamically search through nested configuration structures."""
        if not hasattr(self._tracer, "_merged_config"):
            return None

        config = self._tracer._merged_config

        # Dynamic nested traversal - search all nested objects
        if isinstance(config, dict):
            for _, value in config.items():
                # Check if nested object has the attribute
                if hasattr(value, name):
                    return getattr(value, name)

                # Check if nested dict has the key
                if isinstance(value, dict) and name in value:
                    return value[name]

        # For Pydantic models, check all nested attributes
        if hasattr(config, "__dict__"):
            for attr_name in dir(config):
                if not attr_name.startswith("_"):
                    attr_value = getattr(config, attr_name, None)
                    if attr_value is not None:
                        # Check nested Pydantic models
                        if hasattr(attr_value, name):
                            return getattr(attr_value, name)

                        # Check nested dicts
                        if isinstance(attr_value, dict) and name in attr_value:
                            return attr_value[name]

        return None

    def _try_environment_variable_access(self, name: str) -> Any:
        """Dynamically resolve environment variables based on naming patterns."""
        # Dynamic environment variable mapping based on common patterns
        env_patterns = [
            f"HH_{name.upper()}",  # HH_API_KEY, HH_BATCH_SIZE
            f"HONEYHIVE_{name.upper()}",  # HONEYHIVE_API_KEY
            f"HH_{name.upper().replace('_', '_')}",  # Handle underscores
        ]

        # Try each pattern
        for env_key in env_patterns:
            env_value = os.getenv(env_key)
            if env_value is not None:
                converted_value = self._convert_env_value(name, env_value)
                if converted_value is not None:  # Valid conversion
                    return converted_value

        # If no environment variable found, return sensible default
        return self._get_sensible_default(name)

    def _convert_env_value(self, name: str, env_value: str) -> Any:
        """Dynamically convert environment variable based on context clues.

        Returns None if conversion fails and the value is invalid for the expected type.
        This allows the get() method to use its default value.
        """
        # Dynamic type inference based on name patterns and value content
        name_lower = name.lower()

        # Boolean detection - return None for invalid boolean values
        if any(
            keyword in name_lower
            for keyword in ["enabled", "enable", "disabled", "disable", "is_", "has_"]
        ):
            return self._convert_boolean_value(env_value)

        # Numeric detection - return None if conversion fails
        if any(
            keyword in name_lower
            for keyword in ["size", "count", "limit", "max", "min", "port"]
        ):
            return self._convert_int_value(env_value)

        # Float detection - return None if conversion fails
        if any(
            keyword in name_lower
            for keyword in ["interval", "timeout", "delay", "rate", "ratio"]
        ):
            return self._convert_float_value(env_value)

        # Try intelligent conversion based on value format
        return self._convert_by_format(env_value)

    def _convert_boolean_value(self, env_value: str) -> Any:
        """Convert string to boolean or None if invalid."""
        valid_true = ("true", "1", "yes", "on", "enabled")
        valid_false = ("false", "0", "no", "off", "disabled")
        env_lower = env_value.lower()
        if env_lower in valid_true:
            return True
        if env_lower in valid_false:
            return False
        return None  # Invalid boolean value, let caller use default

    def _convert_int_value(self, env_value: str) -> Any:
        """Convert string to int or None if invalid."""
        try:
            return int(env_value)
        except ValueError:
            return None  # Invalid numeric value, let caller use default

    def _convert_float_value(self, env_value: str) -> Any:
        """Convert string to float or None if invalid."""
        try:
            return float(env_value)
        except ValueError:
            return None  # Invalid float value, let caller use default

    def _convert_by_format(self, env_value: str) -> Any:
        """Convert based on value format, fallback to string."""
        try:
            # Integer
            if env_value.isdigit() or (
                env_value.startswith("-") and env_value[1:].isdigit()
            ):
                return int(env_value)

            # Float
            if "." in env_value:
                return float(env_value)

            # Boolean
            if env_value.lower() in (
                "true",
                "false",
                "1",
                "0",
                "yes",
                "no",
                "on",
                "off",
            ):
                return env_value.lower() in ("true", "1", "yes", "on")
        except (ValueError, TypeError):
            pass

        # Return as string if no conversion possible
        return env_value

    def _get_sensible_default(self, name: str) -> Any:
        """Get sensible default values for configuration keys using dynamic logic.

        Defaults are based on ENVIRONMENT_VARIABLES.md documentation.
        """
        # Dynamic default mapping - matches original SDK defaults from main branch
        defaults = {
            # API Configuration (matches original main branch behavior)
            "api_key": None,  # Required - fallback to HH_API_KEY env var
            "server_url": "https://api.honeyhive.ai",  # Original DEFAULT_API_URL
            "project": None,  # Required - fallback to HH_PROJECT env var
            "source": "dev",  # Original: os.getenv("HH_SOURCE", "dev")
            # "session_name" removed - should use dynamic inference
            # (ID/name pattern → None)
            "session_id": None,  # Generated UUID in original
            # Tracing Configuration (matches current constructor defaults)
            "disable_tracing": False,  # Not in original, but logical default
            "disable_http_tracing": True,  # New SDK default for performance
            "disable_batch": False,  # Matches current constructor default
            "test_mode": False,  # New parameter in current version
            "verbose": False,  # Matches current constructor default
            "is_evaluation": False,  # Matches current constructor default
            "inputs": None,  # Original constructor default
            "run_id": None,  # Original constructor default
            "dataset_id": None,  # Original constructor default
            "datapoint_id": None,  # Original constructor default
            "link_carrier": None,  # Original constructor default
            # OTLP Configuration
            "otlp_enabled": True,
            "otlp_endpoint": None,  # Auto-detected
            "otlp_headers": None,
            "batch_size": 100,
            "flush_interval": 5.0,
            # HTTP Client Configuration - Connection Pool
            "max_connections": 10,
            "max_keepalive_connections": 20,
            "keepalive_expiry": 30.0,
            "pool_timeout": 10.0,
            # HTTP Client Configuration - Rate Limiting
            "rate_limit_calls": 100,
            "rate_limit_window": 60.0,
            # HTTP Client Configuration - Proxy
            "http_proxy": None,
            "https_proxy": None,
            "no_proxy": None,
            # HTTP Client Configuration - SSL and Redirects
            "verify_ssl": True,
            "follow_redirects": True,
            # Experiment Harness Configuration
            "experiment_id": None,
            "experiment_name": None,
            "experiment_variant": None,
            "experiment_group": None,
            "experiment_metadata": None,
            # SDK Configuration
            "timeout": 30.0,
            "max_retries": 3,
            # Additional common defaults
            "async_enabled": True,
            "http_tracing_enabled": False,
        }

        # Check if we have a specific default
        if name in defaults:
            return defaults[name]

        # Dynamic default inference based on name patterns
        name_lower = name.lower()

        # Boolean flags (enabled/disabled, is_/has_)
        if any(
            pattern in name_lower for pattern in ["enabled", "disabled", "is_", "has_"]
        ):
            return "enabled" in name_lower

        # Size/count/limit values
        if any(pattern in name_lower for pattern in ["size", "count", "limit", "max"]):
            return 100

        # Time intervals
        if any(pattern in name_lower for pattern in ["interval", "timeout", "delay"]):
            return 5.0

        # URLs/endpoints
        if any(pattern in name_lower for pattern in ["url", "endpoint", "host"]):
            return None

        # IDs and names
        if any(pattern in name_lower for pattern in ["id", "name"]):
            return None

        # Default fallback
        return None

    def _try_tracer_attribute_access(self, name: str) -> Any:
        """Try accessing tracer instance attributes."""
        if hasattr(self._tracer, name):
            return getattr(self._tracer, name)
        return None

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default.

        Args:
            key: Configuration key name
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def __contains__(self, key: str) -> bool:
        """Check if configuration key exists.

        Args:
            key: Configuration key name

        Returns:
            True if key exists, False otherwise
        """
        try:
            self.__getattr__(key)
            return True
        except AttributeError:
            return False

    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dict-style access.

        Args:
            key: Configuration key name

        Returns:
            Configuration value

        Raises:
            KeyError: If configuration key doesn't exist
        """
        try:
            return self.__getattr__(key)
        except AttributeError as exc:
            raise KeyError(f"Configuration key '{key}' not found") from exc

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for debugging/inspection.

        Uses dynamic logic to discover all available configuration values
        rather than hardcoded attribute lists.

        Returns:
            Dictionary representation of configuration
        """
        result = {}

        # Dynamic config extraction
        result.update(self._extract_merged_config())
        result.update(self._extract_tracer_attributes())

        return result

    def _extract_merged_config(self) -> Dict[str, Any]:
        """Dynamically extract all values from merged config."""
        if not hasattr(self._tracer, "_merged_config"):
            return {}

        config = self._tracer._merged_config
        result = {}

        # Pydantic model extraction
        if hasattr(config, "model_dump"):
            result.update(config.model_dump())
        elif hasattr(config, "__dict__"):
            # Extract all non-private attributes from object
            for attr_name in dir(config):
                if not attr_name.startswith("_") and not callable(
                    getattr(config, attr_name, None)
                ):
                    try:
                        result[attr_name] = getattr(config, attr_name)
                    except (AttributeError, TypeError):
                        continue
        elif isinstance(config, dict):
            # Dictionary config
            result.update(config)

        return result

    def _extract_tracer_attributes(self) -> Dict[str, Any]:
        """Dynamically extract relevant tracer instance attributes."""
        result = {}

        # Dynamic attribute discovery - look for config-like attributes
        for attr_name in dir(self._tracer):
            if (
                not attr_name.startswith("_")
                and not callable(getattr(self._tracer, attr_name, None))
                and self._is_config_like_attribute(attr_name)
            ):
                try:
                    result[attr_name] = getattr(self._tracer, attr_name)
                except (AttributeError, TypeError):
                    continue

        return result

    def _is_config_like_attribute(self, attr_name: str) -> bool:
        """Determine if an attribute is configuration-related using dynamic logic."""
        # Common configuration attribute patterns
        config_patterns = [
            "api_key",
            "project",
            "source",
            "session",
            "endpoint",
            "url",
            "enabled",
            "disabled",
            "timeout",
            "interval",
            "size",
            "limit",
            "host",
            "port",
            "token",
            "key",
            "id",
            "name",
            "version",
            "batch",
            "flush",
            "otlp",
            "http",
            "async",
            "sync",
        ]

        attr_lower = attr_name.lower()

        # Check if attribute name contains any configuration-related keywords
        return any(pattern in attr_lower for pattern in config_patterns)

    def __repr__(self) -> str:
        """String representation for debugging."""
        try:
            config_dict = self.to_dict()
            # Dynamic sanitization of sensitive values
            sanitized = self._sanitize_config_dict(config_dict)
            return f"TracerConfig({sanitized})"
        except Exception:
            return "TracerConfig(<error accessing config>)"

    def _sanitize_config_dict(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically sanitize sensitive configuration values."""
        sanitized = {}

        for key, value in config_dict.items():
            if self._is_sensitive_key(key):
                sanitized[key] = "***" if value else None
            else:
                sanitized[key] = value

        return sanitized

    def _is_sensitive_key(self, key: str) -> bool:
        """Determine if a configuration key contains sensitive data."""
        key_lower = key.lower()

        # Dynamic sensitive data detection patterns
        sensitive_patterns = [
            "key",
            "token",
            "secret",
            "password",
            "pass",
            "auth",
            "credential",
            "private",
            "secure",
            "sensitive",
        ]

        # Check if key contains any sensitive patterns
        return any(pattern in key_lower for pattern in sensitive_patterns)


# Commonly accessed configuration properties for easy reference
class CommonConfigKeys:  # pylint: disable=too-few-public-methods
    """Common configuration keys for easy reference and IDE autocomplete."""

    # Core tracer settings
    API_KEY = "api_key"
    PROJECT = "project"
    SOURCE = "source"
    SESSION_NAME = "session_name"

    # OTLP/Export settings
    BATCH_SIZE = "batch_size"
    FLUSH_INTERVAL = "flush_interval"
    OTLP_ENABLED = "otlp_enabled"
    OTLP_ENDPOINT = "otlp_endpoint"

    # Evaluation settings
    RUN_ID = "run_id"
    DATASET_ID = "dataset_id"
    DATAPOINT_ID = "datapoint_id"
    IS_EVALUATION = "is_evaluation"

    # Performance settings
    HTTP_TRACING_ENABLED = "http_tracing_enabled"
    ASYNC_ENABLED = "async_enabled"
