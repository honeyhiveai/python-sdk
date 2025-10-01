# RC3 Comprehensive Implementation Plan
## Complete Semantic Convention Architecture with Full Context

## 🎯 Executive Summary

Based on comprehensive analysis of:
- **Main Branch Tracer**: Traceloop-based with honeyhive_* attributes
- **Refactored Tracer**: Native OpenTelemetry with preserved API compatibility
- **BYOI Architecture**: Multi-instance, multi-instrumentor support
- **Caching Infrastructure**: Enterprise-grade performance optimization
- **Deep Research Prod Events**: Target schema validation

**RC3 Goal**: Add semantic convention support as **additive enhancement** to the existing, production-ready refactored tracer while maintaining 100% API compatibility, leveraging existing performance infrastructure, and **preserving critical backend compatibility mappings**.

## 🚨 **CRITICAL Backend Compatibility Requirement**

**MANDATORY**: The current span processor sets dual attributes for backend compatibility:
- `honeyhive.session_id` + `traceloop.association.properties.session_id`
- `honeyhive.project` + `traceloop.association.properties.project`  
- `honeyhive.source` + `traceloop.association.properties.source`
- `honeyhive.parent_id` (single mapping)

**This dual mapping MUST be preserved in RC3** - the backend system currently depends on both attribute formats for proper operation.

## 📋 Context-Driven Architecture Decisions

### **1. Migration Reality: 90% Complete**
- ✅ **Infrastructure Migration**: Traceloop → Native OpenTelemetry (DONE)
- ✅ **API Compatibility**: Exact same @trace and enrich_span API (PRESERVED)
- ✅ **HoneyHive Attributes**: Full honeyhive_* support (WORKING)
- ✅ **Multi-Instance Support**: BYOI architecture (READY)
- ✅ **Performance Infrastructure**: Thread-safe caching (PRODUCTION-READY)

### **2. Semantic Convention Support is Purely Additive**
```python
# EXISTING (works perfectly): Main branch patterns
@trace(event_type="model", config={"model": "gpt-4"})
def my_function():
    enrich_span(metadata={"custom": "data"})

# NEW (adding): Semantic convention auto-processing
# OpenAI instrumentor creates llm.* → automatically converted to HoneyHive schema
response = openai_client.chat.completions.create(...)
```

### **3. Integration Point: Span Processor Enhancement**
Perfect integration point identified: `_convert_span_to_event()` method in `HoneyHiveSpanProcessor`

## 🎯 **Prerequisites for New Session**

### **Essential File References:**
- `event_analysis/first_event_complete.json` - Target HoneyHive schema format
- `src/honeyhive/tracer/processing/span_processor.py` - Current span processor (874 lines)
- `src/honeyhive/utils/cache.py` - CacheManager implementation
- `src/honeyhive/tracer/core/base.py` - Tracer base classes

### **Required Analysis Steps:**
1. **Load Target Schema**: Review Deep Research Prod event format
2. **Examine Current Implementation**: Understand existing span processor structure  
3. **Review Caching Infrastructure**: Understand CacheManager usage patterns
4. **Test Data Preparation**: Create sample spans for each semantic convention

### **Complete Import Statements:**
```python
# All required imports for implementation
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

from opentelemetry import baggage
from opentelemetry.trace import ReadableSpan
from opentelemetry.sdk.trace import SpanData as OTelSpanData

# Project imports (adjust paths as needed)
from honeyhive.utils.cache import CacheManager
from honeyhive.tracer.core.base import BaseTracer
```

### **Sample Test Data for Implementation:**
```python
# Sample span data for testing each extractor
SAMPLE_HONEYHIVE_NATIVE_SPAN = {
    "attributes": {
        "honeyhive_event_type": "model",
        "honeyhive_config": {"model": "gpt-4", "temperature": 0.7},
        "honeyhive_inputs._params_.prompt": "Hello world",
        "honeyhive_outputs.result": "Hi there!",
        "honeyhive_metadata": {"custom": "data"}
    }
}

SAMPLE_OPENINFERENCE_SPAN = {
    "attributes": {
        "llm.model_name": "gpt-4",
        "llm.temperature": 0.7,
        "llm.input_messages": '[{"role": "user", "content": "Hello world"}]',
        "llm.output_messages": '[{"role": "assistant", "content": "Hi there!"}]',
        "llm.token_count.prompt": 10,
        "llm.token_count.completion": 5
    }
}

SAMPLE_TRACELOOP_SPAN = {
    "attributes": {
        "gen_ai.request.model": "gpt-4",
        "gen_ai.request.temperature": 0.7,
        "gen_ai.request.messages.0.role": "user",
        "gen_ai.request.messages.0.content": "Hello world",
        "gen_ai.response.text": "Hi there!",
        "gen_ai.usage.prompt_tokens": 10,
        "gen_ai.usage.completion_tokens": 5
    }
}

SAMPLE_OPENLIT_SPAN = {
    "attributes": {
        "gen_ai.request.model": "gpt-4",
        "gen_ai.usage.input_tokens": 10,
        "gen_ai.usage.output_tokens": 5,
        "gen_ai.response.text": "Hi there!"
    }
}
```

## 🏗️ Detailed Implementation Plan

### **PHASE 1: Core Semantic Convention Architecture (TODOs 1-10)**

#### **TODO 1: Create Semantic Conventions Module Structure**
```
src/honeyhive/tracer/semantic_conventions/
├── __init__.py                 # Public API exports
├── registry.py                 # Convention detection
├── mapper.py                   # Main conversion orchestrator
├── extractors/
│   ├── __init__.py
│   ├── base.py                # Abstract base class
│   ├── honeyhive_native.py    # HIGHEST PRIORITY - existing patterns
│   ├── openinference.py       # llm.* attributes
│   ├── traceloop.py           # gen_ai.* attributes (migration)
│   └── openlit.py             # gen_ai.usage.input_tokens patterns
└── utils/
    ├── __init__.py
    ├── message_parsing.py     # Chat message extraction
    └── performance.py         # Caching integration
```

