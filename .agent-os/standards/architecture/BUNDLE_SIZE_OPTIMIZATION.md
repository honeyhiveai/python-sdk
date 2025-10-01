# DSL Bundle Size Optimization Strategies

**Date**: 2025-09-30  
**Problem**: Bundle size could grow with many providers  
**Solution**: Multiple optimization strategies to keep bundles lean

---

## 📊 Benchmark Results

### **Realistic Production Bundle**
| Providers | JSON (raw) | Pickle+gzip | Compression | Load Time |
|-----------|------------|-------------|-------------|-----------|
| 10 | 250 KB | **3.8 KB** | **65x** | 0.445 ms |
| 20 | 499 KB | **5.5 KB** | **90x** | 0.962 ms |
| 50 | 1,245 KB | **10.8 KB** | **115x** | 2.445 ms |
| 100 (est) | 2,500 KB | **~20 KB** | **125x** | ~5 ms |

**Key Insight**: Gzip compression is **spectacularly effective** for DSL bundles (60-115x reduction!)

---

## 🎯 Strategy 1: Compression (RECOMMENDED)

### **Implementation**

#### **Python SDK**
```python
# Bundle distribution: ship .pkl.gz
import gzip
import pickle

class BundleLoader:
    def load(self):
        # Try compressed pickle first (production)
        pkl_gz_path = Path(__file__).parent / "dsl-bundle.pkl.gz"
        if pkl_gz_path.exists():
            with gzip.open(pkl_gz_path, 'rb') as f:
                return pickle.load(f)
        
        # Fallback to JSON (development)
        json_path = Path(__file__).parent / "dsl-bundle.json"
        with open(json_path) as f:
            return json.load(f)
```

#### **TypeScript SDK**
```typescript
// Bundle distribution: ship .json.gz
import * as zlib from 'zlib';
import * as fs from 'fs';

class BundleLoader {
  load(): DSLBundle {
    // Try compressed JSON (production)
    const gzPath = path.join(__dirname, 'dsl-bundle.json.gz');
    if (fs.existsSync(gzPath)) {
      const compressed = fs.readFileSync(gzPath);
      const decompressed = zlib.gunzipSync(compressed);
      return JSON.parse(decompressed.toString());
    }
    
    // Fallback to plain JSON
    return JSON.parse(fs.readFileSync('dsl-bundle.json', 'utf-8'));
  }
}
```

#### **Go SDK**
```go
// Bundle distribution: ship .json.gz
import (
    "compress/gzip"
    "encoding/json"
    "os"
)

func LoadBundle() (*DSLBundle, error) {
    // Try compressed JSON
    f, err := os.Open("dsl-bundle.json.gz")
    if err == nil {
        defer f.Close()
        gr, _ := gzip.NewReader(f)
        defer gr.Close()
        
        var bundle DSLBundle
        json.NewDecoder(gr).Decode(&bundle)
        return &bundle, nil
    }
    
    // Fallback to plain JSON
    // ...
}
```

### **Results**
- **50 providers**: 1.2 MB → **11 KB** (99% reduction!)
- **Load time**: Still fast (2-5 ms with decompression)
- **Distribution**: Tiny bundle ships with SDK

---

## 🎯 Strategy 2: Lazy Loading (If Needed)

### **Concept**
Only load providers that are actually detected in runtime.

### **Implementation**

#### **Bundle Structure**
```
dsl-bundles/
├── core-bundle.pkl.gz           # Detection patterns only (1-2 KB)
├── providers/
│   ├── openai.pkl.gz            # OpenAI extractors/mappings (500 bytes)
│   ├── anthropic.pkl.gz         # Anthropic extractors/mappings (500 bytes)
│   └── ...
```

