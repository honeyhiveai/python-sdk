# Classes - Generation Phase

## 🎯 **PHASE 4: CODE GENERATION FOR CLASSES**

**Purpose**: Generate high-quality classes using proven templates and object-oriented design patterns.

**Quality Targets**: 10.0/10 Pylint, 0 MyPy errors, 100% type annotations, comprehensive docstrings, robust validation.

---

## 📋 **MANDATORY GENERATION COMMANDS**

### **Command 1: Select Class Template & Patterns**
```bash
# AI MUST select appropriate template and design patterns
echo "Template selected: [TEMPLATE_NAME] from classes/templates.md"
echo "Design patterns applied: [PATTERN_LIST]"
echo "OOP principles enforced: [PRINCIPLE_LIST]"
```

**Required Output:**
- Specific class template name and justification
- Design patterns to be implemented
- Object-oriented principles to enforce
- Template customization strategy

### **Command 2: Generate Class Structure**
```bash
# AI MUST generate complete class structure
echo "Class structure generated: attributes, methods, properties, inheritance"
```

**Required Output:**
- Complete class definition with inheritance
- All attributes with type annotations
- Method signatures and implementations
- Property definitions and logic
- Class and static methods

### **Command 3: Implement Validation Logic**
```bash
# AI MUST implement comprehensive validation
echo "Validation implemented: [FIELD_VALIDATION, CROSS_FIELD_VALIDATION, BUSINESS_RULES]"
```

**Required Output:**
- Field-level validation with custom validators
- Cross-field validation logic
- Business rule enforcement
- Validation error handling
- Custom exception types

### **Command 4: Add Serialization Support**
```bash
# AI MUST implement serialization/deserialization
echo "Serialization implemented: [JSON, DICT, DATABASE, API] with [TRANSFORMATION_LOGIC]"
```

**Required Output:**
- Multiple serialization formats
- Data transformation logic
- Deserialization with validation
- Custom serialization methods
- Format-specific optimizations

### **Command 5: Integrate Design Patterns**
```bash
# AI MUST integrate selected design patterns
echo "Design patterns integrated: [PATTERN_IMPLEMENTATIONS] with [PATTERN_INTERACTIONS]"
```

**Required Output:**
- Pattern implementations in class structure
- Pattern interactions and composition
- Pattern-specific methods and attributes
- Pattern compliance verification

---

## 🛠️ **PROVEN CLASS TEMPLATES**

**MANDATORY: Use existing proven templates from `templates.md`:**

### **📝 Available Templates:**
1. **Pydantic Data Model Template** - Validated data models with serialization
2. **Service Class Template** - Business logic and external service integration
3. **Configuration Class Template** - Settings management with validation
4. **Manager Class Template** - Resource and state management
5. **Factory Class Template** - Object creation and dependency injection
6. **Builder Class Template** - Complex object construction
7. **Repository Class Template** - Data access and persistence abstraction

### **🎯 Template Selection Criteria:**

| Class Type | Template | Use When |
|------------|----------|----------|
| **Data Models** | Pydantic Data Model | API models, configuration, validation |
| **Business Logic** | Service Class | External integrations, business operations |
| **Configuration** | Configuration Class | Settings, environment management |
| **Resource Management** | Manager Class | Resource lifecycle, state management |
| **Object Creation** | Factory Class | Dynamic object creation, plugin systems |
| **Complex Construction** | Builder Class | Multi-step object creation |
| **Data Access** | Repository Class | Database abstraction, data persistence |

---

## 🏗️ **DESIGN PATTERNS FOR CLASSES**

### **Essential Patterns to Apply:**

#### **1. Singleton Pattern (Configuration Classes)**
```python
from typing import Optional, Dict, Any
import threading

class ConfigurationManager:
    """Thread-safe singleton configuration manager."""
    
    _instance: Optional['ConfigurationManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'ConfigurationManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._config: Dict[str, Any] = {}
            self._initialized = True
```

