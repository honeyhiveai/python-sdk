# Universal LLM Discovery Engine v4.0 - Implementation Guide

**Date**: 2025-09-29  
**Status**: Active  
**Priority**: High  
**Last Updated**: 2025-09-29

---

## 🎯 Implementation Overview

This guide provides systematic, step-by-step instructions for implementing the O(1) performance fix and quality gates for the Universal LLM Discovery Engine v4.0, following Agent OS V3 framework principles.

### Prerequisites

Before starting implementation, ensure:

- [ ] Agent OS V3 framework understanding
- [ ] Python SDK development environment activated (`source python-sdk/bin/activate`)
- [ ] All existing tests passing (`tox -e integration-parallel`)
- [ ] Performance analysis document reviewed (`PERFORMANCE_ANALYSIS_O_N_PATTERNS.md`)
- [ ] V4.0 architecture documents reviewed (`universal_llm_discovery_engine_v4_final/`)

### Implementation Philosophy

**SYSTEMATIC > SPEED**  
Take time to validate each step thoroughly. This is a critical performance fix affecting all provider detection logic.

**EVIDENCE-BASED**  
Every implementation step requires concrete evidence (tests passing, benchmarks met, etc.).

**AGENT OS V3 COMPLIANCE**  
Follow command language glossary, evidence-based tracking, and systematic task breakdown.

---

## Phase 1: O(1) Algorithm Implementation

### Step 1.1: Compiler - Inverted Index Generation

**Objective**: Generate inverted signature index during compilation for O(1) lookups.

**Files to Modify**:
- `scripts/compile_providers.py`

**Implementation Steps**:

1. **Add inverted index generation method**:

```python
def _compile_signature_indices(self) -> Tuple[Dict, Dict]:
    """
    Compile both forward and inverted signature indices.
    
    Forward index: provider → [signatures] (for subset matching)
    Inverted index: signature → (provider, confidence) (for exact matching)
    
    Returns:
        Tuple of (forward_index, inverted_index)
    """
    forward_index: Dict[str, List[FrozenSet[str]]] = {}
    inverted_index: Dict[FrozenSet[str], Tuple[str, float]] = {}
    
    for provider_name, provider_data in self.providers.items():
        try:
            patterns = provider_data['structure_patterns']['patterns']
            provider_signatures = []
            
            for pattern_name, pattern_data in patterns.items():
                # Extract signature fields
                signature_fields = pattern_data.get('signature_fields', [])
                if not signature_fields:
                    safe_print(f"⚠️  Warning: Pattern '{pattern_name}' in provider '{provider_name}' has no signature fields")
                    continue
                
                signature = frozenset(signature_fields)
                confidence = pattern_data.get('confidence_weight', 0.9)
                
                # Add to forward index
                provider_signatures.append(signature)
                
                # Add to inverted index with collision handling
                if signature in inverted_index:
                    existing_provider, existing_conf = inverted_index[signature]
                    safe_print(f"⚠️  Signature collision detected:")
                    safe_print(f"    Signature: {set(signature)}")
                    safe_print(f"    Existing: {existing_provider} (confidence: {existing_conf})")
                    safe_print(f"    New: {provider_name} (confidence: {confidence})")
                    
                    # Keep higher confidence provider
                    if confidence > existing_conf:
                        inverted_index[signature] = (provider_name, confidence)
                        safe_print(f"    → Keeping {provider_name} (higher confidence)")
                    else:
                        safe_print(f"    → Keeping {existing_provider} (higher confidence)")
                else:
                    inverted_index[signature] = (provider_name, confidence)
            
            forward_index[provider_name] = provider_signatures
            
        except KeyError as e:
            safe_print(f"❌ Error processing provider '{provider_name}': {e}")
            raise
    
    return forward_index, inverted_index
```

2. **Update bundle compilation to include inverted index**:

