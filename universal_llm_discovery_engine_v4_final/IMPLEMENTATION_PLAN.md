# Universal LLM Discovery Engine v4.0 - Implementation Plan

**Version**: 4.0 Final  
**Date**: 2025-01-27  
**Status**: Implementation Ready  
**Timeline**: 4-Week Implementation with Build System

---

## 🎯 **Implementation Overview**

This plan provides a complete 4-week roadmap for implementing the Universal LLM Discovery Engine v4.0 with provider-isolated architecture and build-time compilation.

### **Key Implementation Principles**
1. **Provider Isolation First**: Each provider is completely independent
2. **Build-Time Optimization**: All YAML configs compiled to optimized Python structures
3. **Development-Aware Loading**: Seamless development and production workflows
4. **AI Assistant Optimized**: Small, focused files enable parallel development
5. **Customer Application Ready**: Self-contained, minimal footprint, predictable performance

## 📅 **4-Week Implementation Timeline**

### **Week 1: Foundation & Build System**
- **Days 1-2**: Provider-isolated DSL structure and build system
- **Days 3-4**: Development-aware bundle loading system
- **Days 5-7**: Core processing engine and validation framework

### **Week 2: Core Provider Implementation**
- **Days 8-9**: OpenAI provider (complete 4-file implementation)
- **Days 10-11**: Anthropic provider (complete 4-file implementation)
- **Days 12-14**: Gemini provider and provider detection testing

### **Week 3: Extended Provider Support**
- **Days 15-16**: Cohere and AWS Bedrock providers
- **Days 17-18**: Remaining providers (Mistral, NVIDIA, IBM, Groq, Ollama)
- **Days 19-21**: Integration testing and performance optimization

### **Week 4: Production Deployment**
- **Days 22-23**: CI/CD integration and automated testing
- **Days 24-25**: Production deployment and monitoring
- **Days 26-28**: Documentation, training, and handoff

## 📋 **Phase 1: Foundation & Build System (Week 1)**

### **Task 1.1: Provider-Isolated DSL Structure (Days 1-2)**

#### **Day 1: Directory Structure and Templates**

**Create Provider Directory Structure**:
```bash
mkdir -p config/dsl/providers/{openai,anthropic,gemini,cohere,aws_bedrock,mistral,nvidia,ibm,groq,ollama}
mkdir -p config/dsl/shared
mkdir -p scripts
mkdir -p tests/providers
```

**Generate Provider Template System**:
```python
# scripts/generate_provider_template.py
"""Generate template files for new providers."""

import yaml
from pathlib import Path
from typing import Dict, Any

class ProviderTemplateGenerator:
    """Generate consistent provider templates."""
    
    def generate_provider_files(self, provider_name: str) -> None:
        """Generate all 4 provider files from templates."""
        
        provider_dir = Path(f"config/dsl/providers/{provider_name}")
        provider_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate structure_patterns.yaml
        self._generate_structure_patterns(provider_dir, provider_name)
        
        # Generate navigation_rules.yaml
        self._generate_navigation_rules(provider_dir, provider_name)
        
        # Generate field_mappings.yaml
        self._generate_field_mappings(provider_dir, provider_name)
        
        # Generate transforms.yaml
        self._generate_transforms(provider_dir, provider_name)
    
    def _generate_structure_patterns(self, provider_dir: Path, provider_name: str):
        """Generate structure_patterns.yaml template."""
        
        template = {
            "version": "1.0",
            "provider": provider_name,
            "dsl_type": "provider_structure_patterns",
            "patterns": {
                f"{provider_name}_primary": {
                    "signature_fields": ["field1", "field2", "field3"],
                    "optional_fields": ["optional1", "optional2"],
                    "confidence_weight": 0.95,
                    "description": f"Primary {provider_name} detection pattern"
                }
            },
            "validation": {
                "minimum_signature_fields": 2,
                "maximum_patterns": 5,
                "confidence_threshold": 0.80
            }
        }
        
        with open(provider_dir / "structure_patterns.yaml", 'w') as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)
```

**Create Shared Configuration Files**:
```python
# Generate config/dsl/shared/core_schema.yaml
core_schema = {
    "version": "1.0",
    "dsl_type": "honeyhive_core_schema",
    "honeyhive_schema": {
        "inputs": {
            "description": "User inputs, chat history, prompts, context",
            "required_fields": [],
            "optional_fields": ["chat_history", "prompt", "context", "system_message"]
        },
        "outputs": {
            "description": "Model responses, completions, tool calls, results",
            "required_fields": [],
            "optional_fields": ["response", "completion", "tool_calls", "function_calls"]
        },
        "config": {
            "description": "Model parameters, temperature, max tokens, system prompts",
            "required_fields": [],
            "optional_fields": ["model", "temperature", "max_tokens", "top_p", "frequency_penalty"]
        },
        "metadata": {
            "description": "Usage metrics, timestamps, provider info, performance data",
            "required_fields": ["provider"],
            "optional_fields": ["prompt_tokens", "completion_tokens", "total_tokens", "latency"]
        }
    }
}
```

#### **Day 2: Build System Core**

**Create Provider Compiler**:
```python
# scripts/compile_providers.py
"""
Provider Bundle Compilation System

Compiles provider YAML files to optimized Python structures for O(1) runtime performance.
"""

import yaml
import pickle
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Set, FrozenSet, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class CompiledProviderBundle:
    """Compiled provider bundle structure."""
    provider_signatures: Dict[str, List[FrozenSet[str]]]
    extraction_functions: Dict[str, str]  # Function code strings
    field_mappings: Dict[str, Dict[str, Any]]
    transform_registry: Dict[str, Dict[str, Any]]
    validation_rules: Dict[str, Any]
    build_metadata: Dict[str, Any]

class ProviderCompiler:
    """Compile provider YAML files to optimized bundle."""
    
    def __init__(self, source_dir: Path, output_dir: Path):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.providers = {}
        self.shared_config = {}
        
    def compile_all_providers(self) -> CompiledProviderBundle:
        """Main compilation entry point."""
        
        logger.info("Starting provider bundle compilation...")
        
        # Step 1: Load and validate all files
        self._load_shared_configuration()
        self._load_all_providers()
        
        # Step 2: Compile to optimized structures
        provider_signatures = self._compile_provider_signatures()
        extraction_functions = self._compile_extraction_functions()
        field_mappings = self._compile_field_mappings()
        transform_registry = self._compile_transform_registry()
        validation_rules = self._compile_validation_rules()
        
        # Step 3: Create bundle with metadata
        bundle = CompiledProviderBundle(
            provider_signatures=provider_signatures,
            extraction_functions=extraction_functions,
            field_mappings=field_mappings,
            transform_registry=transform_registry,
            validation_rules=validation_rules,
            build_metadata=self._generate_build_metadata()
        )
        
        # Step 4: Validate and save bundle
        self._validate_bundle(bundle)
        self._save_bundle(bundle)
        
        logger.info(f"Successfully compiled {len(self.providers)} providers")
        return bundle
    
    def _compile_provider_signatures(self) -> Dict[str, List[FrozenSet[str]]]:
        """Compile provider signatures for O(1) detection."""
        
        signatures = {}
        
        for provider_name, provider_data in self.providers.items():
            patterns = provider_data['structure_patterns']['patterns']
            
            # Create frozenset for each pattern
            provider_signatures = []
            for pattern_name, pattern_data in patterns.items():
                signature_fields = frozenset(pattern_data['signature_fields'])
                provider_signatures.append(signature_fields)
            
            signatures[provider_name] = provider_signatures
            logger.debug(f"Compiled {len(provider_signatures)} signatures for {provider_name}")
            
        return signatures
```

