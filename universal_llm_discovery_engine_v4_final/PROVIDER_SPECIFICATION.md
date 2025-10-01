# Universal LLM Discovery Engine v4.0 - Provider Specification

**Version**: 4.0 Final  
**Date**: 2025-01-27  
**Status**: Implementation Ready  
**Focus**: Provider-Per-File DSL Specification and Build System

---

## 🎯 **Provider-Per-File DSL Architecture**

The v4.0 architecture uses **provider isolation** as the primary organizational principle. Each provider gets its own directory with exactly 4 focused YAML files, enabling parallel AI assistant development and zero cross-provider contamination.

### **Provider Directory Structure Template**

```
config/dsl/providers/{provider_name}/
├── structure_patterns.yaml      # Provider signature detection
├── navigation_rules.yaml        # Field extraction paths  
├── field_mappings.yaml          # HoneyHive schema mapping
└── transforms.yaml              # Data transformation functions
```

## 📋 **DSL File Specifications**

### **1. Structure Patterns (Provider Signature Detection)**

**Purpose**: Define unique field combinations that identify this provider's data structures.

```yaml
# config/dsl/providers/{provider}/structure_patterns.yaml
version: "1.0"
provider: "{provider_name}"
dsl_type: "provider_structure_patterns"

# Provider signature patterns for O(1) detection
patterns:
  # Primary pattern - highest confidence
  primary_pattern:
    signature_fields: ["field1", "field2", "field3"]    # Required fields for detection
    optional_fields: ["optional1", "optional2"]         # Optional fields that may be present
    confidence_weight: 0.95                              # Detection confidence (0.0-1.0)
    description: "Primary detection pattern for {provider}"
    
  # Secondary pattern - fallback detection
  secondary_pattern:
    signature_fields: ["alt_field1", "alt_field2"]
    optional_fields: ["alt_optional1"]
    confidence_weight: 0.85
    description: "Secondary detection pattern for {provider}"

# Validation rules for pattern integrity
validation:
  minimum_signature_fields: 2      # Minimum fields required for reliable detection
  maximum_patterns: 5              # Maximum patterns per provider
  confidence_threshold: 0.80       # Minimum confidence for pattern acceptance
```

**Example - OpenAI Structure Patterns**:
```yaml
version: "1.0"
provider: "openai"
dsl_type: "provider_structure_patterns"

patterns:
  openai_chat_completion:
    signature_fields: ["llm.input_messages", "llm.output_messages", "llm.model_name"]
    optional_fields: ["llm.token_count_prompt", "llm.token_count_completion", "llm.temperature"]
    confidence_weight: 0.95
    description: "OpenAI chat completion via OpenInference"
    
  openai_traceloop:
    signature_fields: ["gen_ai.request.model", "gen_ai.completion", "gen_ai.system"]
    optional_fields: ["gen_ai.usage.prompt_tokens", "gen_ai.usage.completion_tokens"]
    confidence_weight: 0.90
    description: "OpenAI via Traceloop instrumentation"
```

### **2. Navigation Rules (Field Extraction Paths)**

**Purpose**: Define how to extract data from detected provider structures.

```yaml
# config/dsl/providers/{provider}/navigation_rules.yaml
version: "1.0"
provider: "{provider_name}"
dsl_type: "provider_navigation_rules"

# Field extraction rules
navigation_rules:
  # Direct field extraction
  extract_field_name:
    source_field: "source.field.path"           # Source field path
    extraction_method: "direct_copy"            # Extraction method
    fallback_value: null                        # Value if field missing
    validation: "non_empty_string"              # Optional validation
    description: "Extract field description"
    
  # Complex extraction with transformation
  extract_complex_field:
    source_field: "nested.field.array[*].content"
    extraction_method: "array_flatten"
    fallback_value: []
    transform: "join_with_newlines"
    validation: "array_of_strings"
    description: "Extract and flatten nested array content"

# Available extraction methods
extraction_methods:
  direct_copy: "Copy field value directly"
  array_flatten: "Flatten nested arrays"
  object_merge: "Merge multiple objects"
  string_concat: "Concatenate string values"
  numeric_sum: "Sum numeric values"
  first_non_null: "Return first non-null value from array"

# Available validation rules
validation_rules:
  non_empty_string: "Ensure string is not empty"
  positive_number: "Ensure number is positive"
  array_of_strings: "Ensure array contains only strings"
  valid_json: "Ensure valid JSON structure"
  non_null: "Ensure value is not null"
```

