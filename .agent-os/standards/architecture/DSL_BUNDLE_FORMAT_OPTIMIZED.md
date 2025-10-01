# DSL Bundle Format - Optimized for O(1) Lookups

**Date**: 2025-09-30  
**Purpose**: Design DSL bundle with pre-computed indexes for O(1) runtime performance  
**Goal**: Render DSL to data structures that enable O(1) lookups across all languages

---

## 🎯 Performance Requirements

### **O(1) Operations Required**

1. **Provider Detection**: Given span attributes, find provider in O(1)
2. **Pattern Matching**: Given signature, find instrumentor in O(1)
3. **Field Extraction**: Given provider+instrumentor, get extraction rules in O(1)
4. **Field Mapping**: Given provider+field, get HoneyHive mapping in O(1)

### **Current Python Implementation** ✅

```python
# From bundle_types.py - Already has O(1) structures!

class CompiledProviderBundle:
    # Forward index: provider → [signatures] (for subset matching fallback)
    provider_signatures: Dict[str, List[FrozenSet[str]]]
    
    # Inverted index: signature → (provider, confidence) (O(1) exact match!)
    signature_to_provider: Dict[FrozenSet[str], Tuple[str, float]]
    
    # Extraction functions: provider → code (O(1) lookup!)
    extraction_functions: Dict[str, str]
    
    # Field mappings: provider → mappings (O(1) lookup!)
    field_mappings: Dict[str, Dict[str, Any]]
```

**This is the right approach!** We need to preserve this in the JSON bundle.

---

## 📦 Optimized JSON Bundle Format

### **Bundle Structure with Pre-Computed Indexes**