### **Task 1.2: Development-Aware Bundle Loading (Days 3-4)**

#### **Day 3: Bundle Loader Implementation**

**Create Bundle Loader**:
```python
# src/honeyhive/tracer/processing/semantic_conventions/bundle_loader.py
"""
Development-Aware Bundle Loading System

Automatically handles development vs production loading with seamless recompilation.
"""

import os
import sys
import pickle
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Callable

logger = logging.getLogger(__name__)

class DevelopmentAwareBundleLoader:
    """Intelligent bundle loader for development and production environments."""
    
    def __init__(self, bundle_path: Path, source_path: Optional[Path] = None):
        self.bundle_path = bundle_path
        self.source_path = source_path
        self.bundle_metadata_path = bundle_path.parent / "bundle_metadata.json"
        self._cached_bundle = None
        self._cached_functions = {}
        
    def load_provider_bundle(self) -> Dict[str, Any]:
        """Load bundle with development-aware recompilation."""
        
        if self._is_development_environment():
            return self._load_development_bundle()
        else:
            return self._load_production_bundle()
    
    def _is_development_environment(self) -> bool:
        """Detect if running in development vs production."""
        
        development_indicators = [
            self.source_path and self.source_path.exists(),  # Source files present
            os.environ.get('HONEYHIVE_DEV_MODE') == 'true',  # Explicit dev flag
            'pytest' in sys.modules,                         # Running tests
            Path('.git').exists(),                           # Git repository
            os.environ.get('CI') != 'true',                  # Not in CI environment
        ]
        
        is_dev = any(development_indicators)
        logger.debug(f"Environment detection: development={is_dev}")
        return is_dev
    
    def _load_development_bundle(self) -> Dict[str, Any]:
        """Load bundle in development mode with auto-recompilation."""
        
        if self._needs_recompilation():
            logger.info("Source files updated, recompiling provider bundle...")
            self._recompile_bundle()
            self._cached_bundle = None  # Force reload
        
        return self._load_bundle_with_debug_info()
    
    def _needs_recompilation(self) -> bool:
        """Check if source files are newer than compiled bundle."""
        
        if not self.bundle_path.exists():
            logger.debug("Bundle doesn't exist, recompilation needed")
            return True
            
        if not self.source_path or not self.source_path.exists():
            logger.debug("No source path, no recompilation needed")
            return False
            
        bundle_mtime = self.bundle_path.stat().st_mtime
        
        # Check all YAML files in source directory
        for yaml_file in self.source_path.rglob("*.yaml"):
            if yaml_file.stat().st_mtime > bundle_mtime:
                logger.debug(f"Source file {yaml_file} is newer than bundle")
                return True
                
        return False
    
    def _recompile_bundle(self):
        """Recompile bundle from source files."""
        
        try:
            # Run compilation script
            compile_script = Path(__file__).parent.parent.parent.parent.parent / "scripts" / "compile_providers.py"
            
            result = subprocess.run([
                sys.executable, str(compile_script),
                "--source-dir", str(self.source_path),
                "--output-dir", str(self.bundle_path.parent)
            ], capture_output=True, text=True, check=True)
            
            logger.info("Bundle recompilation completed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Bundle recompilation failed: {e.stderr}")
            raise RuntimeError(f"Failed to recompile provider bundle: {e.stderr}")
    
    def _load_bundle_with_debug_info(self) -> Dict[str, Any]:
        """Load bundle with development debugging information."""
        
        if self._cached_bundle is None:
            with open(self.bundle_path, 'rb') as f:
                self._cached_bundle = pickle.load(f)
            
            # Compile extraction functions
            self._compile_extraction_functions()
            
            logger.info(f"Loaded bundle with {len(self._cached_bundle.provider_signatures)} providers")
            
        return self._cached_bundle
    
    def _compile_extraction_functions(self):
        """Compile extraction function code strings to callable functions."""
        
        for provider_name, function_code in self._cached_bundle.extraction_functions.items():
            try:
                # Compile function code
                compiled_code = compile(function_code, f"<{provider_name}_extraction>", "exec")
                
                # Execute to create function in local namespace
                local_namespace = {}
                exec(compiled_code, globals(), local_namespace)
                
                # Extract the function
                function_name = f"extract_{provider_name}_data"
                if function_name in local_namespace:
                    self._cached_functions[provider_name] = local_namespace[function_name]
                else:
                    logger.error(f"Function {function_name} not found in compiled code")
                    
            except Exception as e:
                logger.error(f"Failed to compile extraction function for {provider_name}: {e}")
                raise
```

#### **Day 4: Bundle Validation and Testing**