#### **Lazy Loader**
```python
class LazyBundleLoader:
    def __init__(self):
        # Load core (detection patterns only)
        self.core = self._load_gz("core-bundle.pkl.gz")
        self.provider_cache = {}
    
    def detect_provider(self, attributes):
        """O(1) detection using core bundle."""
        signature = "|".join(sorted(attributes.keys()))
        return self.core["signature_index"].get(signature)
    
    def extract_data(self, provider, instrumentor, attributes):
        """Lazy load provider-specific bundle on first use."""
        if provider not in self.provider_cache:
            # Load provider bundle on-demand
            provider_bundle = self._load_gz(f"providers/{provider}.pkl.gz")
            self.provider_cache[provider] = provider_bundle
        
        provider_data = self.provider_cache[provider]
        # Extract using provider-specific extractors
        # ...
```

### **Results**
- **Initial load**: Only 1-2 KB (core patterns)
- **Runtime load**: 500 bytes per provider as needed
- **Memory**: Only load what you use

---

## 🎯 Strategy 3: Bundle Splitting (Alternative)

### **Concept**
Split bundle by instrumentor instead of provider.

### **Structure**
```
dsl-bundles/
├── traceloop-bundle.pkl.gz      # All Traceloop patterns (3-4 KB)
├── openinference-bundle.pkl.gz  # All OpenInference patterns (3-4 KB)
└── openlit-bundle.pkl.gz        # All OpenLit patterns (3-4 KB)
```

### **Load Strategy**
```python
class InstrumentorBundleLoader:
    def __init__(self):
        self.bundles = {}
    
    def detect_and_load(self, attributes):
        # Quick check: which instrumentor namespace?
        if any(k.startswith("gen_ai.") for k in attributes):
            # Likely Traceloop or OpenLit
            if "traceloop" not in self.bundles:
                self.bundles["traceloop"] = self._load_gz("traceloop-bundle.pkl.gz")
        
        elif any(k.startswith("llm.") for k in attributes):
            # Likely OpenInference
            if "openinference" not in self.bundles:
                self.bundles["openinference"] = self._load_gz("openinference-bundle.pkl.gz")
        
        # Use loaded bundle
        # ...
```

### **Results**
- **Initial load**: 0 KB (nothing loaded)
- **Runtime load**: 3-4 KB per instrumentor as detected
- **Typical usage**: Only 1 instrumentor, so 3-4 KB total

---

## 🎯 Strategy 4: CDN Distribution (Future)

### **Concept**
Don't ship bundle with SDK, fetch from CDN at runtime.

### **Implementation**
```python
class CDNBundleLoader:
    BUNDLE_CDN = "https://cdn.honeyhive.ai/dsl-bundles/"
    
    def __init__(self):
        self.cache_dir = Path.home() / ".honeyhive" / "bundles"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self):
        # Check local cache first
        cached = self.cache_dir / "dsl-bundle.pkl.gz"
        if cached.exists() and self._is_fresh(cached):
            return self._load_gz(cached)
        
        # Fetch from CDN
        version = self._get_sdk_version()
        url = f"{self.BUNDLE_CDN}v{version}/dsl-bundle.pkl.gz"
        
        response = requests.get(url)
        cached.write_bytes(response.content)
        
        return self._load_gz(cached)
```

### **Benefits**
- **SDK size**: No bundle shipped (0 KB)
- **Updates**: Can update bundle without SDK release
- **Versioning**: Different bundles per SDK version

### **Tradeoffs**
- **Network dependency**: Requires internet on first run
- **Latency**: First load slower (download time)
- **Complexity**: CDN infrastructure needed

---

## 📊 Strategy Comparison

| Strategy | SDK Size | First Load | Runtime Load | Complexity | Recommended |
|----------|----------|------------|--------------|------------|-------------|
| **Compression** | 11-20 KB | 2-5 ms | 2-5 ms | Low | ✅ **YES** |
| **Lazy Loading** | 1-2 KB | 1 ms | +0.5 ms/provider | Medium | Maybe |
| **Bundle Splitting** | 0 KB | 0 ms | 3-4 KB/instrumentor | Medium | Maybe |
| **CDN** | 0 KB | 50-200 ms | 2-5 ms | High | Future |

