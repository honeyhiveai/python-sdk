# Semantic Convention DSL Architecture

**Date**: 2025-09-30  
**Purpose**: Convert semantic conventions to YAML DSL with programmatic source generation  
**Problem**: Semantic conventions are manually created Python files, should be systematic and language-agnostic

---

## 🎯 The Vision

### **Unified DSL System**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INSTRUMENTOR SOURCE ANALYSIS (Programmatic Discovery)    │
│    Scan instrumentor repositories to discover attributes     │
│                                                             │
│    Input:  Instrumentor GitHub repos (Traceloop, OpenLit)  │
│    Output: Discovered attributes, patterns, versions       │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SEMANTIC CONVENTION YAML DSL (Human-Curated)             │
│    Define detection and mapping rules in YAML               │
│                                                             │
│    config/semantic_conventions/{instrumentor}/              │
│    ├── detection_patterns.yaml  # How to detect            │
│    ├── attribute_mappings.yaml  # How to map               │
│    └── versions.yaml             # Version tracking         │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. JSON IR + CODE GENERATION (Cross-Language)               │
│    Compile to JSON IR, then generate language-specific code │
│                                                             │
│    Output: Python/TypeScript/Go implementations             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Part 1: Programmatic Instrumentor Discovery

### **Instrumentor Source Analyzer**

**Script**: `scripts/analyze_instrumentor_source.py`