**Module __init__.py files:**
```python
# src/honeyhive/tracer/semantic_conventions/__init__.py
from .mapper import SemanticConventionMapper
from .registry import SemanticConventionRegistry
from .extractors.base import BaseExtractor, SpanData
from .extractors.honeyhive_native import HoneyHiveNativeExtractor
from .extractors.openinference import OpenInferenceExtractor
from .extractors.traceloop import TraceloopExtractor
from .extractors.openlit import OpenLitExtractor

__all__ = [
    "SemanticConventionMapper",
    "SemanticConventionRegistry", 
    "BaseExtractor",
    "SpanData",
    "HoneyHiveNativeExtractor",
    "OpenInferenceExtractor",
    "TraceloopExtractor",
    "OpenLitExtractor"
]

# src/honeyhive/tracer/semantic_conventions/extractors/__init__.py
from .base import BaseExtractor, SpanData
from .honeyhive_native import HoneyHiveNativeExtractor
from .openinference import OpenInferenceExtractor
from .traceloop import TraceloopExtractor
from .openlit import OpenLitExtractor

__all__ = [
    "BaseExtractor", 
    "SpanData",
    "HoneyHiveNativeExtractor",
    "OpenInferenceExtractor", 
    "TraceloopExtractor",
    "OpenLitExtractor"
]

# src/honeyhive/tracer/semantic_conventions/utils/__init__.py
from .message_parsing import MessageParser
from .performance import configure_semantic_convention_caching

__all__ = ["MessageParser", "configure_semantic_convention_caching"]
```

#### **TODO 2: Implement BaseExtractor with Caching Integration**
```python
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from opentelemetry.trace import ReadableSpan
from ...utils.cache import CacheManager

@dataclass
class SpanData:
    """Span data structure for semantic convention processing."""
    attributes: Dict[str, Any]
    name: str
    start_time: float
    end_time: Optional[float] = None
    
    @classmethod
    def from_readable_span(cls, span: ReadableSpan) -> 'SpanData':
        """Convert ReadableSpan to SpanData."""
        return cls(
            attributes=dict(span.attributes or {}),
            name=span.name,
            start_time=span.start_time,
            end_time=span.end_time
        )

class BaseExtractor(ABC):
    """Base class for semantic convention extractors with caching support."""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager
    
    def extract_to_honeyhive_schema(self, span_data: SpanData) -> dict:
        """Extract span data to HoneyHive schema with caching."""
        
        if self.cache_manager:
            # Cache based on attribute signature for performance
            cache_key = self._generate_extraction_key(span_data.attributes)
            return self.cache_manager.get_cached_attributes(
                attr_key=cache_key,
                normalizer_func=lambda: self._perform_extraction(span_data)
            )
        
        return self._perform_extraction(span_data)
    
    def _perform_extraction(self, span_data: SpanData) -> dict:
        """Perform actual extraction logic."""
        honeyhive_event = self._initialize_honeyhive_event(span_data)
        
        honeyhive_event["config"] = self.extract_config(span_data.attributes)
        honeyhive_event["inputs"] = self.extract_inputs(span_data.attributes)
        honeyhive_event["outputs"] = self.extract_outputs(span_data.attributes)
        honeyhive_event["metadata"] = self.extract_metadata(span_data.attributes)
        
        return honeyhive_event
    
    def _initialize_honeyhive_event(self, span_data: SpanData) -> dict:
        """Initialize base HoneyHive event structure."""
        return {
            "event_name": span_data.name,
            "event_type": "tool",  # Default, will be overridden by extractors
            "start_time": span_data.start_time,
            "end_time": span_data.end_time,
            "config": {},
            "inputs": {},
            "outputs": {},
            "metadata": {}
        }
    
    def _generate_extraction_key(self, attributes: dict) -> str:
        """Generate cache key for extraction results."""
        # Create deterministic key from attribute signature
        sorted_keys = sorted(attributes.keys())
        key_signature = "|".join(sorted_keys)
        return hashlib.md5(key_signature.encode()).hexdigest()
    
    @abstractmethod
    def extract_config(self, attributes: dict) -> dict: ...
    
    @abstractmethod  
    def extract_inputs(self, attributes: dict) -> dict: ...
    
    @abstractmethod
    def extract_outputs(self, attributes: dict) -> dict: ...
    
    @abstractmethod
    def extract_metadata(self, attributes: dict) -> dict: ...
```

#### **TODO 3: HoneyHiveNativeExtractor (CRITICAL - Preserve Main Branch)**
```python
class HoneyHiveNativeExtractor(BaseExtractor):
    """HIGHEST PRIORITY: Preserve ALL main branch honeyhive_* patterns."""
    
    def extract_config(self, attributes: dict) -> dict:
        """Handle main branch honeyhive_config patterns exactly."""
        config = {}
        
        # Direct honeyhive_config attribute (main branch pattern)
        if "honeyhive_config" in attributes:
            config.update(attributes["honeyhive_config"])
        
        # Individual config attributes from decorators
        for key, value in attributes.items():
            if key.startswith("honeyhive_") and key.endswith(("_model", "_provider", "_temperature")):
                clean_key = key.replace("honeyhive_", "")
                config[clean_key] = value
        
        return config
    
    def extract_inputs(self, attributes: dict) -> dict:
        """Handle main branch honeyhive_inputs patterns exactly."""
        inputs = {}
        
        # Direct honeyhive_inputs attribute
        if "honeyhive_inputs" in attributes:
            inputs.update(attributes["honeyhive_inputs"])
        
        # Parameter inputs from @trace decorator (main branch pattern)
        param_inputs = {}
        for key, value in attributes.items():
            if key.startswith("honeyhive_inputs._params_."):
                param_name = key.replace("honeyhive_inputs._params_.", "")
                param_inputs[param_name] = value
        
        if param_inputs:
            inputs["parameters"] = param_inputs
        
        return inputs
    
    def extract_outputs(self, attributes: dict) -> dict:
        """Handle main branch honeyhive_outputs patterns exactly."""
        outputs = {}
        
        # Direct honeyhive_outputs attribute
        if "honeyhive_outputs" in attributes:
            outputs.update(attributes["honeyhive_outputs"])
        
        # Result output from @trace decorator (main branch pattern)
        if "honeyhive_outputs.result" in attributes:
            outputs["result"] = attributes["honeyhive_outputs.result"]
        
        return outputs
    
    def extract_metadata(self, attributes: dict) -> dict:
        """Handle honeyhive_metadata, honeyhive_metrics, honeyhive_feedback."""
        metadata = {}
        
        if "honeyhive_metadata" in attributes:
            metadata.update(attributes["honeyhive_metadata"])
        
        if "honeyhive_metrics" in attributes:
            metadata["metrics"] = attributes["honeyhive_metrics"]
            
        if "honeyhive_feedback" in attributes:
            metadata["feedback"] = attributes["honeyhive_feedback"]
        
        return metadata
```