**Example - OpenAI Navigation Rules**:
```yaml
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
    
  extract_model_name:
    source_field: "llm.model_name"
    extraction_method: "direct_copy"
    fallback_value: "unknown"
    validation: "non_empty_string"
    description: "Extract model name"
    
  extract_completion_text:
    source_field: "llm.output_messages[*].content"
    extraction_method: "array_flatten"
    fallback_value: ""
    transform: "join_with_newlines"
    validation: "non_empty_string"
    description: "Extract and join completion text from messages"
    
  extract_token_usage:
    source_field: ["llm.token_count_prompt", "llm.token_count_completion"]
    extraction_method: "object_merge"
    fallback_value: {"prompt_tokens": 0, "completion_tokens": 0}
    validation: "numeric_object"
    description: "Merge token usage metrics"
```

### **3. Field Mappings (HoneyHive Schema Mapping)**

**Purpose**: Map extracted provider data to HoneyHive's 4-section schema.

```yaml
# config/dsl/providers/{provider}/field_mappings.yaml
version: "1.0"
provider: "{provider_name}"
dsl_type: "provider_field_mappings"

# HoneyHive schema mapping
field_mappings:
  # inputs: User inputs, chat history, prompts, context
  inputs:
    chat_history:
      source_rule: "extract_input_messages"     # Reference to navigation rule
      required: false
      description: "User conversation history"
      
    prompt:
      source_rule: "extract_user_prompt"
      required: false
      description: "User prompt text"
      
    context:
      source_rule: "extract_context_data"
      required: false
      description: "Additional context information"
  
  # outputs: Model responses, completions, tool calls, results  
  outputs:
    response:
      source_rule: "extract_output_messages"
      required: false
      description: "Model response messages"
      
    completion:
      source_rule: "extract_completion_text"
      required: false
      description: "Completion text content"
      
    tool_calls:
      source_rule: "extract_tool_calls"
      required: false
      description: "Function/tool call results"
  
  # config: Model parameters, temperature, max tokens, system prompts
  config:
    model:
      source_rule: "extract_model_name"
      required: true
      description: "Model identifier"
      
    temperature:
      source_rule: "extract_temperature"
      required: false
      description: "Model temperature setting"
      
    max_tokens:
      source_rule: "extract_max_tokens"
      required: false
      description: "Maximum token limit"
  
  # metadata: Usage metrics, timestamps, provider info, performance data
  metadata:
    provider:
      source_rule: "static_provider_name"       # Static value
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
      
    instrumentor:
      source_rule: "detect_instrumentor"        # Dynamic detection
      required: false
      description: "Instrumentor framework used"

# Schema validation rules
schema_validation:
  inputs:
    allow_empty: true
    max_fields: 20
    
  outputs:
    allow_empty: true
    max_fields: 20
    
  config:
    require_model: true
    allow_empty: false
    
  metadata:
    require_provider: true
    allow_empty: false
```

**Example - OpenAI Field Mappings**:
```yaml
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

### **4. Transforms (Data Transformation Functions)**

**Purpose**: Define reusable transformation functions for data processing.

```yaml
# config/dsl/providers/{provider}/transforms.yaml
version: "1.0"
provider: "{provider_name}"
dsl_type: "provider_transforms"

# Transformation function definitions
transforms:
  # String transformation functions
  extract_user_prompt:
    function_type: "string_extraction"
    implementation: "extract_user_message_content"
    parameters:
      role_filter: "user"
      content_field: "content"
      join_multiple: true
      separator: "\n\n"
    description: "Extract user prompt from message array"
    
  # Array transformation functions
  flatten_message_content:
    function_type: "array_transformation"
    implementation: "flatten_and_join"
    parameters:
      content_field: "content"
      separator: "\n"
      filter_empty: true
    description: "Flatten message content into single string"
    
  # Numeric transformation functions
  calculate_total_tokens:
    function_type: "numeric_calculation"
    implementation: "sum_fields"
    parameters:
      source_fields: ["prompt_tokens", "completion_tokens"]
      fallback_value: 0
    description: "Calculate total token usage"
    
  # Object transformation functions
  merge_usage_metrics:
    function_type: "object_transformation"
    implementation: "merge_objects"
    parameters:
      source_objects: ["token_usage", "timing_metrics"]
      conflict_resolution: "prefer_first"
    description: "Merge usage and timing metrics"