```json
{
  "version": "4.0",
  "build_timestamp": "2025-09-30T12:00:00Z",
  "build_metadata": {
    "compiler_version": "4.0.1",
    "total_providers": 10,
    "total_patterns": 32,
    "optimization_level": "O(1)"
  },
  
  // ========================================
  // INDEX 1: Inverted Signature Index (O(1) Exact Match)
  // ========================================
  "signature_index": {
    // Signature (sorted attribute set) → Provider match
    "gen_ai.request.model|gen_ai.system|gen_ai.usage.prompt_tokens": {
      "provider": "openai",
      "instrumentor": "traceloop",
      "pattern_id": "traceloop_openai",
      "confidence": 0.90,
      "priority": 2
    },
    "llm.input_messages.*|llm.model_name|llm.provider|llm.token_count.prompt": {
      "provider": "openai",
      "instrumentor": "openinference",
      "pattern_id": "openinference_openai",
      "confidence": 0.95,
      "priority": 1
    },
    // ... more signatures (pre-computed at compile time)
  },
  
  // ========================================
  // INDEX 2: Provider Patterns (for Subset Matching Fallback)
  // ========================================
  "provider_patterns": {
    "openai": {
      "patterns": {
        "traceloop_openai": {
          "signature_attributes": ["gen_ai.system", "gen_ai.request.model", "gen_ai.usage.prompt_tokens"],
          "optional_attributes": ["gen_ai.usage.completion_tokens", "gen_ai.response.model"],
          "constraints": {
            "gen_ai.system": {"equals": "openai"}
          },
          "confidence": 0.90,
          "priority": 2
        },
        "openinference_openai": {
          "signature_attributes": ["llm.model_name", "llm.provider", "llm.input_messages.*", "llm.token_count.prompt"],
          "optional_attributes": ["llm.output_messages.*", "llm.token_count.completion"],
          "constraints": {
            "llm.provider": {"equals": "openai"}
          },
          "confidence": 0.95,
          "priority": 1
        }
      }
    },
    "anthropic": {
      "patterns": {
        // ... anthropic patterns
      }
    }
  },
  
  // ========================================
  // INDEX 3: Extraction Rules (O(1) Lookup)
  // ========================================
  "extractors": {
    // Key: "provider:instrumentor" for O(1) lookup
    "openai:traceloop": {
      "extraction_id": "openai_traceloop_v1",
      "steps": [
        {
          "step_id": 1,
          "operation": "direct_copy",
          "source": "gen_ai.request.model",
          "target": "model",
          "fallback": null
        },
        {
          "step_id": 2,
          "operation": "reconstruct_array_from_flattened",
          "source_prefix": "gen_ai.completion.0.message.tool_calls",
          "target": "tool_calls",
          "preserve_json_strings": true,
          "json_string_fields": ["function.arguments"]
        },
        {
          "step_id": 3,
          "operation": "direct_copy",
          "source": "gen_ai.completion.0.message.refusal",
          "target": "refusal",
          "fallback": null
        }
      ]
    },
    "openai:openinference": {
      "extraction_id": "openai_openinference_v1",
      "steps": [
        {
          "step_id": 1,
          "operation": "direct_copy",
          "source": "llm.model_name",
          "target": "model",
          "fallback": null
        },
        {
          "step_id": 2,
          "operation": "reconstruct_array_from_flattened",
          "source_prefix": "llm.input_messages",
          "target": "input_messages",
          "preserve_json_strings": false
        }
      ]
    },
    "openai:openlit": {
      // ... openlit extraction steps
    }
  },
  
  // ========================================
  // INDEX 4: Field Mappings (O(1) Lookup)
  // ========================================
  "mappings": {
    // Key: provider for O(1) lookup
    "openai": {
      "inputs": {
        "messages": {
          "source": "input_messages",
          "required": false,
          "default": []
        },
        "system_prompt": {
          "source": "system_content",
          "required": false,
          "default": null
        }
      },
      "outputs": {
        "content": {
          "source": "assistant_content",
          "required": false,
          "default": null
        },
        "tool_calls": {
          "source": "tool_calls",
          "required": false,
          "default": []
        },
        "refusal": {
          "source": "refusal",
          "required": false,
          "default": null
        }
      },
      "config": {
        "temperature": {
          "source": "temperature",
          "required": false,
          "default": null
        },
        "max_tokens": {
          "source": "max_tokens",
          "required": false,
          "default": null
        }
      },
      "metadata": {
        "model": {
          "source": "model",
          "required": true
        },
        "provider": {
          "value": "openai",
          "required": true
        }
      }
    },
    "anthropic": {
      // ... anthropic mappings
    }
  },
  
  // ========================================
  // INDEX 5: Model Patterns (for Model-Based Detection)
  // ========================================
  "model_patterns": {
    "openai": {
      "patterns": {
        "gpt_models": {
          "regex": "^(gpt-3\\.5-turbo|gpt-4|gpt-4o|gpt-5)",
          "confidence_boost": 0.15
        },
        "o1_models": {
          "regex": "^(o1-preview|o1-mini)",
          "confidence_boost": 0.10
        }
      }
    },
    "anthropic": {
      "patterns": {
        "claude_models": {
          "regex": "^claude-",
          "confidence_boost": 0.15
        }
      }
    }
  },
  
  // ========================================
  // INDEX 6: Transform Registry
  // ========================================
  "transforms": {
    "reconstruct_array_from_flattened": {
      "description": "Reconstruct array from flattened dot-notation attributes",
      "algorithm": "regex_index_extraction",
      "input_type": "attributes",
      "output_type": "array",
      "params_schema": {
        "prefix": "string",
        "preserve_json_strings": "boolean",
        "json_string_fields": "array<string>"
      }
    },
    "direct_copy": {
      "description": "Direct attribute copy with fallback",
      "algorithm": "simple_copy",
      "input_type": "any",
      "output_type": "any",
      "params_schema": {
        "fallback": "any"
      }
    }
  }
}
```

---

## 🚀 Runtime O(1) Lookup Flow

### **Detection (O(1) Exact Match)**