**Create Bundle Validator**:
```python
# scripts/validate_bundle.py
"""
Provider Bundle Validation System

Validates compiled provider bundles for correctness and performance.
"""

import pickle
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Set

logger = logging.getLogger(__name__)

class BundleValidator:
    """Validate compiled provider bundles."""
    
    def __init__(self, bundle_path: Path):
        self.bundle_path = bundle_path
        self.bundle = None
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_bundle(self) -> bool:
        """Main validation entry point."""
        
        logger.info("Starting bundle validation...")
        
        # Load bundle
        self._load_bundle()
        
        # Run validation checks
        self._validate_structure()
        self._validate_provider_signatures()
        self._validate_extraction_functions()
        self._validate_field_mappings()
        self._validate_performance_characteristics()
        
        # Report results
        self._report_validation_results()
        
        return len(self.validation_errors) == 0
    
    def _validate_provider_signatures(self):
        """Validate provider signature patterns."""
        
        signatures = self.bundle.provider_signatures
        
        for provider_name, provider_signatures in signatures.items():
            # Check signature uniqueness
            signature_strings = set()
            for signature in provider_signatures:
                signature_str = frozenset_to_string(signature)
                if signature_str in signature_strings:
                    self.validation_errors.append(
                        f"Duplicate signature in provider {provider_name}: {signature_str}"
                    )
                signature_strings.add(signature_str)
            
            # Check minimum signature size
            for signature in provider_signatures:
                if len(signature) < 2:
                    self.validation_warnings.append(
                        f"Small signature in provider {provider_name}: {signature} (may cause false positives)"
                    )
```

### **Task 1.3: Core Processing Engine (Days 5-7)**

#### **Day 5: Provider Detection Engine**

**Create Provider Processor**:
```python
# src/honeyhive/tracer/processing/semantic_conventions/provider_processor.py
"""
Universal LLM Discovery Engine v4.0 - Core Processing Engine

O(1) provider detection and data extraction using pre-compiled bundles.
"""

import logging
from typing import Dict, Any, Optional, FrozenSet, List, Callable
from pathlib import Path

logger = logging.getLogger(__name__)

class UniversalProviderProcessor:
    """Core processing engine for Universal LLM Discovery Engine v4.0."""
    
    def __init__(self, bundle_loader):
        self.bundle_loader = bundle_loader
        self.bundle = None
        self.extraction_functions = {}
        self._load_bundle()
    
    def _load_bundle(self):
        """Load and prepare provider bundle."""
        
        self.bundle = self.bundle_loader.load_provider_bundle()
        
        # Compile extraction functions if needed
        if hasattr(self.bundle_loader, '_cached_functions'):
            self.extraction_functions = self.bundle_loader._cached_functions
        else:
            self._compile_extraction_functions()
    
    def process_span_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing entry point.
        
        Convert span attributes to HoneyHive schema using O(1) provider detection.
        """
        
        # Step 1: O(1) Provider Detection
        provider = self._detect_provider(attributes)
        
        if provider == 'unknown':
            logger.debug("No provider detected, using fallback processing")
            return self._fallback_processing(attributes)
        
        # Step 2: O(1) Data Extraction
        honeyhive_data = self._extract_provider_data(provider, attributes)
        
        # Step 3: Validation and Enhancement
        validated_data = self._validate_and_enhance(honeyhive_data, provider)
        
        logger.debug(f"Successfully processed span data using {provider} provider")
        return validated_data
    
    def _detect_provider(self, attributes: Dict[str, Any]) -> str:
        """
        O(1) provider detection using frozenset operations.
        
        Performance: O(1) - frozenset.issubset() is hash-based
        """
        
        attribute_keys = frozenset(attributes.keys())
        
        # Check each provider's signatures
        for provider_name, signatures in self.bundle.provider_signatures.items():
            for signature in signatures:
                if signature.issubset(attribute_keys):
                    logger.debug(f"Detected provider: {provider_name} (signature match)")
                    return provider_name
        
        return 'unknown'
    
    def _extract_provider_data(self, provider: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        O(1) data extraction using compiled extraction functions.
        
        Performance: O(1) - dict lookup + compiled function execution
        """
        
        if provider not in self.extraction_functions:
            logger.error(f"No extraction function found for provider: {provider}")
            return self._fallback_processing(attributes)
        
        try:
            extraction_function = self.extraction_functions[provider]
            return extraction_function(attributes)
            
        except Exception as e:
            logger.error(f"Extraction function failed for provider {provider}: {e}")
            return self._fallback_processing(attributes)
    
    def _validate_and_enhance(self, data: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Validate and enhance extracted data."""
        
        # Ensure all required sections exist
        for section in ['inputs', 'outputs', 'config', 'metadata']:
            if section not in data:
                data[section] = {}
        
        # Ensure provider is set in metadata
        if 'provider' not in data['metadata']:
            data['metadata']['provider'] = provider
        
        # Add processing metadata
        data['metadata']['processing_engine'] = 'universal_llm_discovery_v4'
        data['metadata']['detection_method'] = 'signature_based'
        
        return data
    
    def _fallback_processing(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback processing for unknown providers."""
        
        # Basic extraction using common patterns
        inputs = {}
        outputs = {}
        config = {}
        metadata = {'provider': 'unknown'}
        
        # Extract common fields
        for key, value in attributes.items():
            if 'input' in key.lower() or 'prompt' in key.lower():
                inputs[key] = value
            elif 'output' in key.lower() or 'completion' in key.lower():
                outputs[key] = value
            elif 'model' in key.lower() or 'temperature' in key.lower():
                config[key] = value
            else:
                metadata[key] = value
        
        return {
            'inputs': inputs,
            'outputs': outputs,
            'config': config,
            'metadata': metadata
        }
```

#### **Day 6: Integration with Existing Tracer**

**Create Tracer Integration**:
```python
# src/honeyhive/tracer/processing/semantic_conventions/universal_processor.py
"""
Integration layer for Universal LLM Discovery Engine v4.0 with existing HoneyHive tracer.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .bundle_loader import DevelopmentAwareBundleLoader
from .provider_processor import UniversalProviderProcessor

logger = logging.getLogger(__name__)

class UniversalSemanticConventionProcessor:
    """Integration layer for Universal LLM Discovery Engine with HoneyHive tracer."""
    
    def __init__(self, cache_manager=None):
        self.cache_manager = cache_manager
        self.processor = None
        self._initialize_processor()
    
    def _initialize_processor(self):
        """Initialize the universal processor with bundle loading."""
        
        # Determine bundle and source paths
        current_dir = Path(__file__).parent
        bundle_path = current_dir / "compiled_providers.pkl"
        source_path = current_dir.parent.parent.parent.parent.parent / "config" / "dsl"
        
        # Create bundle loader
        bundle_loader = DevelopmentAwareBundleLoader(
            bundle_path=bundle_path,
            source_path=source_path if source_path.exists() else None
        )
        
        # Create processor
        self.processor = UniversalProviderProcessor(bundle_loader)
        
        logger.info("Universal LLM Discovery Engine v4.0 initialized")
    
    def process_span(self, span_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process span data using Universal LLM Discovery Engine.
        
        This replaces the existing semantic convention processing.
        """
        
        if not self.processor:
            logger.error("Universal processor not initialized")
            return span_data
        
        try:
            # Extract attributes from span data
            attributes = span_data.get('attributes', {})
            
            # Process using universal engine
            honeyhive_data = self.processor.process_span_attributes(attributes)
            
            # Merge with existing span data
            processed_span = {**span_data}
            processed_span.update(honeyhive_data)
            
            # Cache if cache manager available
            if self.cache_manager:
                cache_key = self._generate_cache_key(attributes)
                self.cache_manager.set(cache_key, honeyhive_data)
            
            return processed_span
            
        except Exception as e:
            logger.error(f"Universal processing failed: {e}")
            return span_data
    
    def _generate_cache_key(self, attributes: Dict[str, Any]) -> str:
        """Generate cache key for processed data."""
        
        # Use sorted attribute keys as cache key
        key_parts = sorted(attributes.keys())
        return f"universal_v4::{':'.join(key_parts)}"
```