#### **TODO 4: OpenInferenceExtractor (New Capability)**
```python
class OpenInferenceExtractor(BaseExtractor):
    """Extract OpenInference llm.* attributes to HoneyHive schema."""
    
    # Pre-compiled mappings for O(1) performance
    CONFIG_MAPPINGS = {
        "llm.model_name": "model",
        "llm.provider": "provider",
        "llm.temperature": "temperature", 
        "llm.max_tokens": "max_tokens",
        "llm.top_p": "top_p"
    }
    
    def extract_config(self, attributes: dict) -> dict:
        """Map OpenInference config to HoneyHive format."""
        config = {}
        
        # Fast O(1) lookups using pre-compiled mappings
        for otel_key, hh_key in self.CONFIG_MAPPINGS.items():
            if otel_key in attributes:
                config[hh_key] = attributes[otel_key]
        
        return config
    
    def extract_inputs(self, attributes: dict) -> dict:
        """Extract OpenInference inputs with cached message parsing."""
        inputs = {}
        
        if "llm.input_messages" in attributes:
            # Use cached message parsing for performance
            from ..utils.message_parsing import MessageParser
            parser = MessageParser(self.cache_manager)
            inputs["chat_history"] = parser.parse_openinference_messages(
                attributes["llm.input_messages"]
            )
        
        if "llm.prompts" in attributes:
            inputs["prompts"] = attributes["llm.prompts"]
        
        return inputs
    
    def extract_outputs(self, attributes: dict) -> dict:
        """Extract OpenInference outputs."""
        outputs = {}
        
        if "llm.output_messages" in attributes:
            from ..utils.message_parsing import MessageParser
            parser = MessageParser(self.cache_manager)
            outputs["messages"] = parser.parse_openinference_messages(
                attributes["llm.output_messages"]
            )
        
        return outputs
    
    def extract_metadata(self, attributes: dict) -> dict:
        """Extract OpenInference metadata including token usage."""
        metadata = {}
        
        # Token usage
        if "llm.token_count.prompt" in attributes:
            metadata["usage"] = {
                "prompt_tokens": attributes.get("llm.token_count.prompt", 0),
                "completion_tokens": attributes.get("llm.token_count.completion", 0),
                "total_tokens": attributes.get("llm.token_count.total", 0)
            }
        
        return metadata
```

#### **TODO 5: TraceloopExtractor (Migration Support)**
```python
class TraceloopExtractor(BaseExtractor):
    """Extract Traceloop gen_ai.* attributes - CRITICAL for migration."""
    
    def extract_config(self, attributes: dict) -> dict:
        """Map Traceloop gen_ai.* config to HoneyHive format."""
        config = {}
        
        if "gen_ai.request.model" in attributes:
            config["model"] = attributes["gen_ai.request.model"]
        
        if "gen_ai.system" in attributes:
            config["provider"] = attributes["gen_ai.system"]
        
        if "gen_ai.request.temperature" in attributes:
            config["temperature"] = attributes["gen_ai.request.temperature"]
        
        if "gen_ai.request.max_tokens" in attributes:
            config["max_tokens"] = attributes["gen_ai.request.max_tokens"]
        
        return config
    
    def extract_inputs(self, attributes: dict) -> dict:
        """Extract Traceloop message format with pattern matching."""
        inputs = {}
        
        # Traceloop pattern: gen_ai.request.messages.{index}.{field}
        from ..utils.message_parsing import MessageParser
        parser = MessageParser(self.cache_manager)
        messages = parser.parse_traceloop_messages(attributes)
        if messages:
            inputs["chat_history"] = messages
        
        return inputs
    
    def extract_outputs(self, attributes: dict) -> dict:
        """Extract Traceloop response format."""
        outputs = {}
        
        # Response content from gen_ai.response.* attributes
        if "gen_ai.response.text" in attributes:
            outputs["text"] = attributes["gen_ai.response.text"]
        
        if "gen_ai.response.finish_reason" in attributes:
            outputs["finish_reason"] = attributes["gen_ai.response.finish_reason"]
        
        return outputs
    
    def extract_metadata(self, attributes: dict) -> dict:
        """Extract Traceloop usage and metadata."""
        metadata = {}
        
        # Token usage (Traceloop pattern)
        if "gen_ai.usage.prompt_tokens" in attributes:
            metadata["usage"] = {
                "prompt_tokens": attributes["gen_ai.usage.prompt_tokens"],
                "completion_tokens": attributes.get("gen_ai.usage.completion_tokens", 0),
                "total_tokens": attributes.get("gen_ai.usage.total_tokens", 0)
            }
        
        return metadata
```

