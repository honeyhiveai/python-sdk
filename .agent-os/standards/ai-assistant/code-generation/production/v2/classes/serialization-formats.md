# Classes - Serialization Formats (v2)

## 🎯 **SERIALIZATION FORMATS FOR CLASSES**

**Purpose**: Comprehensive serialization and deserialization strategies for multiple formats and use cases.

**Focus**: JSON, dictionary, database, API, and cache serialization with transformation logic.

---

## 📋 **SERIALIZATION FORMATS**

### **1. JSON Serialization**
**Purpose**: Standard JSON format for API communication and file storage

```python
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserModel(BaseModel):
    """User model with JSON serialization."""
    
    name: str
    email: str
    role: UserRole
    created_at: datetime
    metadata: Dict[str, Any] = {}
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UserRole: lambda v: v.value
        }
    
    def to_json(self, *, indent: Optional[int] = None) -> str:
        """Convert to JSON string."""
        return self.json(indent=indent)
    
    def to_json_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        data = self.dict()
        
        # Convert datetime to ISO string
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        
        # Convert enum to value
        if isinstance(data.get('role'), UserRole):
            data['role'] = data['role'].value
        
        return data
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UserModel':
        """Create instance from JSON string."""
        return cls.parse_raw(json_str)
    
    @classmethod
    def from_json_dict(cls, data: Dict[str, Any]) -> 'UserModel':
        """Create instance from JSON dictionary."""
        # Convert ISO string to datetime
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # Convert string to enum
        if 'role' in data and isinstance(data['role'], str):
            data['role'] = UserRole(data['role'])
        
        return cls(**data)
```

### **2. API Response Serialization**
**Purpose**: Optimized format for API responses with field filtering and computed fields

```python
from typing import Set, Optional, List

class UserModel(BaseModel):
    """User model with API serialization."""
    
    id: str
    name: str
    email: str
    age: int
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    _internal_notes: str = ""  # Internal field
    
    def to_api_response(
        self,
        *,
        include_sensitive: bool = False,
        include_computed: bool = True,
        exclude_fields: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """Convert to API response format with field control."""
        
        # Base exclusions
        exclude = {'_internal_notes'}
        
        # Add sensitive fields if not requested
        if not include_sensitive:
            exclude.update({'metadata', 'last_login'})
        
        # Add user-specified exclusions
        if exclude_fields:
            exclude.update(exclude_fields)
        
        # Get base data
        data = self.dict(exclude=exclude)
        
        # Format timestamps for API
        if 'created_at' in data and data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        
        if 'last_login' in data and data['last_login']:
            data['last_login'] = data['last_login'].isoformat()
        
        # Add computed fields if requested
        if include_computed:
            data['display_name'] = self.name.title()
            data['is_adult'] = self.age >= 18
            data['account_age_days'] = (datetime.now() - self.created_at).days
        
        # Add API metadata
        data['_api_version'] = '2.1'
        data['_timestamp'] = datetime.now().isoformat()
        
        return data
    
    def to_public_api_response(self) -> Dict[str, Any]:
        """Convert to public API format (minimal data)."""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.name.title(),
            'role': self.role.value,
            'is_adult': self.age >= 18
        }
    
    def to_admin_api_response(self) -> Dict[str, Any]:
        """Convert to admin API format (full data)."""
        return self.to_api_response(
            include_sensitive=True,
            include_computed=True
        )
```

### **3. Database Serialization**
**Purpose**: Optimized format for database storage with normalization and indexing