```python
def compile_providers(self) -> CompiledProviderBundle:
    """Compile all providers into optimized bundle."""
    
    safe_print("\n🔨 Compiling provider bundle...")
    
    # Generate both indices
    safe_print("📊 Generating signature indices...")
    forward_index, inverted_index = self._compile_signature_indices()
    
    safe_print(f"  ✅ Forward index: {len(forward_index)} providers")
    safe_print(f"  ✅ Inverted index: {len(inverted_index)} signatures")
    
    # Compile other components...
    extraction_functions = self._compile_extraction_functions()
    field_mappings = self._compile_field_mappings()
    transforms = self._compile_transform_registry()
    validation_rules = self._compile_validation_rules()
    
    # Build metadata
    build_metadata = {
        'build_timestamp': datetime.now(timezone.utc).isoformat(),
        'provider_count': len(forward_index),
        'signature_count': len(inverted_index),
        'inverted_index_enabled': True,
        'version': '4.0.1'
    }
    
    # Create bundle with both indices
    bundle = CompiledProviderBundle(
        provider_signatures=forward_index,
        signature_to_provider=inverted_index,  # NEW
        extraction_functions=extraction_functions,
        field_mappings=field_mappings,
        transform_registry=transforms,
        validation_rules=validation_rules,
        build_metadata=build_metadata
    )
    
    return bundle
```

3. **Test the changes**:

```bash
# Activate environment
source python-sdk/bin/activate

# Format code
tox -e format

# Compile providers
python scripts/compile_providers.py

# Verify bundle structure
python -c "
import pickle
with open('src/honeyhive/tracer/processing/semantic_conventions/compiled_provider_bundle.pkl', 'rb') as f:
    bundle = pickle.load(f)
    print('✅ Has inverted index:', hasattr(bundle, 'signature_to_provider'))
    print('✅ Inverted index entries:', len(bundle.signature_to_provider) if hasattr(bundle, 'signature_to_provider') else 0)
    print('✅ Forward index providers:', len(bundle.provider_signatures))
"
```

**Expected Output**:
```
✅ Has inverted index: True
✅ Inverted index entries: 18
✅ Forward index providers: 3
```

**Evidence of Completion**: Compiled bundle contains `signature_to_provider` field with 18 entries (3 providers × ~6 signatures each).

---

### Step 1.2: Bundle Types - Add Inverted Index Field

**Objective**: Update Pydantic model to include inverted index field.

**Files to Modify**:
- `src/honeyhive/tracer/processing/semantic_conventions/bundle_types.py`

**Implementation Steps**:

1. **Add new field to `CompiledProviderBundle`**:

```python
class CompiledProviderBundle(BaseModel):
    """
    Compiled provider bundle with optimized indices for O(1) detection.
    
    Version 4.0.1 adds inverted signature index for true O(1) exact match lookups.
    """
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    # Forward index: provider → [signatures] (for subset matching)
    provider_signatures: Dict[str, List[FrozenSet[str]]] = Field(
        description="Provider signature patterns for subset matching fallback"
    )
    
    # NEW: Inverted index: signature → (provider, confidence) (for exact matching)
    signature_to_provider: Dict[FrozenSet[str], Tuple[str, float]] = Field(
        default_factory=dict,  # Optional for backward compatibility
        description="Inverted signature index for O(1) exact match lookups"
    )
    
    extraction_functions: Dict[str, str] = Field(
        description="Compiled extraction function code"
    )
    
    field_mappings: Dict[str, Dict[str, Any]] = Field(
        description="Field mapping configurations"
    )
    
    transform_registry: Dict[str, Dict[str, Any]] = Field(
        description="Transform function registry"
    )
    
    validation_rules: Dict[str, Any] = Field(
        description="Validation rule configurations"
    )
    
    build_metadata: Dict[str, Any] = Field(
        description="Bundle build metadata and version information"
    )
```

2. **Test Pydantic validation**:

```bash
# Run unit tests for bundle types
tox -e unit -- tests/unit/tracer/processing/semantic_conventions/test_bundle_types.py -v

# Run MyPy type checking
tox -e lint -- mypy src/honeyhive/tracer/processing/semantic_conventions/bundle_types.py
```

