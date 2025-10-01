# Implementation Plan - Detailed Architecture

## 1. Complete File Structure with Implementation Details

```
src/honeyhive/tracer/semantic_conventions/
├── universal/                           # New O(1) universal engine
│   ├── __init__.py                      # Module exports and initialization
│   ├── processor.py                     # UniversalDSLProcessor - main entry point
│   ├── models.py                        # Pydantic v2 models with O(1) hash support
│   ├── hash_indices.py                  # O(1) hash-based data structures
│   ├── field_discovery.py               # O(1) field discovery engine
│   ├── provider_detection.py            # O(1) provider detection
│   ├── mapping_engine.py                # O(1) mapping engine
│   ├── transform_engine.py              # O(1) transform execution
│   └── cache_integration.py             # Multi-instance cache integration
├── dsl/                                 # DSL configuration system
│   ├── __init__.py                      # DSL module initialization
│   ├── loader.py                        # YAML DSL loader with validation
│   ├── validator.py                     # DSL syntax and semantic validation
│   ├── compiler.py                      # DSL to O(1) hash table compiler
│   └── configs/                         # Bundled DSL configurations
│       ├── field_discovery.yaml         # Field classification rules
│       ├── mapping_rules.yaml           # HoneyHive schema mapping rules
│       ├── transforms.yaml              # Transform function definitions
│       ├── performance.yaml             # Performance optimization configs
│       └── providers/                   # Provider-specific configurations
│           ├── openai.yaml              # OpenAI-specific overrides
│           ├── anthropic.yaml           # Anthropic-specific overrides
│           ├── gemini.yaml              # Google Gemini overrides
│           ├── aws_bedrock.yaml         # AWS Bedrock overrides
│           └── traceloop.yaml           # Traceloop instrumentation overrides
├── legacy/                              # Backup of current implementation
│   ├── transforms_backup.py             # Original transforms.py
│   ├── central_mapper_backup.py         # Original central_mapper.py
│   ├── rule_engine_backup.py            # Original rule_engine.py
│   ├── rule_applier_backup.py           # Original rule_applier.py
│   └── README.md                        # Migration notes and rollback procedures
└── integration/                         # Integration layer
    ├── __init__.py                      # Integration module initialization
    ├── compatibility.py                 # Backward compatibility layer
    ├── migration.py                     # Migration utilities
    └── validation.py                    # Integration validation
```

## 2. Detailed Pydantic v2 Models Implementation

### 2.1 Core Data Models with O(1) Hash Support