# Available function types and implementations
function_registry:
  string_extraction:
    - extract_user_message_content
    - extract_assistant_message_content
    - extract_system_message_content
    - extract_first_non_empty
    
  array_transformation:
    - flatten_and_join
    - filter_by_role
    - extract_field_values
    - deduplicate_array
    
  numeric_calculation:
    - sum_fields
    - average_fields
    - max_fields
    - min_fields
    
  object_transformation:
    - merge_objects
    - filter_object_fields
    - rename_object_keys
    - flatten_nested_object

# Transform validation rules
validation:
  max_transforms_per_provider: 20
  required_parameters: ["function_type", "implementation"]
  allowed_function_types: ["string_extraction", "array_transformation", "numeric_calculation", "object_transformation"]
```

**Example - OpenAI Transforms**:
```yaml
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

## 🏗️ **Build System Specification**

### **Compilation Process**

The build system compiles all provider YAML files into optimized Python structures for runtime performance.

```python
# scripts/compile_providers.py
"""
Provider Bundle Compilation System

Compiles provider YAML files to optimized Python structures:
1. Load and validate all provider YAML files
2. Compile to hash-based data structures for O(1) operations
3. Generate compiled extraction functions
4. Serialize to compressed bundle for runtime loading
"""

import yaml
import pickle
import hashlib
from pathlib import Path
from typing import Dict, Any, Set, FrozenSet
from dataclasses import dataclass

@dataclass
class ProviderBundle:
    """Compiled provider bundle structure."""
    provider_signatures: Dict[str, FrozenSet[str]]
    extraction_functions: Dict[str, callable]
    field_mappings: Dict[str, Dict[str, Any]]
    transform_registry: Dict[str, callable]
    validation_rules: Dict[str, Any]
    build_metadata: Dict[str, Any]

class ProviderCompiler:
    """Compile provider YAML files to optimized bundle."""
    
    def __init__(self, source_dir: Path, output_dir: Path):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.providers = {}
        
    def compile_all_providers(self) -> ProviderBundle:
        """Main compilation entry point."""
        
        # Step 1: Load and validate all provider files
        self.load_all_providers()
        
        # Step 2: Compile to optimized structures
        provider_signatures = self.compile_provider_signatures()
        extraction_functions = self.compile_extraction_functions()
        field_mappings = self.compile_field_mappings()
        transform_registry = self.compile_transform_registry()
        validation_rules = self.compile_validation_rules()
        
        # Step 3: Create bundle with metadata
        bundle = ProviderBundle(
            provider_signatures=provider_signatures,
            extraction_functions=extraction_functions,
            field_mappings=field_mappings,
            transform_registry=transform_registry,
            validation_rules=validation_rules,
            build_metadata=self.generate_build_metadata()
        )
        
        # Step 4: Validate and save bundle
        self.validate_bundle(bundle)
        self.save_bundle(bundle)
        
        return bundle
    
    def compile_provider_signatures(self) -> Dict[str, FrozenSet[str]]:
        """Compile provider signatures for O(1) detection."""
        signatures = {}
        
        for provider_name, provider_data in self.providers.items():
            patterns = provider_data['structure_patterns']['patterns']
            
            # Create frozenset for each pattern
            provider_signatures = []
            for pattern_name, pattern_data in patterns.items():
                signature_fields = frozenset(pattern_data['signature_fields'])
                provider_signatures.append(signature_fields)
            
            # Store all signatures for this provider
            signatures[provider_name] = provider_signatures
            
        return signatures
    
    def compile_extraction_functions(self) -> Dict[str, callable]:
        """Compile extraction functions for each provider."""
        functions = {}
        
        for provider_name, provider_data in self.providers.items():
            # Generate compiled extraction function
            function_code = self.generate_extraction_function(provider_name, provider_data)
            
            # Compile to callable function
            compiled_function = self.compile_function_code(function_code)
            functions[provider_name] = compiled_function
            
        return functions
    
    def generate_extraction_function(self, provider_name: str, provider_data: Dict) -> str:
        """Generate Python code for provider extraction function."""
        
        navigation_rules = provider_data['navigation_rules']['navigation_rules']
        field_mappings = provider_data['field_mappings']['field_mappings']
        transforms = provider_data['transforms']['transforms']
        
        # Generate function code
        function_lines = [
            f"def extract_{provider_name}_data(attributes):",
            f'    """Compiled extraction function for {provider_name} provider."""',
            f"    ",
        ]
        
        # Generate extraction code for each schema section
        for section_name, section_mappings in field_mappings.items():
            function_lines.append(f"    # {section_name.upper()} section")
            function_lines.append(f"    {section_name} = {{}}")
            
            for field_name, field_config in section_mappings.items():
                source_rule = field_config['source_rule']
                extraction_code = self.generate_field_extraction_code(
                    field_name, source_rule, navigation_rules, transforms
                )
                function_lines.append(f"    {section_name}['{field_name}'] = {extraction_code}")
            
            function_lines.append("")
        
        # Generate return statement
        function_lines.extend([
            "    return {",
            "        'inputs': inputs,",
            "        'outputs': outputs,",
            "        'config': config,",
            "        'metadata': metadata",
            "    }"
        ])
        
        return "\n".join(function_lines)
```