#### **TODO 6: OpenLitExtractor (Additional Support)**
```python
class OpenLitExtractor(BaseExtractor):
    """Extract OpenLit gen_ai.usage.input_tokens patterns."""
    
    def extract_config(self, attributes: dict) -> dict:
        """OpenLit config extraction (similar to Traceloop but different usage pattern)."""
        config = {}
        
        # OpenLit uses similar gen_ai.* patterns but different usage attributes
        if "gen_ai.request.model" in attributes:
            config["model"] = attributes["gen_ai.request.model"]
        
        return config
    
    def extract_metadata(self, attributes: dict) -> dict:
        """Extract OpenLit-specific usage patterns."""
        metadata = {}
        
        # OpenLit pattern: gen_ai.usage.input_tokens (vs Traceloop's prompt_tokens)
        if "gen_ai.usage.input_tokens" in attributes:
            metadata["usage"] = {
                "prompt_tokens": attributes["gen_ai.usage.input_tokens"],
                "completion_tokens": attributes.get("gen_ai.usage.output_tokens", 0),
                "total_tokens": (
                    attributes.get("gen_ai.usage.input_tokens", 0) + 
                    attributes.get("gen_ai.usage.output_tokens", 0)
                )
            }
        
        return metadata
```

#### **TODO 7: SemanticConventionRegistry with Caching**
```python
import hashlib
from typing import Optional
from ...utils.cache import CacheManager

class SemanticConventionRegistry:
    """Fast semantic convention detection with caching."""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager
        
        # Pre-compiled detection patterns for performance
        self.CONVENTION_PATTERNS = {
            "honeyhive_native": self._detect_honeyhive_native,
            "openinference": self._detect_openinference, 
            "traceloop": self._detect_traceloop,
            "openlit": self._detect_openlit
        }
    
    def detect_primary_convention(self, attributes: dict) -> str:
        """Fast O(1) convention detection with caching."""
        
        if self.cache_manager:
            # Cache based on attribute signature
            attr_signature = self._generate_attribute_signature(attributes)
            cache_key = f"convention_detect:{attr_signature}"
            
            return self.cache_manager.get_cached_attributes(
                attr_key=cache_key,
                normalizer_func=lambda: self._perform_detection(attributes)
            )
        
        return self._perform_detection(attributes)
    
    def _generate_attribute_signature(self, attributes: dict) -> str:
        """Generate signature for attribute pattern caching."""
        # Create signature based on key patterns, not values
        key_patterns = []
        for key in sorted(attributes.keys()):
            if key.startswith(("honeyhive_", "llm.", "gen_ai.")):
                key_patterns.append(key.split('.')[0])  # Use prefix for pattern matching
        
        signature = "|".join(sorted(set(key_patterns)))
        return hashlib.md5(signature.encode()).hexdigest()
    
    def _perform_detection(self, attributes: dict) -> str:
        """Perform actual convention detection with priority order."""
        
        # Priority 1: HoneyHive native (highest - preserve existing)
        if self._detect_honeyhive_native(attributes):
            return "honeyhive_native"
        
        # Priority 2: Traceloop (migration support)  
        if self._detect_traceloop(attributes):
            return "traceloop"
        
        # Priority 3: OpenInference (alternative choice)
        if self._detect_openinference(attributes):
            return "openinference"
        
        # Priority 4: OpenLit (additional support)
        if self._detect_openlit(attributes):
            return "openlit"
        
        return "unknown"
    
    def _detect_honeyhive_native(self, attributes: dict) -> bool:
        """Detect HoneyHive native attributes (highest priority)."""
        return any(key.startswith("honeyhive_") for key in attributes)
    
    def _detect_openinference(self, attributes: dict) -> bool:
        """Detect OpenInference llm.* attributes."""
        return any(key.startswith("llm.") for key in attributes)
    
    def _detect_traceloop(self, attributes: dict) -> bool:
        """Detect Traceloop gen_ai.* with prompt_tokens pattern."""
        return (
            any(key.startswith("gen_ai.") for key in attributes) and
            "gen_ai.usage.prompt_tokens" in attributes
        )
    
    def _detect_openlit(self, attributes: dict) -> bool:
        """Detect OpenLit gen_ai.* with input_tokens pattern."""
        return (
            any(key.startswith("gen_ai.") for key in attributes) and
            "gen_ai.usage.input_tokens" in attributes
        )
```