```python
#!/usr/bin/env python3
"""
Analyze instrumentor source code to discover semantic convention attributes.

This script clones and analyzes instrumentor repositories to extract:
- Attribute names they set on spans
- Detection patterns (signature attributes)
- Version information
- Provider support
"""

import os
import git
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Any
import yaml


class InstrumentorAnalyzer:
    """Analyze instrumentor source code for semantic convention discovery."""
    
    INSTRUMENTORS = {
        "traceloop": {
            "repo": "https://github.com/traceloop/openllmetry",
            "base_path": "packages/opentelemetry-instrumentation-*",
            "attribute_patterns": [
                r'span\.set_attribute\(["\']([^"\']+)["\']',
                r'@staticmethod\s+def\s+(\w+)\(\)',
            ]
        },
        "openinference": {
            "repo": "https://github.com/Arize-ai/openinference",
            "base_path": "python/instrumentation/openinference-instrumentation-*",
            "attribute_patterns": [
                r'SpanAttributes\.([A-Z_]+)',
                r'["\']([a-z]+\.[a-z_.]+)["\']',
            ]
        },
        "openlit": {
            "repo": "https://github.com/openlit/openlit",
            "base_path": "sdk/python/src/openlit/instrumentation/*",
            "attribute_patterns": [
                r'span\.set_attribute\(["\']([^"\']+)["\']',
                r'gen_ai\.([a-z_.]+)',
            ]
        }
    }
    
    def analyze_instrumentor(self, name: str) -> Dict[str, Any]:
        """Analyze an instrumentor's source code."""
        
        config = self.INSTRUMENTORS[name]
        
        # Clone or update repo
        repo_path = self._ensure_repo(name, config["repo"])
        
        # Find provider instrumentation packages
        providers = self._discover_providers(repo_path, config["base_path"])
        
        # Analyze each provider
        results = {
            "instrumentor": name,
            "version": self._get_version(repo_path),
            "last_updated": self._get_last_commit(repo_path),
            "providers": {}
        }
        
        for provider in providers:
            provider_data = self._analyze_provider(
                repo_path, 
                provider, 
                config["attribute_patterns"]
            )
            results["providers"][provider] = provider_data
        
        return results
    
    def _analyze_provider(
        self, 
        repo_path: Path, 
        provider: str, 
        patterns: List[str]
    ) -> Dict[str, Any]:
        """Analyze a specific provider's instrumentation."""
        
        # Find Python files for this provider
        provider_files = list(Path(repo_path).glob(f"**/{provider}/**/*.py"))
        
        attributes_found = set()
        signature_attributes = set()
        
        for file_path in provider_files:
            with open(file_path) as f:
                content = f.read()
                
                # Extract attributes using patterns
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    attributes_found.update(matches)
                
                # Identify signature attributes (commonly set ones)
                if "def _set_span_attribute" in content or "set_attribute" in content:
                    # Parse AST to find attribute setting patterns
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            if hasattr(node.func, 'attr') and node.func.attr == 'set_attribute':
                                if node.args and isinstance(node.args[0], ast.Constant):
                                    attr_name = node.args[0].value
                                    signature_attributes.add(attr_name)
        
        return {
            "all_attributes": sorted(list(attributes_found)),
            "signature_attributes": sorted(list(signature_attributes)),
            "file_count": len(provider_files),
            "analyzed_files": [str(f.relative_to(repo_path)) for f in provider_files]
        }
    
    def _ensure_repo(self, name: str, repo_url: str) -> Path:
        """Clone or update instrumentor repository."""
        repo_dir = Path(f"/tmp/instrumentor_analysis/{name}")
        
        if repo_dir.exists():
            # Pull latest
            repo = git.Repo(repo_dir)
            repo.remotes.origin.pull()
        else:
            # Clone
            repo_dir.parent.mkdir(parents=True, exist_ok=True)
            git.Repo.clone_from(repo_url, repo_dir)
        
        return repo_dir
    
    def _discover_providers(self, repo_path: Path, pattern: str) -> List[str]:
        """Discover which providers are supported."""
        matching_dirs = list(repo_path.glob(pattern))
        providers = []
        
        for dir_path in matching_dirs:
            # Extract provider name from path
            # e.g., "opentelemetry-instrumentation-openai" -> "openai"
            provider = dir_path.name.split("-")[-1]
            providers.append(provider)
        
        return providers
    
    def _get_version(self, repo_path: Path) -> str:
        """Get instrumentor version from setup.py or pyproject.toml."""
        # Implementation to extract version
        setup_py = repo_path / "setup.py"
        if setup_py.exists():
            with open(setup_py) as f:
                content = f.read()
                match = re.search(r'version=["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
        return "unknown"
    
    def _get_last_commit(self, repo_path: Path) -> str:
        """Get last commit date."""
        repo = git.Repo(repo_path)
        return repo.head.commit.committed_datetime.isoformat()
    
    def generate_yaml_template(self, analysis: Dict[str, Any], provider: str) -> str:
        """Generate YAML template from analysis."""
        
        provider_data = analysis["providers"].get(provider, {})
        
        template = f"""# {analysis['instrumentor'].title()} Semantic Convention for {provider.title()}
# Auto-discovered from source analysis
# Instrumentor version: {analysis['version']}
# Last updated: {analysis['last_updated']}

version: '{analysis['version']}'
instrumentor: {analysis['instrumentor']}
provider: {provider}

# Detection patterns
detection:
  # Required attributes that MUST be present
  signature_attributes:
"""
        
        # Add discovered signature attributes
        for attr in provider_data.get("signature_attributes", [])[:5]:  # Top 5
            template += f"    - \"{attr}\"\n"
        
        template += """
  # Optional attributes that MAY be present
  optional_attributes:
"""
        
        # Add other discovered attributes
        other_attrs = set(provider_data.get("all_attributes", [])) - set(provider_data.get("signature_attributes", []))
        for attr in sorted(list(other_attrs))[:10]:  # Top 10
            template += f"    - \"{attr}\"\n"
        
        template += """
  # Confidence weight for detection
  confidence_weight: 0.90
  
  # Priority (lower = higher priority)
  priority: 1

# Attribute mappings (to be manually filled)
mappings:
  inputs:
    # Map instrumentor attributes to HoneyHive inputs schema
    # Example:
    # messages:
    #   source: "llm.input_messages.*"
    #   transform: "reconstruct_array_from_flattened"
    
  outputs:
    # Map instrumentor attributes to HoneyHive outputs schema
    
  config:
    # Map instrumentor attributes to HoneyHive config schema
    
  metadata:
    # Map instrumentor attributes to HoneyHive metadata schema

# Source tracking
source_analysis:
  discovered_attributes: {len(provider_data.get('all_attributes', []))}
  analyzed_files: {provider_data.get('file_count', 0)}
  analysis_date: {analysis['last_updated']}
"""
        
        return template


def main():
    """Analyze all instrumentors and generate YAML templates."""
    
    analyzer = InstrumentorAnalyzer()
    
    for instrumentor_name in ["traceloop", "openinference", "openlit"]:
        print(f"\n=== Analyzing {instrumentor_name} ===")
        
        # Analyze source
        analysis = analyzer.analyze_instrumentor(instrumentor_name)
        
        # Save analysis results
        output_dir = Path(f"config/semantic_conventions/{instrumentor_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save raw analysis
        with open(output_dir / "source_analysis.yaml", "w") as f:
            yaml.dump(analysis, f, default_flow_style=False)
        
        print(f"  Version: {analysis['version']}")
        print(f"  Providers found: {len(analysis['providers'])}")
        
        # Generate YAML templates for each provider
        for provider in analysis["providers"].keys():
            template = analyzer.generate_yaml_template(analysis, provider)
            
            template_path = output_dir / f"{provider}.yaml"
            with open(template_path, "w") as f:
                f.write(template)
            
            print(f"    - {provider}: {template_path}")


if __name__ == "__main__":
    main()
```