```python
import time
from typing import Dict, Any, Optional

class UserModel(BaseModel):
    """User model with database serialization."""
    
    def to_database_dict(self) -> Dict[str, Any]:
        """Convert to database storage format."""
        data = self.dict()
        
        # Convert datetime objects to timestamps for database efficiency
        if 'created_at' in data and data['created_at']:
            data['created_at'] = int(data['created_at'].timestamp())
        
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = int(data['updated_at'].timestamp())
        
        # Convert enum to string for database storage
        if 'role' in data and hasattr(data['role'], 'value'):
            data['role'] = data['role'].value
        
        # Serialize complex fields as JSON strings
        if 'metadata' in data and data['metadata']:
            data['metadata'] = json.dumps(data['metadata'])
        
        # Add database-specific fields
        data['_schema_version'] = '2.1.0'
        data['_created_timestamp'] = int(time.time())
        data['_updated_timestamp'] = int(time.time())
        
        # Create search-optimized fields
        data['name_lower'] = data.get('name', '').lower()
        data['email_domain'] = data.get('email', '').split('@')[-1] if '@' in data.get('email', '') else ''
        
        return data
    
    @classmethod
    def from_database_dict(cls, data: Dict[str, Any]) -> 'UserModel':
        """Create instance from database record."""
        # Convert timestamps back to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], (int, float)):
            data['created_at'] = datetime.fromtimestamp(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], (int, float)):
            data['updated_at'] = datetime.fromtimestamp(data['updated_at'])
        
        # Convert string back to enum
        if 'role' in data and isinstance(data['role'], str):
            data['role'] = UserRole(data['role'])
        
        # Deserialize JSON fields
        if 'metadata' in data and isinstance(data['metadata'], str):
            try:
                data['metadata'] = json.loads(data['metadata'])
            except json.JSONDecodeError:
                data['metadata'] = {}
        
        # Remove database-specific fields
        for key in list(data.keys()):
            if key.startswith('_') or key.endswith('_lower') or key.endswith('_domain'):
                data.pop(key, None)
        
        return cls(**data)
    
    def to_database_insert(self) -> Dict[str, Any]:
        """Convert to database insert format with all required fields."""
        data = self.to_database_dict()
        
        # Ensure required fields for insert
        if 'id' not in data or not data['id']:
            import uuid
            data['id'] = str(uuid.uuid4())
        
        return data
    
    def to_database_update(self) -> Dict[str, Any]:
        """Convert to database update format (exclude immutable fields)."""
        data = self.to_database_dict()
        
        # Remove fields that shouldn't be updated
        immutable_fields = {'id', 'created_at', '_created_timestamp'}
        for field in immutable_fields:
            data.pop(field, None)
        
        return data
```

### **4. Cache Serialization**
**Purpose**: Lightweight format for caching with size optimization and TTL support

```python
import pickle
import zlib
from typing import Dict, Any, Optional

class UserModel(BaseModel):
    """User model with cache serialization."""
    
    def to_cache_dict(self, *, compress: bool = False) -> Dict[str, Any]:
        """Convert to cache format with size optimization."""
        # Minimal data for caching
        cache_data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role.value,
            'is_active': getattr(self, 'is_active', True),
            'display_name': self.name.title(),
            '_cached_at': time.time(),
            '_cache_version': '1.0'
        }
        
        if compress:
            # Compress large fields
            if len(str(cache_data)) > 1000:
                cache_data = {
                    '_compressed': True,
                    '_data': zlib.compress(pickle.dumps(cache_data))
                }
        
        return cache_data
    
    @classmethod
    def from_cache_dict(cls, data: Dict[str, Any]) -> Optional['UserModel']:
        """Create instance from cache data."""
        try:
            # Handle compressed data
            if data.get('_compressed'):
                data = pickle.loads(zlib.decompress(data['_data']))
            
            # Check cache version compatibility
            cache_version = data.get('_cache_version', '1.0')
            if cache_version != '1.0':
                return None  # Cache version mismatch
            
            # Check cache age
            cached_at = data.get('_cached_at', 0)
            cache_ttl = 3600  # 1 hour
            if time.time() - cached_at > cache_ttl:
                return None  # Cache expired
            
            # Convert role back to enum
            if 'role' in data:
                data['role'] = UserRole(data['role'])
            
            # Remove cache-specific fields
            for key in ['_cached_at', '_cache_version', 'display_name']:
                data.pop(key, None)
            
            return cls(**data)
            
        except (KeyError, ValueError, pickle.PickleError, zlib.error):
            return None  # Cache corruption
    
    def to_cache_key(self) -> str:
        """Generate cache key for this instance."""
        return f"user:{self.id}:v1"
    
    @classmethod
    def cache_key_pattern(cls) -> str:
        """Get cache key pattern for bulk operations."""
        return "user:*:v1"
```

### **5. Configuration Serialization**
**Purpose**: Human-readable format for configuration files and settings