#### **TODO 8: SemanticConventionMapper (Main Orchestrator)**
```python
from typing import Optional
from opentelemetry import baggage

class UnknownExtractor(BaseExtractor):
    """Fallback extractor for unknown semantic conventions."""
    
    def extract_config(self, attributes: dict) -> dict:
        """Extract any config-like attributes."""
        config = {}
        for key, value in attributes.items():
            if any(config_term in key.lower() for config_term in ["model", "temperature", "provider"]):
                config[key] = value
        return config
    
    def extract_inputs(self, attributes: dict) -> dict:
        """Extract any input-like attributes."""
        inputs = {}
        for key, value in attributes.items():
            if any(input_term in key.lower() for input_term in ["input", "prompt", "message"]):
                inputs[key] = value
        return inputs
    
    def extract_outputs(self, attributes: dict) -> dict:
        """Extract any output-like attributes."""
        outputs = {}
        for key, value in attributes.items():
            if any(output_term in key.lower() for output_term in ["output", "response", "result"]):
                outputs[key] = value
        return outputs
    
    def extract_metadata(self, attributes: dict) -> dict:
        """Extract remaining attributes as metadata."""
        metadata = {}
        for key, value in attributes.items():
            if not any(term in key.lower() for term in ["model", "temperature", "provider", "input", "prompt", "message", "output", "response", "result"]):
                metadata[key] = value
        return metadata

class SemanticConventionMapper:
    """Main orchestrator for semantic convention processing."""
    
    def __init__(self, tracer_instance=None):
        self.tracer_instance = tracer_instance
        self.cache_manager = tracer_instance._cache_manager if tracer_instance else None
        
        self.registry = SemanticConventionRegistry(self.cache_manager)
        self.extractors = {
            "honeyhive_native": HoneyHiveNativeExtractor(self.cache_manager),
            "openinference": OpenInferenceExtractor(self.cache_manager),
            "traceloop": TraceloopExtractor(self.cache_manager),
            "openlit": OpenLitExtractor(self.cache_manager),
            "unknown": UnknownExtractor(self.cache_manager)
        }
    
    def convert_to_honeyhive_schema(self, span_data: SpanData) -> dict:
        """Convert span data to HoneyHive schema using appropriate extractor."""
        
        # Fast convention detection (cached)
        primary_convention = self.registry.detect_primary_convention(span_data.attributes)
        
        # Use appropriate extractor (cached extraction)
        extractor = self.extractors[primary_convention]
        honeyhive_event = extractor.extract_to_honeyhive_schema(span_data)
        
        # Add session context with tracer instance priority
        self._add_session_context(honeyhive_event, span_data)
        
        return honeyhive_event
    
    def _add_session_context(self, honeyhive_event: dict, span_data: SpanData):
        """Add session context with tracer instance priority and backend compatibility."""
        
        # Session ID: tracer instance takes priority over baggage
        session_id = None
        if self.tracer_instance and hasattr(self.tracer_instance, "session_id"):
            session_id = self.tracer_instance.session_id
        
        if not session_id:
            session_id = baggage.get_baggage("session_id")
        
        if session_id:
            honeyhive_event["session_id"] = session_id
            # CRITICAL: Backend compatibility - also add to span attributes
            span_data.attributes["honeyhive.session_id"] = session_id
            span_data.attributes["traceloop.association.properties.session_id"] = session_id
        
        # Project context
        project = getattr(self.tracer_instance, "project_name", None) if self.tracer_instance else None
        if not project:
            project = baggage.get_baggage("project")
        
        if project:
            honeyhive_event["project"] = project
            # CRITICAL: Backend compatibility - also add to span attributes
            span_data.attributes["honeyhive.project"] = project
            span_data.attributes["traceloop.association.properties.project"] = project
        
        # Source context
        source = getattr(self.tracer_instance, "source_environment", None) if self.tracer_instance else None
        if not source:
            source = baggage.get_baggage("source")
        
        if source:
            honeyhive_event["source"] = source
            # CRITICAL: Backend compatibility - also add to span attributes
            span_data.attributes["honeyhive.source"] = source
            span_data.attributes["traceloop.association.properties.source"] = source
        
        # Parent ID context
        parent_id = baggage.get_baggage("parent_id")
        if parent_id:
            honeyhive_event["parent_id"] = parent_id
            span_data.attributes["honeyhive.parent_id"] = parent_id
```

#### **TODO 9: Efficient Message Parsing with Caching**
```python
# In utils/message_parsing.py
import hashlib
import json
from typing import Any, Optional, List
from ...utils.cache import CacheManager

class MessageParser:
    """High-performance message parsing with caching."""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager
    
    def parse_openinference_messages(self, messages_data: Any) -> list:
        """Parse OpenInference message format with caching."""
        if not self.cache_manager:
            return self._parse_openinference_messages(messages_data)
        
        # Cache based on content hash
        message_hash = hashlib.md5(str(messages_data).encode()).hexdigest()
        cache_key = f"oi_messages:{message_hash}"
        
        return self.cache_manager.get_cached_attributes(
            attr_key=cache_key,
            normalizer_func=lambda: self._parse_openinference_messages(messages_data)
        )
    
    def parse_traceloop_messages(self, attributes: dict) -> list:
        """Parse Traceloop gen_ai.request.messages.{index}.{field} pattern."""
        if not self.cache_manager:
            return self._parse_traceloop_messages(attributes)
        
        # Cache based on attribute signature
        attr_signature = self._generate_traceloop_signature(attributes)
        cache_key = f"tl_messages:{attr_signature}"
        
        return self.cache_manager.get_cached_attributes(
            attr_key=cache_key,
            normalizer_func=lambda: self._parse_traceloop_messages(attributes)
        )
    
    def _generate_traceloop_signature(self, attributes: dict) -> str:
        """Generate signature for Traceloop message attributes."""
        message_keys = [key for key in attributes.keys() if key.startswith("gen_ai.request.messages.")]
        signature = "|".join(sorted(message_keys))
        return hashlib.md5(signature.encode()).hexdigest()
    
    def _parse_openinference_messages(self, messages_data: Any) -> list:
        """Actual OpenInference message parsing logic."""
        if isinstance(messages_data, str):
            try:
                return json.loads(messages_data)
            except json.JSONDecodeError:
                return []
        elif isinstance(messages_data, list):
            return messages_data
        else:
            return []
    
    def _parse_traceloop_messages(self, attributes: dict) -> list:
        """Actual Traceloop message parsing logic."""
        messages = {}
        
        # Extract gen_ai.request.messages.{index}.{field} patterns
        for key, value in attributes.items():
            if key.startswith("gen_ai.request.messages."):
                parts = key.split(".")
                if len(parts) >= 5:  # gen_ai.request.messages.{index}.{field}
                    try:
                        index = int(parts[3])
                        field = parts[4]
                        
                        if index not in messages:
                            messages[index] = {}
                        messages[index][field] = value
                    except (ValueError, IndexError):
                        continue
        
        # Convert to sorted list
        return [messages[i] for i in sorted(messages.keys())]
```