#### **Day 7: Testing Framework**

**Create Test Framework**:
```python
# tests/test_universal_processor.py
"""
Test suite for Universal LLM Discovery Engine v4.0
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from src.honeyhive.tracer.processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor
from src.honeyhive.tracer.processing.semantic_conventions.provider_processor import UniversalProviderProcessor
from src.honeyhive.tracer.processing.semantic_conventions.bundle_loader import DevelopmentAwareBundleLoader

class TestUniversalProcessor:
    """Test suite for Universal LLM Discovery Engine."""
    
    @pytest.fixture
    def mock_bundle_data(self):
        """Create mock bundle data for testing."""
        
        return {
            'provider_signatures': {
                'openai': [frozenset(['llm.input_messages', 'llm.output_messages', 'llm.model_name'])],
                'anthropic': [frozenset(['llm.input_messages', 'llm.output_messages', 'llm.usage.input_tokens'])]
            },
            'extraction_functions': {
                'openai': '''
def extract_openai_data(attributes):
    return {
        'inputs': {'chat_history': attributes.get('llm.input_messages', [])},
        'outputs': {'response': attributes.get('llm.output_messages', [])},
        'config': {'model': attributes.get('llm.model_name', '')},
        'metadata': {'provider': 'openai'}
    }
''',
                'anthropic': '''
def extract_anthropic_data(attributes):
    return {
        'inputs': {'chat_history': attributes.get('llm.input_messages', [])},
        'outputs': {'response': attributes.get('llm.output_messages', [])},
        'config': {'model': attributes.get('llm.model_name', '')},
        'metadata': {'provider': 'anthropic'}
    }
'''
            }
        }
    
    @pytest.fixture
    def mock_bundle_loader(self, mock_bundle_data):
        """Create mock bundle loader."""
        
        loader = Mock(spec=DevelopmentAwareBundleLoader)
        loader.load_provider_bundle.return_value = Mock()
        loader.load_provider_bundle.return_value.provider_signatures = mock_bundle_data['provider_signatures']
        loader.load_provider_bundle.return_value.extraction_functions = mock_bundle_data['extraction_functions']
        loader._cached_functions = {}
        
        return loader
    
    def test_openai_provider_detection(self, mock_bundle_loader):
        """Test OpenAI provider detection."""
        
        processor = UniversalProviderProcessor(mock_bundle_loader)
        
        # OpenAI attributes
        attributes = {
            'llm.input_messages': [{'role': 'user', 'content': 'Hello'}],
            'llm.output_messages': [{'role': 'assistant', 'content': 'Hi there'}],
            'llm.model_name': 'gpt-3.5-turbo'
        }
        
        provider = processor._detect_provider(attributes)
        assert provider == 'openai'
    
    def test_anthropic_provider_detection(self, mock_bundle_loader):
        """Test Anthropic provider detection."""
        
        processor = UniversalProviderProcessor(mock_bundle_loader)
        
        # Anthropic attributes
        attributes = {
            'llm.input_messages': [{'role': 'user', 'content': 'Hello'}],
            'llm.output_messages': [{'role': 'assistant', 'content': 'Hi there'}],
            'llm.usage.input_tokens': 10
        }
        
        provider = processor._detect_provider(attributes)
        assert provider == 'anthropic'
    
    def test_unknown_provider_fallback(self, mock_bundle_loader):
        """Test fallback for unknown providers."""
        
        processor = UniversalProviderProcessor(mock_bundle_loader)
        
        # Unknown provider attributes
        attributes = {
            'custom.input': 'Hello',
            'custom.output': 'Hi there',
            'custom.model': 'custom-model'
        }
        
        provider = processor._detect_provider(attributes)
        assert provider == 'unknown'
        
        # Test fallback processing
        result = processor.process_span_attributes(attributes)
        assert result['metadata']['provider'] == 'unknown'
        assert 'inputs' in result
        assert 'outputs' in result
        assert 'config' in result
        assert 'metadata' in result
```

## 📋 **Phase 2: Core Provider Implementation (Week 2)**

### **Task 2.1: OpenAI Provider (Days 8-9)**

#### **Day 8: OpenAI Provider Configuration**

**Create OpenAI Structure Patterns**:
```yaml
# config/dsl/providers/openai/structure_patterns.yaml
version: "1.0"
provider: "openai"
dsl_type: "provider_structure_patterns"

patterns:
  openinference_openai:
    signature_fields: ["llm.input_messages", "llm.output_messages", "llm.model_name"]
    optional_fields: ["llm.token_count_prompt", "llm.token_count_completion", "llm.temperature"]
    confidence_weight: 0.95
    description: "OpenAI via OpenInference instrumentation"
    
  traceloop_openai:
    signature_fields: ["gen_ai.request.model", "gen_ai.completion", "gen_ai.system"]
    optional_fields: ["gen_ai.usage.prompt_tokens", "gen_ai.usage.completion_tokens"]
    confidence_weight: 0.90
    description: "OpenAI via Traceloop instrumentation"
    
  direct_openai:
    signature_fields: ["openai.model", "openai.messages", "openai.response"]
    optional_fields: ["openai.usage", "openai.parameters"]
    confidence_weight: 0.85
    description: "Direct OpenAI SDK usage"

validation:
  minimum_signature_fields: 3
  maximum_patterns: 5
  confidence_threshold: 0.80
```

