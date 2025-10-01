# Cross-Language DSL Architecture

**Date**: 2025-09-30  
**Purpose**: Design language-agnostic DSL compilation for Python, TypeScript, and Go  
**Problem**: Python pickle won't work for TypeScript/Go

---

## 🚨 The Challenge

### **Current Python Implementation**

```python
# Python-specific approach
compiled_providers.pkl  # Pickled Python objects
↓
CompiledProviderBundle(
    provider_signatures: Dict[str, List[FrozenSet[str]]],
    extraction_functions: Dict[str, str],  # Python code strings!
    field_mappings: Dict[str, Dict[str, Any]],
    transform_registry: Dict[str, Dict[str, Any]]
)
↓
exec() at runtime  # Execute Python code strings
```

**Problems**:
1. ❌ Pickle is Python-only
2. ❌ Extraction functions are Python code strings
3. ❌ `exec()` at runtime (security, portability)
4. ❌ Can't be used by TypeScript or Go

---

## 💡 The Solution: Multi-Tier Compilation

### **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: YAML Source (Language-Agnostic)                     │
│                                                             │
│ config/dsl/providers/{provider}/                            │
│ ├── structure_patterns.yaml                                │
│ ├── navigation_rules.yaml                                  │
│ ├── transforms.yaml                                        │
│ └── field_mappings.yaml                                    │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: JSON Intermediate Representation (IR)               │
│         (Language-Agnostic, Platform-Wide)                  │
│                                                             │
│ config/dsl/compiled/                                        │
│ ├── providers.bundle.json  # Detection patterns            │
│ ├── extractors.json        # Extraction logic (DSL AST)    │
│ ├── mappings.json          # Field mappings                │
│ └── transforms.json        # Transform specs               │
└─────────────────────────────────────────────────────────────┘
                             ↓
              ┌──────────────┴──────────────┬──────────────┐
              ↓                             ↓              ↓
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ TIER 3a: Python      │  │ TIER 3b: TypeScript  │  │ TIER 3c: Go          │
│                      │  │                      │  │                      │
│ Codegen:             │  │ Codegen:             │  │ Codegen:             │
│ JSON → Python funcs  │  │ JSON → TS funcs      │  │ JSON → Go funcs      │
│                      │  │                      │  │                      │
│ Output:              │  │ Output:              │  │ Output:              │
│ compiled_bundle.py   │  │ compiled_bundle.ts   │  │ compiled_bundle.go   │
│ (or .pkl for perf)   │  │ (native TS code)     │  │ (native Go code)     │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

---

## 📋 Tier 2: JSON IR Specification

### **1. Detection Patterns Bundle**

**File**: `config/dsl/compiled/providers.bundle.json`

```json
{
  "version": "4.0",
  "build_timestamp": "2025-09-30T12:00:00Z",
  "providers": {
    "openai": {
      "patterns": {
        "openinference_openai": {
          "signature_fields": [
            "llm.model_name",
            "llm.provider",
            "llm.input_messages.*",
            "llm.token_count.prompt"
          ],
          "optional_fields": [
            "llm.output_messages.*",
            "llm.token_count.completion"
          ],
          "confidence_weight": 0.95,
          "priority": 1,
          "instrumentor_framework": "openinference"
        },
        "traceloop_openai": {
          "signature_fields": [
            "gen_ai.system",
            "gen_ai.request.model",
            "gen_ai.usage.prompt_tokens"
          ],
          "optional_fields": [
            "gen_ai.usage.completion_tokens",
            "gen_ai.response.model"
          ],
          "confidence_weight": 0.90,
          "priority": 2,
          "instrumentor_framework": "traceloop"
        }
      },
      "model_patterns": {
        "gpt_models": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"],
        "o1_models": ["o1-preview", "o1-mini"]
      }
    }
  },
  "inverted_index": {
    "llm.model_name,llm.provider": {
      "provider": "openai",
      "pattern": "openinference_openai",
      "confidence": 0.95
    }
  }
}
```

---

### **2. Extraction Logic (DSL AST)**

**File**: `config/dsl/compiled/extractors.json`

**Key Insight**: Instead of Python code strings, use a **DSL AST** (Abstract Syntax Tree) that any language can interpret!