---

## 📋 Part 2: Semantic Convention YAML DSL

### **Directory Structure**

```
config/semantic_conventions/
├── traceloop/
│   ├── openai.yaml              # Traceloop → OpenAI mapping
│   ├── anthropic.yaml           # Traceloop → Anthropic mapping
│   ├── versions.yaml            # Version tracking
│   └── source_analysis.yaml     # Auto-discovered attributes
│
├── openinference/
│   ├── openai.yaml
│   ├── anthropic.yaml
│   ├── versions.yaml
│   └── source_analysis.yaml
│
├── openlit/
│   ├── openai.yaml
│   ├── anthropic.yaml
│   ├── versions.yaml
│   └── source_analysis.yaml
│
└── README.md
```

### **YAML DSL Specification**

**File**: `config/semantic_conventions/traceloop/openai.yaml`

```yaml
# Traceloop Semantic Convention for OpenAI
# Maps Traceloop's gen_ai.* attributes to HoneyHive schema

version: '0.46.2'
instrumentor: traceloop
provider: openai

# Detection patterns (how to identify this instrumentor + provider)
detection:
  # Attributes that MUST be present
  signature_attributes:
    - "gen_ai.system"
    - "gen_ai.request.model"
    - "gen_ai.usage.prompt_tokens"
  
  # Attributes that MAY be present (boost confidence if found)
  optional_attributes:
    - "gen_ai.usage.completion_tokens"
    - "gen_ai.response.model"
    - "gen_ai.request.temperature"
    - "gen_ai.completion"
    - "gen_ai.prompt"
  
  # Attribute value constraints
  constraints:
    "gen_ai.system":
      equals: "openai"  # Must be "openai" for this mapping
  
  # Confidence weight (0.0-1.0)
  confidence_weight: 0.90
  
  # Priority (lower = checked first)
  priority: 2

# Attribute mappings to HoneyHive schema
mappings:
  inputs:
    messages:
      # Reconstruct messages array from flattened attributes
      source: "gen_ai.prompt.*"
      transform: "reconstruct_array_from_flattened"
      params:
        prefix: "gen_ai.prompt"
        preserve_json_strings: false
      fallback:
        # If gen_ai.prompt.* not found, try gen_ai.request.messages.*
        source: "gen_ai.request.messages.*"
        transform: "reconstruct_array_from_flattened"
        params:
          prefix: "gen_ai.request.messages"
    
    system_prompt:
      source: "gen_ai.request.system_prompt"
      transform: "direct_copy"
    
    prompt:
      # For completion-style requests (legacy)
      source: "gen_ai.request.prompt"
      transform: "direct_copy"
  
  outputs:
    content:
      source: "gen_ai.completion.0.content"
      transform: "direct_copy"
      fallback:
        source: "gen_ai.completion"
        transform: "extract_first_if_array"
    
    tool_calls:
      source: "gen_ai.completion.0.message.tool_calls.*"
      transform: "reconstruct_array_from_flattened"
      params:
        prefix: "gen_ai.completion.0.message.tool_calls"
        preserve_json_strings: true
        json_string_fields:
          - "function.arguments"
    
    refusal:
      source: "gen_ai.completion.0.message.refusal"
      transform: "direct_copy"
    
    role:
      source: "gen_ai.completion.0.role"
      transform: "direct_copy"
      fallback:
        value: "assistant"  # Default if not present
    
    finish_reason:
      source: "gen_ai.response.finish_reasons.0"
      transform: "direct_copy"
      fallback:
        source: "gen_ai.completion.0.finish_reason"
        transform: "direct_copy"
  
  config:
    temperature:
      source: "gen_ai.request.temperature"
      transform: "direct_copy"
    
    max_tokens:
      source: "gen_ai.request.max_tokens"
      transform: "direct_copy"
    
    top_p:
      source: "gen_ai.request.top_p"
      transform: "direct_copy"
    
    frequency_penalty:
      source: "gen_ai.request.frequency_penalty"
      transform: "direct_copy"
    
    presence_penalty:
      source: "gen_ai.request.presence_penalty"
      transform: "direct_copy"
    
    streaming:
      source: "gen_ai.request.streaming"
      transform: "direct_copy"
  
  metadata:
    model:
      source: "gen_ai.response.model"
      transform: "direct_copy"
      fallback:
        source: "gen_ai.request.model"
        transform: "direct_copy"
    
    provider:
      value: "openai"  # Static value
    
    operation_name:
      source: "gen_ai.operation.name"
      transform: "direct_copy"
    
    prompt_tokens:
      source: "gen_ai.usage.prompt_tokens"
      transform: "direct_copy"
    
    completion_tokens:
      source: "gen_ai.usage.completion_tokens"
      transform: "direct_copy"
    
    total_tokens:
      source: "gen_ai.usage.total_tokens"
      transform: "direct_copy"

# Transform definitions (shared across instrumentors)
transforms:
  - reconstruct_array_from_flattened
  - direct_copy
  - extract_first_if_array

# Source tracking
source:
  discovered_from: "https://github.com/traceloop/openllmetry"
  version: "0.46.2"
  last_verified: "2025-09-30"
  analysis_method: "programmatic_source_scan"
```

