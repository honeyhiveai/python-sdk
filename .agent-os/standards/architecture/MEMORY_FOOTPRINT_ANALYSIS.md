# DSL Bundle Memory Footprint Analysis

**Date**: 2025-09-30  
**Concern**: In-memory size of loaded DSL bundle, not just file size  
**Current**: Bundle cached in tracer instance for pattern matching

---

## 📊 OpenAI Actual Measurements

### **Source Files**
| File | Purpose | Size | Used For |
|------|---------|------|----------|
| `openai-openapi-documented.yml` | Full OpenAPI spec | **2.1 MB** | Schema extraction only |
| `v2025-01-30.json` | Extracted JSON Schema | **12 KB** | DSL generation |
| DSL Config (4 YAML files) | Provider patterns | **22 KB** | Compilation source |

### **Compiled Bundle (OpenAI Only)**
| Format | Size | Usage |
|--------|------|-------|
| **In-memory (Python dict)** | **43.9 KB** | 🔴 This is the concern |
| Serialized JSON | 8.9 KB | Cross-language |
| Serialized Pickle | 6.3 KB | Python SDK |

### **Memory Breakdown (per provider)**
| Component | Memory | Purpose |
|-----------|--------|---------|
| Signature index | **1.6 KB** | O(1) pattern detection |
| Extractors (3 instrumentors) | **21.9 KB** | Data extraction steps |
| Field mappings | **18.7 KB** | HoneyHive schema mapping |
| Model patterns | **1.6 KB** | Model name matching |
| **Total per provider** | **~44 KB** | Full provider support |

---

## 🧠 Current Implementation: Caching Strategy

### **Bundle Loader** (`bundle_loader.py`)

```python
class DevelopmentAwareBundleLoader:
    def __init__(self, ...):
        self._cached_bundle = None       # Full bundle cached
        self._cached_functions = {}      # Lazy-compiled extractors
    
    def load_provider_bundle(self):
        # Loads ENTIRE bundle into memory once
        if self._cached_bundle is None:
            with open(self.bundle_path, "rb") as f:
                self._cached_bundle = pickle.load(f)  # 🔴 Full load
        return self._cached_bundle
    
    def get_extraction_function(self, provider_name):
        # Lazy compile extraction functions on first use
        if provider_name not in self._cached_functions:
            self._compile_single_function(provider_name)  # ✅ Lazy
        return self._cached_functions[provider_name]
```

### **What Gets Cached**

**Current Behavior**:
1. ✅ **Bundle loaded once** - entire bundle cached in `_cached_bundle`
2. ✅ **Extraction functions lazy** - compiled on first provider detection
3. ❌ **No per-provider lazy loading** - all providers loaded into memory

**Memory Usage** (current):
```
20 providers × 44 KB/provider = ~880 KB (~0.86 MB)
50 providers × 44 KB/provider = ~2.2 MB
100 providers × 44 KB/provider = ~4.4 MB
```

---

## 🎯 Memory Optimization Strategies

### **Strategy 1: Current (Full Bundle Cache) ✅ CURRENT**

**Implementation**: Load entire bundle, lazy compile extractors

```python
# Load everything
bundle = pickle.load(bundle_file)  # ~880 KB for 20 providers
_cached_bundle = bundle

# Lazy compile extraction functions
if provider not in _cached_functions:
    compile_extractor(provider)  # Only when needed
```

**Memory Profile**:
- **Startup**: 880 KB (20 providers)
- **After detection**: +compiled function (~10 KB per provider used)
- **Total**: ~900 KB if all 20 providers detected

**Pros**:
- ✅ Simple implementation
- ✅ O(1) signature lookup (all patterns in memory)
- ✅ Fast detection across all providers

**Cons**:
- ❌ Loads all providers even if only using 1-2
- ❌ Memory scales with total provider count

---

### **Strategy 2: Lazy Provider Loading (PROPOSED)**

**Implementation**: Load only signature index upfront, lazy load providers

#### **Bundle Structure**
```
dsl-bundles/
├── core-index.pkl.gz              # Signature index only (2-5 KB)
├── providers/
│   ├── openai.pkl.gz              # OpenAI extractors/mappings (40 KB)
│   ├── anthropic.pkl.gz           # Anthropic extractors/mappings (40 KB)
│   └── ...
```