#### **TODO 10: Session Context Integration**
```python
# Enhanced session context handling
class SessionContextManager:
    """Manage session context for multi-instance scenarios."""
    
    def __init__(self, tracer_instance=None):
        self.tracer_instance = tracer_instance
    
    def enrich_with_session_context(self, honeyhive_event: dict, span_data: SpanData):
        """Add session context with proper priority handling and backend compatibility."""
        
        # Session ID priority: tracer instance > baggage > span attributes
        session_id = self._get_session_id(span_data)
        if session_id:
            honeyhive_event["session_id"] = session_id
            # CRITICAL: Backend compatibility - dual attribute mapping
            span_data.attributes["honeyhive.session_id"] = session_id
            span_data.attributes["traceloop.association.properties.session_id"] = session_id
        
        # Project context
        project = self._get_project(span_data)
        if project:
            honeyhive_event["project"] = project
            # CRITICAL: Backend compatibility - dual attribute mapping
            span_data.attributes["honeyhive.project"] = project
            span_data.attributes["traceloop.association.properties.project"] = project
        
        # Source context
        source = self._get_source(span_data)
        if source:
            honeyhive_event["source"] = source
            # CRITICAL: Backend compatibility - dual attribute mapping
            span_data.attributes["honeyhive.source"] = source
            span_data.attributes["traceloop.association.properties.source"] = source
        
        # Parent ID context
        parent_id = self._get_parent_id(span_data)
        if parent_id:
            honeyhive_event["parent_id"] = parent_id
            span_data.attributes["honeyhive.parent_id"] = parent_id
        
        # Experiment attributes if present
        self._add_experiment_attributes(honeyhive_event, span_data)
    
    def _get_session_id(self, span_data: SpanData) -> Optional[str]:
        """Get session ID with proper priority."""
        # Priority 1: Tracer instance
        if self.tracer_instance and hasattr(self.tracer_instance, "session_id"):
            return self.tracer_instance.session_id
        
        # Priority 2: Baggage
        session_id = baggage.get_baggage("session_id")
        if session_id:
            return session_id
        
        # Priority 3: Span attributes
        return span_data.attributes.get("honeyhive_session_id")
    
    def _get_project(self, span_data: SpanData) -> Optional[str]:
        """Get project with proper priority."""
        # Priority 1: Tracer instance
        if self.tracer_instance and hasattr(self.tracer_instance, "project_name"):
            return self.tracer_instance.project_name
        
        # Priority 2: Baggage
        project = baggage.get_baggage("project")
        if project:
            return project
        
        # Priority 3: Span attributes
        return span_data.attributes.get("honeyhive_project")
    
    def _get_source(self, span_data: SpanData) -> Optional[str]:
        """Get source with proper priority."""
        # Priority 1: Tracer instance
        if self.tracer_instance and hasattr(self.tracer_instance, "source_environment"):
            return self.tracer_instance.source_environment
        
        # Priority 2: Baggage
        source = baggage.get_baggage("source")
        if source:
            return source
        
        # Priority 3: Span attributes
        return span_data.attributes.get("honeyhive_source", "python-sdk")
    
    def _get_parent_id(self, span_data: SpanData) -> Optional[str]:
        """Get parent ID from baggage or span attributes."""
        # Priority 1: Baggage
        parent_id = baggage.get_baggage("parent_id")
        if parent_id:
            return parent_id
        
        # Priority 2: Span attributes
        return span_data.attributes.get("honeyhive_parent_id")
    
    def _add_experiment_attributes(self, honeyhive_event: dict, span_data: SpanData):
        """Add experiment attributes if present."""
        # Add any experiment-related attributes from span data
        for key, value in span_data.attributes.items():
            if key.startswith("honeyhive_experiment_"):
                experiment_key = key.replace("honeyhive_experiment_", "")
                if "experiment" not in honeyhive_event:
                    honeyhive_event["experiment"] = {}
                honeyhive_event["experiment"][experiment_key] = value
```

### **PHASE 2: Integration & Export (TODOs 11-16)**

#### **TODO 11: Create Exporters Module**
```
src/honeyhive/tracer/exporters/
├── __init__.py
├── base.py                    # Abstract exporter interface
└── honeyhive_exporter.py      # HoneyHive-specific export logic
```

#### **TODO 12: HoneyHiveExporter Implementation**
```python
class HoneyHiveExporter:
    """Handle both client and OTLP export modes with error handling."""
    
    def __init__(self, tracer_instance=None, **config):
        self.tracer_instance = tracer_instance
        self.client_mode = config.get("client_mode", True)
        self.otlp_mode = config.get("otlp_mode", False)
    
    def export_event(self, honeyhive_event: dict) -> bool:
        """Export event using configured mode."""
        try:
            if self.client_mode:
                return self._export_via_client(honeyhive_event)
            elif self.otlp_mode:
                return self._export_via_otlp(honeyhive_event)
            else:
                return False
        except Exception as e:
            self._handle_export_error(e, honeyhive_event)
            return False
```

#### **TODO 13: Span Processor Integration**
```python
import logging
from opentelemetry.trace import ReadableSpan
from .semantic_conventions import SemanticConventionMapper
from .exporters import HoneyHiveExporter
from .context import SessionContextManager

class SemanticConventionError(Exception):
    """Base exception for semantic convention processing."""
    pass

class HoneyHiveSpanProcessor:
    """Enhanced span processor with semantic convention support."""
    
    def __init__(self, tracer_instance=None, **config):
        self.tracer_instance = tracer_instance
        self.logger = logging.getLogger(__name__)
        
        # Semantic convention components
        self.semantic_mapper = SemanticConventionMapper(tracer_instance)
        self.exporter = HoneyHiveExporter(tracer_instance, **config)
        self.context_manager = SessionContextManager(tracer_instance)
    
    def on_end(self, span: ReadableSpan) -> None:
        """Process span using semantic conventions as primary logic."""
        try:
            # Convert span to structured data
            span_data = SpanData.from_readable_span(span)
            
            # Process through semantic convention mapper
            honeyhive_event = self.semantic_mapper.convert_to_honeyhive_schema(span_data)
            
            # Enrich with session context
            self.context_manager.enrich_with_session_context(honeyhive_event, span_data)
            
            # Export the event
            success = self.exporter.export_event(honeyhive_event)
            
            if not success:
                self._log_export_failure(honeyhive_event)
                
        except Exception as e:
            self._handle_processing_error(e, span)
    
    def _handle_processing_error(self, error: Exception, span: ReadableSpan):
        """Handle processing errors gracefully."""
        self.logger.error(f"Semantic convention processing failed: {error}")
        
        # Create minimal event for critical failures
        try:
            minimal_event = self._create_minimal_event(span)
            self.exporter.export_event(minimal_event)
        except Exception as fallback_error:
            self.logger.error(f"Minimal event creation failed: {fallback_error}")
    
    def _create_minimal_event(self, span: ReadableSpan) -> dict:
        """Create minimal event structure for error cases."""
        return {
            "event_name": span.name,
            "event_type": "error",
            "start_time": span.start_time,
            "end_time": span.end_time,
            "config": {},
            "inputs": {},
            "outputs": {},
            "metadata": {"error": "semantic_convention_processing_failed"}
        }
    
    def _log_export_failure(self, event: dict):
        """Log export failures for debugging."""
        self.logger.warning(f"Event export failed for: {event.get('event_name', 'unknown')}")
```