#### **2. Factory Pattern (Object Creation)**
```python
from typing import Dict, Type, Any, Protocol
from abc import ABC, abstractmethod

class Processor(Protocol):
    def process(self, data: Any) -> Any: ...

class ProcessorFactory:
    """Factory for creating processor instances."""
    
    _processors: Dict[str, Type[Processor]] = {}
    
    @classmethod
    def register(cls, name: str, processor_class: Type[Processor]) -> None:
        """Register a processor class."""
        cls._processors[name] = processor_class
    
    @classmethod
    def create(cls, name: str, **kwargs) -> Processor:
        """Create a processor instance."""
        if name not in cls._processors:
            raise ValueError(f"Unknown processor type: {name}")
        
        processor_class = cls._processors[name]
        return processor_class(**kwargs)
```

#### **3. Builder Pattern (Complex Construction)**
```python
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class APIRequest:
    """API request configuration."""
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    timeout: float = 30.0

class APIRequestBuilder:
    """Builder for constructing API requests."""
    
    def __init__(self, url: str) -> None:
        self._url = url
        self._method = "GET"
        self._headers: Dict[str, str] = {}
        self._params: Dict[str, Any] = {}
        self._data: Optional[Dict[str, Any]] = None
        self._timeout = 30.0
    
    def method(self, method: str) -> 'APIRequestBuilder':
        """Set HTTP method."""
        self._method = method.upper()
        return self
    
    def header(self, key: str, value: str) -> 'APIRequestBuilder':
        """Add header."""
        self._headers[key] = value
        return self
    
    def param(self, key: str, value: Any) -> 'APIRequestBuilder':
        """Add query parameter."""
        self._params[key] = value
        return self
    
    def json_data(self, data: Dict[str, Any]) -> 'APIRequestBuilder':
        """Set JSON data."""
        self._data = data
        self._headers["Content-Type"] = "application/json"
        return self
    
    def timeout(self, seconds: float) -> 'APIRequestBuilder':
        """Set timeout."""
        self._timeout = seconds
        return self
    
    def build(self) -> APIRequest:
        """Build the API request."""
        return APIRequest(
            url=self._url,
            method=self._method,
            headers=self._headers.copy(),
            params=self._params.copy(),
            data=self._data.copy() if self._data else None,
            timeout=self._timeout
        )
```

#### **4. Repository Pattern (Data Access)**
```python
from typing import List, Optional, Dict, Any, Protocol
from abc import ABC, abstractmethod

class Entity(Protocol):
    id: str

class Repository(ABC, Generic[T]):
    """Abstract repository for data access."""
    
    @abstractmethod
    async def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    async def find_all(self, **filters) -> List[T]:
        """Find all entities matching filters."""
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save entity."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity by ID."""
        pass

class DatabaseRepository(Repository[T]):
    """Database implementation of repository pattern."""
    
    def __init__(self, db_client: DatabaseClient, table_name: str) -> None:
        self._db = db_client
        self._table = table_name
    
    async def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID."""
        query = f"SELECT * FROM {self._table} WHERE id = ?"
        result = await self._db.fetch_one(query, entity_id)
        return self._deserialize(result) if result else None
    
    async def save(self, entity: T) -> T:
        """Save entity with upsert logic."""
        data = self._serialize(entity)
        
        if await self.find_by_id(entity.id):
            # Update existing
            await self._update(entity.id, data)
        else:
            # Insert new
            await self._insert(data)
        
        return entity
```

#### **5. Observer Pattern (Event Handling)**
```python
from typing import List, Protocol, Any
from abc import ABC, abstractmethod

class Observer(Protocol):
    def update(self, event: str, data: Any) -> None: ...

class Observable:
    """Observable class for event notifications."""
    
    def __init__(self) -> None:
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event: str, data: Any = None) -> None:
        """Notify all observers."""
        for observer in self._observers:
            try:
                observer.update(event, data)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")
```

