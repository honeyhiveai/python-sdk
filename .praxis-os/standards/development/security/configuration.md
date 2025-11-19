# Configuration Management - HoneyHive Python SDK

**🎯 MISSION: Secure, flexible, and maintainable configuration management with proper validation and defaults**

## Environment Variable Patterns

### Hierarchical Configuration

```python
# Configuration precedence (highest to lowest)
# 1. Constructor parameters (highest)
# 2. HH_* environment variables  
# 3. Standard environment variables
# 4. Default values (lowest)

class ConfigManager:
    """Hierarchical configuration management."""
    
    def __init__(self, **kwargs):
        self.api_key = self._get_config_value("api_key", **kwargs)
        self.server_url = self._get_config_value("server_url", **kwargs)
        self.timeout = self._get_config_value("timeout", **kwargs)
    
    def _get_config_value(self, key: str, **kwargs) -> Any:
        """Get configuration value with precedence."""
        # 1. Constructor parameter
        if key in kwargs:
            return kwargs[key]
        
        # 2. HH_* environment variable
        hh_key = f"HH_{key.upper()}"
        if hh_key in os.environ:
            return os.environ[hh_key]
        
        # 3. Standard environment variable
        std_key = key.upper()
        if std_key in os.environ:
            return os.environ[std_key]
        
        # 4. Default value
        return self._get_default_value(key)
```

### Multi-Prefix Support

```python
# Support multiple prefixes for compatibility
def get_api_key() -> Optional[str]:
    """Get API key from multiple possible sources."""
    return (
        os.getenv("HH_API_KEY") or           # Primary
        os.getenv("HONEYHIVE_API_KEY") or    # Alternative
        os.getenv("API_KEY")                 # Generic fallback
    )

def get_server_url() -> str:
    """Get server URL with fallbacks."""
    return (
        os.getenv("HH_SERVER_URL") or
        os.getenv("HONEYHIVE_SERVER_URL") or
        os.getenv("SERVER_URL") or
        "https://api.honeyhive.ai"  # Default
    )
```

### Environment-Specific Configuration

```python
class EnvironmentConfig:
    """Environment-specific configuration."""
    
    def __init__(self):
        self.environment = self._detect_environment()
        self.config = self._load_environment_config()
    
    def _detect_environment(self) -> str:
        """Detect current environment."""
        env = os.getenv("HH_ENVIRONMENT", "production").lower()
        
        # Normalize environment names
        env_mapping = {
            "dev": "development",
            "local": "development", 
            "test": "testing",
            "staging": "staging",
            "prod": "production",
            "production": "production"
        }
        
        return env_mapping.get(env, "production")
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration."""
        base_config = {
            "timeout": 30.0,
            "max_retries": 3,
            "verify_ssl": True,
            "log_level": "INFO",
            "rate_limit": 100,
        }
        
        if self.environment == "development":
            base_config.update({
                "timeout": 60.0,        # Longer timeout for debugging
                "verify_ssl": False,    # Allow self-signed certs
                "log_level": "DEBUG",   # Verbose logging
                "rate_limit": 1000,     # Higher rate limit
            })
        
        elif self.environment == "testing":
            base_config.update({
                "timeout": 10.0,        # Faster timeout for tests
                "max_retries": 1,       # Fewer retries in tests
                "log_level": "WARNING", # Less noise in tests
            })
        
        return base_config
```

## Configuration Validation

### Type Validation and Conversion

```python
from typing import Union, Type, Any
import json

class ConfigValidator:
    """Validate and convert configuration values."""
    
    @staticmethod
    def validate_and_convert(
        value: Any, 
        expected_type: Type, 
        field_name: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        allowed_values: Optional[List[Any]] = None
    ) -> Any:
        """Validate and convert configuration value."""
        
        if value is None:
            return None
        
        # Type conversion
        try:
            if expected_type == bool:
                converted_value = ConfigValidator._convert_to_bool(value)
            elif expected_type == int:
                converted_value = int(value)
            elif expected_type == float:
                converted_value = float(value)
            elif expected_type == str:
                converted_value = str(value)
            elif expected_type == dict:
                converted_value = json.loads(value) if isinstance(value, str) else dict(value)
            elif expected_type == list:
                converted_value = json.loads(value) if isinstance(value, str) else list(value)
            else:
                converted_value = value
        
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid {field_name}: {value} (expected {expected_type.__name__}): {e}")
        
        # Range validation
        if min_value is not None and converted_value < min_value:
            raise ValueError(f"{field_name} must be >= {min_value}, got {converted_value}")
        
        if max_value is not None and converted_value > max_value:
            raise ValueError(f"{field_name} must be <= {max_value}, got {converted_value}")
        
        # Allowed values validation
        if allowed_values is not None and converted_value not in allowed_values:
            raise ValueError(f"{field_name} must be one of {allowed_values}, got {converted_value}")
        
        return converted_value
    
    @staticmethod
    def _convert_to_bool(value: Any) -> bool:
        """Convert various formats to boolean."""
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on", "enabled")
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        return bool(value)
```