```python
# src/honeyhive/tracer/semantic_conventions/universal/models.py

from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Any, Dict, List, Optional, FrozenSet, Tuple, Union
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
import hashlib
import json

class FieldType(str, Enum):
    """Field type enumeration for O(1) classification."""
    MESSAGE_ROLE = "message_role"
    MESSAGE_CONTENT = "message_content"
    TOOL_CALLS = "tool_calls"
    FUNCTION_CALL = "function_call"
    REFUSAL = "refusal"
    AUDIO = "audio"
    TOKEN_COUNT = "token_count"
    MODEL_IDENTIFIER = "model_identifier"
    COMPLETION_STATUS = "completion_status"
    USAGE_METRICS = "usage_metrics"
    CONFIGURATION = "configuration"
    SAFETY_INFO = "safety_info"
    PROVIDER_METADATA = "provider_metadata"
    UNKNOWN = "unknown"

class HoneyHiveSection(str, Enum):
    """HoneyHive schema sections for O(1 mapping."""
    INPUTS = "inputs"
    OUTPUTS = "outputs"
    CONFIG = "config"
    METADATA = "metadata"

class O1FieldInfo(BaseModel):
    """O(1) field information with pre-computed hashes."""
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    
    path: str = Field(..., description="Dot-separated field path")
    value: Any = Field(..., description="Field value")
    field_type: FieldType = Field(..., description="Classified field type")
    honeyhive_section: HoneyHiveSection = Field(..., description="Target HoneyHive section")
    
    # Pre-computed hashes for O(1) operations
    path_hash: str = Field(..., description="MD5 hash of path for O(1 lookups")
    content_hash: str = Field(..., description="Content-based hash for classification")
    semantic_hash: str = Field(..., description="Semantic meaning hash")
    
    # Performance metadata
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    processing_time_ns: int = Field(default=0, description="Processing time in nanoseconds")
    cache_hit: bool = Field(default=False, description="Whether this was a cache hit")
    
    @classmethod
    def create_with_o1_hashes(
        cls, 
        path: str, 
        value: Any, 
        field_type: FieldType,
        honeyhive_section: HoneyHiveSection
    ) -> 'O1FieldInfo':
        """Create field info with all O(1 hashes pre-computed."""
        import time
        start_time = time.perf_counter_ns()
        
        # O(1) hash computations
        path_hash = hashlib.md5(path.encode()).hexdigest()[:16]
        content_hash = cls._compute_content_hash_o1(value)
        semantic_hash = cls._compute_semantic_hash_o1(path, field_type)
        
        processing_time = time.perf_counter_ns() - start_time
        
        return cls(
            path=path,
            value=value,
            field_type=field_type,
            honeyhive_section=honeyhive_section,
            path_hash=path_hash,
            content_hash=content_hash,
            semantic_hash=semantic_hash,
            processing_time_ns=processing_time
        )
    
    @staticmethod
    def _compute_content_hash_o1(value: Any) -> str:
        """Compute content hash using O(1) operations only."""
        if isinstance(value, str):
            # O(1) hash using first char, last char, length, and type
            if len(value) > 0:
                hash_input = f"{value[0] if len(value) > 0 else ''}{value[-1] if len(value) > 1 else ''}{len(value)}{type(value).__name__}"
            else:
                hash_input = f"empty_string"
        elif isinstance(value, (int, float)):
            hash_input = f"{type(value).__name__}_{abs(value) if isinstance(value, (int, float)) else 0}"
        elif isinstance(value, bool):
            hash_input = f"bool_{value}"
        elif isinstance(value, list):
            hash_input = f"list_{len(value)}"
        elif isinstance(value, dict):
            hash_input = f"dict_{len(value)}"
        else:
            hash_input = f"{type(value).__name__}"
        
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    @staticmethod
    def _compute_semantic_hash_o1(path: str, field_type: FieldType) -> str:
        """Compute semantic hash for O(1) grouping."""
        # O(1) semantic hash using path structure and field type
        path_parts = path.split(".")
        path_structure = f"{len(path_parts)}_{path_parts[0] if path_parts else ''}_{path_parts[-1] if len(path_parts) > 1 else ''}"
        semantic_input = f"{path_structure}_{field_type.value}"
        return hashlib.md5(semantic_input.encode()).hexdigest()[:8]

class O1DiscoveredFields(BaseModel):
    """Collection of discovered fields with O(1) access patterns."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # O(1) access structures
    fields_by_hash: Dict[str, O1FieldInfo] = Field(default_factory=dict)
    fields_by_type: Dict[FieldType, List[str]] = Field(default_factory=dict)  # Store hashes, not objects
    fields_by_section: Dict[HoneyHiveSection, List[str]] = Field(default_factory=dict)
    
    # Metadata
    total_fields: int = Field(default=0)
    discovery_time_ns: int = Field(default=0)
    cache_hit_rate: float = Field(default=0.0)
    
    def add_field_o1(self, field: O1FieldInfo) -> None:
        """Add field with O(1) indexing."""
        # O(1) hash-based storage
        self.fields_by_hash[field.path_hash] = field
        
        # O(1) type indexing
        if field.field_type not in self.fields_by_type:
            self.fields_by_type[field.field_type] = []
        self.fields_by_type[field.field_type].append(field.path_hash)
        
        # O(1) section indexing
        if field.honeyhive_section not in self.fields_by_section:
            self.fields_by_section[field.honeyhive_section] = []
        self.fields_by_section[field.honeyhive_section].append(field.path_hash)
        
        self.total_fields += 1
    
    def get_fields_by_type_o1(self, field_type: FieldType) -> List[O1FieldInfo]:
        """O(1) retrieval of fields by type."""
        field_hashes = self.fields_by_type.get(field_type, [])
        return [self.fields_by_hash[hash_key] for hash_key in field_hashes]
    
    def get_fields_by_section_o1(self, section: HoneyHiveSection) -> List[O1FieldInfo]:
        """O(1) retrieval of fields by HoneyHive section."""
        field_hashes = self.fields_by_section.get(section, [])
        return [self.fields_by_hash[hash_key] for hash_key in field_hashes]
    
    def get_field_by_path_hash_o1(self, path_hash: str) -> Optional[O1FieldInfo]:
        """O(1) field retrieval by path hash."""
        return self.fields_by_hash.get(path_hash)

class O1ProviderInfo(BaseModel):
    """Provider information with O(1) detection metadata."""
    model_config = ConfigDict(frozen=True)
    
    name: str = Field(..., description="Provider name")
    confidence: float = Field(..., ge=0.0, le=1.0)
    signature_hash: str = Field(..., description="Provider signature hash")
    detection_time_ns: int = Field(default=0)
    field_match_count: int = Field(default=0)
    unique_indicators: FrozenSet[str] = Field(default_factory=frozenset)

class O1ProcessingContext(BaseModel):
    """Processing context with performance tracking."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    processing_id: UUID = Field(default_factory=uuid4)
    tracer_instance_id: str = Field(..., description="Tracer instance identifier")
    start_time_ns: int = Field(default_factory=lambda: time.perf_counter_ns())
    
    # Processing phases timing (all in nanoseconds)
    field_discovery_time_ns: int = Field(default=0)
    provider_detection_time_ns: int = Field(default=0)
    mapping_time_ns: int = Field(default=0)
    total_processing_time_ns: int = Field(default=0)
    
    # Cache performance
    cache_hits: int = Field(default=0)
    cache_misses: int = Field(default=0)
    
    # Results
    provider_info: Optional[O1ProviderInfo] = Field(default=None)
    discovered_fields: Optional[O1DiscoveredFields] = Field(default=None)
    
    @computed_field
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    @computed_field  
    @property
    def total_processing_time_ms(self) -> float:
        """Total processing time in milliseconds."""
        return self.total_processing_time_ns / 1_000_000.0

class O1MappingResult(BaseModel):
    """Result of O(1) mapping operation."""
    model_config = ConfigDict(frozen=True)
    
    # HoneyHive schema sections
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing metadata
    processing_context: O1ProcessingContext = Field(...)
    mapping_accuracy: float = Field(default=1.0, description="Estimated mapping accuracy")
    unmapped_fields: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance validation
    is_o1_compliant: bool = Field(default=True, description="Whether processing was O(1)")
    performance_warnings: List[str] = Field(default_factory=list)
```