---

## 🔧 **GENERATION PROCESS**

### **Step 1: Template Customization**
**Apply comprehensive customizations to selected template:**

1. **Class Definition**: Set class name, inheritance, and metaclass
2. **Attributes**: Define all instance and class attributes with types
3. **Properties**: Implement computed properties with getters/setters
4. **Methods**: Implement all public and private methods
5. **Validation**: Add field and business rule validation
6. **Serialization**: Implement serialization/deserialization methods
7. **Design Patterns**: Integrate selected patterns
8. **Error Handling**: Add comprehensive exception handling
9. **Documentation**: Create detailed docstrings
10. **Testing Hooks**: Add testability features

### **Step 2: Quality Integration**
**Ensure generated code includes:**

1. **Type Safety**: 100% type annotation coverage
2. **Validation**: Comprehensive input validation
3. **Documentation**: Complete docstrings with examples
4. **Error Handling**: Robust exception handling
5. **Serialization**: Multiple format support
6. **Performance**: Optimized implementations
7. **Thread Safety**: Concurrent access considerations
8. **Testing**: Dependency injection and test-friendly design

### **Step 3: Pattern Integration**
**Integrate design patterns appropriately:**

1. **Pattern Selection**: Choose patterns based on class type
2. **Pattern Implementation**: Implement patterns correctly
3. **Pattern Composition**: Combine patterns effectively
4. **Pattern Testing**: Ensure patterns work as expected

### **Step 4: Code Verification**
**Verify generated code meets all criteria:**

1. **Template Compliance**: Follows selected template structure
2. **Requirements Coverage**: Meets all analysis phase requirements
3. **Pattern Implementation**: Design patterns correctly applied
4. **Quality Standards**: Ready for quality enforcement phase
5. **Integration Ready**: Can be integrated into larger system

---

## 📝 **GENERATION EXAMPLES**

