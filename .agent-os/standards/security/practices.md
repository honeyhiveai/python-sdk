# Security Practices - HoneyHive Python SDK

**🎯 MISSION: Ensure secure handling of credentials, data privacy, and secure development practices**

## API Key Management

### Secure Storage and Usage

```python
# ✅ CORRECT: Never log API keys
def __init__(self, api_key: str):
    self.api_key = api_key
    logger.info("Client initialized")  # Don't log the key!

# ✅ CORRECT: Validate API key format
if not api_key or not api_key.startswith("hh_"):
    raise ValueError("Invalid API key format")

# ✅ CORRECT: Support key rotation
def rotate_api_key(self, new_key: str):
    """Update API key without restart."""
    self.api_key = new_key
    self._reinitialize_client()
```

### Environment Variable Patterns

```python
# Support multiple prefixes for compatibility
api_key = (
    os.getenv("HH_API_KEY") or
    os.getenv("HONEYHIVE_API_KEY") or
    os.getenv("API_KEY")
)

# Configuration precedence
# 1. Constructor parameters (highest)
# 2. HH_* environment variables
# 3. Standard environment variables
# 4. Default values (lowest)
```

### API Key Validation

```python
class APIKeyValidator:
    """Validate API key format and security."""
    
    @staticmethod
    def validate_format(api_key: str) -> bool:
        """Validate API key format."""
        if not api_key:
            return False
        
        # HoneyHive API keys start with "hh_"
        if not api_key.startswith("hh_"):
            return False
        
        # Minimum length check
        if len(api_key) < 20:
            return False
        
        return True
    
    @staticmethod
    def mask_key_for_logging(api_key: str) -> str:
        """Mask API key for safe logging."""
        if not api_key or len(api_key) < 8:
            return "***INVALID***"
        
        return f"{api_key[:4]}...{api_key[-4:]}"
```

### Secure Logging

```python
# ✅ CORRECT: Mask sensitive data in logs
logger.info(f"Initializing client with key: {mask_key_for_logging(api_key)}")

# ❌ WRONG: Never log full API keys
logger.info(f"API key: {api_key}")  # SECURITY VIOLATION

# ✅ CORRECT: Use structured logging with masking
logger.info(
    "Client initialization",
    extra={
        "api_key_prefix": api_key[:4] if api_key else None,
        "key_length": len(api_key) if api_key else 0,
        "key_valid": APIKeyValidator.validate_format(api_key)
    }
)
```

## Data Privacy

### PII Redaction

```python
def redact_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """Redact PII from data."""
    sensitive_keys = ["ssn", "email", "phone", "credit_card", "password"]
    
    def redact_value(key: str, value: Any) -> Any:
        if key.lower() in sensitive_keys:
            return "***REDACTED***"
        
        # Redact email patterns
        if isinstance(value, str) and "@" in value and "." in value:
            return "***EMAIL_REDACTED***"
        
        # Redact phone patterns
        if isinstance(value, str) and re.match(r'^\+?[\d\s\-\(\)]{10,}$', value):
            return "***PHONE_REDACTED***"
        
        return value
    
    if isinstance(data, dict):
        return {k: redact_value(k, v) for k, v in data.items()}
    
    return data

# Configurable data filtering
if config.redact_inputs:
    inputs = redact_pii(inputs)
```

### Data Classification

```python
class DataClassification:
    """Classify data sensitivity levels."""
    
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    
    @staticmethod
    def classify_data(data: Dict[str, Any]) -> str:
        """Classify data based on content."""
        sensitive_indicators = [
            "password", "token", "key", "secret",
            "ssn", "credit_card", "bank_account"
        ]
        
        for key in data.keys():
            if any(indicator in key.lower() for indicator in sensitive_indicators):
                return DataClassification.RESTRICTED
        
        return DataClassification.INTERNAL
```

### Input Sanitization

```python
def sanitize_input(data: Any) -> Any:
    """Sanitize input data for security."""
    if isinstance(data, str):
        # Remove potential script injection
        data = re.sub(r'<script.*?</script>', '', data, flags=re.IGNORECASE)
        
        # Remove SQL injection patterns
        sql_patterns = ['DROP TABLE', 'DELETE FROM', 'INSERT INTO', 'UPDATE SET']
        for pattern in sql_patterns:
            data = data.replace(pattern, f"***{pattern}_BLOCKED***")
    
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    
    return data
```