**Create OpenAI Navigation Rules**:
```yaml
# config/dsl/providers/openai/navigation_rules.yaml
version: "1.0"
provider: "openai"
dsl_type: "provider_navigation_rules"

navigation_rules:
  extract_input_messages:
    source_field: "llm.input_messages"
    extraction_method: "direct_copy"
    fallback_value: []
    validation: "array_of_objects"
    description: "Extract input message array"
    
  extract_output_messages:
    source_field: "llm.output_messages"
    extraction_method: "direct_copy"
    fallback_value: []
    validation: "array_of_objects"
    description: "Extract output message array"
    
  extract_model_name:
    source_field: "llm.model_name"
    extraction_method: "direct_copy"
    fallback_value: "unknown"
    validation: "non_empty_string"
    description: "Extract model name"
    
  extract_prompt_tokens:
    source_field: "llm.token_count_prompt"
    extraction_method: "direct_copy"
    fallback_value: 0
    validation: "positive_number"
    description: "Extract prompt token count"
    
  extract_completion_tokens:
    source_field: "llm.token_count_completion"
    extraction_method: "direct_copy"
    fallback_value: 0
    validation: "positive_number"
    description: "Extract completion token count"
    
  extract_temperature:
    source_field: "llm.temperature"
    extraction_method: "direct_copy"
    fallback_value: null
    validation: "numeric_range_0_2"
    description: "Extract temperature parameter"
    
  extract_max_tokens:
    source_field: "llm.max_tokens"
    extraction_method: "direct_copy"
    fallback_value: null
    validation: "positive_number"
    description: "Extract max tokens parameter"
```

#### **Day 9: OpenAI Field Mappings and Transforms**

**Create OpenAI Field Mappings**:
```yaml
# config/dsl/providers/openai/field_mappings.yaml
version: "1.0"
provider: "openai"
dsl_type: "provider_field_mappings"

field_mappings:
  inputs:
    chat_history:
      source_rule: "extract_input_messages"
      required: false
      description: "OpenAI input message array"
      
    prompt:
      source_rule: "extract_user_prompt"
      required: false
      description: "User prompt from first user message"
      
    system_message:
      source_rule: "extract_system_message"
      required: false
      description: "System message content"
  
  outputs:
    response:
      source_rule: "extract_output_messages"
      required: false
      description: "OpenAI response message array"
      
    completion:
      source_rule: "extract_completion_text"
      required: false
      description: "Assistant message content"
      
    tool_calls:
      source_rule: "extract_tool_calls"
      required: false
      description: "Function calls made by model"
      
    finish_reason:
      source_rule: "extract_finish_reason"
      required: false
      description: "Completion finish reason"
  
  config:
    model:
      source_rule: "extract_model_name"
      required: true
      description: "OpenAI model name"
      
    temperature:
      source_rule: "extract_temperature"
      required: false
      description: "Model temperature parameter"
      
    max_tokens:
      source_rule: "extract_max_tokens"
      required: false
      description: "Maximum token limit"
      
    top_p:
      source_rule: "extract_top_p"
      required: false
      description: "Top-p sampling parameter"
  
  metadata:
    provider:
      source_rule: "static_openai"
      required: true
      description: "Provider identifier"
      
    prompt_tokens:
      source_rule: "extract_prompt_tokens"
      required: false
      description: "Input token count"
      
    completion_tokens:
      source_rule: "extract_completion_tokens"
      required: false
      description: "Output token count"
      
    total_tokens:
      source_rule: "calculate_total_tokens"
      required: false
      description: "Total token usage"
      
    instrumentor:
      source_rule: "detect_instrumentor"
      required: false
      description: "OpenInference, Traceloop, or direct"
```

**Create OpenAI Transforms**:
```yaml
# config/dsl/providers/openai/transforms.yaml
version: "1.0"
provider: "openai"
dsl_type: "provider_transforms"

transforms:
  extract_user_prompt:
    function_type: "string_extraction"
    implementation: "extract_user_message_content"
    parameters:
      role_filter: "user"
      content_field: "content"
      join_multiple: true
      separator: "\n\n"
    description: "Extract user prompt from OpenAI messages"
    
  extract_completion_text:
    function_type: "string_extraction"
    implementation: "extract_assistant_message_content"
    parameters:
      role_filter: "assistant"
      content_field: "content"
      join_multiple: true
      separator: "\n"
    description: "Extract completion text from OpenAI response"
    
  extract_system_message:
    function_type: "string_extraction"
    implementation: "extract_system_message_content"
    parameters:
      role_filter: "system"
      content_field: "content"
      join_multiple: false
    description: "Extract system message from OpenAI messages"
    
  calculate_total_tokens:
    function_type: "numeric_calculation"
    implementation: "sum_fields"
    parameters:
      source_fields: ["prompt_tokens", "completion_tokens"]
      fallback_value: 0
    description: "Calculate total OpenAI token usage"
    
  extract_tool_calls:
    function_type: "array_transformation"
    implementation: "extract_field_values"
    parameters:
      source_array: "tool_calls"
      extract_field: "function"
      preserve_structure: true
    description: "Extract tool call information"
    
  detect_instrumentor:
    function_type: "string_extraction"
    implementation: "detect_instrumentor_framework"
    parameters:
      attribute_patterns: {
        "openinference": ["llm.input_messages", "llm.output_messages"],
        "traceloop": ["gen_ai.request.model", "gen_ai.completion"],
        "direct": ["openai.model", "openai.messages"]
      }
    description: "Detect which instrumentor framework is being used"
```

### **Task 2.2: Anthropic Provider (Days 10-11)**

#### **Day 10: Anthropic Provider Configuration**

**Create Anthropic Structure Patterns**:
```yaml
# config/dsl/providers/anthropic/structure_patterns.yaml
version: "1.0"
provider: "anthropic"
dsl_type: "provider_structure_patterns"

patterns:
  anthropic_claude:
    signature_fields: ["llm.input_messages", "llm.output_messages", "llm.model_name"]
    optional_fields: ["llm.usage.input_tokens", "llm.usage.output_tokens", "llm.stop_reason"]
    confidence_weight: 0.95
    description: "Anthropic Claude via OpenInference"
    
  anthropic_direct:
    signature_fields: ["anthropic.model", "anthropic.messages", "anthropic.content"]
    optional_fields: ["anthropic.usage", "anthropic.stop_reason"]
    confidence_weight: 0.90
    description: "Direct Anthropic SDK usage"
    
  anthropic_traceloop:
    signature_fields: ["gen_ai.request.model", "gen_ai.completion", "gen_ai.usage.input_tokens"]
    optional_fields: ["gen_ai.usage.output_tokens", "gen_ai.stop_reason"]
    confidence_weight: 0.85
    description: "Anthropic via Traceloop instrumentation"

validation:
  minimum_signature_fields: 3
  maximum_patterns: 5
  confidence_threshold: 0.80
```