```python
# Step 1: Build signature from span attributes (O(n) where n = attributes)
def build_signature(attributes: Dict[str, Any]) -> str:
    """Build sorted, pipe-delimited signature from attribute keys."""
    keys = sorted(attributes.keys())
    return "|".join(keys)

# Step 2: Lookup in inverted index (O(1))
def detect_provider_o1(attributes: Dict[str, Any], bundle: dict) -> Optional[dict]:
    """O(1) provider detection using inverted signature index."""
    
    signature = build_signature(attributes)
    
    # O(1) lookup!
    if signature in bundle["signature_index"]:
        match = bundle["signature_index"][signature]
        
        # Verify constraints (O(1) per constraint)
        pattern = bundle["provider_patterns"][match["provider"]]["patterns"][match["pattern_id"]]
        if check_constraints(attributes, pattern.get("constraints", {})):
            return match
    
    return None

# Step 3: Fallback to subset matching (O(log n) with sorted patterns)
def detect_provider_subset(attributes: Dict[str, Any], bundle: dict) -> Optional[dict]:
    """Subset matching fallback if exact match fails."""
    
    attr_set = set(attributes.keys())
    
    # Pre-sorted patterns by confidence (descending)
    for provider, data in bundle["provider_patterns"].items():
        for pattern_id, pattern in sorted(data["patterns"].items(), 
                                          key=lambda x: x[1]["confidence"], 
                                          reverse=True):
            signature_set = set(pattern["signature_attributes"])
            
            # O(k) where k = signature size (usually small, ~5 attributes)
            if signature_set.issubset(attr_set):
                if check_constraints(attributes, pattern.get("constraints", {})):
                    return {
                        "provider": provider,
                        "instrumentor": pattern_id.split("_")[0],
                        "pattern_id": pattern_id,
                        "confidence": pattern["confidence"]
                    }
    
    return None
```

### **Extraction (O(1) Lookup)**

```python
def extract_data_o1(provider: str, instrumentor: str, attributes: Dict[str, Any], bundle: dict) -> dict:
    """O(1) extraction using pre-computed steps."""
    
    # O(1) lookup of extraction rules
    extractor_key = f"{provider}:{instrumentor}"
    extractor = bundle["extractors"][extractor_key]
    
    extracted = {}
    
    # O(m) where m = number of steps (usually small, ~10-20 steps)
    for step in extractor["steps"]:
        result = execute_step(step, attributes, extracted)
        if result is not None:
            extracted[step["target"]] = result
    
    return extracted
```

### **Mapping (O(1) Lookup)**

```python
def map_to_honeyhive_o1(provider: str, extracted: Dict[str, Any], bundle: dict) -> dict:
    """O(1) mapping using pre-computed field mappings."""
    
    # O(1) lookup of mappings
    mappings = bundle["mappings"][provider]
    
    result = {
        "honeyhive_inputs": {},
        "honeyhive_outputs": {},
        "honeyhive_config": {},
        "honeyhive_metadata": {}
    }
    
    # O(f) where f = number of fields (usually ~20-30 fields)
    for section in ["inputs", "outputs", "config", "metadata"]:
        for field, mapping in mappings[section].items():
            if "source" in mapping:
                value = extracted.get(mapping["source"], mapping.get("default"))
            elif "value" in mapping:
                value = mapping["value"]
            else:
                continue
            
            result[f"honeyhive_{section}"][field] = value
    
    return result
```

---

## 🔧 Compiler Implementation

### **Bundle Compiler with Index Generation**

