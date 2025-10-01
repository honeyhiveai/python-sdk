# Config-Driven Cross-Language DSL Architecture

**Date**: 2025-09-30  
**Purpose**: True config-driven approach - no code changes when DSL updates  
**Problem**: Previous design required code generation = code changes per DSL update

---

## 🎯 The Core Principle

### **Config-Driven = Zero Code Changes**

```
When DSL configs change:
❌ BAD:  Generate new code → commit → release SDK
✅ GOOD: Update JSON bundle → release SDK (no code changes!)
```

**Key Insight**: The DSL interpreter/runtime is **code**. The DSL rules are **data**.

---

## 📦 The Solution: Runtime DSL Interpreter

### **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. YAML DSL Source (Single Source of Truth)                 │
│                                                             │
│    config/dsl/providers/{provider}/                         │
│    config/semantic_conventions/{instrumentor}/              │
└─────────────────────────────────────────────────────────────┘
                             ↓ compile once
┌─────────────────────────────────────────────────────────────┐
│ 2. JSON IR Bundle (Language-Agnostic Data)                  │
│                                                             │
│    dsl-bundle.json (or .msgpack, .cbor for performance)     │
│                                                             │
│    This is DATA, not code!                                  │
└─────────────────────────────────────────────────────────────┘
                             ↓ ships with SDK
┌──────────────┬──────────────────────┬──────────────────────┐
│ Python SDK   │ TypeScript SDK       │ Go SDK               │
│              │                      │                      │
│ + bundle     │ + bundle             │ + bundle             │
│ (ONE TIME)   │ (ONE TIME)           │ (ONE TIME)           │
│              │                      │                      │
│ Interpreter  │ Interpreter          │ Interpreter          │
│ (code, v1)   │ (code, v1)           │ (code, v1)           │
│              │                      │                      │
│ Loads bundle │ Loads bundle         │ Loads bundle         │
│ at runtime   │ at runtime           │ at runtime           │
└──────────────┴──────────────────────┴──────────────────────┘
```

**When DSL Changes**:
1. Update YAML sources
2. Recompile to JSON bundle
3. Ship new bundle with SDK
4. **No code changes!** (interpreter is unchanged)

---

## 🔧 DSL Interpreter Pattern

### **Python Implementation**

**File**: `src/honeyhive/tracer/processing/semantic_conventions/dsl_interpreter.py` (ONE TIME)

```python
"""
DSL Interpreter - Runtime execution of DSL rules from JSON bundle.

This file is STABLE - does not change when DSL configs change.
Only the JSON bundle changes.
"""

from typing import Dict, Any, List, Optional
import re
from pathlib import Path
import json