#### **Day 11: Anthropic Field Mappings and Transforms**

**Create Anthropic Field Mappings and Transforms** (similar structure to OpenAI but with Anthropic-specific field names and token usage patterns).

### **Task 2.3: Gemini Provider and Testing (Days 12-14)**

#### **Day 12: Gemini Provider Configuration**

**Create Gemini Provider Files** (following the same 4-file structure).

#### **Day 13-14: Provider Detection Testing**

**Create Comprehensive Provider Tests**:
```python
# tests/test_provider_detection.py
"""
Comprehensive provider detection testing for all implemented providers.
"""

import pytest
from src.honeyhive.tracer.processing.semantic_conventions.provider_processor import UniversalProviderProcessor

class TestProviderDetection:
    """Test provider detection across all implemented providers."""
    
    @pytest.mark.parametrize("provider,attributes", [
        ("openai", {
            "llm.input_messages": [{"role": "user", "content": "Hello"}],
            "llm.output_messages": [{"role": "assistant", "content": "Hi"}],
            "llm.model_name": "gpt-3.5-turbo"
        }),
        ("anthropic", {
            "llm.input_messages": [{"role": "user", "content": "Hello"}],
            "llm.output_messages": [{"role": "assistant", "content": "Hi"}],
            "llm.usage.input_tokens": 10
        }),
        ("gemini", {
            "llm.input_messages": [{"role": "user", "content": "Hello"}],
            "llm.output_messages": [{"role": "assistant", "content": "Hi"}],
            "llm.usage.prompt_token_count": 10
        })
    ])
    def test_provider_detection(self, provider, attributes, universal_processor):
        """Test provider detection for each implemented provider."""
        
        detected_provider = universal_processor._detect_provider(attributes)
        assert detected_provider == provider
    
    def test_provider_processing_performance(self, universal_processor):
        """Test that provider processing meets performance requirements."""
        
        import time
        
        attributes = {
            "llm.input_messages": [{"role": "user", "content": "Hello"}],
            "llm.output_messages": [{"role": "assistant", "content": "Hi"}],
            "llm.model_name": "gpt-3.5-turbo"
        }
        
        # Test processing time
        start_time = time.perf_counter()
        result = universal_processor.process_span_attributes(attributes)
        end_time = time.perf_counter()
        
        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Assert processing time is under 0.1ms
        assert processing_time < 0.1, f"Processing took {processing_time}ms, expected <0.1ms"
        
        # Assert result structure
        assert 'inputs' in result
        assert 'outputs' in result
        assert 'config' in result
        assert 'metadata' in result
        assert result['metadata']['provider'] == 'openai'
```

## 📋 **Phase 3: Extended Provider Support (Week 3)**

### **Task 3.1: Additional Providers (Days 15-18)**

Implement the remaining providers following the same 4-file structure:
- **Cohere** (Days 15-16)
- **AWS Bedrock** (Days 15-16)
- **Mistral AI** (Days 17-18)
- **NVIDIA NeMo** (Days 17-18)
- **IBM watsonx** (Days 17-18)
- **Groq** (Days 17-18)
- **Ollama** (Days 17-18)

### **Task 3.2: Integration Testing and Performance Optimization (Days 19-21)**

#### **Day 19: Integration Testing**

**Create End-to-End Integration Tests**:
```python
# tests/test_integration.py
"""
End-to-end integration tests for Universal LLM Discovery Engine v4.0
"""

import pytest
from src.honeyhive.tracer.processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor

class TestIntegration:
    """End-to-end integration tests."""
    
    def test_full_span_processing_pipeline(self):
        """Test complete span processing pipeline."""
        
        processor = UniversalSemanticConventionProcessor()
        
        # Mock span data
        span_data = {
            'span_id': 'test-span-123',
            'trace_id': 'test-trace-456',
            'attributes': {
                'llm.input_messages': [{'role': 'user', 'content': 'Hello'}],
                'llm.output_messages': [{'role': 'assistant', 'content': 'Hi there'}],
                'llm.model_name': 'gpt-3.5-turbo',
                'llm.token_count_prompt': 5,
                'llm.token_count_completion': 10
            }
        }
        
        # Process span
        result = processor.process_span(span_data)
        
        # Verify HoneyHive schema structure
        assert 'inputs' in result
        assert 'outputs' in result
        assert 'config' in result
        assert 'metadata' in result
        
        # Verify data extraction
        assert result['inputs']['chat_history'] == [{'role': 'user', 'content': 'Hello'}]
        assert result['outputs']['response'] == [{'role': 'assistant', 'content': 'Hi there'}]
        assert result['config']['model'] == 'gpt-3.5-turbo'
        assert result['metadata']['provider'] == 'openai'
        assert result['metadata']['prompt_tokens'] == 5
        assert result['metadata']['completion_tokens'] == 10
```

#### **Day 20-21: Performance Optimization**

**Create Performance Benchmarks**:
```python
# tests/test_performance.py
"""
Performance benchmarks for Universal LLM Discovery Engine v4.0
"""

import pytest
import time
import memory_profiler
from src.honeyhive.tracer.processing.semantic_conventions.universal_processor import UniversalSemanticConventionProcessor

class TestPerformance:
    """Performance benchmarks and optimization tests."""
    
    def test_processing_latency_benchmark(self):
        """Benchmark processing latency across all providers."""
        
        processor = UniversalSemanticConventionProcessor()
        
        test_cases = [
            ("openai", {"llm.input_messages": [], "llm.output_messages": [], "llm.model_name": "gpt-3.5"}),
            ("anthropic", {"llm.input_messages": [], "llm.output_messages": [], "llm.usage.input_tokens": 10}),
            ("gemini", {"llm.input_messages": [], "llm.output_messages": [], "llm.usage.prompt_token_count": 10})
        ]
        
        for provider, attributes in test_cases:
            span_data = {'attributes': attributes}
            
            # Warm up
            for _ in range(10):
                processor.process_span(span_data)
            
            # Benchmark
            times = []
            for _ in range(1000):
                start = time.perf_counter()
                processor.process_span(span_data)
                end = time.perf_counter()
                times.append((end - start) * 1000)  # Convert to ms
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            print(f"{provider}: avg={avg_time:.3f}ms, max={max_time:.3f}ms")
            
            # Assert performance requirements
            assert avg_time < 0.1, f"{provider} avg processing time {avg_time}ms exceeds 0.1ms limit"
            assert max_time < 0.5, f"{provider} max processing time {max_time}ms exceeds 0.5ms limit"
    
    @memory_profiler.profile
    def test_memory_usage_benchmark(self):
        """Benchmark memory usage."""
        
        processor = UniversalSemanticConventionProcessor()
        
        # Process many spans to test memory growth
        for i in range(10000):
            span_data = {
                'attributes': {
                    'llm.input_messages': [{'role': 'user', 'content': f'Message {i}'}],
                    'llm.output_messages': [{'role': 'assistant', 'content': f'Response {i}'}],
                    'llm.model_name': 'gpt-3.5-turbo'
                }
            }
            processor.process_span(span_data)
        
        # Memory usage should remain stable (no memory leaks)
```