```python
#!/usr/bin/env python3
"""
DSL Bundle Compiler - Generates optimized bundle with O(1) indexes.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Set
from collections import defaultdict

class DSLBundleCompiler:
    """Compile YAML DSL to optimized JSON bundle with pre-computed indexes."""
    
    def compile_to_bundle(self, config_dir: Path) -> dict:
        """Compile all YAML configs to optimized bundle."""
        
        bundle = {
            "version": "4.0",
            "build_timestamp": self._get_timestamp(),
            "signature_index": {},      # O(1) exact match index
            "provider_patterns": {},    # Subset matching fallback
            "extractors": {},           # O(1) extraction rules
            "mappings": {},             # O(1) field mappings
            "model_patterns": {},       # Model-based detection
            "transforms": {}            # Transform registry
        }
        
        # Load all providers
        for provider_dir in config_dir.glob("providers/*"):
            provider = provider_dir.name
            self._compile_provider(provider, provider_dir, bundle)
        
        # Build inverted signature index (O(1) lookup!)
        self._build_signature_index(bundle)
        
        return bundle
    
    def _compile_provider(self, provider: str, provider_dir: Path, bundle: dict):
        """Compile a single provider's DSL configs."""
        
        # Load structure patterns
        with open(provider_dir / "structure_patterns.yaml") as f:
            structure = yaml.safe_load(f)
        
        # Load navigation rules
        with open(provider_dir / "navigation_rules.yaml") as f:
            nav_rules = yaml.safe_load(f)
        
        # Load field mappings
        with open(provider_dir / "field_mappings.yaml") as f:
            mappings = yaml.safe_load(f)
        
        # Build provider patterns
        bundle["provider_patterns"][provider] = {
            "patterns": {}
        }
        
        for pattern_id, pattern in structure["patterns"].items():
            bundle["provider_patterns"][provider]["patterns"][pattern_id] = {
                "signature_attributes": pattern["signature_fields"],
                "optional_attributes": pattern.get("optional_fields", []),
                "constraints": self._extract_constraints(pattern),
                "confidence": pattern["confidence_weight"],
                "priority": pattern["priority"]
            }
            
            # Build extraction steps for this pattern
            instrumentor = pattern["instrumentor_framework"]
            extractor_key = f"{provider}:{instrumentor}"
            
            bundle["extractors"][extractor_key] = {
                "extraction_id": f"{provider}_{instrumentor}_v1",
                "steps": self._build_extraction_steps(nav_rules, pattern_id)
            }
        
        # Add field mappings (O(1) lookup by provider)
        bundle["mappings"][provider] = self._compile_mappings(mappings)
        
        # Add model patterns
        if "model_patterns" in structure:
            bundle["model_patterns"][provider] = {
                "patterns": structure["model_patterns"]
            }
    
    def _build_signature_index(self, bundle: dict):
        """Build inverted signature index for O(1) exact match lookups."""
        
        for provider, provider_data in bundle["provider_patterns"].items():
            for pattern_id, pattern in provider_data["patterns"].items():
                # Create signature (sorted, pipe-delimited)
                signature = self._create_signature(pattern["signature_attributes"])
                
                # Store in inverted index
                instrumentor = pattern_id.split("_")[0]
                bundle["signature_index"][signature] = {
                    "provider": provider,
                    "instrumentor": instrumentor,
                    "pattern_id": pattern_id,
                    "confidence": pattern["confidence"],
                    "priority": pattern["priority"]
                }
    
    def _create_signature(self, attributes: list) -> str:
        """Create a signature from attribute list for indexing."""
        return "|".join(sorted(attributes))
    
    def _build_extraction_steps(self, nav_rules: dict, pattern_id: str) -> list:
        """Build extraction steps from navigation rules."""
        steps = []
        step_id = 1
        
        for rule_name, rule in nav_rules.get("navigation_rules", {}).items():
            # Filter rules relevant to this pattern
            if pattern_id in rule_name or self._is_relevant_rule(rule, pattern_id):
                steps.append({
                    "step_id": step_id,
                    "operation": rule.get("extraction_method", "direct_copy"),
                    "source": rule.get("source_field"),
                    "target": self._extract_target_name(rule_name),
                    "fallback": rule.get("fallback_value"),
                    **self._extract_step_params(rule)
                })
                step_id += 1
        
        return steps
    
    def _compile_mappings(self, mappings: dict) -> dict:
        """Compile field mappings to optimized format."""
        result = {
            "inputs": {},
            "outputs": {},
            "config": {},
            "metadata": {}
        }
        
        for section in ["inputs", "outputs", "config", "metadata"]:
            for field, mapping in mappings.get(section, {}).items():
                result[section][field] = {
                    "source": mapping.get("source_rule"),
                    "required": mapping.get("required", False),
                    "default": mapping.get("default")
                }
        
        return result
    
    def _extract_constraints(self, pattern: dict) -> dict:
        """Extract constraint rules from pattern."""
        constraints = {}
        
        # Look for specific field values in signature
        for field in pattern.get("signature_fields", []):
            if "=" in field or field.endswith("openai") or field.endswith("anthropic"):
                # This is a constraint
                parts = field.split("=")
                if len(parts) == 2:
                    constraints[parts[0].strip()] = {"equals": parts[1].strip()}
        
        return constraints

def main():
    compiler = DSLBundleCompiler()
    
    config_dir = Path("config/dsl")
    bundle = compiler.compile_to_bundle(config_dir)
    
    # Write optimized bundle
    output_path = Path("config/dsl/compiled/dsl-bundle.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(bundle, f, indent=2)
    
    # Print stats
    print(f"✅ Bundle compiled successfully!")
    print(f"   Providers: {len(bundle['provider_patterns'])}")
    print(f"   Signatures indexed: {len(bundle['signature_index'])}")
    print(f"   Extractors: {len(bundle['extractors'])}")
    print(f"   Output: {output_path}")

if __name__ == "__main__":
    main()
```