```json
{
  "openai": {
    "openinference": {
      "extraction_function": {
        "type": "function",
        "name": "extract_openai_openinference",
        "steps": [
          {
            "step": "extract_field",
            "operation": "direct_copy",
            "source": "llm.model_name",
            "target": "extracted_data.model",
            "fallback": null
          },
          {
            "step": "extract_array",
            "operation": "reconstruct_array_from_flattened",
            "source_prefix": "llm.input_messages",
            "target": "extracted_data.input_messages",
            "preserve_json_strings": false
          },
          {
            "step": "transform",
            "operation": "extract_user_message_content",
            "source": "extracted_data.input_messages",
            "target": "extracted_data.user_content",
            "params": {
              "role_filter": "user",
              "join_multiple": true
            }
          }
        ]
      }
    },
    "traceloop": {
      "extraction_function": {
        "type": "function",
        "name": "extract_openai_traceloop",
        "steps": [
          {
            "step": "extract_field",
            "operation": "direct_copy",
            "source": "gen_ai.request.model",
            "target": "extracted_data.model"
          },
          {
            "step": "extract_array",
            "operation": "reconstruct_array_from_flattened",
            "source_prefix": "gen_ai.completion.0.message.tool_calls",
            "target": "extracted_data.tool_calls",
            "preserve_json_strings": true,
            "json_string_fields": ["function.arguments"]
          }
        ]
      }
    }
  }
}
```

**DSL Operations** (Language-Agnostic):
- `direct_copy` - Copy value as-is
- `reconstruct_array_from_flattened` - Rebuild array from dot-notation
- `extract_first_non_empty` - Get first non-null value
- `parse_json_string` - Parse JSON string (but preserve if specified)
- `transform` - Apply named transform function

---

### **3. Field Mappings**

**File**: `config/dsl/compiled/mappings.json`

```json
{
  "openai": {
    "inputs": {
      "messages": {
        "source": "extracted_data.input_messages",
        "required": false
      },
      "system_prompt": {
        "source": "extracted_data.system_content",
        "required": false
      }
    },
    "outputs": {
      "content": {
        "source": "extracted_data.assistant_content",
        "required": false
      },
      "tool_calls": {
        "source": "extracted_data.tool_calls",
        "required": false
      },
      "refusal": {
        "source": "extracted_data.refusal",
        "required": false
      }
    },
    "config": {
      "temperature": {
        "source": "extracted_data.temperature",
        "required": false
      },
      "max_tokens": {
        "source": "extracted_data.max_tokens",
        "required": false
      }
    },
    "metadata": {
      "model": {
        "source": "extracted_data.model",
        "required": true
      },
      "provider": {
        "value": "openai",
        "required": true
      }
    }
  }
}
```

---

### **4. Transform Registry**

**File**: `config/dsl/compiled/transforms.json`

```json
{
  "reconstruct_array_from_flattened": {
    "description": "Reconstruct array from flattened dot-notation attributes",
    "input_type": "dict",
    "output_type": "array",
    "params": {
      "prefix": "string",
      "preserve_json_strings": "boolean",
      "json_string_fields": "array<string>"
    },
    "implementation": {
      "algorithm": "regex_index_extraction",
      "steps": [
        "Parse keys matching {prefix}.{index}.{field}",
        "Group by index",
        "Reconstruct objects",
        "Return sorted by index"
      ]
    }
  },
  "extract_user_message_content": {
    "description": "Extract user message content from messages array",
    "input_type": "array",
    "output_type": "string",
    "params": {
      "role_filter": "string",
      "join_multiple": "boolean",
      "separator": "string"
    },
    "implementation": {
      "algorithm": "array_filter_map",
      "steps": [
        "Filter messages by role",
        "Extract content field",
        "Join if multiple"
      ]
    }
  }
}
```

---

## 🔧 Language-Specific Code Generation

### **Python Codegen**

**Input**: `extractors.json` DSL AST  
**Output**: `compiled_bundle.py` (native Python code)