## Secure Configuration

### Configuration Validation

```python
class SecureConfig:
    """Secure configuration management."""
    
    def __init__(self):
        self.api_key = self._validate_api_key()
        self.server_url = self._validate_server_url()
        self.timeout = self._validate_timeout()
    
    def _validate_api_key(self) -> str:
        """Validate and retrieve API key."""
        api_key = os.getenv("HH_API_KEY")
        
        if not api_key:
            raise ValueError("API key is required")
        
        if not APIKeyValidator.validate_format(api_key):
            raise ValueError("Invalid API key format")
        
        return api_key
    
    def _validate_server_url(self) -> str:
        """Validate server URL."""
        url = os.getenv("HH_SERVER_URL", "https://api.honeyhive.ai")
        
        # Ensure HTTPS in production
        if not url.startswith("https://") and not self._is_development():
            raise ValueError("HTTPS required for production")
        
        return url
    
    def _validate_timeout(self) -> float:
        """Validate timeout value."""
        timeout = os.getenv("HH_TIMEOUT", "30.0")
        try:
            value = float(timeout)
            if value <= 0 or value > 300:  # Max 5 minutes
                raise ValueError("Timeout must be between 0 and 300 seconds")
            return value
        except (ValueError, TypeError):
            logger.warning(f"Invalid timeout: {timeout}, using default")
            return 30.0
    
    def _is_development(self) -> bool:
        """Check if running in development mode."""
        return os.getenv("HH_ENVIRONMENT", "production").lower() in ["dev", "development", "local"]
```

### Secure Defaults

```python
# Security-first defaults
DEFAULT_CONFIG = {
    "timeout": 30.0,          # Reasonable timeout
    "max_retries": 3,         # Limit retry attempts
    "verify_ssl": True,       # Always verify SSL
    "redact_inputs": True,    # Redact PII by default
    "log_level": "INFO",      # Don't log debug by default
    "rate_limit": 100,        # Rate limiting
}

# Environment-specific overrides
if os.getenv("HH_ENVIRONMENT") == "development":
    DEFAULT_CONFIG.update({
        "verify_ssl": False,   # Allow self-signed certs in dev
        "log_level": "DEBUG",  # More verbose logging in dev
    })
```

## Dependency Security

### Dependency Scanning

```python
# Regular security scanning
# Run: pip-audit --desc --output=json
# Run: safety check --json

# Pin dependencies for security
# requirements.txt should have exact versions
requests==2.31.0  # Not requests>=2.0.0
```

### Secure HTTP Client Configuration

```python
import httpx
from urllib3.util.retry import Retry

class SecureHTTPClient:
    """HTTP client with security best practices."""
    
    def __init__(self):
        # Configure secure defaults
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            verify=True,  # Always verify SSL
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20
            ),
            headers={
                "User-Agent": f"HoneyHive-Python-SDK/{__version__}",
                "Accept": "application/json",
            }
        )
    
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make secure HTTP request."""
        # Add security headers
        headers = kwargs.get("headers", {})
        headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
        })
        kwargs["headers"] = headers
        
        # Validate URL
        if not url.startswith(("https://", "http://localhost")):
            raise ValueError("Only HTTPS URLs allowed (except localhost)")
        
        return await self.client.request(method, url, **kwargs)
```

## Authentication and Authorization

### Token Management

```python
class TokenManager:
    """Manage authentication tokens securely."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._token_cache = {}
        self._token_expiry = {}
    
    def get_bearer_token(self) -> str:
        """Get bearer token for API requests."""
        # Check cache first
        if self._is_token_valid():
            return self._token_cache.get("bearer")
        
        # Refresh token
        return self._refresh_token()
    
    def _is_token_valid(self) -> bool:
        """Check if cached token is still valid."""
        if "bearer" not in self._token_cache:
            return False
        
        expiry = self._token_expiry.get("bearer")
        if not expiry:
            return False
        
        # Check if token expires within 5 minutes
        return datetime.now() + timedelta(minutes=5) < expiry
    
    def _refresh_token(self) -> str:
        """Refresh authentication token."""
        # Implementation would call auth endpoint
        # Store with expiry time
        pass
```