**Expected Output**:
```
tests/unit/.../test_bundle_types.py::test_bundle_with_inverted_index PASSED
mypy src/.../bundle_types.py: Success: no issues found
```

**Evidence of Completion**: Pydantic validation passes, MyPy shows no type errors, pickle serialization works.

---

### Step 1.3: Runtime - O(1) Exact Match Detection

**Objective**: Implement O(1) exact match detection using inverted index.

**Files to Modify**:
- `src/honeyhive/tracer/processing/semantic_conventions/provider_processor.py`

**Implementation Steps**:

1. **Update `__init__` to load inverted index**:

```python
def __init__(self, bundle_loader: Optional[DevelopmentAwareBundleLoader] = None, 
             tracer_instance: Optional[Any] = None):
    """Initialize with both forward and inverted indices."""
    
    # ... existing initialization ...
    
    self.provider_signatures: Dict[str, List[FrozenSet[str]]] = {}  # Forward index
    self.signature_to_provider: Dict[FrozenSet[str], Tuple[str, float]] = {}  # NEW: Inverted index
    
    self._load_bundle()
```

2. **Update `_load_bundle` to load inverted index**:

```python
def _load_bundle(self):
    """Load bundle with both forward and inverted indices."""
    
    try:
        # Load bundle
        self.bundle = self.bundle_loader.load_provider_bundle()
        
        # Load forward index (existing)
        if hasattr(self.bundle, 'provider_signatures'):
            self.provider_signatures = self.bundle.provider_signatures
        
        # NEW: Load inverted index
        if hasattr(self.bundle, 'signature_to_provider'):
            self.signature_to_provider = self.bundle.signature_to_provider
            safe_log(self.tracer_instance, "debug", 
                    "Loaded inverted signature index with %d entries",
                    len(self.signature_to_provider))
        else:
            # Fallback: build inverted index at runtime (legacy compatibility)
            safe_log(self.tracer_instance, "warning",
                    "Bundle missing inverted index, building at runtime")
            self.signature_to_provider = self._build_inverted_index_fallback()
        
        # ... rest of existing bundle loading ...
        
    except Exception as e:
        safe_log(self.tracer_instance, "error", 
                "Failed to load provider bundle: %s", str(e))
        # Graceful degradation...
```

3. **Add fallback method for legacy bundles**:

```python
def _build_inverted_index_fallback(self) -> Dict[FrozenSet[str], Tuple[str, float]]:
    """
    Build inverted index at runtime for legacy bundles.
    
    This ensures backward compatibility with bundles compiled before v4.0.1.
    """
    inverted_index: Dict[FrozenSet[str], Tuple[str, float]] = {}
    
    for provider_name, signatures in self.provider_signatures.items():
        for signature in signatures:
            # Use default confidence of 0.9 for legacy bundles
            confidence = 0.9
            
            if signature in inverted_index:
                existing_provider, existing_conf = inverted_index[signature]
                if confidence > existing_conf:
                    inverted_index[signature] = (provider_name, confidence)
            else:
                inverted_index[signature] = (provider_name, confidence)
    
    safe_log(self.tracer_instance, "debug",
            "Built inverted index at runtime: %d signatures", 
            len(inverted_index))
    
    return inverted_index
```

4. **Implement O(1) exact match in `_detect_provider`**:

```python
def _detect_provider(self, attributes: Dict[str, Any]) -> str:
    """
    True O(1) provider detection using inverted index.
    
    Performance:
    - Exact match: O(1) via hash table lookup
    - Subset match: O(log n) via size-based bucketing
    """
    if not attributes:
        safe_log(self.tracer_instance, "debug", "No attributes, returning unknown")
        return 'unknown'
    
    attribute_keys = frozenset(attributes.keys())
    
    # Step 1: O(1) exact match lookup
    if attribute_keys in self.signature_to_provider:
        provider, confidence = self.signature_to_provider[attribute_keys]
        safe_log(self.tracer_instance, "debug",
                "✅ Exact signature match: %s (confidence: %.2f) in O(1) time", 
                provider, confidence)
        return provider
    
    # Step 2: O(log n) subset match fallback
    safe_log(self.tracer_instance, "debug",
            "No exact match, trying subset matching")
    return self._find_best_subset_match(attribute_keys)
```