### **Bundle Loading System**

```python
# src/honeyhive/tracer/processing/semantic_conventions/bundle_loader.py
"""
Development-Aware Bundle Loading System

Automatically handles development vs production loading:
- Development: Auto-recompilation when source files change
- Production: Fast loading of pre-compiled bundle
"""

import os
import pickle
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DevelopmentAwareBundleLoader:
    """Intelligent bundle loader for development and production."""
    
    def __init__(self, bundle_path: Path, source_path: Optional[Path] = None):
        self.bundle_path = bundle_path
        self.source_path = source_path
        self.bundle_metadata_path = bundle_path.parent / "bundle_metadata.json"
        self._cached_bundle = None
        
    def load_provider_bundle(self) -> Dict[str, Any]:
        """Load bundle with development-aware recompilation."""
        
        if self.is_development_environment():
            return self._load_development_bundle()
        else:
            return self._load_production_bundle()
    
    def is_development_environment(self) -> bool:
        """Detect if running in development vs production."""
        
        development_indicators = [
            self.source_path and self.source_path.exists(),  # Source files present
            os.environ.get('HONEYHIVE_DEV_MODE') == 'true',  # Explicit dev flag
            'pytest' in sys.modules,                         # Running tests
            Path('.git').exists(),                           # Git repository
        ]
        
        return any(development_indicators)
    
    def _load_development_bundle(self) -> Dict[str, Any]:
        """Load bundle in development mode with auto-recompilation."""
        
        if self._needs_recompilation():
            logger.info("Source files updated, recompiling provider bundle...")
            self._recompile_bundle()
        
        return self._load_bundle_with_debug_info()
    
    def _load_production_bundle(self) -> Dict[str, Any]:
        """Load bundle in production mode (fast path)."""
        
        if self._cached_bundle is None:
            with open(self.bundle_path, 'rb') as f:
                self._cached_bundle = pickle.load(f)
                
        return self._cached_bundle
    
    def _needs_recompilation(self) -> bool:
        """Check if source files are newer than compiled bundle."""
        
        if not self.bundle_path.exists():
            return True
            
        if not self.source_path or not self.source_path.exists():
            return False
            
        bundle_mtime = self.bundle_path.stat().st_mtime
        
        # Check all YAML files in source directory
        for yaml_file in self.source_path.rglob("*.yaml"):
            if yaml_file.stat().st_mtime > bundle_mtime:
                return True
                
        return False
    
    def _recompile_bundle(self):
        """Recompile bundle from source files."""
        
        # Import compiler (only needed in development)
        from scripts.compile_providers import ProviderCompiler
        
        compiler = ProviderCompiler(
            source_dir=self.source_path,
            output_dir=self.bundle_path.parent
        )
        
        compiler.compile_all_providers()
        
        # Clear cached bundle to force reload
        self._cached_bundle = None
```