## 📋 **Phase 4: Production Deployment (Week 4)**

### **Task 4.1: CI/CD Integration (Days 22-23)**

#### **Day 22: GitHub Actions Integration**

**Create Build Workflow**:
```yaml
# .github/workflows/build-universal-engine.yml
name: Build Universal LLM Discovery Engine

on:
  push:
    paths:
      - 'config/dsl/providers/**'
      - 'config/dsl/shared/**'
      - 'scripts/compile_providers.py'
      - 'src/honeyhive/tracer/processing/semantic_conventions/**'
  pull_request:
    paths:
      - 'config/dsl/providers/**'
      - 'config/dsl/shared/**'
      - 'scripts/compile_providers.py'
      - 'src/honeyhive/tracer/processing/semantic_conventions/**'

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
          
      - name: Compile provider bundle
        run: |
          python scripts/compile_providers.py
          
      - name: Validate bundle
        run: |
          python scripts/validate_bundle.py
          
      - name: Run provider detection tests
        run: |
          python -m pytest tests/test_provider_detection.py -v
          
      - name: Run integration tests
        run: |
          python -m pytest tests/test_integration.py -v
          
      - name: Run performance benchmarks
        run: |
          python -m pytest tests/test_performance.py -v
          
      - name: Upload bundle artifact
        uses: actions/upload-artifact@v3
        with:
          name: compiled-provider-bundle-${{ matrix.python-version }}
          path: |
            src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl
            src/honeyhive/tracer/processing/semantic_conventions/bundle_metadata.json
  
  deploy:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Download bundle artifact
        uses: actions/download-artifact@v3
        with:
          name: compiled-provider-bundle-3.11
          path: src/honeyhive/tracer/processing/semantic_conventions/
          
      - name: Commit compiled bundle
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl
          git add src/honeyhive/tracer/processing/semantic_conventions/bundle_metadata.json
          git commit -m "Auto-compile provider bundle [skip ci]" || exit 0
          git push
```

#### **Day 23: Automated Testing and Validation**

**Create Comprehensive Test Suite**:
```python
# tests/test_comprehensive.py
"""
Comprehensive test suite covering all aspects of Universal LLM Discovery Engine v4.0
"""

import pytest
import json
from pathlib import Path

class TestComprehensive:
    """Comprehensive test coverage."""
    
    def test_all_providers_have_required_files(self):
        """Test that all providers have the required 4 files."""
        
        providers_dir = Path("config/dsl/providers")
        
        for provider_dir in providers_dir.iterdir():
            if provider_dir.is_dir():
                required_files = [
                    "structure_patterns.yaml",
                    "navigation_rules.yaml", 
                    "field_mappings.yaml",
                    "transforms.yaml"
                ]
                
                for required_file in required_files:
                    file_path = provider_dir / required_file
                    assert file_path.exists(), f"Missing {required_file} for provider {provider_dir.name}"
    
    def test_bundle_compilation_deterministic(self):
        """Test that bundle compilation is deterministic."""
        
        # Compile bundle twice
        import subprocess
        import sys
        
        compile_script = Path("scripts/compile_providers.py")
        
        # First compilation
        subprocess.run([sys.executable, str(compile_script)], check=True)
        bundle_path = Path("src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl")
        first_content = bundle_path.read_bytes()
        
        # Second compilation
        subprocess.run([sys.executable, str(compile_script)], check=True)
        second_content = bundle_path.read_bytes()
        
        # Should be identical
        assert first_content == second_content, "Bundle compilation is not deterministic"
    
    def test_all_documented_providers_implemented(self):
        """Test that all documented providers are implemented."""
        
        documented_providers = [
            "openai", "anthropic", "gemini", "cohere", "aws_bedrock",
            "mistral", "nvidia", "ibm", "groq", "ollama"
        ]
        
        providers_dir = Path("config/dsl/providers")
        implemented_providers = [d.name for d in providers_dir.iterdir() if d.is_dir()]
        
        for provider in documented_providers:
            assert provider in implemented_providers, f"Provider {provider} not implemented"
```

### **Task 4.2: Production Deployment (Days 24-25)**

#### **Day 24: Production Bundle Generation**

**Create Production Build Script**:
```python
# scripts/build_production.py
"""
Production build script for Universal LLM Discovery Engine v4.0
"""

import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_production_bundle():
    """Build production-ready bundle with optimizations."""
    
    logger.info("Starting production build...")
    
    # Step 1: Validate all provider files
    logger.info("Validating provider configurations...")
    validate_result = subprocess.run([
        sys.executable, "scripts/validate_providers.py"
    ], capture_output=True, text=True)
    
    if validate_result.returncode != 0:
        logger.error(f"Provider validation failed: {validate_result.stderr}")
        return False
    
    # Step 2: Compile bundle with production optimizations
    logger.info("Compiling provider bundle...")
    compile_result = subprocess.run([
        sys.executable, "scripts/compile_providers.py",
        "--production",
        "--optimize-size",
        "--validate-performance"
    ], capture_output=True, text=True)
    
    if compile_result.returncode != 0:
        logger.error(f"Bundle compilation failed: {compile_result.stderr}")
        return False
    
    # Step 3: Run performance benchmarks
    logger.info("Running performance benchmarks...")
    benchmark_result = subprocess.run([
        sys.executable, "-m", "pytest", "tests/test_performance.py", "-v"
    ], capture_output=True, text=True)
    
    if benchmark_result.returncode != 0:
        logger.error(f"Performance benchmarks failed: {benchmark_result.stderr}")
        return False
    
    # Step 4: Generate production metadata
    logger.info("Generating production metadata...")
    generate_production_metadata()
    
    logger.info("Production build completed successfully!")
    return True

def generate_production_metadata():
    """Generate metadata for production deployment."""
    
    bundle_path = Path("src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl")
    metadata_path = Path("src/honeyhive/tracer/processing/semantic_conventions/bundle_metadata.json")
    
    import json
    import hashlib
    import time
    
    # Calculate bundle hash
    with open(bundle_path, 'rb') as f:
        bundle_hash = hashlib.sha256(f.read()).hexdigest()
    
    # Generate metadata
    metadata = {
        "version": "4.0",
        "build_timestamp": int(time.time()),
        "bundle_hash": bundle_hash,
        "bundle_size": bundle_path.stat().st_size,
        "environment": "production",
        "optimization_level": "maximum"
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    success = build_production_bundle()
    sys.exit(0 if success else 1)
```