### **PHASE 3: Performance & Validation (TODOs 17-22)**

#### **TODO 17: Performance Optimization with Caching**
```python
# Cache configuration for semantic conventions
SEMANTIC_CONVENTION_CACHE_CONFIG = CacheConfig(
    max_size=2000,          # More patterns than basic attributes  
    default_ttl=600.0,      # 10 minutes (balance freshness/performance)
    cleanup_interval=120.0  # Active cleanup for hot path
)

# Integration with existing CacheManager
def configure_semantic_convention_caching(tracer_instance):
    """Configure optimal caching for semantic convention processing."""
    if not tracer_instance._cache_manager:
        return
    
    # Create semantic convention specific caches
    tracer_instance._cache_manager.get_cache(
        "convention_detect", 
        SEMANTIC_CONVENTION_CACHE_CONFIG
    )
    tracer_instance._cache_manager.get_cache(
        "extraction_results",
        SEMANTIC_CONVENTION_CACHE_CONFIG  
    )
    tracer_instance._cache_manager.get_cache(
        "message_parsing",
        CacheConfig(max_size=1000, default_ttl=300.0)  # Shorter TTL for dynamic content
    )
```

#### **TODO 18: Event Validation**
```python
class HoneyHiveEventValidator:
    """Validate generated events match Deep Research Prod format."""
    
    def validate_event_structure(self, event: dict) -> bool:
        """Validate against Deep Research Prod schema."""
        required_fields = ["project", "source", "event_type", "config", "inputs", "outputs", "metadata"]
        
        for field in required_fields:
            if field not in event:
                return False
        
        # Validate specific field structures
        return (
            self._validate_config_structure(event["config"]) and
            self._validate_inputs_structure(event["inputs"]) and
            self._validate_outputs_structure(event["outputs"]) and
            self._validate_metadata_structure(event["metadata"])
        )
```

#### **TODO 19: Performance Benchmarking**
```python
class SemanticConventionBenchmark:
    """Benchmark semantic convention processing performance."""
    
    def benchmark_processing_time(self, sample_spans: List[SpanData]) -> Dict[str, float]:
        """Ensure <100μs per span processing time."""
        
        results = {}
        
        for convention_type in ["honeyhive_native", "openinference", "traceloop", "openlit"]:
            times = []
            
            for span_data in sample_spans:
                start_time = time.perf_counter()
                
                # Process span
                self.semantic_mapper.convert_to_honeyhive_schema(span_data)
                
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1_000_000)  # Convert to microseconds
            
            results[convention_type] = {
                "avg_microseconds": sum(times) / len(times),
                "max_microseconds": max(times),
                "p95_microseconds": sorted(times)[int(0.95 * len(times))]
            }
        
        return results
```

### **PHASE 4: Testing & Quality (TODOs 23-28)**

#### **TODO 23-25: Comprehensive Testing Strategy**
```python
# Unit Tests for Extractors
class TestHoneyHiveNativeExtractor:
    """Test main branch compatibility patterns."""
    
    def test_main_branch_trace_decorator_compatibility(self):
        """Ensure @trace decorator patterns work exactly as main branch."""
        attributes = {
            "honeyhive_event_type": "model",
            "honeyhive_config": {"model": "gpt-4", "temperature": 0.7},
            "honeyhive_inputs._params_.prompt": "Hello world",
            "honeyhive_outputs.result": "Hi there!"
        }
        
        extractor = HoneyHiveNativeExtractor()
        result = extractor.extract_to_honeyhive_schema(SpanData(attributes=attributes))
        
        assert result["config"]["model"] == "gpt-4"
        assert result["inputs"]["parameters"]["prompt"] == "Hello world"
        assert result["outputs"]["result"] == "Hi there!"

# Integration Tests with Deep Research Prod
class TestDeepResearchProdCompatibility:
    """Test against actual Deep Research Prod event samples."""
    
    def test_generated_events_match_deep_research_prod_format(self):
        """Validate generated events exactly match Deep Research Prod samples."""
        
        # Load sample from event_analysis/first_event_complete.json
        with open("event_analysis/first_event_complete.json") as f:
            target_event = json.load(f)
        
        # Generate event using semantic convention mapper
        generated_event = self.semantic_mapper.convert_to_honeyhive_schema(sample_span_data)
        
        # Validate structure matches exactly
        assert_event_structure_matches(generated_event, target_event)

# BYOI Multi-Instrumentor Tests  
class TestBYOIPatterns:
    """Test BYOI patterns with mixed instrumentors."""
    
    def test_mixed_openinference_traceloop_instrumentors(self):
        """Test scenario with both OpenInference and Traceloop instrumentors."""
        
        # Simulate spans from different instrumentors in same application
        openinference_span = create_span_with_llm_attributes()
        traceloop_span = create_span_with_gen_ai_attributes()
        
        # Both should be processed correctly
        oi_result = self.semantic_mapper.convert_to_honeyhive_schema(openinference_span)
        tl_result = self.semantic_mapper.convert_to_honeyhive_schema(traceloop_span)
        
        assert oi_result["config"]["model"] == "gpt-4"  # From llm.model_name
        assert tl_result["config"]["model"] == "gpt-4"  # From gen_ai.request.model
```