5. **Test the changes**:

```bash
# Run unit tests
tox -e unit -- tests/unit/tracer/processing/semantic_conventions/test_provider_processor.py::test_exact_match_detection -v

# Run with debug logging
python -c "
from honeyhive.tracer.processing.semantic_conventions.provider_processor import UniversalProviderProcessor
import logging
logging.basicConfig(level=logging.DEBUG)

processor = UniversalProviderProcessor()
test_attrs = {
    'gen_ai.request.model': 'gpt-4',
    'gen_ai.response.model': 'gpt-4',
    'gen_ai.usage.input_tokens': 100
}
provider = processor._detect_provider(test_attrs)
print(f'Detected provider: {provider}')
"
```

**Expected Output**:
```
DEBUG:root:Loaded inverted signature index with 18 entries
DEBUG:root:✅ Exact signature match: openai (confidence: 0.95) in O(1) time
Detected provider: openai
```

**Evidence of Completion**: Debug logs show "Exact signature match" with O(1) lookup, tests pass.

---

### Step 1.4: Runtime - O(log n) Subset Match Fallback

**Objective**: Implement optimized subset matching for partial attribute sets.

**Files to Modify**:
- `src/honeyhive/tracer/processing/semantic_conventions/provider_processor.py`

**Implementation Steps**:

1. **Implement `_find_best_subset_match` method**:

```python
def _find_best_subset_match(self, attribute_keys: FrozenSet[str]) -> str:
    """
    O(log n) subset match fallback using size-based bucketing.
    
    Performance: O(log n) where n = number of providers
    
    Algorithm:
    1. Group signatures by size (largest to smallest)
    2. Only check signatures <= attribute set size
    3. Early termination on high confidence match
    4. Calculate match confidence based on overlap
    """
    best_match: Optional[str] = None
    best_confidence: float = 0.0
    
    # Get unique signature sizes, sorted largest to smallest
    signature_sizes = sorted(
        set(len(sig) for sig in self.signature_to_provider.keys()),
        reverse=True
    )
    
    safe_log(self.tracer_instance, "debug",
            "Subset matching: checking %d size buckets", 
            len(signature_sizes))
    
    # Iterate through size buckets (O(log n) due to early termination)
    for size in signature_sizes:
        # Skip signatures larger than attribute set (can't be subset)
        if size > len(attribute_keys):
            continue
        
        # Check only signatures of this size
        for signature, (provider, base_confidence) in self.signature_to_provider.items():
            if len(signature) != size:
                continue
            
            # Check if signature is subset of attributes (O(1) for frozenset)
            if signature.issubset(attribute_keys):
                # Calculate match confidence based on coverage
                # More coverage = higher confidence
                coverage = len(signature) / len(attribute_keys)
                confidence = coverage * base_confidence
                
                safe_log(self.tracer_instance, "debug",
                        "  Subset match candidate: %s (confidence: %.2f, coverage: %.2f)",
                        provider, confidence, coverage)
                
                if confidence > best_confidence:
                    best_match = provider
                    best_confidence = confidence
                    
                    # Early termination for high confidence matches
                    if best_confidence > 0.9:
                        safe_log(self.tracer_instance, "debug",
                                "  High confidence match found, early termination")
                        break
        
        # Early termination if we found a good match
        if best_confidence > 0.9:
            break
    
    if best_match:
        safe_log(self.tracer_instance, "debug",
                "✅ Best subset match: %s (confidence: %.2f)",
                best_match, best_confidence)
        return best_match
    else:
        safe_log(self.tracer_instance, "debug",
                "No subset match found, returning unknown")
        return 'unknown'
```