#### **Day 25: Deployment and Monitoring**

**Create Deployment Monitoring**:
```python
# src/honeyhive/tracer/processing/semantic_conventions/monitoring.py
"""
Monitoring and observability for Universal LLM Discovery Engine v4.0
"""

import logging
import time
import threading
from typing import Dict, Any, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class UniversalEngineMonitor:
    """Monitor performance and health of Universal LLM Discovery Engine."""
    
    def __init__(self, max_metrics_history: int = 1000):
        self.max_metrics_history = max_metrics_history
        self.metrics = defaultdict(deque)
        self.counters = defaultdict(int)
        self.lock = threading.Lock()
        
    def record_processing_time(self, provider: str, processing_time_ms: float):
        """Record processing time for a provider."""
        
        with self.lock:
            self.metrics[f"{provider}_processing_time"].append(processing_time_ms)
            if len(self.metrics[f"{provider}_processing_time"]) > self.max_metrics_history:
                self.metrics[f"{provider}_processing_time"].popleft()
    
    def record_provider_detection(self, provider: str):
        """Record provider detection event."""
        
        with self.lock:
            self.counters[f"{provider}_detections"] += 1
    
    def record_fallback_usage(self):
        """Record fallback processing usage."""
        
        with self.lock:
            self.counters["fallback_usage"] += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        
        with self.lock:
            summary = {}
            
            # Processing time statistics
            for metric_name, values in self.metrics.items():
                if "_processing_time" in metric_name:
                    if values:
                        summary[metric_name] = {
                            "avg": sum(values) / len(values),
                            "min": min(values),
                            "max": max(values),
                            "count": len(values)
                        }
            
            # Detection counters
            summary["detection_counts"] = dict(self.counters)
            
            return summary
    
    def check_performance_health(self) -> Dict[str, Any]:
        """Check if performance is within acceptable bounds."""
        
        health_status = {"healthy": True, "issues": []}
        summary = self.get_performance_summary()
        
        # Check processing times
        for metric_name, stats in summary.items():
            if "_processing_time" in metric_name and isinstance(stats, dict):
                if stats["avg"] > 0.1:  # 0.1ms threshold
                    health_status["healthy"] = False
                    health_status["issues"].append(f"{metric_name} average {stats['avg']:.3f}ms exceeds 0.1ms threshold")
                
                if stats["max"] > 1.0:  # 1.0ms max threshold
                    health_status["healthy"] = False
                    health_status["issues"].append(f"{metric_name} max {stats['max']:.3f}ms exceeds 1.0ms threshold")
        
        # Check fallback usage
        fallback_count = summary.get("detection_counts", {}).get("fallback_usage", 0)
        total_detections = sum(v for k, v in summary.get("detection_counts", {}).items() if k.endswith("_detections"))
        
        if total_detections > 0:
            fallback_rate = fallback_count / (total_detections + fallback_count)
            if fallback_rate > 0.05:  # 5% fallback threshold
                health_status["healthy"] = False
                health_status["issues"].append(f"Fallback usage rate {fallback_rate:.1%} exceeds 5% threshold")
        
        return health_status
```

### **Task 4.3: Documentation and Handoff (Days 26-28)**

#### **Day 26-27: Documentation**

**Create Operations Guide**:
```markdown
# Universal LLM Discovery Engine v4.0 - Operations Guide

## Production Deployment

### Bundle Compilation
```bash
# Compile production bundle
python scripts/build_production.py

# Validate bundle
python scripts/validate_bundle.py

# Run performance tests
python -m pytest tests/test_performance.py
```

### Monitoring

Monitor the following metrics:
- Processing time per provider (target: <0.1ms average)
- Provider detection accuracy (target: >99%)
- Fallback usage rate (target: <5%)
- Memory usage (target: <30KB per tracer)

### Troubleshooting

Common issues and solutions:
1. **High processing times**: Check bundle compilation, ensure production mode
2. **High fallback usage**: Review provider signatures, add missing patterns
3. **Memory growth**: Check for caching issues, validate bundle loading
```

#### **Day 28: Training and Handoff**

**Create Training Materials** and conduct handoff sessions covering:
- Architecture overview and design decisions
- Provider configuration and extension process
- Build system and deployment procedures
- Monitoring and troubleshooting
- Performance optimization techniques

## ✅ **Implementation Success Criteria**

### **Technical Requirements**
- [ ] All operations provably O(1) with performance monitoring
- [ ] Zero provider-specific logic in processing code
- [ ] Complete provider isolation with parallel AI development capability
- [ ] >99% mapping accuracy across all 11+ documented providers
- [ ] <0.1ms processing time per span (average)
- [ ] <30KB memory usage per tracer instance

### **Architectural Requirements**
- [ ] Provider-per-file isolation with focused 1-2KB files
- [ ] Build-time compilation to optimized Python structures
- [ ] Development-aware loading with automatic recompilation
- [ ] Comprehensive error handling and fallback strategies
- [ ] Full backward compatibility with existing HoneyHive SDK

### **Operational Requirements**
- [ ] Seamless integration with existing HoneyHive tracer
- [ ] Self-contained operation in customer applications
- [ ] AI-optimized development workflows with parallel capability
- [ ] Zero-downtime deployment with automated CI/CD
- [ ] Production monitoring and health checking

### **Performance Guarantees**
- [ ] Bundle loading: <3ms (one-time per tracer instance)
- [ ] Provider detection: <0.01ms (O(1) frozenset operations)
- [ ] Field extraction: <0.05ms (compiled native functions)
- [ ] Total processing: <0.1ms per span (all operations combined)
- [ ] Memory footprint: <30KB (compressed structures)

---

**This implementation plan provides a complete 4-week roadmap for building the Universal LLM Discovery Engine v4.0 with provider-isolated architecture, build-time compilation, and production-ready deployment capabilities.**