```python
import yaml
from typing import Dict, Any, Union

class ConfigModel(BaseModel):
    """Configuration model with YAML/TOML serialization."""
    
    def to_yaml(self, *, flow_style: bool = False) -> str:
        """Convert to YAML format."""
        data = self._prepare_config_data()
        return yaml.dump(data, default_flow_style=flow_style, sort_keys=True)
    
    def to_toml(self) -> str:
        """Convert to TOML format."""
        try:
            import toml
        except ImportError:
            raise ImportError("toml package required for TOML serialization")
        
        data = self._prepare_config_data()
        return toml.dumps(data)
    
    def to_env_vars(self, prefix: str = "") -> Dict[str, str]:
        """Convert to environment variables format."""
        data = self._prepare_config_data()
        env_vars = {}
        
        def flatten_dict(d: Dict[str, Any], parent_key: str = "") -> None:
            for key, value in d.items():
                env_key = f"{parent_key}_{key}".upper() if parent_key else key.upper()
                
                if isinstance(value, dict):
                    flatten_dict(value, env_key)
                elif isinstance(value, list):
                    env_vars[env_key] = ",".join(str(v) for v in value)
                else:
                    env_vars[env_key] = str(value)
        
        flatten_dict(data, prefix)
        return env_vars
    
    def _prepare_config_data(self) -> Dict[str, Any]:
        """Prepare data for configuration serialization."""
        data = self.dict()
        
        # Convert datetime to ISO string
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif hasattr(value, 'value'):  # Enum
                data[key] = value.value
        
        # Remove internal fields
        return {k: v for k, v in data.items() if not k.startswith('_')}
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'ConfigModel':
        """Create instance from YAML string."""
        data = yaml.safe_load(yaml_str)
        return cls(**data)
    
    @classmethod
    def from_env_vars(cls, env_vars: Dict[str, str], prefix: str = "") -> 'ConfigModel':
        """Create instance from environment variables."""
        data = {}
        prefix_len = len(prefix) + 1 if prefix else 0
        
        for key, value in env_vars.items():
            if prefix and not key.startswith(f"{prefix}_"):
                continue
            
            clean_key = key[prefix_len:].lower()
            
            # Handle comma-separated lists
            if ',' in value:
                data[clean_key] = value.split(',')
            # Handle boolean values
            elif value.lower() in ('true', 'false'):
                data[clean_key] = value.lower() == 'true'
            # Handle numeric values
            elif value.isdigit():
                data[clean_key] = int(value)
            else:
                data[clean_key] = value
        
        return cls(**data)
```

---

## 🔧 **SERIALIZATION PATTERNS**

### **Format Strategy Pattern**
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class SerializationStrategy(ABC):
    """Abstract serialization strategy."""
    
    @abstractmethod
    def serialize(self, obj: Any) -> Any:
        pass
    
    @abstractmethod
    def deserialize(self, data: Any) -> Any:
        pass

class JSONStrategy(SerializationStrategy):
    """JSON serialization strategy."""
    
    def serialize(self, obj: BaseModel) -> str:
        return obj.json()
    
    def deserialize(self, data: str) -> BaseModel:
        return BaseModel.parse_raw(data)

class SerializationContext:
    """Context for managing serialization strategies."""
    
    def __init__(self) -> None:
        self._strategies: Dict[str, SerializationStrategy] = {}
    
    def register_strategy(self, format_name: str, strategy: SerializationStrategy) -> None:
        """Register serialization strategy."""
        self._strategies[format_name] = strategy
    
    def serialize(self, obj: Any, format_name: str) -> Any:
        """Serialize using specified format."""
        if format_name not in self._strategies:
            raise ValueError(f"Unknown format: {format_name}")
        
        return self._strategies[format_name].serialize(obj)
```

---

## 📊 **SERIALIZATION BEST PRACTICES**

### **✅ Performance Optimization**
- [ ] **Lazy serialization** - Only serialize when needed
- [ ] **Field selection** - Allow selective field serialization
- [ ] **Compression** - Use compression for large objects
- [ ] **Caching** - Cache serialized results when appropriate
- [ ] **Streaming** - Use streaming for large datasets

### **✅ Data Integrity**
- [ ] **Version compatibility** - Handle schema evolution
- [ ] **Validation** - Validate during deserialization
- [ ] **Error handling** - Graceful handling of corruption
- [ ] **Type safety** - Maintain type information
- [ ] **Round-trip testing** - Ensure serialize/deserialize consistency

### **✅ Security Considerations**
- [ ] **Sensitive data** - Exclude sensitive fields appropriately
- [ ] **Input validation** - Validate all deserialized data
- [ ] **Injection prevention** - Prevent code injection attacks
- [ ] **Size limits** - Limit serialized data size
- [ ] **Access control** - Control serialization permissions

---

## 🔗 **RELATED MODULES**

**For complete class implementation, also see:**
- **📋 [Analysis Core](analysis-core.md)** - Requirements gathering (257 lines)
- **🎨 [OOP Patterns](oop-patterns.md)** - Design patterns (504 lines)
- **🔧 [Generation Core](generation-core.md)** - Class creation (290 lines)
- **🛡️ [Validation Strategies](validation-strategies.md)** - Validation patterns (436 lines)
- **📊 [Quality Core](quality-core.md)** - Quality enforcement (pending)

---

**💡 Key Principle**: Serialization strategies should be format-specific, performance-optimized, and maintain data integrity while providing flexibility for different use cases.