### **Example 1: Pydantic Data Model**
```python
from datetime import datetime
from typing import Dict, List, Optional, Any, ClassVar
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from enum import Enum

class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserModel(BaseModel):
    """User data model with comprehensive validation and serialization.
    
    This model represents a user entity with complete validation rules,
    business logic enforcement, and multiple serialization formats.
    Designed for API communication, database storage, and configuration.
    
    Attributes:
        id: Unique user identifier (UUID format)
        name: User's full name (1-100 characters)
        email: User's email address (validated format)
        age: User's age (0-150 years)
        role: User's role in the system
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        tags: List of user tags for categorization
        metadata: Additional user metadata
        is_active: Whether the user account is active
        
    Example:
        >>> user = UserModel(
        ...     name="John Doe",
        ...     email="john@example.com",
        ...     age=30,
        ...     role=UserRole.USER
        ... )
        >>> print(user.display_name)
        "John Doe"
        >>> user_dict = user.to_api_dict()
    """
    
    # Class configuration
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = False
        extra = "forbid"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    # Core attributes
    id: Optional[str] = Field(
        None,
        description="Unique user identifier",
        regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    )
    
    name: str = Field(
        ...,
        description="User's full name",
        min_length=1,
        max_length=100,
        strip_whitespace=True
    )
    
    email: EmailStr = Field(
        ...,
        description="User's email address"
    )
    
    age: int = Field(
        ...,
        description="User's age in years",
        ge=0,
        le=150
    )
    
    role: UserRole = Field(
        UserRole.USER,
        description="User's role in the system"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    
    updated_at: Optional[datetime] = Field(
        None,
        description="Last update timestamp"
    )
    
    # Collections
    tags: List[str] = Field(
        default_factory=list,
        description="User tags for categorization",
        max_items=20
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional user metadata"
    )
    
    # Status
    is_active: bool = Field(
        True,
        description="Whether the user account is active"
    )
    
    # Class constants
    MIN_AGE_FOR_ADMIN: ClassVar[int] = 18
    MAX_TAGS_PER_USER: ClassVar[int] = 20
    
    # Computed properties
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        return self.name.title()
    
    @property
    def is_adult(self) -> bool:
        """Check if user is an adult."""
        return self.age >= 18
    
    @property
    def age_group(self) -> str:
        """Get user's age group category."""
        if self.age < 13:
            return "child"
        elif self.age < 18:
            return "teen"
        elif self.age < 65:
            return "adult"
        else:
            return "senior"
    
    @property
    def can_be_admin(self) -> bool:
        """Check if user can have admin role."""
        return self.age >= self.MIN_AGE_FOR_ADMIN and self.is_active
    
    # Field validators
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate user name."""
        if not v or v.isspace():
            raise ValueError("Name cannot be empty or whitespace")
        
        # Check for email patterns in name
        if '@' in v:
            raise ValueError("Name cannot contain email address")
        
        # Check for special characters
        if any(char in v for char in ['<', '>', '&', '"', "'"]):
            raise ValueError("Name contains invalid characters")
        
        return v
    
    @validator('tags')
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate user tags."""
        if len(v) > cls.MAX_TAGS_PER_USER:
            raise ValueError(f"Maximum {cls.MAX_TAGS_PER_USER} tags allowed")
        
        # Remove duplicates and empty tags
        unique_tags = []
        for tag in v:
            tag = tag.strip().lower()
            if tag and tag not in unique_tags:
                unique_tags.append(tag)
        
        return unique_tags
    
    @validator('metadata')
    def validate_metadata(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata dictionary."""
        # Limit metadata size
        if len(v) > 50:
            raise ValueError("Maximum 50 metadata keys allowed")
        
        # Check key format
        for key in v.keys():
            if not isinstance(key, str) or len(key) > 100:
                raise ValueError("Metadata keys must be strings under 100 characters")
        
        return v
    
    # Root validators (cross-field validation)
    @root_validator
    def validate_admin_requirements(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate admin role requirements."""
        role = values.get('role')
        age = values.get('age')
        is_active = values.get('is_active')
        
        if role == UserRole.ADMIN:
            if age is not None and age < cls.MIN_AGE_FOR_ADMIN:
                raise ValueError(f"Admin users must be at least {cls.MIN_AGE_FOR_ADMIN} years old")
            
            if not is_active:
                raise ValueError("Admin users must have active accounts")
        
        return values
    
    @root_validator
    def validate_email_domain_restrictions(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate email domain restrictions based on role."""
        email = values.get('email')
        role = values.get('role')
        
        if email and role == UserRole.ADMIN:
            # Admin users must use company domain
            if not email.endswith('@company.com'):
                raise ValueError("Admin users must use company email domain")
        
        return values
    
    # Business logic methods
    def update_metadata(self, key: str, value: Any) -> None:
        """Update metadata with validation."""
        if len(key) > 100:
            raise ValueError("Metadata key too long")
        
        if len(self.metadata) >= 50 and key not in self.metadata:
            raise ValueError("Maximum metadata entries reached")
        
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag with validation."""
        tag = tag.strip().lower()
        
        if not tag:
            raise ValueError("Tag cannot be empty")
        
        if len(self.tags) >= self.MAX_TAGS_PER_USER:
            raise ValueError(f"Maximum {self.MAX_TAGS_PER_USER} tags allowed")
        
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag if it exists."""
        tag = tag.strip().lower()
        
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
            return True
        
        return False
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        if self.role == UserRole.ADMIN:
            raise ValueError("Cannot deactivate admin users")
        
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def promote_to_admin(self) -> None:
        """Promote user to admin role."""
        if not self.can_be_admin:
            raise ValueError("User does not meet admin requirements")
        
        self.role = UserRole.ADMIN
        self.updated_at = datetime.utcnow()
    
    # Serialization methods
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with all fields."""
        return self.dict()
    
    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to API response format (exclude internal fields)."""
        return self.dict(exclude={'metadata', 'updated_at'})
    
    def to_database_dict(self) -> Dict[str, Any]:
        """Convert to database storage format."""
        data = self.dict()
        
        # Convert datetime to ISO format
        if data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        if data['updated_at']:
            data['updated_at'] = data['updated_at'].isoformat()
        
        # Convert role to string
        data['role'] = data['role'].value if hasattr(data['role'], 'value') else data['role']
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserModel':
        """Create instance from dictionary with validation."""
        # Convert datetime strings back to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    @classmethod
    def from_api_request(cls, data: Dict[str, Any]) -> 'UserModel':
        """Create instance from API request data."""
        # Filter out read-only fields
        allowed_fields = {'name', 'email', 'age', 'role', 'tags', 'metadata'}
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        return cls(**filtered_data)
    
    # Utility methods
    def __str__(self) -> str:
        """String representation."""
        return f"UserModel(id={self.id}, name='{self.name}', email='{self.email}')"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"UserModel(id={self.id!r}, name={self.name!r}, "
            f"email={self.email!r}, age={self.age}, role={self.role!r})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison based on ID."""
        if not isinstance(other, UserModel):
            return NotImplemented
        
        return self.id == other.id if self.id and other.id else False
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id) if self.id else hash(id(self))
```