## 📊 **Provider Implementation Examples**

### **Complete OpenAI Provider Example**

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

### **Complete Anthropic Provider Example**

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

validation:
  minimum_signature_fields: 3
  maximum_patterns: 3
  confidence_threshold: 0.85
```

## 🔧 **Build System Commands**

### **Development Commands**

```bash
# Compile all providers
python scripts/compile_providers.py

# Compile specific provider
python scripts/compile_providers.py --provider openai

# Validate bundle
python scripts/validate_bundle.py

# Test provider detection
python scripts/test_provider_detection.py --provider openai

# Generate provider template
python scripts/generate_provider_template.py --provider new_provider
```

### **CI/CD Integration**

```yaml
# Build step in CI/CD pipeline
- name: Compile Provider Bundle
  run: |
    python scripts/compile_providers.py
    python scripts/validate_bundle.py
    
- name: Test Provider Detection
  run: |
    python -m pytest tests/test_provider_detection.py -v
    
- name: Commit Compiled Bundle
  run: |
    git add src/honeyhive/tracer/processing/semantic_conventions/compiled_providers.pkl
    git add src/honeyhive/tracer/processing/semantic_conventions/bundle_metadata.json
    git commit -m "Auto-compile provider bundle [skip ci]" || exit 0
```

## 📈 **Provider Extension Process**

### **Adding New Provider (AI Assistant Workflow)**

1. **Create Provider Directory**:
```bash
mkdir -p config/dsl/providers/new_provider
```

2. **Generate Template Files**:
```bash
python scripts/generate_provider_template.py --provider new_provider
```

3. **AI Assistant Edits 4 Files** (7KB total context):
   - `structure_patterns.yaml` - Define provider signatures
   - `navigation_rules.yaml` - Define field extraction
   - `field_mappings.yaml` - Map to HoneyHive schema
   - `transforms.yaml` - Define transformations

4. **Test and Validate**:
```bash
python scripts/test_provider_detection.py --provider new_provider
python scripts/validate_bundle.py
```

5. **Auto-Compilation**: Development environment automatically recompiles bundle

### **Provider Template Generation**

```python
# scripts/generate_provider_template.py
def generate_provider_template(provider_name: str):
    """Generate template files for new provider."""
    
    provider_dir = Path(f"config/dsl/providers/{provider_name}")
    provider_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate structure_patterns.yaml template
    structure_template = f"""version: "1.0"
provider: "{provider_name}"
dsl_type: "provider_structure_patterns"

patterns:
  {provider_name}_primary:
    signature_fields: ["field1", "field2", "field3"]
    optional_fields: ["optional1", "optional2"]
    confidence_weight: 0.95
    description: "Primary {provider_name} detection pattern"

validation:
  minimum_signature_fields: 2
  maximum_patterns: 5
  confidence_threshold: 0.80
"""
    
    # Write template files
    (provider_dir / "structure_patterns.yaml").write_text(structure_template)
    # ... generate other template files
```

## 📊 **Performance Optimization Details**

### **Compilation Optimizations**

1. **Frozenset-Based Detection**: O(1) provider detection using hash-based set operations
2. **Compiled Functions**: Native Python functions generated at build time
3. **Hash-Based Lookups**: All field mappings use dictionary lookups
4. **Compressed Serialization**: Pickle with compression for minimal bundle size

### **Runtime Performance Guarantees**

- **Provider Detection**: <0.01ms (frozenset.issubset operations)
- **Field Extraction**: <0.05ms (compiled native functions)
- **Schema Mapping**: <0.02ms (hash-based dictionary lookups)
- **Total Processing**: <0.1ms per span (all operations combined)

### **Memory Optimization**

- **Bundle Size**: ~20-30KB for 10+ providers
- **Runtime Memory**: <30KB per tracer instance
- **Caching**: Per-instance caching with automatic cleanup
- **Garbage Collection**: Minimal object creation in hot path

---

**This provider specification provides complete technical details for implementing the provider-per-file DSL architecture with build-time compilation optimization for the Universal LLM Discovery Engine v4.0.**