---

## 📋 Part 3: Unified Compilation Pipeline

### **Enhanced Compilation Flow**

```bash
# Step 1: Discover attributes from instrumentor source (optional, periodic)
python scripts/analyze_instrumentor_source.py traceloop
# → Creates: config/semantic_conventions/traceloop/source_analysis.yaml
# → Creates: config/semantic_conventions/traceloop/{provider}.yaml (templates)

# Step 2: Human curates the YAML (fill in mappings)
vim config/semantic_conventions/traceloop/openai.yaml

# Step 3: Compile semantic conventions to JSON IR
python scripts/compile_semantic_conventions.py
# → Creates: config/dsl/compiled/semantic_conventions.json

# Step 4: Compile provider DSL to JSON IR
python scripts/compile_provider_dsl.py
# → Creates: config/dsl/compiled/providers.bundle.json

# Step 5: Merge and generate code for all languages
python scripts/compile_to_json_ir.py --all
# → Creates complete JSON IR bundle

# Step 6: Generate language-specific code
python scripts/codegen/generate_python.py
npm run codegen:typescript
go run scripts/codegen/generate_go.go
```

---

## 📋 Part 4: Unified JSON IR Format

### **Semantic Conventions JSON IR**

**File**: `config/dsl/compiled/semantic_conventions.json`