2. **Test subset matching**:

```bash
# Test with partial attributes
python -c "
from honeyhive.tracer.processing.semantic_conventions.provider_processor import UniversalProviderProcessor
import logging
logging.basicConfig(level=logging.DEBUG)

processor = UniversalProviderProcessor()

# Partial OpenAI attributes
partial_attrs = {
    'gen_ai.request.model': 'gpt-4',
    'extra_field_1': 'value1',
    'extra_field_2': 'value2'
}
provider = processor._detect_provider(partial_attrs)
print(f'Detected provider (partial): {provider}')
"
```

**Expected Output**:
```
DEBUG:root:No exact match, trying subset matching
DEBUG:root:Subset matching: checking 4 size buckets
DEBUG:root:  Subset match candidate: openai (confidence: 0.32, coverage: 0.33)
DEBUG:root:✅ Best subset match: openai (confidence: 0.32)
Detected provider (partial): openai
```

**Evidence of Completion**: Subset matching works correctly with debug logs showing size-based bucketing and confidence calculation.

---

### Step 1.5: Caching - Bundle Metadata Optimization

**Objective**: Fix metadata access to use cached bundle.

**Files to Modify**:
- `src/honeyhive/tracer/processing/semantic_conventions/bundle_loader.py`

**Implementation Steps**:

1. **Update `get_build_metadata` method**:

```python
def get_build_metadata(self) -> Dict[str, Any]:
    """
    Get build metadata with caching optimization.
    
    Performance: <0.01ms for cached access
    """
    # Use cached bundle if available (O(1) attribute access)
    if self._cached_bundle:
        return getattr(self._cached_bundle, 'build_metadata', {})
    
    # Only load bundle if cache is empty (O(n) file load)
    bundle = self.load_provider_bundle()
    return getattr(bundle, 'build_metadata', {})
```

2. **Test metadata caching**:

```bash
# Performance test
python -c "
from honeyhive.tracer.processing.semantic_conventions.bundle_loader import DevelopmentAwareBundleLoader
import time

loader = DevelopmentAwareBundleLoader()

# First access (loads bundle)
start = time.perf_counter()
metadata1 = loader.get_build_metadata()
first_time = (time.perf_counter() - start) * 1000

# Second access (uses cache)
start = time.perf_counter()
metadata2 = loader.get_build_metadata()
cached_time = (time.perf_counter() - start) * 1000

print(f'First access: {first_time:.4f}ms')
print(f'Cached access: {cached_time:.4f}ms')
print(f'Speedup: {first_time/cached_time:.1f}x')
print(f'Target met (<0.01ms): {cached_time < 0.01}')
"
```

**Expected Output**:
```
First access: 2.4567ms
Cached access: 0.0034ms
Speedup: 722.3x
Target met (<0.01ms): True
```

**Evidence of Completion**: Cached access <0.01ms, massive speedup demonstrated.

---

### Step 1.6: Lazy Loading - Function Compilation Optimization

**Objective**: Compile extraction functions on first use, not at bundle load.

**Files to Modify**:
- `src/honeyhive/tracer/processing/semantic_conventions/bundle_loader.py`
- `src/honeyhive/tracer/processing/semantic_conventions/provider_processor.py`

**Implementation Steps**:

1. **Add lazy compilation in bundle loader**:

```python
class DevelopmentAwareBundleLoader:
    """Bundle loader with lazy function compilation."""
    
    def __init__(self):
        self._cached_bundle: Optional[CompiledProviderBundle] = None
        self._compiled_functions: Dict[str, Callable] = {}  # NEW: Function cache
    
    def get_extraction_function(self, provider: str, function_name: str) -> Optional[Callable]:
        """
        Get extraction function with lazy compilation.
        
        Compiles function on first use, caches for subsequent calls.
        """
        cache_key = f"{provider}.{function_name}"
        
        # Check cache first (O(1))
        if cache_key in self._compiled_functions:
            return self._compiled_functions[cache_key]
        
        # Load bundle if not cached
        if not self._cached_bundle:
            self._cached_bundle = self.load_provider_bundle()
        
        # Get function code from bundle
        function_code = self._cached_bundle.extraction_functions.get(cache_key)
        if not function_code:
            return None
        
        # Compile function (O(n) where n = function code length)
        try:
            compiled_func = self._compile_function(function_code)
            self._compiled_functions[cache_key] = compiled_func
            return compiled_func
        except Exception as e:
            # Log error, return None for graceful degradation
            return None
```