```python
# scripts/codegen/generate_python.py

def generate_extraction_function(extractor_spec: dict) -> str:
    """Generate Python function from DSL AST."""
    
    steps = extractor_spec["steps"]
    lines = []
    
    lines.append(f"def {extractor_spec['name']}(attributes: Dict[str, Any]) -> Dict[str, Any]:")
    lines.append("    extracted_data = {}")
    
    for step in steps:
        if step["operation"] == "direct_copy":
            lines.append(f"    extracted_data['{step['target'].split('.')[-1]}'] = attributes.get('{step['source']}', {step.get('fallback', 'None')})")
        
        elif step["operation"] == "reconstruct_array_from_flattened":
            lines.append(f"    extracted_data['{step['target'].split('.')[-1]}'] = TRANSFORM_REGISTRY['reconstruct_array_from_flattened'](")
            lines.append(f"        attributes,")
            lines.append(f"        prefix='{step['source_prefix']}',")
            lines.append(f"        preserve_json_strings={step['preserve_json_strings']}")
            lines.append(f"    )")
        
        elif step["operation"] == "transform":
            params = ", ".join(f"{k}={repr(v)}" for k, v in step.get("params", {}).items())
            lines.append(f"    extracted_data['{step['target'].split('.')[-1]}'] = TRANSFORM_REGISTRY['{step['operation']}'](")
            lines.append(f"        extracted_data['{step['source'].split('.')[-1]}'],")
            lines.append(f"        {params}")
            lines.append(f"    )")
    
    lines.append("    return extracted_data")
    
    return "\n".join(lines)
```

**Generated Python**:
```python
def extract_openai_traceloop(attributes: Dict[str, Any]) -> Dict[str, Any]:
    extracted_data = {}
    extracted_data['model'] = attributes.get('gen_ai.request.model', None)
    extracted_data['tool_calls'] = TRANSFORM_REGISTRY['reconstruct_array_from_flattened'](
        attributes,
        prefix='gen_ai.completion.0.message.tool_calls',
        preserve_json_strings=True
    )
    return extracted_data
```

---

### **TypeScript Codegen**

**Input**: `extractors.json` DSL AST  
**Output**: `compiled_bundle.ts` (native TypeScript code)

```typescript
// scripts/codegen/generate_typescript.ts

function generateExtractionFunction(extractorSpec: any): string {
  const steps = extractorSpec.steps;
  const lines: string[] = [];
  
  lines.push(`export function ${extractorSpec.name}(attributes: Record<string, any>): Record<string, any> {`);
  lines.push(`  const extractedData: Record<string, any> = {};`);
  
  for (const step of steps) {
    if (step.operation === "direct_copy") {
      lines.push(`  extractedData['${step.target.split('.').pop()}'] = attributes['${step.source}'] ?? ${step.fallback ?? 'null'};`);
    }
    
    else if (step.operation === "reconstruct_array_from_flattened") {
      lines.push(`  extractedData['${step.target.split('.').pop()}'] = TRANSFORM_REGISTRY.reconstructArrayFromFlattened(`);
      lines.push(`    attributes,`);
      lines.push(`    { prefix: '${step.source_prefix}', preserveJsonStrings: ${step.preserve_json_strings} }`);
      lines.push(`  );`);
    }
    
    else if (step.operation === "transform") {
      const params = Object.entries(step.params || {})
        .map(([k, v]) => `${k}: ${JSON.stringify(v)}`)
        .join(', ');
      lines.push(`  extractedData['${step.target.split('.').pop()}'] = TRANSFORM_REGISTRY['${step.operation}'](`);
      lines.push(`    extractedData['${step.source.split('.').pop()}'],`);
      lines.push(`    { ${params} }`);
      lines.push(`  );`);
    }
  }
  
  lines.push(`  return extractedData;`);
  lines.push(`}`);
  
  return lines.join('\n');
}
```

**Generated TypeScript**:
```typescript
export function extractOpenaiTraceloop(attributes: Record<string, any>): Record<string, any> {
  const extractedData: Record<string, any> = {};
  extractedData['model'] = attributes['gen_ai.request.model'] ?? null;
  extractedData['tool_calls'] = TRANSFORM_REGISTRY.reconstructArrayFromFlattened(
    attributes,
    { prefix: 'gen_ai.completion.0.message.tool_calls', preserveJsonStrings: true }
  );
  return extractedData;
}
```

---

### **Go Codegen**

**Input**: `extractors.json` DSL AST  
**Output**: `compiled_bundle.go` (native Go code)