class DSLInterpreter:
    """Interpret and execute DSL rules from JSON bundle at runtime."""
    
    def __init__(self, bundle_path: Path):
        """Load DSL bundle (JSON data)."""
        with open(bundle_path) as f:
            self.bundle = json.load(f)
        
        # Build lookup indexes for O(1) detection
        self._build_indexes()
    
    def _build_indexes(self):
        """Build inverted indexes for fast lookups."""
        # Same indexing as before, but from JSON data
        pass
    
    def detect_provider(self, attributes: Dict[str, Any]) -> Optional[str]:
        """Detect provider from span attributes using bundle rules."""
        
        # Get attribute keys
        attr_keys = set(attributes.keys())
        
        # Check exact signature match (O(1) via inverted index)
        for provider, patterns in self.bundle["detection"]["providers"].items():
            for pattern in patterns:
                signature = frozenset(pattern["signature_attributes"])
                
                if signature.issubset(attr_keys):
                    # Check constraints if any
                    if self._check_constraints(attributes, pattern.get("constraints", {})):
                        return provider
        
        return None
    
    def extract_data(self, provider: str, instrumentor: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data using DSL rules from bundle."""
        
        # Get extraction steps for this provider + instrumentor
        extractor = self.bundle["extractors"][provider][instrumentor]
        
        extracted_data = {}
        
        # Execute each step in the DSL
        for step in extractor["steps"]:
            result = self._execute_step(step, attributes, extracted_data)
            if result is not None:
                # Store result at target path
                target_key = step["target"].split(".")[-1]
                extracted_data[target_key] = result
        
        return extracted_data
    
    def _execute_step(self, step: Dict[str, Any], attributes: Dict[str, Any], extracted_data: Dict[str, Any]) -> Any:
        """Execute a single DSL step."""
        
        operation = step["operation"]
        
        if operation == "direct_copy":
            return attributes.get(step["source"], step.get("fallback"))
        
        elif operation == "reconstruct_array_from_flattened":
            return self._reconstruct_array(
                attributes,
                step["source_prefix"],
                step.get("preserve_json_strings", False),
                step.get("json_string_fields", [])
            )
        
        elif operation == "transform":
            # Apply transform to extracted data
            transform_name = step["transform_function"]
            source_key = step["source"].split(".")[-1]
            source_data = extracted_data.get(source_key)
            
            # Call transform from registry
            from .transform_registry import TRANSFORM_REGISTRY
            return TRANSFORM_REGISTRY[transform_name](source_data, **step.get("params", {}))
        
        # Add more operations as needed
        return None
    
    def _reconstruct_array(
        self, 
        attributes: Dict[str, Any], 
        prefix: str,
        preserve_json_strings: bool = False,
        json_string_fields: List[str] = []
    ) -> List[Dict[str, Any]]:
        """Reconstruct array from flattened attributes."""
        
        pattern = re.compile(rf"^{re.escape(prefix)}\.(\d+)\.(.+)$")
        indexed_data = {}
        
        for key, value in attributes.items():
            match = pattern.match(key)
            if match:
                index = int(match.group(1))
                field_name = match.group(2)
                
                if index not in indexed_data:
                    indexed_data[index] = {}
                
                # Check if this field should preserve JSON strings
                should_preserve = preserve_json_strings and any(
                    field_name.endswith(f) for f in json_string_fields
                )
                
                if should_preserve:
                    # Keep as JSON string, don't parse
                    indexed_data[index][field_name] = value
                else:
                    indexed_data[index][field_name] = value
        
        if not indexed_data:
            return []
        
        max_index = max(indexed_data.keys())
        return [indexed_data.get(i, {}) for i in range(max_index + 1)]
    
    def map_to_honeyhive_schema(self, provider: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map extracted data to HoneyHive 4-section schema using bundle mappings."""
        
        mappings = self.bundle["mappings"][provider]
        
        result = {
            "honeyhive_inputs": {},
            "honeyhive_outputs": {},
            "honeyhive_config": {},
            "honeyhive_metadata": {}
        }
        
        for section in ["inputs", "outputs", "config", "metadata"]:
            for field, mapping in mappings[section].items():
                if "source" in mapping:
                    source_key = mapping["source"].split(".")[-1]
                    value = extracted_data.get(source_key, mapping.get("fallback"))
                elif "value" in mapping:
                    value = mapping["value"]
                else:
                    continue
                
                result[f"honeyhive_{section}"][field] = value
        
        return result
```

**Usage** (never changes):
```python
# In span processor (STABLE CODE)
from .dsl_interpreter import DSLInterpreter

# Load bundle once at init
interpreter = DSLInterpreter(Path(__file__).parent / "dsl-bundle.json")

# Use at runtime
def process_span(span):
    attributes = dict(span.attributes)
    
    # Detect provider (using bundle rules)
    provider = interpreter.detect_provider(attributes)
    
    # Extract data (using bundle rules)
    extracted = interpreter.extract_data(provider, "traceloop", attributes)
    
    # Map to HoneyHive schema (using bundle rules)
    honeyhive_attrs = interpreter.map_to_honeyhive_schema(provider, extracted)
    
    return honeyhive_attrs
```

---

### **TypeScript Implementation**

**File**: `sdk/typescript/src/tracer/dsl-interpreter.ts` (ONE TIME)

```typescript
/**
 * DSL Interpreter - Runtime execution of DSL rules from JSON bundle.
 * 
 * This file is STABLE - does not change when DSL configs change.
 * Only the JSON bundle changes.
 */

import * as fs from 'fs';
import * as path from 'path';

interface DSLBundle {
  detection: {
    providers: Record<string, Array<{
      signature_attributes: string[];
      optional_attributes?: string[];
      constraints?: Record<string, any>;
      confidence_weight: number;
    }>>;
  };
  extractors: Record<string, Record<string, {
    steps: Array<{
      operation: string;
      source?: string;
      target: string;
      fallback?: any;
      source_prefix?: string;
      preserve_json_strings?: boolean;
      json_string_fields?: string[];
      params?: Record<string, any>;
    }>;
  }>>;
  mappings: Record<string, {
    inputs: Record<string, any>;
    outputs: Record<string, any>;
    config: Record<string, any>;
    metadata: Record<string, any>;
  }>;
}

export class DSLInterpreter {
  private bundle: DSLBundle;
  
  constructor(bundlePath: string) {
    // Load DSL bundle (JSON data)
    const bundleContent = fs.readFileSync(bundlePath, 'utf-8');
    this.bundle = JSON.parse(bundleContent);
  }
  
  detectProvider(attributes: Record<string, any>): string | null {
    const attrKeys = new Set(Object.keys(attributes));
    
    for (const [provider, patterns] of Object.entries(this.bundle.detection.providers)) {
      for (const pattern of patterns) {
        const signature = new Set(pattern.signature_attributes);
        
        // Check if signature is subset of attributes
        const isSubset = Array.from(signature).every(attr => attrKeys.has(attr));
        
        if (isSubset) {
          // Check constraints
          if (this.checkConstraints(attributes, pattern.constraints || {})) {
            return provider;
          }
        }
      }
    }
    
    return null;
  }
  
  extractData(
    provider: string, 
    instrumentor: string, 
    attributes: Record<string, any>
  ): Record<string, any> {
    const extractor = this.bundle.extractors[provider][instrumentor];
    const extractedData: Record<string, any> = {};
    
    for (const step of extractor.steps) {
      const result = this.executeStep(step, attributes, extractedData);
      
      if (result !== null && result !== undefined) {
        const targetKey = step.target.split('.').pop()!;
        extractedData[targetKey] = result;
      }
    }
    
    return extractedData;
  }
  
  private executeStep(
    step: any,
    attributes: Record<string, any>,
    extractedData: Record<string, any>
  ): any {
    switch (step.operation) {
      case 'direct_copy':
        return attributes[step.source] ?? step.fallback ?? null;
      
      case 'reconstruct_array_from_flattened':
        return this.reconstructArray(
          attributes,
          step.source_prefix,
          step.preserve_json_strings || false,
          step.json_string_fields || []
        );
      
      case 'transform':
        const sourceKey = step.source.split('.').pop();
        const sourceData = extractedData[sourceKey];
        // Call transform from registry
        return TRANSFORM_REGISTRY[step.transform_function](sourceData, step.params || {});
      
      default:
        return null;
    }
  }
  
  private reconstructArray(
    attributes: Record<string, any>,
    prefix: string,
    preserveJsonStrings: boolean,
    jsonStringFields: string[]
  ): Array<Record<string, any>> {
    const pattern = new RegExp(`^${prefix.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\.(\\d+)\\.(.+)$`);
    const indexedData: Record<number, Record<string, any>> = {};
    
    for (const [key, value] of Object.entries(attributes)) {
      const match = key.match(pattern);
      if (match) {
        const index = parseInt(match[1], 10);
        const fieldName = match[2];
        
        if (!indexedData[index]) {
          indexedData[index] = {};
        }
        
        indexedData[index][fieldName] = value;
      }
    }
    
    if (Object.keys(indexedData).length === 0) {
      return [];
    }
    
    const maxIndex = Math.max(...Object.keys(indexedData).map(Number));
    const result: Array<Record<string, any>> = [];
    
    for (let i = 0; i <= maxIndex; i++) {
      result.push(indexedData[i] || {});
    }
    
    return result;
  }
  
  mapToHoneyHiveSchema(provider: string, extractedData: Record<string, any>): Record<string, any> {
    const mappings = this.bundle.mappings[provider];
    
    const result = {
      honeyhive_inputs: {},
      honeyhive_outputs: {},
      honeyhive_config: {},
      honeyhive_metadata: {}
    };
    
    for (const section of ['inputs', 'outputs', 'config', 'metadata'] as const) {
      for (const [field, mapping] of Object.entries(mappings[section])) {
        let value;
        
        if ('source' in mapping) {
          const sourceKey = mapping.source.split('.').pop();
          value = extractedData[sourceKey] ?? mapping.fallback;
        } else if ('value' in mapping) {
          value = mapping.value;
        }
        
        result[`honeyhive_${section}`][field] = value;
      }
    }
    
    return result;
  }
  
  private checkConstraints(attributes: Record<string, any>, constraints: Record<string, any>): boolean {
    for (const [attr, constraint] of Object.entries(constraints)) {
      if ('equals' in constraint && attributes[attr] !== constraint.equals) {
        return false;
      }
    }
    return true;
  }
}

// Usage (STABLE CODE)
import { DSLInterpreter } from './dsl-interpreter';

const interpreter = new DSLInterpreter(path.join(__dirname, 'dsl-bundle.json'));

export function processSpan(span: any): Record<string, any> {
  const attributes = span.attributes;
  
  const provider = interpreter.detectProvider(attributes);
  const extracted = interpreter.extractData(provider, 'traceloop', attributes);
  const honeyhiveAttrs = interpreter.mapToHoneyHiveSchema(provider, extracted);
  
  return honeyhiveAttrs;
}
```

---

### **Go Implementation**

**File**: `sdk/go/tracer/dsl_interpreter.go` (ONE TIME)

```go
/**
 * DSL Interpreter - Runtime execution of DSL rules from JSON bundle.
 * 
 * This file is STABLE - does not change when DSL configs change.
 * Only the JSON bundle changes.
 */

package tracer

import (
    "encoding/json"
    "io/ioutil"
    "regexp"
    "strconv"
    "strings"
)

type DSLBundle struct {
    Detection struct {
        Providers map[string][]struct {
            SignatureAttributes []string               `json:"signature_attributes"`
            OptionalAttributes  []string               `json:"optional_attributes,omitempty"`
            Constraints         map[string]interface{} `json:"constraints,omitempty"`
            ConfidenceWeight    float64                `json:"confidence_weight"`
        } `json:"providers"`
    } `json:"detection"`
    
    Extractors map[string]map[string]struct {
        Steps []struct {
            Operation          string                 `json:"operation"`
            Source             string                 `json:"source,omitempty"`
            Target             string                 `json:"target"`
            Fallback           interface{}            `json:"fallback,omitempty"`
            SourcePrefix       string                 `json:"source_prefix,omitempty"`
            PreserveJSONStrings bool                  `json:"preserve_json_strings,omitempty"`
            JSONStringFields   []string               `json:"json_string_fields,omitempty"`
            Params             map[string]interface{} `json:"params,omitempty"`
        } `json:"steps"`
    } `json:"extractors"`
    
    Mappings map[string]struct {
        Inputs   map[string]interface{} `json:"inputs"`
        Outputs  map[string]interface{} `json:"outputs"`
        Config   map[string]interface{} `json:"config"`
        Metadata map[string]interface{} `json:"metadata"`
    } `json:"mappings"`
}

type DSLInterpreter struct {
    bundle DSLBundle
}

func NewDSLInterpreter(bundlePath string) (*DSLInterpreter, error) {
    data, err := ioutil.ReadFile(bundlePath)
    if err != nil {
        return nil, err
    }
    
    var bundle DSLBundle
    if err := json.Unmarshal(data, &bundle); err != nil {
        return nil, err
    }
    
    return &DSLInterpreter{bundle: bundle}, nil
}

func (d *DSLInterpreter) DetectProvider(attributes map[string]interface{}) string {
    attrKeys := make(map[string]bool)
    for k := range attributes {
        attrKeys[k] = true
    }
    
    for provider, patterns := range d.bundle.Detection.Providers {
        for _, pattern := range patterns {
            allPresent := true
            for _, attr := range pattern.SignatureAttributes {
                if !attrKeys[attr] {
                    allPresent = false
                    break
                }
            }
            
            if allPresent && d.checkConstraints(attributes, pattern.Constraints) {
                return provider
            }
        }
    }
    
    return ""
}

func (d *DSLInterpreter) ExtractData(
    provider string,
    instrumentor string,
    attributes map[string]interface{},
) map[string]interface{} {
    extractor := d.bundle.Extractors[provider][instrumentor]
    extractedData := make(map[string]interface{})
    
    for _, step := range extractor.Steps {
        result := d.executeStep(step, attributes, extractedData)
        
        if result != nil {
            parts := strings.Split(step.Target, ".")
            targetKey := parts[len(parts)-1]
            extractedData[targetKey] = result
        }
    }
    
    return extractedData
}

func (d *DSLInterpreter) executeStep(
    step interface{},
    attributes map[string]interface{},
    extractedData map[string]interface{},
) interface{} {
    stepMap := step.(map[string]interface{})
    operation := stepMap["operation"].(string)
    
    switch operation {
    case "direct_copy":
        source := stepMap["source"].(string)
        if val, ok := attributes[source]; ok {
            return val
        }
        if fallback, ok := stepMap["fallback"]; ok {
            return fallback
        }
        return nil
    
    case "reconstruct_array_from_flattened":
        return d.reconstructArray(
            attributes,
            stepMap["source_prefix"].(string),
            stepMap["preserve_json_strings"].(bool),
            stepMap["json_string_fields"].([]string),
        )
    
    // Add more operations
    }
    
    return nil
}

func (d *DSLInterpreter) reconstructArray(
    attributes map[string]interface{},
    prefix string,
    preserveJSONStrings bool,
    jsonStringFields []string,
) []map[string]interface{} {
    pattern := regexp.MustCompile(`^` + regexp.QuoteMeta(prefix) + `\.(\d+)\.(.+)$`)
    indexedData := make(map[int]map[string]interface{})
    
    for key, value := range attributes {
        match := pattern.FindStringSubmatch(key)
        if match != nil {
            index, _ := strconv.Atoi(match[1])
            fieldName := match[2]
            
            if indexedData[index] == nil {
                indexedData[index] = make(map[string]interface{})
            }
            
            indexedData[index][fieldName] = value
        }
    }
    
    if len(indexedData) == 0 {
        return []map[string]interface{}{}
    }
    
    maxIndex := 0
    for idx := range indexedData {
        if idx > maxIndex {
            maxIndex = idx
        }
    }
    
    result := make([]map[string]interface{}, maxIndex+1)
    for i := 0; i <= maxIndex; i++ {
        if data, ok := indexedData[i]; ok {
            result[i] = data
        } else {
            result[i] = make(map[string]interface{})
        }
    }
    
    return result
}

func (d *DSLInterpreter) checkConstraints(
    attributes map[string]interface{},
    constraints map[string]interface{},
) bool {
    for attr, constraint := range constraints {
        constraintMap := constraint.(map[string]interface{})
        if equals, ok := constraintMap["equals"]; ok {
            if attributes[attr] != equals {
                return false
            }
        }
    }
    return true
}

// Usage (STABLE CODE)
var interpreter *DSLInterpreter

func init() {
    var err error
    interpreter, err = NewDSLInterpreter("dsl-bundle.json")
    if err != nil {
        panic(err)
    }
}

func ProcessSpan(span Span) map[string]interface{} {
    attributes := span.Attributes()
    
    provider := interpreter.DetectProvider(attributes)
    extracted := interpreter.ExtractData(provider, "traceloop", attributes)
    honeyhiveAttrs := interpreter.MapToHoneyHiveSchema(provider, extracted)
    
    return honeyhiveAttrs
}
```

---

## 📦 Bundle Distribution

### **JSON Bundle Format**

**File**: `dsl-bundle.json` (ships with each SDK)

```json
{
  "version": "4.0",
  "build_timestamp": "2025-09-30T12:00:00Z",
  "detection": {
    "providers": {
      "openai": [
        {
          "signature_attributes": ["gen_ai.system", "gen_ai.request.model"],
          "constraints": {"gen_ai.system": {"equals": "openai"}},
          "confidence_weight": 0.90
        }
      ]
    }
  },
  "extractors": {
    "openai": {
      "traceloop": {
        "steps": [
          {
            "operation": "direct_copy",
            "source": "gen_ai.request.model",
            "target": "extracted_data.model"
          },
          {
            "operation": "reconstruct_array_from_flattened",
            "source_prefix": "gen_ai.completion.0.message.tool_calls",
            "target": "extracted_data.tool_calls",
            "preserve_json_strings": true,
            "json_string_fields": ["function.arguments"]
          }
        ]
      }
    }
  },
  "mappings": {
    "openai": {
      "outputs": {
        "tool_calls": {
          "source": "extracted_data.tool_calls"
        }
      }
    }
  }
}
```

---

## 🚀 Release Process

### **When DSL Changes**

```bash
# 1. Update YAML sources
vim config/dsl/providers/openai/field_mappings.yaml

# 2. Compile to JSON bundle
python scripts/compile_to_json_bundle.py
# → Creates: dsl-bundle.json

# 3. Copy bundle to each SDK
cp dsl-bundle.json sdk/python/src/honeyhive/tracer/dsl-bundle.json
cp dsl-bundle.json sdk/typescript/src/tracer/dsl-bundle.json
cp dsl-bundle.json sdk/go/tracer/dsl-bundle.json

# 4. Release SDKs (NO CODE CHANGES!)
# Python:
cd sdk/python && poetry version patch && poetry build
# TypeScript:
cd sdk/typescript && npm version patch && npm publish
# Go:
cd sdk/go && git tag v1.2.3 && git push --tags

# Interpreter code is UNCHANGED!
```

---

## ✅ Benefits of This Approach

### **1. True Config-Driven** ✅
- DSL changes → JSON bundle changes
- No code changes needed
- Same release process as Python pickle

### **2. Interpreter Stability** ✅
- Interpreter code written ONCE
- Only bundle data changes
- Fewer bugs, easier maintenance

### **3. Cross-Language Consistency** ✅
- Same JSON bundle for all languages
- Same behavior across SDKs
- Test once, works everywhere

### **4. Performance** ✅
- **Python**: Can still cache/pickle bundle for speed
- **TypeScript**: Load JSON at init (fast)
- **Go**: Load JSON at init (fast, static compiled)
- Interpreters are optimized, bundle is data

### **5. Versioning** ✅
- Bundle includes version number
- SDKs can support multiple bundle versions
- Backward compatibility easier

---

## 🎯 Comparison

### **Code Generation (Previous Design)**
```
DSL changes → Generate new code → Commit → CI/CD → Release
❌ Code changes required
❌ Different code per language
❌ Hard to maintain consistency
```

### **Interpreter + JSON Bundle (This Design)**
```
DSL changes → Compile to JSON → Copy bundle → Release
✅ No code changes
✅ Same bundle for all languages  
✅ Interpreter is stable
```

---

## 📋 Implementation Priority

### **Phase 1: Build JSON Bundle Compiler**
```bash
scripts/compile_to_json_bundle.py
```
- Load YAML DSL
- Compile to JSON IR
- Optimize for runtime loading

### **Phase 2: Implement Interpreters (One-Time)**
- Python: `dsl_interpreter.py`
- TypeScript: `dsl-interpreter.ts`
- Go: `dsl_interpreter.go`

### **Phase 3: Test & Validate**
- Same bundle, all languages
- Verify identical behavior
- Performance benchmarks

### **Phase 4: Update Release Process**
- Bundle versioning
- Distribution automation
- SDK release scripts

---

**Last Updated**: 2025-09-30  
**Status**: Architecture redesigned for true config-driven approach  
**Next**: Build JSON bundle compiler and Python interpreter