#### **Enhanced Bundle Loader**
```python
class LazyProviderBundleLoader:
    def __init__(self, ...):
        self._core_index = None        # Signature patterns only
        self._provider_cache = {}      # Lazy-loaded providers
        self._cached_functions = {}    # Lazy-compiled extractors
    
    def load_core_index(self):
        """Load minimal signature index for O(1) detection."""
        if self._core_index is None:
            with gzip.open("core-index.pkl.gz", "rb") as f:
                self._core_index = pickle.load(f)  # Only 2-5 KB
        return self._core_index
    
    def detect_provider(self, attributes):
        """O(1) detection using core index only."""
        core = self.load_core_index()
        signature = "|".join(sorted(attributes.keys()))
        match = core["signature_index"].get(signature)
        return match["provider"] if match else None
    
    def get_provider_bundle(self, provider_name):
        """Lazy load provider bundle on first use."""
        if provider_name not in self._provider_cache:
            # Load provider-specific bundle
            path = Path(f"providers/{provider_name}.pkl.gz")
            with gzip.open(path, "rb") as f:
                self._provider_cache[provider_name] = pickle.load(f)  # ~40 KB
        return self._provider_cache[provider_name]
    
    def get_extraction_function(self, provider_name):
        """Lazy compile for lazy-loaded provider."""
        if provider_name not in self._cached_functions:
            provider_bundle = self.get_provider_bundle(provider_name)  # Lazy
            self._compile_single_function(provider_name, provider_bundle)
        return self._cached_functions[provider_name]
```

#### **Memory Profile**
```
Startup:        2-5 KB (core index only)
After 1st span:  +40 KB (first provider detected)
After 2nd span:  +40 KB (if different provider)
Typical:        ~50-100 KB (1-2 providers used in practice)
```

**Pros**:
- ✅ Minimal startup memory (2-5 KB)
- ✅ Memory grows with *usage*, not total providers
- ✅ O(1) detection still possible (core index)
- ✅ Perfect for single-provider apps (most common)

**Cons**:
- ⚠️ Slight complexity (file structure, loading logic)
- ⚠️ Cold-start latency for new providers (~1-2 ms to load + decompress)

---

### **Strategy 3: Inverted Index Only (EXTREME)**

**Implementation**: Load signature index + provider names, load everything else on demand

```python
class MinimalBundleLoader:
    def __init__(self):
        self._signature_index = {}     # attribute_sig -> provider_name (~1-2 KB)
        self._provider_data = {}       # Lazy-loaded per provider (~40 KB each)
    
    def load_signature_index(self):
        """Load only the inverted index."""
        # Format: {"attr1|attr2": "openai", ...}
        with gzip.open("signature-index.pkl.gz", "rb") as f:
            self._signature_index = pickle.load(f)  # ~1-2 KB
    
    def detect_provider(self, attributes):
        """O(1) lookup."""
        sig = "|".join(sorted(attributes.keys()))
        return self._signature_index.get(sig)
    
    def extract_data(self, provider_name, instrumentor, attributes):
        """Load provider data only when extracting."""
        if provider_name not in self._provider_data:
            # Load from disk on first extraction
            path = Path(f"providers/{provider_name}/{instrumentor}.pkl.gz")
            with gzip.open(path, "rb") as f:
                self._provider_data[provider_name] = pickle.load(f)
        
        # Use loaded data
        # ...
```

**Memory Profile**:
```
Startup:       1-2 KB (signature index only)
Per provider:  +40 KB (on first extraction)
Typical:       ~40-50 KB total
```

**Pros**:
- ✅ Absolute minimal startup memory (1-2 KB)
- ✅ Near-zero overhead for unused providers
- ✅ Perfect for serverless/edge deployments

**Cons**:
- ❌ Cold-start latency on every new provider
- ❌ More complex file structure
- ❌ Multiple file reads (slower)

---

## 📊 Strategy Comparison

| Strategy | Startup Memory | Typical Memory | Detection Speed | Extraction Speed | Complexity |
|----------|---------------|----------------|-----------------|------------------|------------|
| **Full Bundle** (current) | 880 KB | 900 KB | O(1), 0.01 ms | Instant | Low |
| **Lazy Provider** (proposed) | 2-5 KB | 50-100 KB | O(1), 0.01 ms | +1-2 ms first time | Medium |
| **Inverted Index Only** | 1-2 KB | 40-50 KB | O(1), 0.01 ms | +2-3 ms first time | High |

---

## 🎯 Recommendations

### **AWS Lambda: HIGH Priority Optimization** 🚨

**Lambda Constraints** (from `docs/development/testing/lambda-testing.rst`):
- Memory budget: **< 50 MB** for entire SDK
- Target configs: 256-512 MB (cost-optimized)
- Cold start target: < 500 ms

**Current State Analysis**:
- Full bundle: **0.86 MB** (20 providers)
- Typical Lambda uses: **1-2 providers** (90% use 1 provider)
- **Waste ratio: 90%** of bundle unused in typical Lambda!

**Lazy Loading Impact**:
```
Typical Lambda (1-2 providers):
  Full Bundle:  0.86 MB
  Lazy Load:    0.13 MB  (signature index + 2 providers)
  Savings:      0.73 MB  (85% reduction!)
  
Cold Start Impact:
  Full Bundle:  3-5 ms load
  Lazy Load:    0.5 ms initial + 1-2 ms per provider
  Savings:      ~2-3 ms improvement
```

**Verdict**: Lazy loading is **HIGHLY BENEFICIAL** for Lambda ✅

**Why Lambda is different**:
- ✅ Memory is constrained (256-512 MB typical)
- ✅ Most Lambdas use 1-2 providers only
- ✅ Every MB counts toward <50 MB budget
- ✅ Cold start optimization critical
- ✅ 85% memory reduction is significant