```go
// scripts/codegen/generate_go.go

func generateExtractionFunction(extractorSpec map[string]interface{}) string {
    steps := extractorSpec["steps"].([]interface{})
    var lines []string
    
    funcName := extractorSpec["name"].(string)
    lines = append(lines, fmt.Sprintf("func %s(attributes map[string]interface{}) map[string]interface{} {", funcName))
    lines = append(lines, "    extractedData := make(map[string]interface{})")
    
    for _, stepInterface := range steps {
        step := stepInterface.(map[string]interface{})
        
        switch step["operation"].(string) {
        case "direct_copy":
            target := strings.Split(step["target"].(string), ".")[len(strings.Split(step["target"].(string), "."))-1]
            source := step["source"].(string)
            fallback := "nil"
            if fb, ok := step["fallback"]; ok {
                fallback = fmt.Sprintf("%v", fb)
            }
            lines = append(lines, fmt.Sprintf("    if val, ok := attributes[\"%s\"]; ok {", source))
            lines = append(lines, fmt.Sprintf("        extractedData[\"%s\"] = val", target))
            lines = append(lines, "    } else {")
            lines = append(lines, fmt.Sprintf("        extractedData[\"%s\"] = %s", target, fallback))
            lines = append(lines, "    }")
        
        case "reconstruct_array_from_flattened":
            target := strings.Split(step["target"].(string), ".")[len(strings.Split(step["target"].(string), "."))-1]
            prefix := step["source_prefix"].(string)
            preserveJson := step["preserve_json_strings"].(bool)
            lines = append(lines, fmt.Sprintf("    extractedData[\"%s\"] = TransformRegistry.ReconstructArrayFromFlattened(", target))
            lines = append(lines, "        attributes,")
            lines = append(lines, fmt.Sprintf("        \"%s\",", prefix))
            lines = append(lines, fmt.Sprintf("        %t,", preserveJson))
            lines = append(lines, "    )")
        }
    }
    
    lines = append(lines, "    return extractedData")
    lines = append(lines, "}")
    
    return strings.Join(lines, "\n")
}
```

**Generated Go**:
```go
func ExtractOpenaiTraceloop(attributes map[string]interface{}) map[string]interface{} {
    extractedData := make(map[string]interface{})
    if val, ok := attributes["gen_ai.request.model"]; ok {
        extractedData["model"] = val
    } else {
        extractedData["model"] = nil
    }
    extractedData["tool_calls"] = TransformRegistry.ReconstructArrayFromFlattened(
        attributes,
        "gen_ai.completion.0.message.tool_calls",
        true,
    )
    return extractedData
}
```

---

## 🏗️ Build Process

### **Development Workflow**

```bash
# 1. Edit YAML source files
vim config/dsl/providers/openai/navigation_rules.yaml

# 2. Compile to JSON IR (language-agnostic)
python scripts/compile_to_json_ir.py openai
# → Creates: config/dsl/compiled/*.json

# 3. Generate language-specific code
python scripts/codegen/generate_python.py
# → Creates: src/honeyhive/tracer/processing/semantic_conventions/compiled_bundle.py

npm run codegen:typescript
# → Creates: sdk/typescript/src/tracer/compiled_bundle.ts

go run scripts/codegen/generate_go.go
# → Creates: sdk/go/tracer/compiled_bundle.go

# 4. (Optional) For Python: Pickle for fast loading
python scripts/pickle_bundle.py
# → Creates: compiled_providers.pkl (Python optimization)
```

---

### **CI/CD Pipeline**

```yaml
# .github/workflows/compile-dsl.yml

name: Compile DSL for All Languages

on:
  push:
    paths:
      - 'config/dsl/**/*.yaml'
      - 'provider_response_schemas/**/*.json'

jobs:
  compile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Compile to JSON IR
        run: python scripts/compile_to_json_ir.py --all
      
      - name: Generate Python Code
        run: python scripts/codegen/generate_python.py
      
      - name: Generate TypeScript Code
        run: npm run codegen:typescript
      
      - name: Generate Go Code
        run: go run scripts/codegen/generate_go.go
      
      - name: Run Tests
        run: |
          pytest tests/unit/test_compiled_bundle.py
          npm test
          go test ./...
      
      - name: Commit Generated Code
        run: |
          git config user.name "DSL Compiler Bot"
          git config user.email "bot@honeyhive.ai"
          git add src/honeyhive/tracer/processing/semantic_conventions/compiled_bundle.py
          git add sdk/typescript/src/tracer/compiled_bundle.ts
          git add sdk/go/tracer/compiled_bundle.go
          git commit -m "chore: recompile DSL for all languages"
          git push
```