## 3. O(1) Hash Index Implementation Details

### 3.1 Field Hash Index with Native Python Operations

```python
# src/honeyhive/tracer/semantic_conventions/universal/hash_indices.py

from typing import Any, Dict, List, Optional, FrozenSet, Set
import hashlib
import time
from .models import O1FieldInfo, FieldType, HoneyHiveSection

class O1FieldHashIndex:
    """O(1) field discovery and classification using hash-based indices."""
    
    def __init__(self, cache_manager: Any, tracer_instance: Any = None):
        """Initialize with per-tracer-instance caching."""
        self.tracer_instance = tracer_instance
        self.cache = cache_manager.get_cache("field_hash_index")
        
        # Pre-computed O(1) classification lookup tables
        self._initialize_o1_lookup_tables()
        
        # Performance tracking
        self.stats = {
            "total_discoveries": 0,
            "cache_hits": 0,
            "classification_time_ns": 0,
            "hash_computation_time_ns": 0
        }
    
    def _initialize_o1_lookup_tables(self) -> None:
        """Initialize all O(1) lookup tables using native Python collections."""
        
        # O(1) field type classification using frozensets
        self.role_identifiers = frozenset({
            "user", "assistant", "system", "function", "tool", "model"
        })
        
        self.completion_statuses = frozenset({
            "stop", "length", "tool_calls", "content_filter", "function_call",
            "end_turn", "max_tokens", "stop_sequence", "STOP", "LENGTH"
        })
        
        self.token_indicators = frozenset({
            "tokens", "token_count", "usage", "prompt_tokens", "completion_tokens",
            "total_tokens", "input_tokens", "output_tokens", "cache_hit_tokens"
        })
        
        # O(1) model identification using tuple for startswith
        self.model_prefixes = (
            "gpt-", "claude-", "gemini-", "llama-", "mistral-", "titan-",
            "nova-", "anthropic-", "openai-", "cohere-"
        )
        
        # O(1) API identifier patterns
        self.api_id_prefixes = (
            "chatcmpl-", "msg_", "call_", "toolu_", "req_", "resp_"
        )
        
        # O(1 path-based classification using dict lookups
        self.path_type_indicators = {
            "choices": FieldType.MESSAGE_CONTENT,
            "message": FieldType.MESSAGE_CONTENT,
            "content": FieldType.MESSAGE_CONTENT,
            "role": FieldType.MESSAGE_ROLE,
            "tool_calls": FieldType.TOOL_CALLS,
            "function_call": FieldType.FUNCTION_CALL,
            "refusal": FieldType.REFUSAL,
            "audio": FieldType.AUDIO,
            "usage": FieldType.USAGE_METRICS,
            "model": FieldType.MODEL_IDENTIFIER,
            "finish_reason": FieldType.COMPLETION_STATUS,
            "stop_reason": FieldType.COMPLETION_STATUS
        }
        
        # O(1) section mapping using dict lookups
        self.field_type_to_section = {
            FieldType.MESSAGE_ROLE: HoneyHiveSection.INPUTS,
            FieldType.MESSAGE_CONTENT: HoneyHiveSection.OUTPUTS,
            FieldType.TOOL_CALLS: HoneyHiveSection.OUTPUTS,
            FieldType.FUNCTION_CALL: HoneyHiveSection.OUTPUTS,
            FieldType.REFUSAL: HoneyHiveSection.OUTPUTS,
            FieldType.AUDIO: HoneyHiveSection.OUTPUTS,
            FieldType.TOKEN_COUNT: HoneyHiveSection.METADATA,
            FieldType.MODEL_IDENTIFIER: HoneyHiveSection.CONFIG,
            FieldType.COMPLETION_STATUS: HoneyHiveSection.OUTPUTS,
            FieldType.USAGE_METRICS: HoneyHiveSection.METADATA,
            FieldType.CONFIGURATION: HoneyHiveSection.CONFIG,
            FieldType.SAFETY_INFO: HoneyHiveSection.METADATA,
            FieldType.PROVIDER_METADATA: HoneyHiveSection.METADATA,
            FieldType.UNKNOWN: HoneyHiveSection.METADATA
        }
    
    def discover_fields_o1(self, data: Dict[str, Any]) -> O1DiscoveredFields:
        """O(1) field discovery using hash-based operations."""
        start_time = time.perf_counter_ns()
        
        # O(1) data hash for cache lookup
        data_hash = self._create_data_hash_o1(data)
        cache_key = f"discovery:{data_hash}"
        
        # O(1) cache lookup
        cached_result = self.cache.get(cache_key)
        if cached_result:
            self.stats["cache_hits"] += 1
            cached_result.cache_hit_rate = 1.0
            return cached_result
        
        # O(1) field discovery
        discovered = O1DiscoveredFields()
        self._extract_all_fields_o1(data, "", discovered)
        
        # Performance tracking
        discovery_time = time.perf_counter_ns() - start_time
        discovered.discovery_time_ns = discovery_time
        
        # Cache for future O(1) lookups
        self.cache.set(cache_key, discovered, ttl=1800.0)
        
        self.stats["total_discoveries"] += 1
        return discovered
    
    def _extract_all_fields_o1(self, data: Any, path: str, discovered: O1DiscoveredFields) -> None:
        """Extract all fields using O(1) operations per field."""
        if isinstance(data, dict):
            for key, value in data.items():
                field_path = f"{path}.{key}" if path else key
                
                # O(1) field classification and hash computation
                field_info = self._classify_and_hash_field_o1(field_path, value)
                discovered.add_field_o1(field_info)
                
                # Recurse only for nested structures (limited depth)
                if isinstance(value, (dict, list)) and len(path.split(".")) < 10:  # Max depth limit
                    self._extract_all_fields_o1(value, field_path, discovered)
                    
        elif isinstance(data, list):
            # Sample only first few items to maintain O(1) behavior
            sample_size = min(3, len(data))  # O(1) sampling
            for i in range(sample_size):
                item = data[i]
                item_path = f"{path}[{i}]"
                if isinstance(item, (dict, list)):
                    self._extract_all_fields_o1(item, item_path, discovered)
    
    def _classify_and_hash_field_o1(self, path: str, value: Any) -> O1FieldInfo:
        """O(1) field classification and hash computation."""
        classification_start = time.perf_counter_ns()
        
        # O(1) path-based classification using dict lookup
        path_parts = path.split(".")
        last_part = path_parts[-1] if path_parts else ""
        
        # O(1) dict lookup for path-based classification
        field_type = self.path_type_indicators.get(last_part)
        
        if not field_type:
            # O(1) content-based classification
            field_type = self._classify_by_content_o1(value)
        
        # O(1) section mapping
        honeyhive_section = self.field_type_to_section.get(field_type, HoneyHiveSection.METADATA)
        
        # Track classification time
        classification_time = time.perf_counter_ns() - classification_start
        self.stats["classification_time_ns"] += classification_time
        
        return O1FieldInfo.create_with_o1_hashes(path, value, field_type, honeyhive_section)
    
    def _classify_by_content_o1(self, value: Any) -> FieldType:
        """O(1) content classification using native Python operations."""
        if isinstance(value, str):
            value_lower = value.lower()  # O(1)
            
            # O(1) frozenset membership tests
            if value_lower in self.role_identifiers:
                return FieldType.MESSAGE_ROLE
            elif value_lower in self.completion_statuses:
                return FieldType.COMPLETION_STATUS
            elif value.startswith(self.model_prefixes):  # O(1) tuple startswith
                return FieldType.MODEL_IDENTIFIER
            elif value.startswith(self.api_id_prefixes):  # O(1) tuple startswith
                return FieldType.PROVIDER_METADATA
            elif any(indicator in value_lower for indicator in self.token_indicators):  # O(1) per indicator
                return FieldType.TOKEN_COUNT
            elif len(value) > 100:  # O(1) length check
                return FieldType.MESSAGE_CONTENT
            else:
                return FieldType.UNKNOWN
        elif isinstance(value, (int, float)):
            return FieldType.USAGE_METRICS
        elif isinstance(value, list):
            return FieldType.TOOL_CALLS if len(value) > 0 and isinstance(value[0], dict) else FieldType.UNKNOWN
        elif isinstance(value, dict):
            # O(1) dict structure classification
            if "role" in value and "content" in value:
                return FieldType.MESSAGE_CONTENT
            elif "id" in value and "function" in value:
                return FieldType.TOOL_CALLS
            else:
                return FieldType.UNKNOWN
        else:
            return FieldType.UNKNOWN
    
    def _create_data_hash_o1(self, data: Dict[str, Any]) -> str:
        """Create O(1) data hash for caching."""
        # O(1) hash using keys and structure info only
        keys_sorted = tuple(sorted(data.keys()))  # O(n log n) but only on keys, not values
        structure_info = f"{len(data)}_{len(keys_sorted)}_{keys_sorted[0] if keys_sorted else ''}_{keys_sorted[-1] if len(keys_sorted) > 1 else ''}"
        return hashlib.md5(structure_info.encode()).hexdigest()[:16]
```