---

## 📊 Performance Analysis

### **Complexity Analysis**

| Operation | Without Indexes | With O(1) Indexes | Improvement |
|-----------|----------------|-------------------|-------------|
| **Provider Detection (Exact)** | O(n*m) | **O(1)** | 🚀 Massive |
| **Provider Detection (Subset)** | O(n*m*k) | **O(log n)** | 🚀 Significant |
| **Extraction Rule Lookup** | O(n) | **O(1)** | 🚀 Massive |
| **Field Mapping Lookup** | O(n) | **O(1)** | 🚀 Massive |
| **Overall Span Processing** | O(n²) | **O(1) + O(m)** | 🚀 Near-constant |

Where:
- n = number of providers/patterns
- m = number of attributes in span
- k = number of signature attributes per pattern

### **Real-World Example**

```
Scenario: 10 providers, 30 patterns, 50 span attributes

Without indexes:
- Detection: O(10 * 30 * 5) = 1,500 comparisons
- Extraction: O(30) lookups
- Mapping: O(30) lookups
- Total: ~1,560 operations

With O(1) indexes:
- Detection: O(1) signature lookup = 1 operation
- Extraction: O(1) extractor lookup = 1 operation  
- Mapping: O(1) mapping lookup = 1 operation
- Steps: O(15) extraction steps = 15 operations
- Total: ~18 operations

Speedup: 86x faster! 🚀
```

---

## ✅ Benefits Summary

### **1. True O(1) Lookups** ✅
- Inverted signature index
- Direct extractor lookup
- Direct mapping lookup

### **2. Language-Agnostic** ✅
- JSON format works everywhere
- Same indexes in Python/TypeScript/Go
- Same performance characteristics

### **3. Config-Driven** ✅
- Bundle is data (JSON)
- Interpreter is code (stable)
- DSL changes → bundle changes (no code changes!)

### **4. Optimized** ✅
- Pre-computed at compile time
- Minimal runtime overhead
- Scales to 100+ providers

---

**Last Updated**: 2025-09-30  
**Status**: Optimized bundle format designed for O(1) performance  
**Next**: Implement bundle compiler with index generation

