# Master DSL Architecture - Unified Documentation

**Date**: 2025-09-30  
**Purpose**: Unified architecture for the complete DSL system - from source to runtime  
**Scope**: Provider schemas → Semantic conventions → YAML DSL → O(1) indexes → Cross-language runtime

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [The Complete Pipeline](#the-complete-pipeline)
3. [Phase 1: Provider Schema Extraction](#phase-1-provider-schema-extraction)
4. [Phase 2: Semantic Convention Discovery](#phase-2-semantic-convention-discovery)
5. [Phase 3: YAML DSL Configuration](#phase-3-yaml-dsl-configuration)
6. [Phase 4: Bundle Compilation](#phase-4-bundle-compilation)
7. [Phase 5: Cross-Language Runtime](#phase-5-cross-language-runtime)
8. [Tools & Utilities](#tools--utilities)
9. [Release Process](#release-process)

---

## 🎯 System Overview

### **The Problem**

HoneyHive needs to:
1. Support **any instrumentor** (OpenLit, Traceloop, OpenInference) - BYOI architecture
2. Support **any provider** (OpenAI, Anthropic, etc.) - neutrality
3. Support **multiple languages** (Python, TypeScript, Go) - platform-wide
4. Handle **complex LLM responses** (tool calls, multimodal, etc.) - data fidelity
5. **Zero code changes** when providers/instrumentors update - config-driven

### **The Solution**

A **unified DSL system** that:
- Extracts provider schemas programmatically
- Discovers semantic conventions from instrumentor source
- Compiles to YAML DSL (single source of truth)
- Generates O(1) optimized bundles
- Loads in any language with no code changes

---

## 🔄 The Complete Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: PROVIDER SCHEMA EXTRACTION                         │
│ (What fields exist in provider API responses?)              │
│                                                             │
│ Input:  OpenAPI specs, SDK types, API docs                 │
│ Tool:   Provider Schema Extraction Framework               │
│ Output: provider_response_schemas/{provider}/              │
│         ├── v{version}.json (JSON Schema)                  │
│         ├── examples/*.json (validated examples)           │
│         └── CRITICAL_FINDINGS.md (DSL guidance)            │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: SEMANTIC CONVENTION DISCOVERY                      │
│ (What attributes do instrumentors set?)                     │
│                                                             │
│ Input:  Instrumentor GitHub repos                          │
│ Tool:   analyze_instrumentor_source.py                     │
│ Output: config/semantic_conventions/{instrumentor}/        │
│         ├── source_analysis.yaml (discovered attrs)        │
│         └── {provider}.yaml.template (auto-generated)      │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: YAML DSL CONFIGURATION                             │
│ (How to detect, extract, and map?)                         │
│                                                             │
│ Human Curation:                                             │
│   1. Use provider schema to understand fields              │
│   2. Use semantic convention discovery for attributes      │
│   3. Create YAML configs:                                  │
│                                                             │
│ config/dsl/providers/{provider}/                            │
│ ├── structure_patterns.yaml    # Detection                 │
│ ├── navigation_rules.yaml      # Extraction                │
│ ├── transforms.yaml             # Transformations          │
│ └── field_mappings.yaml         # HoneyHive mapping        │
│                                                             │
│ config/semantic_conventions/{instrumentor}/                 │
│ └── {provider}.yaml             # Instrumentor mappings    │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: BUNDLE COMPILATION                                 │
│ (Compile to O(1) optimized bundle)                         │
│                                                             │
│ Tool:   compile_dsl_bundle.py                              │
│ Output: config/dsl/compiled/dsl-bundle.json                │
│                                                             │
│ Bundle Structure:                                           │
│ ├── signature_index: {}      # O(1) provider detection     │
│ ├── extractors: {}            # O(1) extraction rules       │
│ ├── mappings: {}              # O(1) field mappings         │
│ └── transforms: {}            # Transform registry          │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: CROSS-LANGUAGE RUNTIME                             │
│ (Load bundle in any language, no code changes)             │
│                                                             │
│ Python:     dsl_interpreter.py + dsl-bundle.json           │
│ TypeScript: dsl-interpreter.ts + dsl-bundle.json           │
│ Go:         dsl_interpreter.go + dsl-bundle.json           │
│                                                             │
│ All use SAME bundle, SAME O(1) performance                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Phase 1: Provider Schema Extraction

### **Purpose**

Extract and validate the **actual structure** of provider API responses.

### **Why This Matters**

- Provider responses are complex (tool calls with JSON strings, multimodal, etc.)
- Need to know **what fields exist** before building DSL
- Critical findings inform DSL design (e.g., "arguments is a JSON string, not object")

### **Framework**

**Location**: `.agent-os/standards/ai-assistant/provider-schema-extraction/`

**Phases**:
0. Pre-Research Setup
1. Schema Discovery (find OpenAPI specs, SDK types)
2. Schema Extraction (download and parse)
3. Example Collection (gather real responses)
4. JSON Schema Creation (convert to JSON Schema)
5. Validation (test examples against schema)
6. Documentation (document critical findings)
7. Integration Testing (ready for DSL)

### **Output Structure**

```
provider_response_schemas/
└── {provider}/                    # e.g., openai
    ├── v{version}.json            # JSON Schema (e.g., v2025-01-30.json)
    ├── examples/                  # Validated examples
    │   ├── basic_chat.json
    │   ├── tool_calls.json
    │   ├── refusal.json
    │   ├── audio_response.json
    │   └── ...
    ├── CHANGELOG.md               # Version history
    ├── CRITICAL_FINDINGS.md       # DSL integration guidance
    ├── SDK_SOURCES.md             # Source tracking
    ├── PROVIDER_INFO.md           # Provider metadata
    └── validate_schema.py         # Validation tool
```

### **Critical Findings Example (OpenAI)**

```markdown
# From CRITICAL_FINDINGS.md

🚨 Tool Call Arguments are JSON STRINGS
- Type: `string` (JSON-serialized, NOT object)
- DSL Impact: Must preserve as JSON string, not parse

🚨 Content Can Be Null
- Null when `tool_calls` or `refusal` is primary response
- DSL Impact: Requires null-safe extraction with fallback

🚨 Arrays are Flattened in Instrumentor Spans
- Instrumentors flatten to: `gen_ai.completion.0.message.tool_calls.0.id`
- DSL Impact: Must reconstruct arrays with `reconstruct_array_from_flattened()`
```

### **How This Feeds Into DSL**

```yaml
# Provider schema tells us:
# - tool_calls is an array
# - function.arguments is a JSON string
# - Can be null

# This informs DSL navigation rules:
navigation_rules:
  traceloop_tool_calls_flattened:
    source_field: "gen_ai.completion.0.message.tool_calls"
    extraction_method: "array_reconstruction"  # ← From schema type
    preserve_json_strings: true                # ← From schema format
    json_string_fields:
      - "function.arguments"                   # ← From schema definition
```

---

## 🔍 Phase 2: Semantic Convention Discovery

### **Purpose**

Discover **what attributes instrumentors actually set** on spans.

### **Why This Matters**

- Can't manually track every instrumentor's attributes
- Instrumentors evolve and add new attributes
- Need programmatic discovery for accuracy

### **Tool: Instrumentor Source Analyzer**

**Script**: `scripts/analyze_instrumentor_source.py`

**What it does**:
1. Clones instrumentor GitHub repos
2. Scans Python source code using AST parsing
3. Finds all `span.set_attribute()` calls
4. Identifies signature vs optional attributes
5. Generates YAML templates

**Usage**:
```bash
python scripts/analyze_instrumentor_source.py traceloop
```

**Output**:
```
config/semantic_conventions/traceloop/
├── source_analysis.yaml       # Discovered attributes
└── openai.yaml.template       # Auto-generated template
```

### **Auto-Generated Template**

```yaml
# config/semantic_conventions/traceloop/openai.yaml.template
# Auto-discovered from source analysis

version: '0.46.2'
instrumentor: traceloop
provider: openai

detection:
  # Auto-discovered signature attributes
  signature_attributes:
    - "gen_ai.system"
    - "gen_ai.request.model"
    - "gen_ai.usage.prompt_tokens"
  
  # Auto-discovered optional attributes
  optional_attributes:
    - "gen_ai.usage.completion_tokens"
    - "gen_ai.response.model"
    - "gen_ai.completion"

# Human fills in mappings below:
mappings:
  inputs: {}
  outputs: {}
  config: {}
  metadata: {}
```

### **Human Curation**

After auto-generation, humans fill in the mappings:

```yaml
# config/semantic_conventions/traceloop/openai.yaml
# Human-curated mappings

mappings:
  outputs:
    tool_calls:
      source: "gen_ai.completion.0.message.tool_calls.*"
      transform: "reconstruct_array_from_flattened"
      params:
        prefix: "gen_ai.completion.0.message.tool_calls"
        preserve_json_strings: true           # ← From provider schema!
        json_string_fields:
          - "function.arguments"              # ← From CRITICAL_FINDINGS!
```

**Key**: Provider schema informs the semantic convention mapping!

---

## 📝 Phase 3: YAML DSL Configuration

### **Purpose**

Create the **single source of truth** for detection, extraction, and mapping logic.

### **Two Types of YAML Configs**

#### **Type 1: Provider DSL** (Provider-centric)

**Location**: `config/dsl/providers/{provider}/`

**Files**:

1. **structure_patterns.yaml** - How to detect provider
   ```yaml
   patterns:
     openinference_openai:
       signature_fields:
         - "llm.model_name"
         - "llm.provider"
       confidence_weight: 0.95
       instrumentor_framework: "openinference"
   ```

2. **navigation_rules.yaml** - How to extract fields
   ```yaml
   navigation_rules:
     traceloop_tool_calls_flattened:
       source_field: "gen_ai.completion.0.message.tool_calls"
       extraction_method: "array_reconstruction"
       preserve_json_strings: true
   ```

3. **transforms.yaml** - How to transform data
   ```yaml
   transforms:
     extract_tool_calls:
       function_type: "array_reconstruction"
       implementation: "reconstruct_array_from_flattened"
       parameters:
         preserve_json_strings: true
   ```

4. **field_mappings.yaml** - How to map to HoneyHive schema
   ```yaml
   outputs:
     tool_calls:
       source_rule: "traceloop_tool_calls_flattened"
       transform: "extract_tool_calls"
       required: false
   ```

#### **Type 2: Semantic Convention DSL** (Instrumentor-centric)

**Location**: `config/semantic_conventions/{instrumentor}/`

**Files**:

```yaml
# config/semantic_conventions/traceloop/openai.yaml

version: '0.46.2'
instrumentor: traceloop
provider: openai

detection:
  signature_attributes: [...]
  constraints:
    "gen_ai.system": {"equals": "openai"}

mappings:
  outputs:
    tool_calls:
      source: "gen_ai.completion.0.message.tool_calls.*"
      transform: "reconstruct_array_from_flattened"
      params:
        prefix: "gen_ai.completion.0.message.tool_calls"
        preserve_json_strings: true
```

### **How They Work Together**

The compiler **merges** both types:
1. Provider DSL defines overall structure
2. Semantic conventions add instrumentor-specific details
3. Both compile to the same unified bundle

---

## 🔧 Phase 4: Bundle Compilation

### **Purpose**

Compile YAML configs into an **O(1) optimized bundle** for runtime.

### **Tool: Bundle Compiler**

**Script**: `scripts/compile_dsl_bundle.py`

**What it does**:
1. Loads all YAML configs (provider DSL + semantic conventions)
2. Merges and validates
3. Builds O(1) indexes:
   - **Signature index**: attribute set → provider (O(1) detection)
   - **Extractor index**: provider:instrumentor → steps (O(1) extraction)
   - **Mapping index**: provider → fields (O(1) mapping)
4. Outputs optimized JSON bundle

**Usage**:
```bash
python scripts/compile_dsl_bundle.py --output config/dsl/compiled/dsl-bundle.json
```

### **Bundle Format (O(1) Optimized)**

```json
{
  "version": "4.0",
  "build_timestamp": "2025-09-30T12:00:00Z",
  
  // ========================================
  // INDEX 1: O(1) Signature Index
  // ========================================
  "signature_index": {
    // Key: sorted attribute signature
    // Value: provider match
    "gen_ai.request.model|gen_ai.system|gen_ai.usage.prompt_tokens": {
      "provider": "openai",
      "instrumentor": "traceloop",
      "confidence": 0.90
    }
  },
  
  // ========================================
  // INDEX 2: O(1) Extractor Index
  // ========================================
  "extractors": {
    // Key: "provider:instrumentor"
    "openai:traceloop": {
      "steps": [
        {
          "operation": "direct_copy",
          "source": "gen_ai.request.model",
          "target": "model"
        },
        {
          "operation": "reconstruct_array_from_flattened",
          "source_prefix": "gen_ai.completion.0.message.tool_calls",
          "target": "tool_calls",
          "preserve_json_strings": true,
          "json_string_fields": ["function.arguments"]
        }
      ]
    }
  },
  
  // ========================================
  // INDEX 3: O(1) Mapping Index
  // ========================================
  "mappings": {
    // Key: provider
    "openai": {
      "outputs": {
        "tool_calls": {
          "source": "tool_calls",
          "required": false
        }
      }
    }
  },
  
  // ========================================
  // INDEX 4: Transform Registry
  // ========================================
  "transforms": {
    "reconstruct_array_from_flattened": {
      "description": "Reconstruct array from flattened attributes",
      "algorithm": "regex_index_extraction"
    }
  }
}
```

### **O(1) Performance**

```python
# Detection: O(1)
signature = "|".join(sorted(span.attributes.keys()))
match = bundle["signature_index"][signature]  # Hash lookup!

# Extraction: O(1) lookup + O(m) steps
extractor = bundle["extractors"][f"{provider}:{instrumentor}"]  # Hash lookup!

# Mapping: O(1) lookup + O(f) fields
mappings = bundle["mappings"][provider]  # Hash lookup!
```

**Complexity**: O(1) + O(m) + O(f) where m and f are small constants (~10-30)

---

## 🌍 Phase 5: Cross-Language Runtime

### **Purpose**

Load and interpret the bundle in **any language** with **no code changes**.

### **The Key Principle**

- **Bundle** = Data (JSON with O(1) indexes)
- **Interpreter** = Code (stable, written once)
- DSL changes → Bundle changes (no code changes!)

### **Implementation Per Language**

#### **Python Interpreter**

**File**: `src/honeyhive/tracer/processing/semantic_conventions/dsl_interpreter.py`

```python
class DSLInterpreter:
    def __init__(self, bundle_path: Path):
        with open(bundle_path) as f:
            self.bundle = json.load(f)
    
    def detect_provider(self, attributes: Dict) -> Optional[str]:
        """O(1) detection using signature index."""
        signature = "|".join(sorted(attributes.keys()))
        match = self.bundle["signature_index"].get(signature)
        return match["provider"] if match else None
    
    def extract_data(self, provider: str, instrumentor: str, attributes: Dict) -> Dict:
        """O(1) extraction using extractor index."""
        extractor_key = f"{provider}:{instrumentor}"
        extractor = self.bundle["extractors"][extractor_key]
        
        extracted = {}
        for step in extractor["steps"]:
            result = self._execute_step(step, attributes, extracted)
            if result is not None:
                extracted[step["target"]] = result
        
        return extracted
```

#### **TypeScript Interpreter**

**File**: `sdk/typescript/src/tracer/dsl-interpreter.ts`

```typescript
export class DSLInterpreter {
  private bundle: DSLBundle;
  
  constructor(bundlePath: string) {
    this.bundle = JSON.parse(fs.readFileSync(bundlePath, 'utf-8'));
  }
  
  detectProvider(attributes: Record<string, any>): string | null {
    const signature = Object.keys(attributes).sort().join('|');
    const match = this.bundle.signature_index[signature];
    return match ? match.provider : null;
  }
  
  extractData(provider: string, instrumentor: string, attributes: Record<string, any>): Record<string, any> {
    const extractorKey = `${provider}:${instrumentor}`;
    const extractor = this.bundle.extractors[extractorKey];
    
    const extracted: Record<string, any> = {};
    for (const step of extractor.steps) {
      const result = this.executeStep(step, attributes, extracted);
      if (result !== null) extracted[step.target] = result;
    }
    
    return extracted;
  }
}
```

#### **Go Interpreter**

**File**: `sdk/go/tracer/dsl_interpreter.go`

```go
type DSLInterpreter struct {
    bundle DSLBundle
}

func NewDSLInterpreter(bundlePath string) (*DSLInterpreter, error) {
    data, _ := ioutil.ReadFile(bundlePath)
    var bundle DSLBundle
    json.Unmarshal(data, &bundle)
    return &DSLInterpreter{bundle: bundle}, nil
}

func (d *DSLInterpreter) DetectProvider(attributes map[string]interface{}) string {
    keys := make([]string, 0, len(attributes))
    for k := range attributes {
        keys = append(keys, k)
    }
    sort.Strings(keys)
    signature := strings.Join(keys, "|")
    
    if match, ok := d.bundle.SignatureIndex[signature]; ok {
        return match.Provider
    }
    return ""
}
```

### **Key Point**

**All three languages**:
- Load the **same JSON bundle**
- Use the **same O(1) indexes**
- Execute the **same DSL operations**
- **No code changes** when bundle updates

---

## 🛠️ Tools & Utilities

### **1. Provider Schema Extraction**

```bash
# Extract OpenAI schema
python scripts/extract_provider_schema.py openai

# Output:
# provider_response_schemas/openai/v2025-01-30.json
# provider_response_schemas/openai/CRITICAL_FINDINGS.md
```

### **2. Semantic Convention Discovery**

```bash
# Discover Traceloop attributes
python scripts/analyze_instrumentor_source.py traceloop

# Output:
# config/semantic_conventions/traceloop/source_analysis.yaml
# config/semantic_conventions/traceloop/openai.yaml.template
```

### **3. DSL Bundle Compilation**

```bash
# Compile all YAML configs to O(1) bundle
python scripts/compile_dsl_bundle.py

# Output:
# config/dsl/compiled/dsl-bundle.json (with O(1) indexes)
```

### **4. Bundle Format Converter (NEW)**

**Purpose**: Convert bundle to language-specific optimized formats

**Script**: `scripts/convert_bundle_format.py`

```bash
# Convert to Python pickle (for performance)
python scripts/convert_bundle_format.py --input dsl-bundle.json \
                                        --output dsl-bundle.pkl \
                                        --format pickle

# Convert to MessagePack (compact binary)
python scripts/convert_bundle_format.py --input dsl-bundle.json \
                                        --output dsl-bundle.msgpack \
                                        --format msgpack

# Convert to CBOR (Go-friendly binary)
python scripts/convert_bundle_format.py --input dsl-bundle.json \
                                        --output dsl-bundle.cbor \
                                        --format cbor
```

**Supported Formats**:
- **JSON** (universal, human-readable, ~2MB)
- **Pickle** (Python, fastest, ~1MB)
- **MessagePack** (compact binary, ~1.5MB, all languages)
- **CBOR** (efficient binary, ~1.5MB, Go-friendly)

### **5. Coverage Validator (Future)**

```bash
# Validate DSL coverage against provider schema
python scripts/validate_dsl_coverage.py openai

# Output:
# Coverage: 85%
# Missing: tool_calls, refusal, audio
```

### **6. DSL Test Suite (Future)**

```bash
# Test DSL extraction against schema examples
python scripts/test_dsl_against_examples.py openai

# Output:
# 11/11 examples passed
# tool_calls.json: ✅ All fields extracted
# refusal.json: ✅ All fields extracted
```

---

## 🚀 Release Process

### **When DSL Changes**

```bash
# ========================================
# Step 1: Update YAML Sources
# ========================================
vim config/dsl/providers/openai/navigation_rules.yaml
# (Add tool_calls extraction)

# ========================================
# Step 2: Compile to Bundle
# ========================================
python scripts/compile_dsl_bundle.py

# Output: config/dsl/compiled/dsl-bundle.json

# ========================================
# Step 3: Convert to Language-Specific Formats
# ========================================
# Python (pickle for performance)
python scripts/convert_bundle_format.py \
    --input dsl-bundle.json \
    --output dsl-bundle.pkl \
    --format pickle

# TypeScript (keep JSON)
cp dsl-bundle.json sdk/typescript/src/tracer/

# Go (MessagePack for efficiency)
python scripts/convert_bundle_format.py \
    --input dsl-bundle.json \
    --output dsl-bundle.msgpack \
    --format msgpack
cp dsl-bundle.msgpack sdk/go/tracer/

# ========================================
# Step 4: Release SDKs (NO CODE CHANGES!)
# ========================================
# Python
cd sdk/python
poetry version patch
poetry build
poetry publish

# TypeScript
cd sdk/typescript
npm version patch
npm publish

# Go
cd sdk/go
git tag v1.2.3
git push --tags
```

### **Version Compatibility**

Bundle includes version number:
```json
{
  "version": "4.0",
  "min_interpreter_version": "1.0",
  "max_interpreter_version": "2.0"
}
```

Interpreters check compatibility:
```python
def load_bundle(bundle_path):
    bundle = json.load(open(bundle_path))
    
    if not is_compatible(bundle["version"], INTERPRETER_VERSION):
        raise ValueError(f"Bundle v{bundle['version']} not compatible with interpreter v{INTERPRETER_VERSION}")
    
    return bundle
```

---

## 📊 Complete Flow Example

### **Scenario: Add OpenAI Tool Calls Support**

#### **1. Provider Schema** (Already Extracted)
```json
// provider_response_schemas/openai/v2025-01-30.json
{
  "tool_calls": {
    "type": "array",
    "items": {
      "properties": {
        "function": {
          "properties": {
            "arguments": {
              "type": "string",        // ← JSON string!
              "format": "json-string"  // ← Critical!
            }
          }
        }
      }
    }
  }
}
```

#### **2. Semantic Convention** (Already Discovered)
```yaml
# config/semantic_conventions/traceloop/source_analysis.yaml
discovered_attributes:
  - "gen_ai.completion.0.message.tool_calls.0.id"
  - "gen_ai.completion.0.message.tool_calls.0.function.name"
  - "gen_ai.completion.0.message.tool_calls.0.function.arguments"
```

#### **3. YAML DSL** (Human Creates Using Above)
```yaml
# config/dsl/providers/openai/navigation_rules.yaml
traceloop_tool_calls_flattened:
  source_field: "gen_ai.completion.0.message.tool_calls"
  extraction_method: "array_reconstruction"
  preserve_json_strings: true           # ← From schema!
  json_string_fields:
    - "function.arguments"              # ← From schema!
```

#### **4. Bundle Compilation** (Automatic)
```bash
python scripts/compile_dsl_bundle.py
```

```json
// dsl-bundle.json (auto-generated)
{
  "extractors": {
    "openai:traceloop": {
      "steps": [
        {
          "operation": "reconstruct_array_from_flattened",
          "source_prefix": "gen_ai.completion.0.message.tool_calls",
          "target": "tool_calls",
          "preserve_json_strings": true,
          "json_string_fields": ["function.arguments"]
        }
      ]
    }
  }
}
```

#### **5. Runtime** (Zero Code Changes)
```python
# Python interpreter (unchanged)
interpreter = DSLInterpreter("dsl-bundle.json")  # New bundle, same code!

extracted = interpreter.extract_data("openai", "traceloop", span.attributes)
# → extracted["tool_calls"] = [{"function": {"arguments": '{"location": "SF"}'}}]
# → JSON string preserved! ✅
```

---

## 📋 Summary

### **The Complete System**

1. **Provider Schemas** → Understand API responses
2. **Semantic Conventions** → Discover instrumentor attributes
3. **YAML DSL** → Single source of truth (informed by 1 & 2)
4. **Bundle Compilation** → O(1) optimized indexes
5. **Cross-Language Runtime** → Load bundle, no code changes

### **Key Benefits**

✅ **Config-Driven**: DSL changes → bundle changes (no code!)  
✅ **O(1) Performance**: Pre-computed indexes  
✅ **Cross-Language**: Same bundle for Python/TypeScript/Go  
✅ **Data Fidelity**: Provider schemas ensure accuracy  
✅ **Maintainable**: Programmatic discovery + human curation  
✅ **Scalable**: Works with 10 or 100 providers  

### **File Locations**

```
python-sdk/
├── .agent-os/standards/architecture/
│   └── MASTER_DSL_ARCHITECTURE.md        # ← THIS FILE
│
├── provider_response_schemas/            # Phase 1
│   └── {provider}/
│       ├── v{version}.json
│       └── CRITICAL_FINDINGS.md
│
├── config/
│   ├── dsl/providers/{provider}/         # Phase 3a
│   │   ├── structure_patterns.yaml
│   │   ├── navigation_rules.yaml
│   │   ├── transforms.yaml
│   │   └── field_mappings.yaml
│   │
│   ├── semantic_conventions/{instrumentor}/  # Phase 3b
│   │   └── {provider}.yaml
│   │
│   └── dsl/compiled/                     # Phase 4
│       └── dsl-bundle.json
│
├── scripts/
│   ├── extract_provider_schema.py        # Phase 1
│   ├── analyze_instrumentor_source.py    # Phase 2
│   ├── compile_dsl_bundle.py             # Phase 4
│   └── convert_bundle_format.py          # Utility
│
└── src/honeyhive/tracer/processing/semantic_conventions/
    ├── dsl_interpreter.py                # Phase 5 (Python)
    └── dsl-bundle.{json|pkl}             # Runtime bundle
```

---

**Last Updated**: 2025-09-30  
**Status**: Unified architecture complete  
**Next Steps**: Implement missing tools (bundle compiler, format converter)