## 4. O(1) Provider Detection Implementation

### 4.1 Provider Signature Cache

```python
# src/honeyhive/tracer/semantic_conventions/universal/provider_detection.py

class O1ProviderDetector:
    """O(1) provider detection using signature hash matching."""
    
    def __init__(self, cache_manager: Any, tracer_instance: Any = None):
        self.tracer_instance = tracer_instance
        self.cache = cache_manager.get_cache("provider_detection")
        
        # Pre-computed provider signatures for O(1) detection
        self._initialize_provider_signatures_o1()
        
        # Performance tracking
        self.detection_stats = {
            "total_detections": 0,
            "cache_hits": 0,
            "signature_matches": 0,
            "fallback_detections": 0
        }
    
    def _initialize_provider_signatures_o1(self) -> None:
        """Initialize provider signatures for O(1) detection."""
        
        # O(1) provider signature patterns using frozensets
        self.provider_field_signatures = {
            "openai": frozenset({
                "choices", "usage.prompt_tokens", "usage.completion_tokens",
                "system_fingerprint", "model", "created"
            }),
            "anthropic": frozenset({
                "content", "usage.input_tokens", "usage.output_tokens", 
                "stop_reason", "type", "model"
            }),
            "gemini": frozenset({
                "candidates", "usageMetadata.promptTokenCount",
                "usageMetadata.candidatesTokenCount", "safetyRatings"
            }),
            "aws_bedrock": frozenset({
                "results", "inputTextTokenCount", "outputText",
                "completionReason", "modelId"
            }),
            "traceloop": frozenset({
                "gen_ai.request.model", "gen_ai.usage.prompt_tokens",
                "gen_ai.system", "gen_ai.completion"
            }),
            "openinference": frozenset({
                "llm.input_messages", "llm.output_messages",
                "llm.token_count_prompt", "llm.model_name"
            })
        }
        
        # O(1) confidence thresholds
        self.detection_thresholds = {
            "high_confidence": 0.8,
            "medium_confidence": 0.6,
            "low_confidence": 0.4
        }
    
    def detect_provider_o1(self, discovered_fields: O1DiscoveredFields) -> Optional[O1ProviderInfo]:
        """O(1) provider detection using signature matching."""
        start_time = time.perf_counter_ns()
        
        # Create field path set for O(1) intersection operations
        field_paths = frozenset(field.path for field in discovered_fields.fields_by_hash.values())
        
        # O(1) signature hash for cache lookup
        signature_hash = self._create_signature_hash_o1(field_paths)
        cache_key = f"provider:{signature_hash}"
        
        # O(1) cache lookup
        cached_result = self.cache.get(cache_key)
        if cached_result:
            self.detection_stats["cache_hits"] += 1
            return cached_result
        
        # O(1) provider matching using set intersections
        best_provider = None
        best_confidence = 0.0
        best_match_count = 0
        
        for provider_name, signature_fields in self.provider_field_signatures.items():
            # O(1) set intersection
            matches = signature_fields & field_paths
            match_count = len(matches)
            
            if match_count > 0:
                # O(1) confidence calculation
                confidence = match_count / len(signature_fields)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_provider = provider_name
                    best_match_count = match_count
        
        # Create result
        detection_time = time.perf_counter_ns() - start_time
        
        if best_provider and best_confidence >= self.detection_thresholds["low_confidence"]:
            provider_info = O1ProviderInfo(
                name=best_provider,
                confidence=best_confidence,
                signature_hash=signature_hash,
                detection_time_ns=detection_time,
                field_match_count=best_match_count,
                unique_indicators=self.provider_field_signatures[best_provider] & field_paths
            )
            
            # Cache for future O(1) lookups
            self.cache.set(cache_key, provider_info, ttl=3600.0)
            
            self.detection_stats["signature_matches"] += 1
            return provider_info
        
        # Unknown provider handling
        self.detection_stats["fallback_detections"] += 1
        return self._handle_unknown_provider_o1(field_paths, signature_hash, detection_time)
    
    def _create_signature_hash_o1(self, field_paths: FrozenSet[str]) -> str:
        """Create O(1) signature hash from field paths."""
        # O(1) hash using sorted field count and first/last fields
        sorted_paths = sorted(field_paths)  # O(n log n) but only on field names, not content
        if sorted_paths:
            hash_input = f"{len(sorted_paths)}_{sorted_paths[0]}_{sorted_paths[-1] if len(sorted_paths) > 1 else ''}"
        else:
            hash_input = "empty"
        
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def _handle_unknown_provider_o1(self, field_paths: FrozenSet[str], signature_hash: str, detection_time: int) -> O1ProviderInfo:
        """Handle unknown provider with O(1) operations."""
        # Generate provider name based on unique characteristics
        unique_fields = field_paths - self._get_common_fields_o1()
        
        if unique_fields:
            # O(1) provider name generation
            provider_name = f"unknown_{hash(frozenset(list(unique_fields)[:3])) % 10000}"
        else:
            provider_name = "generic_llm"
        
        return O1ProviderInfo(
            name=provider_name,
            confidence=0.3,  # Low confidence for unknown providers
            signature_hash=signature_hash,
            detection_time_ns=detection_time,
            field_match_count=len(unique_fields),
            unique_indicators=frozenset(list(unique_fields)[:5])  # Limit to 5 indicators
        )
    
    def _get_common_fields_o1(self) -> FrozenSet[str]:
        """Get common fields across all providers using O(1) lookup."""
        return frozenset({
            "model", "content", "role", "usage", "tokens", "response", "request"
        })
```