### **Example 2: Service Class with Async Operations**
```python
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, AsyncContextManager
from contextlib import asynccontextmanager
import httpx
from dataclasses import dataclass, field

from ..models.errors import APIError, AuthenticationError, RateLimitError
from ..utils.circuit_breaker import AsyncCircuitBreaker
from ..utils.rate_limiter import AsyncRateLimiter
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configuration for API service."""
    base_url: str
    api_key: str
    timeout: float = 30.0
    max_retries: int = 3
    rate_limit: int = 100  # requests per minute
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0

class ExternalAPIService:
    """Service class for external API integration with comprehensive error handling.
    
    This service provides a robust interface for communicating with external APIs,
    including authentication, rate limiting, circuit breaker pattern, retry logic,
    and comprehensive error handling. Designed for high-reliability production use.
    
    Features:
    - Async HTTP client with connection pooling
    - Automatic authentication and token refresh
    - Rate limiting to respect API quotas
    - Circuit breaker for failure protection
    - Exponential backoff retry logic
    - Comprehensive error handling and recovery
    - Request/response logging and metrics
    - Health monitoring and status reporting
    
    Example:
        >>> config = APIConfig(
        ...     base_url="https://api.example.com",
        ...     api_key="your-api-key"
        ... )
        >>> 
        >>> async with ExternalAPIService(config) as service:
        ...     result = await service.get("/users/123")
        ...     print(result["name"])
    """
    
    def __init__(self, config: APIConfig) -> None:
        """Initialize API service with configuration.
        
        Args:
            config: API configuration with connection settings
            
        Raises:
            ValueError: If configuration is invalid
        """
        self._validate_config(config)
        
        self._config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._authenticated = False
        self._auth_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        
        # Initialize components
        self._circuit_breaker = AsyncCircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold,
            timeout=config.circuit_breaker_timeout
        )
        
        self._rate_limiter = AsyncRateLimiter(
            max_requests=config.rate_limit,
            time_window=60.0  # per minute
        )
        
        self._metrics = MetricsCollector("external_api_service")
        
        # Request statistics
        self._request_count = 0
        self._error_count = 0
        self._last_request_time: Optional[float] = None
        
        logger.info(f"Initialized API service for {config.base_url}")
    
    async def __aenter__(self) -> 'ExternalAPIService':
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    # Connection management
    async def connect(self) -> None:
        """Establish connection to API service."""
        if self._client is not None:
            return
        
        try:
            self._client = httpx.AsyncClient(
                base_url=self._config.base_url,
                timeout=httpx.Timeout(self._config.timeout),
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100
                )
            )
            
            # Authenticate on connection
            await self._authenticate()
            
            logger.info("API service connected successfully")
            self._metrics.increment("connection_established")
            
        except Exception as e:
            logger.error(f"Failed to connect to API service: {e}")
            self._metrics.increment("connection_failed")
            raise APIError(f"Connection failed: {e}") from e
    
    async def close(self) -> None:
        """Close API service connection."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            self._authenticated = False
            self._auth_token = None
            
            logger.info("API service connection closed")
            self._metrics.increment("connection_closed")
    
    # Authentication
    async def _authenticate(self) -> None:
        """Authenticate with API service."""
        if not self._client:
            raise APIError("Client not connected")
        
        try:
            response = await self._client.post(
                "/auth/token",
                json={"api_key": self._config.api_key}
            )
            response.raise_for_status()
            
            auth_data = response.json()
            self._auth_token = auth_data["access_token"]
            self._token_expires_at = time.time() + auth_data.get("expires_in", 3600)
            self._authenticated = True
            
            logger.info("API authentication successful")
            self._metrics.increment("authentication_success")
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key") from e
            else:
                raise APIError(f"Authentication failed: {e}") from e
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            self._metrics.increment("authentication_failed")
            raise APIError(f"Authentication error: {e}") from e
    
    async def _ensure_authenticated(self) -> None:
        """Ensure valid authentication token."""
        if not self._authenticated or not self._auth_token:
            await self._authenticate()
            return
        
        # Check token expiration
        if self._token_expires_at and time.time() >= self._token_expires_at - 300:  # 5 min buffer
            logger.info("Token expiring soon, refreshing...")
            await self._authenticate()
    
    # HTTP methods
    async def get(
        self,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """Make GET request to API endpoint.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Parsed JSON response
            
        Raises:
            APIError: For API-related errors
            RateLimitError: When rate limit is exceeded
        """
        return await self._make_request("GET", endpoint, params=params, headers=headers)
    
    async def post(
        self,
        endpoint: str,
        *,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """Make POST request to API endpoint.
        
        Args:
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Parsed JSON response
            
        Raises:
            APIError: For API-related errors
            RateLimitError: When rate limit is exceeded
        """
        return await self._make_request("POST", endpoint, data=data, params=params, headers=headers)
    
    async def put(
        self,
        endpoint: str,
        *,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """Make PUT request to API endpoint."""
        return await self._make_request("PUT", endpoint, data=data, params=params, headers=headers)
    
    async def delete(
        self,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """Make DELETE request to API endpoint."""
        return await self._make_request("DELETE", endpoint, params=params, headers=headers)
    
    # Core request method
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        *,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """Make HTTP request with comprehensive error handling."""
        if not self._client:
            raise APIError("Client not connected")
        
        # Rate limiting
        await self._rate_limiter.acquire()
        
        # Circuit breaker check
        if self._circuit_breaker.is_open():
            raise APIError("Circuit breaker is open - service unavailable")
        
        # Ensure authentication
        await self._ensure_authenticated()
        
        # Prepare request
        request_headers = {"Authorization": f"Bearer {self._auth_token}"}
        if headers:
            request_headers.update(headers)
        
        request_data = {
            "method": method,
            "url": endpoint,
            "params": params,
            "headers": request_headers
        }
        
        if data is not None:
            request_data["json"] = data
        
        # Execute request with retry logic
        last_exception = None
        
        for attempt in range(self._config.max_retries + 1):
            try:
                start_time = time.time()
                
                response = await self._client.request(**request_data)
                
                # Record metrics
                request_time = time.time() - start_time
                self._metrics.histogram("request_duration", request_time)
                self._metrics.increment(f"request_{method.lower()}")
                
                # Handle response
                await self._handle_response(response)
                
                # Parse and return result
                result = await self._parse_response(response)
                
                # Success - record in circuit breaker
                self._circuit_breaker.record_success()
                self._request_count += 1
                self._last_request_time = time.time()
                
                logger.debug(f"Request successful: {method} {endpoint}")
                return result
                
            except httpx.HTTPStatusError as e:
                last_exception = await self._handle_http_error(e, attempt)
                
            except httpx.RequestError as e:
                last_exception = await self._handle_request_error(e, attempt)
                
            except Exception as e:
                last_exception = APIError(f"Unexpected error: {e}")
                logger.error(f"Unexpected request error: {e}")
                break
            
            # Exponential backoff for retries
            if attempt < self._config.max_retries:
                delay = 2 ** attempt
                logger.warning(f"Request failed, retrying in {delay}s (attempt {attempt + 1})")
                await asyncio.sleep(delay)
        
        # All retries exhausted
        self._circuit_breaker.record_failure()
        self._error_count += 1
        self._metrics.increment("request_failed")
        
        logger.error(f"Request failed after {self._config.max_retries + 1} attempts: {method} {endpoint}")
        raise last_exception
    
    # Response handling
    async def _handle_response(self, response: httpx.Response) -> None:
        """Handle HTTP response status codes."""
        if response.status_code == 429:
            # Rate limit exceeded
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(f"Rate limit exceeded, retry after {retry_after}s")
        
        if response.status_code == 401:
            # Authentication failed
            self._authenticated = False
            self._auth_token = None
            raise AuthenticationError("Authentication failed")
        
        # Raise for other HTTP errors
        response.raise_for_status()
    
    async def _parse_response(self, response: httpx.Response) -> Union[Dict[str, Any], List[Any]]:
        """Parse HTTP response to JSON."""
        try:
            return response.json()
        except ValueError as e:
            # Non-JSON response
            if response.status_code == 204:  # No Content
                return {}
            
            logger.warning(f"Non-JSON response: {response.text[:200]}")
            raise APIError(f"Invalid JSON response: {e}") from e
    
    async def _handle_http_error(self, error: httpx.HTTPStatusError, attempt: int) -> APIError:
        """Handle HTTP status errors."""
        status_code = error.response.status_code
        
        if 400 <= status_code < 500:
            # Client errors - don't retry
            error_msg = f"Client error {status_code}: {error}"
            logger.error(error_msg)
            return APIError(error_msg)
        
        elif 500 <= status_code < 600:
            # Server errors - retry
            error_msg = f"Server error {status_code}: {error}"
            logger.warning(f"Server error on attempt {attempt + 1}: {error_msg}")
            return APIError(error_msg)
        
        else:
            # Other status codes
            error_msg = f"HTTP error {status_code}: {error}"
            logger.error(error_msg)
            return APIError(error_msg)
    
    async def _handle_request_error(self, error: httpx.RequestError, attempt: int) -> APIError:
        """Handle request errors (network, timeout, etc.)."""
        if isinstance(error, httpx.TimeoutException):
            error_msg = f"Request timeout: {error}"
            logger.warning(f"Timeout on attempt {attempt + 1}: {error_msg}")
            return APIError(error_msg)
        
        elif isinstance(error, httpx.ConnectError):
            error_msg = f"Connection error: {error}"
            logger.warning(f"Connection error on attempt {attempt + 1}: {error_msg}")
            return APIError(error_msg)
        
        else:
            error_msg = f"Request error: {error}"
            logger.error(error_msg)
            return APIError(error_msg)
    
    # Health and status
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on API service.
        
        Returns:
            Health status information
        """
        try:
            start_time = time.time()
            
            # Make a simple request to check connectivity
            await self.get("/health")
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "authenticated": self._authenticated,
                "circuit_breaker_open": self._circuit_breaker.is_open(),
                "request_count": self._request_count,
                "error_count": self._error_count,
                "error_rate": self._error_count / max(self._request_count, 1)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "authenticated": self._authenticated,
                "circuit_breaker_open": self._circuit_breaker.is_open(),
                "request_count": self._request_count,
                "error_count": self._error_count
            }
    
    # Properties
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._client is not None
    
    @property
    def is_authenticated(self) -> bool:
        """Check if service is authenticated."""
        return self._authenticated
    
    @property
    def request_count(self) -> int:
        """Get total request count."""
        return self._request_count
    
    @property
    def error_count(self) -> int:
        """Get total error count."""
        return self._error_count
    
    @property
    def error_rate(self) -> float:
        """Get current error rate."""
        return self._error_count / max(self._request_count, 1)
    
    # Utility methods
    def _validate_config(self, config: APIConfig) -> None:
        """Validate API configuration."""
        if not config.base_url:
            raise ValueError("base_url is required")
        
        if not config.api_key:
            raise ValueError("api_key is required")
        
        if config.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        if config.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        
        if config.rate_limit <= 0:
            raise ValueError("rate_limit must be positive")
    
    def __str__(self) -> str:
        """String representation."""
        return f"ExternalAPIService(base_url='{self._config.base_url}')"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"ExternalAPIService(base_url={self._config.base_url!r}, "
            f"connected={self.is_connected}, authenticated={self.is_authenticated})"
        )
```