---

## 📦 Runtime Loading

### **Python Runtime**

```python
# Option 1: Load from pickle (fast)
with open('compiled_providers.pkl', 'rb') as f:
    bundle = pickle.load(f)

# Option 2: Load from JSON IR (portable)
with open('config/dsl/compiled/extractors.json') as f:
    extractors = json.load(f)
    # Interpret DSL AST at runtime (slower but portable)
```

### **TypeScript Runtime**

```typescript
// Load compiled native code
import { 
  extractOpenaiTraceloop,
  extractOpenaiOpeninference 
} from './compiled_bundle';

// Use directly
const extracted = extractOpenaiTraceloop(spanAttributes);
```

### **Go Runtime**

```go
// Load compiled native code
import "honeyhive/tracer/compiled_bundle"

// Use directly
extracted := compiled_bundle.ExtractOpenaiTraceloop(spanAttributes)
```

---

## 🎯 Benefits of This Approach

### **1. True Cross-Language Support** ✅
- YAML → JSON IR → Language-specific code
- Each SDK gets native, optimized code
- No runtime interpretation overhead (except Python dev mode)

### **2. Single Source of Truth** ✅
- YAML configs are the source
- JSON IR is the intermediate representation
- Generated code is disposable (can regenerate anytime)

### **3. Performance** ✅
- **Python**: Can still use pickle for ultra-fast loading
- **TypeScript**: Native TS functions (V8 optimized)
- **Go**: Native Go functions (compiled)

### **4. Maintainability** ✅
- Update YAML once
- Regenerate all languages
- Version control tracks YAML changes, not generated code

### **5. Extensibility** ✅
- New languages? Just add a codegen script
- New DSL operations? Add to JSON IR spec, implement in each language

---

## 📋 Migration Plan

### **Phase 1: Build JSON IR Compiler**
```bash
scripts/compile_to_json_ir.py  # YAML → JSON
```

### **Phase 2: Build Python Codegen**
```bash
scripts/codegen/generate_python.py  # JSON → Python
```

### **Phase 3: Build TypeScript Codegen**
```bash
scripts/codegen/generate_typescript.ts  # JSON → TypeScript
```

### **Phase 4: Build Go Codegen**
```bash
scripts/codegen/generate_go.go  # JSON → Go
```

### **Phase 5: Update Build Process**
- Add to CI/CD
- Update documentation
- Deprecate manual pickle creation

---

## 🔗 Repository Structure

```
honeyhive-mono-repo/
├── config/dsl/
│   ├── providers/
│   │   ├── openai/
│   │   │   ├── navigation_rules.yaml        # Source
│   │   │   ├── transforms.yaml
│   │   │   └── field_mappings.yaml
│   │   └── anthropic/...
│   └── compiled/                             # JSON IR (generated)
│       ├── providers.bundle.json
│       ├── extractors.json
│       ├── mappings.json
│       └── transforms.json
│
├── scripts/
│   ├── compile_to_json_ir.py                # YAML → JSON
│   └── codegen/
│       ├── generate_python.py               # JSON → Python
│       ├── generate_typescript.ts           # JSON → TypeScript
│       └── generate_go.go                   # JSON → Go
│
├── sdk/
│   ├── python/
│   │   └── src/honeyhive/tracer/processing/semantic_conventions/
│   │       ├── compiled_bundle.py           # Generated
│   │       └── compiled_providers.pkl       # Generated (optional, for perf)
│   │
│   ├── typescript/
│   │   └── src/tracer/
│   │       └── compiled_bundle.ts           # Generated
│   │
│   └── go/
│       └── tracer/
│           └── compiled_bundle.go           # Generated
```

---

**Last Updated**: 2025-09-30  
**Status**: Architecture designed, ready to implement  
**Next**: Build JSON IR compiler and Python codegen