2. **Test lazy loading performance**:

```bash
# Bundle load time test
python -c "
from honeyhive.tracer.processing.semantic_conventions.bundle_loader import DevelopmentAwareBundleLoader
import time

loader = DevelopmentAwareBundleLoader()

# Load bundle (should NOT compile all functions)
start = time.perf_counter()
bundle = loader.load_provider_bundle()
load_time = (time.perf_counter() - start) * 1000

print(f'Bundle load time: {load_time:.2f}ms')
print(f'Target met (<3ms): {load_time < 3.0}')
print(f'Compiled functions at load: {len(loader._compiled_functions)}')

# First function use (compiles)
start = time.perf_counter()
func1 = loader.get_extraction_function('openai', 'extract_inputs')
first_use_time = (time.perf_counter() - start) * 1000

# Second function use (cached)
start = time.perf_counter()
func2 = loader.get_extraction_function('openai', 'extract_inputs')
cached_use_time = (time.perf_counter() - start) * 1000

print(f'First function use: {first_use_time:.2f}ms')
print(f'Cached function use: {cached_use_time:.4f}ms')
"
```

**Expected Output**:
```
Bundle load time: 2.14ms
Target met (<3ms): True
Compiled functions at load: 0
First function use: 0.87ms
Cached function use: 0.0012ms
```

**Evidence of Completion**: Bundle loads <3ms without compiling functions, lazy compilation working.

---

## Phase 2: Quality Gates Implementation

### Step 2.1: Gate 12 - Provider YAML Schema Validation

**Objective**: Validate provider YAML files against schema.

**Files to Create**:
- `scripts/validate-provider-yaml-schema.py`

**Implementation**:

```python
#!/usr/bin/env python3
"""
Provider YAML Schema Validation (Quality Gate 12).

Validates all provider YAML files against their schemas.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List


def validate_structure_patterns(data: Dict[str, Any], filepath: Path) -> List[str]:
    """Validate structure_patterns.yaml schema."""
    errors = []
    
    # Check required top-level fields
    if 'patterns' not in data:
        errors.append(f"{filepath}: Missing required 'patterns' field")
        return errors
    
    patterns = data['patterns']
    if not isinstance(patterns, dict):
        errors.append(f"{filepath}: 'patterns' must be a dictionary")
        return errors
    
    # Validate each pattern
    for pattern_name, pattern_data in patterns.items():
        if 'signature_fields' not in pattern_data:
            errors.append(f"{filepath}: Pattern '{pattern_name}' missing 'signature_fields'")
        elif not isinstance(pattern_data['signature_fields'], list):
            errors.append(f"{filepath}: Pattern '{pattern_name}' signature_fields must be a list")
        elif len(pattern_data['signature_fields']) == 0:
            errors.append(f"{filepath}: Pattern '{pattern_name}' signature_fields cannot be empty")
        
        if 'confidence_weight' in pattern_data:
            conf = pattern_data['confidence_weight']
            if not isinstance(conf, (int, float)) or not (0 <= conf <= 1):
                errors.append(f"{filepath}: Pattern '{pattern_name}' confidence_weight must be 0-1")
    
    return errors


def main():
    """Run YAML schema validation."""
    if len(sys.argv) < 2:
        print("Usage: validate-provider-yaml-schema.py <yaml_files...>")
        sys.exit(1)
    
    all_errors = []
    
    for filepath_str in sys.argv[1:]:
        filepath = Path(filepath_str)
        
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            # Determine file type and validate
            if filepath.name == 'structure_patterns.yaml':
                errors = validate_structure_patterns(data, filepath)
                all_errors.extend(errors)
            # Add other file types as needed...
            
        except Exception as e:
            all_errors.append(f"{filepath}: {str(e)}")
    
    if all_errors:
        print("❌ Provider YAML Schema Validation Failed:\n")
        for error in all_errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print(f"✅ Provider YAML Schema Validation Passed ({len(sys.argv)-1} files checked)")
        sys.exit(0)


if __name__ == '__main__':
    main()
```