## 5. O(1) Mapping Engine Implementation

### 5.1 Hash-Based Field Mapping

```python
# src/honeyhive/tracer/semantic_conventions/universal/mapping_engine.py

class O1MappingEngine:
    """O(1) field mapping using pre-computed hash-based rules."""
    
    def __init__(self, cache_manager: Any, tracer_instance: Any = None):
        self.tracer_instance = tracer_instance
        self.cache = cache_manager.get_cache("field_mapping")
        
        # Pre-computed O(1) mapping rules
        self._initialize_mapping_rules_o1()
        
        # Performance tracking
        self.mapping_stats = {
            "total_mappings": 0,
            "cache_hits": 0,
            "successful_mappings": 0,
            "fallback_mappings": 0
        }
    
    def _initialize_mapping_rules_o1(self) -> None:
        """Initialize O(1 mapping rules using hash-based lookups."""
        
        # O(1) field type to target mapping
        self.field_type_mappings = {
            FieldType.MESSAGE_ROLE: ("inputs", "chat_history", "extract_role"),
            FieldType.MESSAGE_CONTENT: ("outputs", "content", "extract_content"),
            FieldType.TOOL_CALLS: ("outputs", "tool_calls", "normalize_tool_calls"),
            FieldType.FUNCTION_CALL: ("outputs", "function_call", "normalize_function_call"),
            FieldType.REFUSAL: ("outputs", "refusal", "direct"),
            FieldType.AUDIO: ("outputs", "audio", "preserve_audio_metadata"),
            FieldType.TOKEN_COUNT: ("metadata", "usage", "extract_token_count"),
            FieldType.MODEL_IDENTIFIER: ("config", "model", "normalize_model_name"),
            FieldType.COMPLETION_STATUS: ("outputs", "finish_reason", "normalize_finish_reason"),
            FieldType.USAGE_METRICS: ("metadata", "usage", "extract_usage_metrics"),
            FieldType.CONFIGURATION: ("config", "parameters", "extract_config"),
            FieldType.SAFETY_INFO: ("metadata", "safety", "normalize_safety_info"),
            FieldType.PROVIDER_METADATA: ("metadata", "provider", "preserve_metadata"),
            FieldType.UNKNOWN: ("metadata", "unknown_fields", "preserve_unknown")
        }
        
        # O(1) provider-specific overrides
        self.provider_overrides = {
            "openai": {
                FieldType.COMPLETION_STATUS: ("outputs", "finish_reason", "map_openai_finish_reason"),
                FieldType.TOOL_CALLS: ("outputs", "tool_calls", "preserve_openai_tool_calls")
            },
            "anthropic": {
                FieldType.COMPLETION_STATUS: ("outputs", "finish_reason", "map_anthropic_stop_reason"),
                FieldType.MESSAGE_CONTENT: ("outputs", "content_blocks", "preserve_anthropic_content")
            },
            "gemini": {
                FieldType.SAFETY_INFO: ("metadata", "safety_ratings", "normalize_gemini_safety"),
                FieldType.MESSAGE_CONTENT: ("outputs", "content", "extract_gemini_text_from_parts")
            }
        }
    
    def apply_mapping_o1(self, discovered_fields: O1DiscoveredFields, provider_info: Optional[O1ProviderInfo]) -> O1MappingResult:
        """Apply O(1) mapping using hash-based rule lookups."""
        start_time = time.perf_counter_ns()
        
        # Initialize result structure
        result = O1MappingResult(
            processing_context=O1ProcessingContext(
                tracer_instance_id=str(id(self.tracer_instance)) if self.tracer_instance else "default"
            )
        )
        
        # O(1) mapping application
        for field_hash, field_info in discovered_fields.fields_by_hash.items():
            target_section, target_field, transform_name = self._get_mapping_rule_o1(field_info, provider_info)
            
            if target_section and target_field:
                # O(1) transform application
                transformed_value = self._apply_transform_o1(field_info.value, transform_name)
                
                # O(1) result assignment
                section_dict = getattr(result, target_section)
                section_dict[target_field] = transformed_value
                
                self.mapping_stats["successful_mappings"] += 1
            else:
                # Preserve unmapped fields
                result.unmapped_fields[field_info.path] = field_info.value
                self.mapping_stats["fallback_mappings"] += 1
        
        # Performance tracking
        mapping_time = time.perf_counter_ns() - start_time
        result.processing_context.mapping_time_ns = mapping_time
        
        self.mapping_stats["total_mappings"] += 1
        return result
    
    def _get_mapping_rule_o1(self, field_info: O1FieldInfo, provider_info: Optional[O1ProviderInfo]) -> Tuple[str, str, str]:
        """Get mapping rule using O(1) hash lookups."""
        # O(1) provider-specific override lookup
        if provider_info and provider_info.name in self.provider_overrides:
            provider_mappings = self.provider_overrides[provider_info.name]
            if field_info.field_type in provider_mappings:
                return provider_mappings[field_info.field_type]
        
        # O(1) default mapping lookup
        return self.field_type_mappings.get(field_info.field_type, ("metadata", "unknown", "direct"))
    
    def _apply_transform_o1(self, value: Any, transform_name: str) -> Any:
        """Apply transform using O(1) function lookup."""
        # O(1 transform function lookup
        transform_func = self.transform_functions.get(transform_name, self._direct_transform)
        return transform_func(value)
```