### Configuration Schema

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class HoneyHiveConfig:
    """HoneyHive SDK configuration schema."""
    
    # Authentication
    api_key: Optional[str] = None
    
    # Server configuration
    server_url: str = "https://api.honeyhive.ai"
    timeout: float = 30.0
    max_retries: int = 3
    verify_ssl: bool = True
    
    # Project configuration
    project: Optional[str] = None
    source: str = "python-sdk"
    
    # Behavior configuration
    test_mode: bool = False
    verbose: bool = False
    
    # Privacy configuration
    redact_inputs: bool = True
    redact_outputs: bool = False
    
    # Performance configuration
    batch_size: int = 100
    flush_interval: float = 5.0
    rate_limit: int = 100
    
    # Advanced configuration
    custom_headers: Dict[str, str] = field(default_factory=dict)
    instrumentation_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values."""
        validator = ConfigValidator()
        
        # Validate API key format
        if self.api_key and not self.api_key.startswith("hh_"):
            raise ValueError("API key must start with 'hh_'")
        
        # Validate timeout
        self.timeout = validator.validate_and_convert(
            self.timeout, float, "timeout", min_value=1.0, max_value=300.0
        )
        
        # Validate max_retries
        self.max_retries = validator.validate_and_convert(
            self.max_retries, int, "max_retries", min_value=0, max_value=10
        )
        
        # Validate batch_size
        self.batch_size = validator.validate_and_convert(
            self.batch_size, int, "batch_size", min_value=1, max_value=1000
        )
        
        # Validate server URL
        if not self.server_url.startswith(("http://", "https://")):
            raise ValueError("Server URL must start with http:// or https://")
```

## Configuration Loading

### Configuration File Support

```python
import yaml
import json
from pathlib import Path

class ConfigLoader:
    """Load configuration from multiple sources."""
    
    def __init__(self):
        self.config_paths = [
            Path.cwd() / ".honeyhive.yml",
            Path.cwd() / ".honeyhive.yaml", 
            Path.cwd() / ".honeyhive.json",
            Path.home() / ".honeyhive" / "config.yml",
            Path("/etc/honeyhive/config.yml"),
        ]
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from files and environment."""
        config = {}
        
        # Load from configuration files
        for config_path in self.config_paths:
            if config_path.exists():
                file_config = self._load_config_file(config_path)
                config.update(file_config)
                break  # Use first found config file
        
        # Override with environment variables
        env_config = self._load_env_config()
        config.update(env_config)
        
        return config
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix in ['.yml', '.yaml']:
                    return yaml.safe_load(f) or {}
                elif config_path.suffix == '.json':
                    return json.load(f)
                else:
                    return {}
        except (yaml.YAMLError, json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return {}
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        # Map environment variables to config keys
        env_mapping = {
            "HH_API_KEY": "api_key",
            "HH_SERVER_URL": "server_url", 
            "HH_PROJECT": "project",
            "HH_SOURCE": "source",
            "HH_TIMEOUT": "timeout",
            "HH_TEST_MODE": "test_mode",
            "HH_VERBOSE": "verbose",
            "HH_BATCH_SIZE": "batch_size",
            "HH_FLUSH_INTERVAL": "flush_interval",
        }
        
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                config[config_key] = os.environ[env_var]
        
        return config
```

### Dynamic Configuration Updates

```python
class DynamicConfig:
    """Support dynamic configuration updates."""
    
    def __init__(self, initial_config: Dict[str, Any]):
        self._config = initial_config.copy()
        self._callbacks = []
        self._lock = threading.Lock()
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration dynamically."""
        with self._lock:
            old_config = self._config.copy()
            self._config.update(updates)
            
            # Validate new configuration
            try:
                validated_config = HoneyHiveConfig(**self._config)
                self._config = validated_config.__dict__
            except ValueError as e:
                # Rollback on validation failure
                self._config = old_config
                raise ValueError(f"Configuration update failed: {e}")
            
            # Notify callbacks
            self._notify_callbacks(old_config, self._config)
    
    def register_callback(self, callback: Callable[[Dict, Dict], None]):
        """Register callback for configuration changes."""
        self._callbacks.append(callback)
    
    def _notify_callbacks(self, old_config: Dict, new_config: Dict):
        """Notify registered callbacks of configuration changes."""
        for callback in self._callbacks:
            try:
                callback(old_config, new_config)
            except Exception as e:
                logger.error(f"Configuration callback failed: {e}")
```

## Configuration Security

### Sensitive Data Handling

```python
class SecureConfigManager:
    """Secure configuration management."""
    
    SENSITIVE_KEYS = {
        "api_key", "secret_key", "password", "token", 
        "private_key", "certificate", "credentials"
    }
    
    def __init__(self, config: Dict[str, Any]):
        self.config = self._secure_config(config)
    
    def _secure_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Secure sensitive configuration values."""
        secured_config = {}
        
        for key, value in config.items():
            if self._is_sensitive_key(key):
                # Store encrypted or use secure storage
                secured_config[key] = self._secure_value(value)
            else:
                secured_config[key] = value
        
        return secured_config
    
    def _is_sensitive_key(self, key: str) -> bool:
        """Check if configuration key contains sensitive data."""
        key_lower = key.lower()
        return any(sensitive in key_lower for sensitive in self.SENSITIVE_KEYS)
    
    def _secure_value(self, value: str) -> str:
        """Secure sensitive configuration value."""
        # In production, use proper encryption/key management
        # This is a simplified example
        return f"SECURED:{len(value)}:{hash(value) % 10000}"
    
    def get_config_for_logging(self) -> Dict[str, Any]:
        """Get configuration safe for logging."""
        safe_config = {}
        
        for key, value in self.config.items():
            if self._is_sensitive_key(key):
                safe_config[key] = self._mask_sensitive_value(value)
            else:
                safe_config[key] = value
        
        return safe_config
    
    def _mask_sensitive_value(self, value: str) -> str:
        """Mask sensitive value for logging."""
        if not value or len(value) < 8:
            return "***MASKED***"
        
        return f"{value[:4]}...{value[-4:]}"
```

## Configuration Testing

### Configuration Test Cases

```python
import pytest
from unittest.mock import patch
import tempfile
import yaml

class TestConfiguration:
    """Test configuration management."""
    
    def test_environment_variable_precedence(self):
        """Test configuration precedence."""
        with patch.dict(os.environ, {
            "HH_API_KEY": "env_key",
            "HH_TIMEOUT": "45.0"
        }):
            config = ConfigLoader().load_config()
            
            assert config["api_key"] == "env_key"
            assert float(config["timeout"]) == 45.0
    
    def test_config_file_loading(self):
        """Test configuration file loading."""
        config_data = {
            "api_key": "file_key",
            "project": "test_project",
            "timeout": 60.0
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader()
            loader.config_paths = [Path(config_path)]
            config = loader.load_config()
            
            assert config["api_key"] == "file_key"
            assert config["project"] == "test_project"
            assert config["timeout"] == 60.0
        finally:
            os.unlink(config_path)
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Valid configuration
        valid_config = HoneyHiveConfig(
            api_key="hh_test_key",
            timeout=30.0,
            max_retries=3
        )
        assert valid_config.timeout == 30.0
        
        # Invalid timeout
        with pytest.raises(ValueError, match="timeout must be"):
            HoneyHiveConfig(timeout=-1.0)
        
        # Invalid API key format
        with pytest.raises(ValueError, match="API key must start with"):
            HoneyHiveConfig(api_key="invalid_key")
    
    def test_sensitive_data_masking(self):
        """Test sensitive data is properly masked."""
        config = {
            "api_key": "hh_secret_key_12345",
            "project": "test_project",
            "timeout": 30.0
        }
        
        secure_manager = SecureConfigManager(config)
        safe_config = secure_manager.get_config_for_logging()
        
        assert "hh_secret_key_12345" not in str(safe_config)
        assert safe_config["project"] == "test_project"  # Non-sensitive unchanged
```

## Best Practices

### Configuration Guidelines

1. **Security First**:
   - Never log sensitive configuration values
   - Use environment variables for secrets
   - Validate all configuration inputs
   - Use secure defaults

2. **Flexibility**:
   - Support multiple configuration sources
   - Allow runtime configuration updates
   - Provide clear precedence rules
   - Support environment-specific configs

3. **Reliability**:
   - Validate configuration on startup
   - Provide meaningful error messages
   - Use type-safe configuration classes
   - Test configuration loading thoroughly

4. **Maintainability**:
   - Document all configuration options
   - Use consistent naming conventions
   - Provide configuration examples
   - Version configuration schemas

## References

- **[Security Practices](practices.md)** - Security considerations for configuration
- **[Environment Setup](../development/environment-setup.md)** - Development environment configuration
- **[Testing Standards](../development/testing-standards.md)** - Configuration testing requirements

---

**📝 Next Steps**: Review [Security Practices](practices.md) for additional security considerations.