---

## 🎯 Recommended Approach

### **Phase 1: Compression (NOW)**

Ship compressed bundles with SDK:

```
Python SDK:
  └── dsl-bundle.pkl.gz   (10-20 KB for 50 providers)

TypeScript SDK:
  └── dsl-bundle.json.gz  (13-25 KB for 50 providers)

Go SDK:
  └── dsl-bundle.json.gz  (13-25 KB for 50 providers)
```

**Why**:
- ✅ Simple implementation
- ✅ Tiny size (10-25 KB even with 50+ providers)
- ✅ Fast load times (2-5 ms)
- ✅ No complexity

### **Phase 2: Lazy Loading (IF NEEDED)**

Only if we hit 100+ providers and size becomes an issue.

Split into:
```
core-bundle.pkl.gz       (2 KB - detection only)
providers/*.pkl.gz       (500 bytes each - lazy loaded)
```

**When**:
- If bundle exceeds 50 KB compressed
- If we have 100+ providers
- If startup time becomes an issue

### **Phase 3: CDN (FUTURE)**

Only for advanced use cases:
- Very large bundles (100+ providers)
- Frequent updates without SDK releases
- Multi-SDK synchronization

---

## 💡 Size Projections

### **Current Trajectory**

| Providers | Uncompressed | Compressed (pkl.gz) | Ship with SDK? |
|-----------|--------------|---------------------|----------------|
| 10 | 250 KB | **3.8 KB** | ✅ Easy |
| 20 | 500 KB | **5.5 KB** | ✅ Easy |
| 50 | 1.2 MB | **10.8 KB** | ✅ Easy |
| 100 | 2.5 MB | **~20 KB** | ✅ Still fine |
| 200 | 5 MB | **~40 KB** | ⚠️ Consider lazy loading |
| 500 | 12 MB | **~100 KB** | ❌ Need lazy loading or CDN |

### **Size Budget**

**Recommended limits**:
- ✅ **< 25 KB**: Ship compressed bundle with SDK
- ⚠️ **25-100 KB**: Consider lazy loading providers
- ❌ **> 100 KB**: Implement lazy loading or CDN

**Current status**: With 50 providers @ 11 KB, we're in the **optimal zone** ✅

---

## 🔧 Implementation Plan

### **Week 1: Add Compression Support**

```bash
# Update bundle compiler
python scripts/compile_dsl_bundle.py --output dsl-bundle.json
python scripts/compress_bundle.py --input dsl-bundle.json --output dsl-bundle.pkl.gz

# Update loaders
# - Python: support .pkl.gz loading
# - TypeScript: support .json.gz loading
# - Go: support .json.gz loading
```

### **Week 2: Measure & Monitor**

```python
# Add bundle size tracking
class BundleMetrics:
    def report(self):
        print(f"Bundle size: {self.size_kb} KB")
        print(f"Load time: {self.load_ms} ms")
        print(f"Providers: {self.provider_count}")
        
        if self.size_kb > 25:
            warn("Consider lazy loading")
```

### **Week 3: Optimize If Needed**

Only if bundle > 25 KB:
- Implement lazy loading
- Or implement bundle splitting
- Or implement CDN distribution

---

## 📋 Conclusion

**Current size concerns**: **SOLVED** ✅

With gzip compression:
- 50 providers = **11 KB** (totally acceptable!)
- 100 providers = **~20 KB** (still fine!)
- Even 200 providers = **~40 KB** (manageable!)

**Recommendation**:
1. **Ship compressed bundles** (pkl.gz for Python, json.gz for others)
2. **Monitor size** as providers increase
3. **Add lazy loading** only if we hit 100+ providers and >50 KB

**No immediate action needed** - compression solves the size problem! 🎉

---

**Last Updated**: 2025-09-30  
**Status**: Size concerns resolved with compression  
**Next**: Implement compression support in bundle compiler