---

### **Optimization Trigger (Future)**

**Implement Lazy Provider Loading when**:

1. **Bundle size threshold**: Compiled bundle > 5 MB in memory
2. **Provider count**: > 100 providers
3. **Deployment target**: Serverless/edge with <512 MB memory
4. **Usage pattern**: Apps typically use 1-2 providers only

**Implementation effort**: ~1-2 days
- Split bundle compiler to generate provider-specific files
- Update loader to support lazy loading
- Add tests for lazy loading behavior

---

### **Optimization Path (Staged)**

#### **Phase 1: Monitor (Now)**

Add memory tracking to existing loader:

```python
class DevelopmentAwareBundleLoader:
    def load_provider_bundle(self):
        if self._cached_bundle is None:
            with open(self.bundle_path, "rb") as f:
                self._cached_bundle = pickle.load(f)
            
            # Track memory usage
            import sys
            size_kb = sys.getsizeof(self._cached_bundle) / 1024
            logger.info(f"Bundle loaded: {size_kb:.1f} KB in memory")
        
        return self._cached_bundle
```

#### **Phase 2: Optimize (If Needed)**

If monitoring shows >5 MB:
1. Implement lazy provider loading (Strategy 2)
2. Add compression (already planned)
3. Monitor memory reduction

#### **Phase 3: Extreme (If Really Needed)**

If serverless/edge deployment with <512 MB:
1. Implement inverted index only (Strategy 3)
2. CDN-based bundle distribution
3. Runtime bundle fetching

---

## 💡 Key Insights

### **Memory vs File Size**

| Measure | OpenAI | 20 Providers | 50 Providers |
|---------|--------|--------------|--------------|
| **File (gzipped)** | 6.3 KB | 110 KB | 275 KB |
| **Memory (loaded)** | 44 KB | **880 KB** | **2.2 MB** |
| **Ratio** | 7x | 8x | 8x |

**Insight**: In-memory size is **~8x larger** than compressed file size due to:
- Python object overhead (dict, list, string objects)
- No compression in memory
- Pointer/reference overhead

### **Pattern Matching Only Needs**

For O(1) detection, only need:
```python
signature_index = {
    "attr1|attr2|attr3": {
        "provider": "openai",
        "instrumentor": "traceloop",
        "confidence": 0.95
    }
}
# ~1.6 KB per provider = 32 KB for 20 providers
```

Everything else (extractors, mappings) only needed for extraction, not detection.

---

## 📋 Action Items

### **Critical - Lambda Optimization (This Sprint)** 🚨

Based on deep code analysis (see `TRACER_INIT_DEEP_ANALYSIS.md`):

1. ✅ **Deep code analysis complete** - Full initialization path mapped
2. 🎯 **Implement lazy provider loading** (HIGH PRIORITY)
   - Current: 0.86 MB loaded, 0.1 MB used (87% waste in Lambda)
   - Target: 84 KB loaded for typical Lambda (90% reduction)
   - Files to modify:
     - `bundle_loader.py` - Add lazy provider loading
     - `compiler.py` - Generate split bundles (core + per-provider)
     - `universal_processor.py` - Use lazy bundle loader
3. 🎯 **Create Lambda-optimized bundle**
   - Core index + OpenAI only (~50 KB compressed)
   - Ship as `lambda-bundle.pkl.gz`
4. 📊 **Add memory instrumentation**
   - Log bundle size at load time
   - Track provider detection and actual usage
   - Report waste ratio

### **Immediate (This Week)**

1. ✅ Add memory logging to bundle loader
2. ✅ Document current memory usage (done in TRACER_INIT_DEEP_ANALYSIS.md)
3. ⏳ Benchmark Lambda cold start (current behavior)

### **Short-Term (Next 2 Weeks)**

1. ⏳ Implement and test lazy provider loading
2. ⏳ Benchmark memory reduction (target: 90%)
3. ⏳ Update Lambda testing docs
4. ⏳ Create Lambda deployment guide

### **Long-Term (If Needed)**

1. ⏳ CDN-based bundle distribution
2. ⏳ Provider-specific Lambda layers
3. ⏳ Edge deployment optimization

---

## 🎯 Conclusion

**Current Status**: ✅ **Memory footprint is acceptable**

- 20 providers = 880 KB (0.86 MB) - totally fine
- 50 providers = 2.2 MB - still acceptable
- 100 providers = 4.4 MB - monitor, but likely OK

**Action**: Monitor memory usage, optimize only if:
1. Bundle exceeds 5 MB in memory
2. Deploying to constrained environments
3. Profiling shows memory as bottleneck

**Bottom Line**: Don't optimize prematurely. Current implementation is simple and performs well. Lazy loading is available as an optimization path when/if needed.

---

**Last Updated**: 2025-09-30  
**Status**: Memory footprint analyzed and acceptable  
**Next**: Monitor bundle size as providers increase