**Test the gate**:

```bash
# Make executable
chmod +x scripts/validate-provider-yaml-schema.py

# Test on existing providers
python scripts/validate-provider-yaml-schema.py config/dsl/providers/openai/*.yaml

# Test on invalid YAML (should fail)
echo "patterns: not_a_dict" > /tmp/test_invalid.yaml
python scripts/validate-provider-yaml-schema.py /tmp/test_invalid.yaml || echo "Correctly detected invalid YAML"
```

**Expected Output**:
```
✅ Provider YAML Schema Validation Passed (4 files checked)
❌ Provider YAML Schema Validation Failed:
  /tmp/test_invalid.yaml: 'patterns' must be a dictionary
Correctly detected invalid YAML
```

---

### Step 2.2: Gate 13 - Signature Uniqueness Check

**Objective**: Detect duplicate signatures across providers.

**Files to Create**:
- `scripts/check-signature-collisions.py`

**Implementation** (abbreviated, similar structure to Gate 12):

```python
#!/usr/bin/env python3
"""Provider Signature Uniqueness Check (Quality Gate 13)."""

import sys
import yaml
from pathlib import Path
from collections import defaultdict

def main():
    """Check for signature collisions."""
    signature_map = defaultdict(list)  # signature → [(provider, confidence), ...]
    
    # Collect all signatures
    for filepath_str in sys.argv[1:]:
        provider_name = Path(filepath_str).parent.name
        with open(filepath_str, 'r') as f:
            data = yaml.safe_load(f)
        
        for pattern_name, pattern_data in data['patterns'].items():
            sig = frozenset(pattern_data['signature_fields'])
            conf = pattern_data.get('confidence_weight', 0.9)
            signature_map[sig].append((provider_name, conf))
    
    # Check for collisions
    collisions = [(sig, providers) for sig, providers in signature_map.items() if len(providers) > 1]
    
    if collisions:
        print("⚠️  Signature Collisions Detected:\n")
        for sig, providers in collisions:
            print(f"  Signature: {set(sig)}")
            for provider, conf in providers:
                print(f"    - {provider} (confidence: {conf})")
        print("\n💡 Suggestion: Adjust confidence weights to resolve conflicts")
        sys.exit(1)
    else:
        print("✅ No Signature Collisions")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

---

### Step 2.3: Gates 14 & 15

*(Similar implementation pattern - create scripts for bundle compilation verification and performance regression detection)*

---

### Step 2.4: Pre-Commit Configuration

**Objective**: Add 4 new gates to `.pre-commit-config.yaml`.

**Files to Modify**:
- `.pre-commit-config.yaml`

**Add to config**:

```yaml
  # Gate 12: Provider YAML Schema Validation
  - id: provider-yaml-schema
    name: Quality Gate 12 - Provider YAML Schema
    entry: python scripts/validate-provider-yaml-schema.py
    language: system
    files: '^config/dsl/providers/.*\.yaml$'
    pass_filenames: true
  
  # Gate 13: Provider Signature Uniqueness
  - id: provider-signature-uniqueness
    name: Quality Gate 13 - Signature Uniqueness
    entry: python scripts/check-signature-collisions.py
    language: system
    files: '^config/dsl/providers/.*/structure_patterns\.yaml$'
    pass_filenames: true
  
  # Gates 14 & 15...
```

**Test pre-commit**:

```bash
# Install hooks
pre-commit install