### **PHASE 5: Release Preparation (TODOs 29-33)**

#### **TODO 29: Migration Documentation**
```markdown
# Migration Guide: Main Branch → RC3

## Zero-Code Migration (Recommended)

### Before (Main Branch):
```python
from honeyhive import HoneyHiveTracer, trace, enrich_span

tracer = HoneyHiveTracer.init(project="my-project")

@trace(event_type="model", config={"model": "gpt-4"})
def my_function():
    enrich_span(metadata={"custom": "data"})
```

### After (RC3):
```python
from honeyhive import HoneyHiveTracer, trace, enrich_span

tracer = HoneyHiveTracer.init(project="my-project")  # SAME API

@trace(event_type="model", config={"model": "gpt-4"})  # SAME DECORATOR
def my_function():
    enrich_span(metadata={"custom": "data"})  # SAME ENRICHMENT
```

**Result**: Identical functionality + enhanced semantic convention support!

## Enhanced BYOI Usage (New Capability)

### Add OpenInference Instrumentor:
```python
from honeyhive import HoneyHiveTracer
from openinference.instrumentation.openai import OpenAIInstrumentor

tracer = HoneyHiveTracer.init(project="my-project")
instrumentor = OpenAIInstrumentor()
instrumentor.instrument(tracer_provider=tracer.provider)

# Now OpenAI calls automatically generate llm.* attributes
# which are automatically converted to HoneyHive schema
response = openai_client.chat.completions.create(...)
```
```

#### **TODO 30: Final RC3 Validation**
```python
class RC3ValidationSuite:
    """Comprehensive RC3 validation against all requirements."""
    
    def validate_main_branch_compatibility(self):
        """Ensure 100% main branch API compatibility."""
        # Test all main branch patterns work identically
        
    def validate_semantic_convention_support(self):
        """Ensure all semantic conventions properly supported."""
        # Test OpenInference, Traceloop, OpenLit, HoneyHive native
        
    def validate_deep_research_prod_format(self):
        """Ensure generated events match Deep Research Prod exactly."""
        # Test against actual event samples
        
    def validate_performance_requirements(self):
        """Ensure <100μs processing time maintained."""
        # Benchmark all convention types
        
    def validate_byoi_architecture(self):
        """Ensure BYOI patterns work correctly."""
        # Test multi-instrumentor scenarios
        
    def validate_multi_instance_isolation(self):
        """Ensure multi-instance tracer isolation maintained."""
        # Test cache isolation, session isolation
```

## 🎯 Success Criteria & Validation

### **Primary Success Criteria:**
1. ✅ **100% Main Branch Compatibility**: All existing @trace and enrich_span patterns work identically
2. ✅ **Backend Compatibility**: Dual attribute mapping (honeyhive.* + traceloop.association.properties.*) preserved
3. ✅ **Semantic Convention Support**: OpenInference, Traceloop, OpenLit automatically converted
4. ✅ **Deep Research Prod Format**: Generated events match target schema exactly
5. ✅ **Performance**: <100μs per span processing with caching benefits
6. ✅ **BYOI Architecture**: Multi-instrumentor scenarios work seamlessly

### **Performance Targets:**
- **Convention Detection**: <10μs (cached)
- **Extraction Processing**: <50μs (cached)  
- **Total Processing**: <100μs (including validation)
- **Cache Hit Rate**: >80% for repeated patterns
- **Memory Usage**: <50MB additional for caching

### **Compatibility Validation:**
- **API Compatibility**: Identical imports, identical decorators, identical behavior
- **Session Management**: Multi-instance isolation preserved
- **Error Handling**: Graceful degradation to existing logic
- **Performance**: No regression, preferably improvement with caching

## 🚀 Implementation Timeline

### **Week 1: Core Architecture (Phase 1)**
- Days 1-2: Module structure and BaseExtractor
- Days 3-4: HoneyHiveNativeExtractor (CRITICAL)
- Days 5-7: OpenInference, Traceloop, OpenLit extractors

### **Week 2: Integration (Phase 2)**  
- Days 1-3: SemanticConventionMapper and Registry
- Days 4-5: Span processor integration
- Days 6-7: Export and context management

### **Week 3: Performance & Testing (Phases 3-4)**
- Days 1-2: Caching integration and performance optimization
- Days 3-5: Comprehensive testing suite
- Days 6-7: BYOI and multi-instance testing

### **Week 4: Release Preparation (Phase 5)**
- Days 1-3: Documentation and migration guides
- Days 4-5: Deep Research Prod validation
- Days 6-7: Final RC3 validation and release preparation

## 💡 Risk Mitigation

### **Low Risk Factors:**
- ✅ **Infrastructure Complete**: Migration 90% done, caching production-ready
- ✅ **Clear Integration Point**: Span processor enhancement well-defined
- ✅ **Additive Enhancement**: No replacement of existing functionality
- ✅ **Fallback Strategy**: Existing logic preserved as backup

### **Mitigation Strategies:**
1. **Preserve Existing Logic**: Always maintain fallback to current span processing
2. **Incremental Testing**: Test each extractor independently before integration
3. **Performance Monitoring**: Continuous benchmarking during development
4. **Graceful Degradation**: Semantic convention failures never break existing functionality

## 🎯 Conclusion

This comprehensive plan leverages all discovered context to implement semantic convention support as a **low-risk, high-value enhancement** to the existing production-ready refactored tracer. The approach ensures **100% backward compatibility** while adding **powerful new capabilities** for the BYOI architecture.

**RC3 Success = Main Branch Compatibility + Enhanced Semantic Convention Support + Production Performance**