### Request Signing

```python
import hmac
import hashlib
from datetime import datetime

class RequestSigner:
    """Sign requests for additional security."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def sign_request(self, method: str, url: str, body: str = "") -> str:
        """Generate request signature."""
        timestamp = str(int(datetime.now().timestamp()))
        
        # Create signature payload
        payload = f"{method}\n{url}\n{body}\n{timestamp}"
        
        # Generate HMAC signature
        signature = hmac.new(
            self.secret_key,
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}.{signature}"
    
    def verify_signature(self, signature: str, method: str, url: str, body: str = "") -> bool:
        """Verify request signature."""
        try:
            timestamp, expected_sig = signature.split(".", 1)
            
            # Check timestamp (within 5 minutes)
            request_time = datetime.fromtimestamp(int(timestamp))
            if datetime.now() - request_time > timedelta(minutes=5):
                return False
            
            # Verify signature
            payload = f"{method}\n{url}\n{body}\n{timestamp}"
            actual_sig = hmac.new(
                self.secret_key,
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_sig, actual_sig)
        
        except (ValueError, TypeError):
            return False
```

## Security Testing

### Security Test Cases

```python
import pytest
from unittest.mock import patch

class TestSecurity:
    """Security-focused test cases."""
    
    def test_api_key_not_logged(self, caplog):
        """Ensure API keys are never logged."""
        api_key = "hh_test_key_12345"
        
        # Initialize client
        client = HoneyHiveClient(api_key=api_key)
        
        # Check logs don't contain full API key
        for record in caplog.records:
            assert api_key not in record.message
            assert api_key not in str(record.args)
    
    def test_pii_redaction(self):
        """Test PII redaction functionality."""
        sensitive_data = {
            "email": "user@example.com",
            "ssn": "123-45-6789",
            "name": "John Doe",  # Not sensitive
        }
        
        redacted = redact_pii(sensitive_data)
        
        assert redacted["email"] == "***EMAIL_REDACTED***"
        assert redacted["ssn"] == "***REDACTED***"
        assert redacted["name"] == "John Doe"  # Unchanged
    
    def test_input_sanitization(self):
        """Test input sanitization."""
        malicious_input = "<script>alert('xss')</script>DROP TABLE users;"
        
        sanitized = sanitize_input(malicious_input)
        
        assert "<script>" not in sanitized
        assert "DROP TABLE" not in sanitized
    
    @patch.dict(os.environ, {"HH_API_KEY": "invalid_key"})
    def test_invalid_api_key_rejected(self):
        """Test invalid API keys are rejected."""
        with pytest.raises(ValueError, match="Invalid API key format"):
            SecureConfig()
```

### Penetration Testing Checklist

- [ ] **Input Validation**: Test with malicious inputs
- [ ] **Authentication**: Test with invalid/expired tokens
- [ ] **Authorization**: Test access to restricted resources
- [ ] **Data Exposure**: Verify no sensitive data in logs/responses
- [ ] **Rate Limiting**: Test API rate limits
- [ ] **SSL/TLS**: Verify secure connections
- [ ] **Dependency Vulnerabilities**: Regular security scans

## Incident Response

### Security Incident Handling

```python
class SecurityIncidentHandler:
    """Handle security incidents."""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
    
    def report_incident(self, incident_type: str, details: Dict[str, Any]):
        """Report security incident."""
        incident_id = self._generate_incident_id()
        
        # Log incident (without sensitive data)
        self.logger.critical(
            f"Security incident: {incident_type}",
            extra={
                "incident_id": incident_id,
                "incident_type": incident_type,
                "timestamp": datetime.now().isoformat(),
                "details": self._sanitize_details(details)
            }
        )
        
        # Alert security team
        self._alert_security_team(incident_id, incident_type, details)
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from incident details."""
        return redact_pii(details)
```

## References

- **[Configuration Management](configuration.md)** - Secure configuration practices
- **[Environment Setup](../development/environment-setup.md)** - Secure development environment
- **[Testing Standards](../development/testing-standards.md)** - Security testing requirements

---

**📝 Next Steps**: Review [Configuration Management](configuration.md) for secure configuration practices.