```json
{
  "version": "1.0",
  "instrumentors": {
    "traceloop": {
      "version": "0.46.2",
      "providers": {
        "openai": {
          "detection": {
            "signature_attributes": [
              "gen_ai.system",
              "gen_ai.request.model",
              "gen_ai.usage.prompt_tokens"
            ],
            "optional_attributes": [
              "gen_ai.usage.completion_tokens",
              "gen_ai.response.model"
            ],
            "constraints": {
              "gen_ai.system": {"equals": "openai"}
            },
            "confidence_weight": 0.90,
            "priority": 2
          },
          "mappings": {
            "inputs": {
              "messages": {
                "source": "gen_ai.prompt.*",
                "transform": "reconstruct_array_from_flattened",
                "params": {
                  "prefix": "gen_ai.prompt",
                  "preserve_json_strings": false
                },
                "fallback": {
                  "source": "gen_ai.request.messages.*",
                  "transform": "reconstruct_array_from_flattened",
                  "params": {"prefix": "gen_ai.request.messages"}
                }
              }
            },
            "outputs": {
              "tool_calls": {
                "source": "gen_ai.completion.0.message.tool_calls.*",
                "transform": "reconstruct_array_from_flattened",
                "params": {
                  "prefix": "gen_ai.completion.0.message.tool_calls",
                  "preserve_json_strings": true,
                  "json_string_fields": ["function.arguments"]
                }
              }
            }
          }
        }
      }
    },
    "openinference": {
      "version": "0.1.31",
      "providers": {
        "openai": {
          "detection": {...},
          "mappings": {...}
        }
      }
    }
  }
}
```

---

## 🔄 Integration with Provider DSL

### **Unified System**

Both provider DSL and semantic convention DSL compile to the same JSON IR format:

```
Provider DSL (YAML)           Semantic Convention DSL (YAML)
├── structure_patterns.yaml   ├── detection_patterns.yaml
├── navigation_rules.yaml     ├── attribute_mappings.yaml
├── transforms.yaml           └── versions.yaml
└── field_mappings.yaml

              ↓                              ↓
              
         JSON IR (Unified Format)
         ├── providers.bundle.json
         ├── semantic_conventions.json
         ├── extractors.json
         ├── mappings.json
         └── transforms.json

                      ↓
                      
         Code Generation (All Languages)
         ├── compiled_bundle.py
         ├── compiled_bundle.ts
         └── compiled_bundle.go
```

---

## 🎯 Benefits of This Approach

### **1. Programmatic Discovery** ✅
- Scan instrumentor source code to find attributes
- Auto-generate YAML templates
- Reduce manual work and errors

### **2. Human Curation** ✅
- Discovered attributes → YAML templates
- Humans fill in mappings, transforms, fallbacks
- Version control tracks changes

### **3. Single Source of Truth** ✅
- YAML DSL for both providers and semantic conventions
- Consistent format, tooling, workflows
- Language-agnostic compilation

### **4. Cross-Language Support** ✅
- YAML → JSON IR → Python/TypeScript/Go
- Each SDK gets optimized native code
- Same logic, different languages

### **5. Maintainability** ✅
- Update YAML when instrumentor changes
- Rerun source analysis to discover new attributes
- Regenerate code automatically

---

## 📋 Migration Path

### **Phase 1: Build Source Analyzer**
```bash
scripts/analyze_instrumentor_source.py
```
- Clone instrumentor repos
- Scan source code for attributes
- Generate YAML templates

### **Phase 2: Convert Existing Semantic Conventions**
```bash
scripts/convert_semantic_conventions_to_yaml.py
```
- Read existing Python definitions
- Convert to YAML DSL format
- Validate against source analysis

### **Phase 3: Build Semantic Convention Compiler**
```bash
scripts/compile_semantic_conventions.py
```
- Load YAML DSL
- Compile to JSON IR
- Merge with provider DSL

### **Phase 4: Update Code Generation**
- Enhance existing codegen to handle semantic conventions
- Generate language-specific implementations
- Deprecate manual Python definitions

### **Phase 5: Automate Updates**
- Periodic source analysis (weekly/monthly)
- Detect new instrumentor versions
- Auto-generate updated YAML templates
- PR workflow for human curation

---

## 🔧 Implementation Priority

### **Immediate (This Week)**
1. ✅ Document architecture (this file)
2. ⏳ Build `analyze_instrumentor_source.py`
3. ⏳ Test on Traceloop OpenAI (prove concept)

### **Short-Term (Next 2 Weeks)**
1. Build semantic convention compiler
2. Convert existing definitions to YAML
3. Integrate with provider DSL compilation

### **Long-Term (Next Month)**
1. Full automation (source analysis → YAML → code)
2. Deprecate manual Python definitions
3. Add to CI/CD pipeline

---

**Last Updated**: 2025-09-30  
**Status**: Architecture designed, ready to implement  
**Next**: Build instrumentor source analyzer