---

## 🎯 **GENERATION QUALITY CHECKLIST**

### **✅ Template Compliance**
- [ ] **Template selected** from available class templates
- [ ] **Template structure followed** with all required sections
- [ ] **Template customizations applied** appropriately
- [ ] **Design patterns integrated** correctly

### **✅ Class Structure Quality**
- [ ] **Class definition** complete with proper inheritance
- [ ] **Attributes** all defined with type annotations
- [ ] **Methods** implemented with proper signatures
- [ ] **Properties** computed correctly with getters/setters
- [ ] **Class/static methods** used appropriately

### **✅ Validation Implementation**
- [ ] **Field validation** comprehensive with custom validators
- [ ] **Cross-field validation** implemented correctly
- [ ] **Business rules** enforced with clear error messages
- [ ] **Custom exceptions** defined and used appropriately
- [ ] **Validation error handling** robust and informative

### **✅ Serialization Support**
- [ ] **Multiple formats** supported (JSON, dict, database)
- [ ] **Serialization methods** implemented correctly
- [ ] **Deserialization** with validation
- [ ] **Custom transformations** applied appropriately
- [ ] **Format-specific optimizations** included

### **✅ Design Pattern Implementation**
- [ ] **Patterns selected** appropriately for class type
- [ ] **Pattern implementation** follows best practices
- [ ] **Pattern integration** works seamlessly
- [ ] **Pattern interactions** handled correctly

### **✅ Documentation Quality**
- [ ] **Class docstring** comprehensive with purpose and examples
- [ ] **Method documentation** complete with parameters and returns
- [ ] **Attribute documentation** clear with types and constraints
- [ ] **Usage examples** multiple scenarios covered
- [ ] **Design notes** architecture decisions explained

---

## 🚨 **GENERATION GATE CRITERIA**

**✅ GATE PASSED WHEN:**
- Template selected and properly customized
- All 5 mandatory commands executed with evidence
- Class structure complete with all components
- Validation logic comprehensive and tested
- Serialization support implemented for all required formats
- Design patterns correctly integrated
- Quality checklist completed
- Code ready for quality enforcement

**❌ GATE FAILED IF:**
- No template used or improperly customized
- Class structure incomplete or incorrect
- Validation logic insufficient or missing
- Serialization support inadequate
- Design patterns missing or incorrect
- Quality standards not met

---

**💡 Key Principle**: Class generation requires systematic application of object-oriented design principles, proven templates, and comprehensive validation to create robust, maintainable, and extensible class implementations.