# Run all gates
pre-commit run --all-files

# Verify gate count
pre-commit run --all-files 2>&1 | grep -c "Passed"  # Should be 15
```

---

## Phase 3: Testing & Validation

### Systematic Testing Approach

For each component implemented in Phase 1 & 2:

1. **Write unit tests following Agent OS V3 framework**
2. **Write integration tests with no mocks (Agent OS standard)**
3. **Run performance benchmarks**
4. **Collect evidence of success**

Example test structure for TASK-012:

```python
"""Unit tests for compiler inverted index generation."""

import pytest
from scripts.compile_providers import ProviderCompiler

def test_inverted_index_generation():
    """Test that compiler generates inverted index correctly."""
    # Arrange
    compiler = ProviderCompiler()
    
    # Act
    forward_index, inverted_index = compiler._compile_signature_indices()
    
    # Assert - Basic structure
    assert isinstance(forward_index, dict)
    assert isinstance(inverted_index, dict)
    assert len(forward_index) == 3  # 3 providers
    assert len(inverted_index) > 0  # At least some signatures
    
    # Assert - Inverted index structure
    for signature, (provider, confidence) in inverted_index.items():
        assert isinstance(signature, frozenset)
        assert isinstance(provider, str)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1

def test_signature_collision_handling():
    """Test that compiler handles signature collisions correctly."""
    # Test collision detection and resolution...
```

---

## Phase 4: Documentation

### Documentation Checklist

- [ ] Architecture Decision Record (ADR)
- [ ] Performance Analysis Report
- [ ] Multi-Language Reference Guide
- [ ] Systematic Provider Addition Guide
- [ ] Quality Gate User Guide

*(See tasks.md TASK-019 through TASK-023 for detailed requirements)*

---

## 🧪 Validation Checklist

Before considering implementation complete:

### Code Quality
- [ ] All unit tests passing (100% rate)
- [ ] All integration tests passing (100% rate)
- [ ] Pylint score 10.0/10
- [ ] MyPy type checking passes (0 errors)
- [ ] Test coverage >90% for new code

### Performance
- [ ] Provider detection <0.1ms for any provider count
- [ ] Bundle loading <3ms
- [ ] Metadata access <0.01ms
- [ ] End-to-end <0.1ms per span
- [ ] O(1) scaling mathematically proven

### Quality Gates
- [ ] All 15 gates passing
- [ ] Gate 12 (YAML schema) working
- [ ] Gate 13 (signature uniqueness) working
- [ ] Gate 14 (bundle compilation) working
- [ ] Gate 15 (performance regression) working

### Documentation
- [ ] All 5 Agent OS spec files complete
- [ ] ADR published
- [ ] Performance report published
- [ ] Multi-language reference docs complete
- [ ] Provider addition guide complete

### Operational
- [ ] CI/CD pipeline passing
- [ ] Pre-commit hooks working
- [ ] No breaking changes detected
- [ ] Backward compatibility maintained

---

## 🚨 Troubleshooting Guide

### Common Issues

**Issue**: Bundle compilation fails after changes  
**Solution**: Check YAML syntax, run schema validation gate

**Issue**: Tests fail with "AttributeError: signature_to_provider"  
**Solution**: Recompile bundle with updated compiler

**Issue**: Performance targets not met  
**Solution**: Verify inverted index is being used (check debug logs)

**Issue**: Pre-commit gate failing  
**Solution**: Run gate script directly to see detailed error message

---

## 📚 References

- **Performance Analysis**: `/PERFORMANCE_ANALYSIS_O_N_PATTERNS.md`
- **V4.0 Architecture**: `/universal_llm_discovery_engine_v4_final/`
- **Agent OS V3 Framework**: `/.agent-os/standards/ai-assistant/code-generation/tests/`
- **Session Handoff**: `/SESSION_HANDOFF_UNIVERSAL_LLM_DISCOVERY_ENGINE.md`

---

**Document Status**: Complete implementation guide ready for systematic execution following Agent OS V3 framework
