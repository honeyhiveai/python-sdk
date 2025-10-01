#!/usr/bin/env python3
"""
Benchmark different bundle format load times.

Compares JSON, pickle, MessagePack, and CBOR for DSL bundle loading.
"""

import json
import pickle
import time
import sys
from pathlib import Path
from typing import Dict, Any
import msgpack  # pip install msgpack
import cbor2    # pip install cbor2

def create_sample_bundle(size: str = "medium") -> Dict[str, Any]:
    """Create a sample DSL bundle for benchmarking."""
    
    if size == "small":
        num_providers = 3
        num_patterns = 10
    elif size == "medium":
        num_providers = 10
        num_patterns = 30
    else:  # large
        num_providers = 50
        num_patterns = 150
    
    bundle = {
        "version": "4.0",
        "signature_index": {},
        "extractors": {},
        "mappings": {},
        "provider_patterns": {}
    }
    
    # Build signature index
    for i in range(num_patterns):
        sig = f"attr1|attr2|attr3|attr{i}"
        bundle["signature_index"][sig] = {
            "provider": f"provider_{i % num_providers}",
            "instrumentor": "traceloop",
            "confidence": 0.90
        }
    
    # Build extractors
    for i in range(num_providers):
        bundle["extractors"][f"provider_{i}:traceloop"] = {
            "steps": [
                {
                    "operation": "direct_copy",
                    "source": f"gen_ai.field_{j}",
                    "target": f"target_{j}"
                }
                for j in range(15)  # 15 steps per extractor
            ]
        }
    
    # Build mappings
    for i in range(num_providers):
        bundle["mappings"][f"provider_{i}"] = {
            "inputs": {f"input_{j}": {"source": f"src_{j}"} for j in range(10)},
            "outputs": {f"output_{j}": {"source": f"src_{j}"} for j in range(10)},
            "config": {f"config_{j}": {"source": f"src_{j}"} for j in range(10)},
            "metadata": {f"meta_{j}": {"source": f"src_{j}"} for j in range(10)}
        }
    
    return bundle


def benchmark_format(name: str, save_func, load_func, bundle: Dict[str, Any], file_path: Path, iterations: int = 1000):
    """Benchmark a specific format."""
    
    # Save once
    save_func(bundle, file_path)
    file_size = file_path.stat().st_size
    
    # Warm up
    for _ in range(10):
        load_func(file_path)
    
    # Benchmark loads
    start = time.perf_counter()
    for _ in range(iterations):
        data = load_func(file_path)
    end = time.perf_counter()
    
    avg_time_ms = ((end - start) / iterations) * 1000
    
    return {
        "name": name,
        "avg_load_time_ms": avg_time_ms,
        "file_size_kb": file_size / 1024,
        "loads_per_second": 1000 / avg_time_ms if avg_time_ms > 0 else 0
    }


# JSON
def save_json(bundle, path):
    with open(path, 'w') as f:
        json.dump(bundle, f)

def load_json(path):
    with open(path) as f:
        return json.load(f)


# Pickle
def save_pickle(bundle, path):
    with open(path, 'wb') as f:
        pickle.dump(bundle, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_pickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


# MessagePack
def save_msgpack(bundle, path):
    with open(path, 'wb') as f:
        msgpack.dump(bundle, f)

def load_msgpack(path):
    with open(path, 'rb') as f:
        return msgpack.load(f)


# CBOR
def save_cbor(bundle, path):
    with open(path, 'wb') as f:
        cbor2.dump(bundle, f)

def load_cbor(path):
    with open(path, 'rb') as f:
        return cbor2.load(f)


def main():
    print("=" * 80)
    print("DSL Bundle Format Benchmark")
    print("=" * 80)
    print()
    
    sizes = ["small", "medium", "large"]
    
    for size in sizes:
        print(f"\n{'=' * 80}")
        print(f"Bundle Size: {size.upper()}")
        print(f"{'=' * 80}\n")
        
        bundle = create_sample_bundle(size)
        
        if size == "small":
            iterations = 10000
        elif size == "medium":
            iterations = 1000
        else:
            iterations = 100
        
        print(f"Iterations: {iterations}")
        print()
        
        results = []
        
        # Benchmark JSON
        print("Benchmarking JSON...")
        results.append(benchmark_format(
            "JSON",
            save_json,
            load_json,
            bundle,
            Path(f"/tmp/bundle_{size}.json"),
            iterations
        ))
        
        # Benchmark Pickle
        print("Benchmarking Pickle...")
        results.append(benchmark_format(
            "Pickle",
            save_pickle,
            load_pickle,
            bundle,
            Path(f"/tmp/bundle_{size}.pkl"),
            iterations
        ))
        
        # Benchmark MessagePack
        print("Benchmarking MessagePack...")
        try:
            results.append(benchmark_format(
                "MessagePack",
                save_msgpack,
                load_msgpack,
                bundle,
                Path(f"/tmp/bundle_{size}.msgpack"),
                iterations
            ))
        except ImportError:
            print("  ⚠️  msgpack not installed (pip install msgpack)")
        
        # Benchmark CBOR
        print("Benchmarking CBOR...")
        try:
            results.append(benchmark_format(
                "CBOR",
                save_cbor,
                load_cbor,
                bundle,
                Path(f"/tmp/bundle_{size}.cbor"),
                iterations
            ))
        except ImportError:
            print("  ⚠️  cbor2 not installed (pip install cbor2)")
        
        # Print results
        print()
        print(f"{'Format':<15} {'Avg Load (ms)':<15} {'File Size (KB)':<15} {'Loads/sec':<15} {'vs JSON':<15}")
        print("-" * 80)
        
        json_time = next(r["avg_load_time_ms"] for r in results if r["name"] == "JSON")
        
        for result in sorted(results, key=lambda x: x["avg_load_time_ms"]):
            speedup = json_time / result["avg_load_time_ms"]
            print(
                f"{result['name']:<15} "
                f"{result['avg_load_time_ms']:<15.3f} "
                f"{result['file_size_kb']:<15.1f} "
                f"{result['loads_per_second']:<15.0f} "
                f"{speedup:.1f}x faster"
            )
        
        print()
        
        # Recommendations
        fastest = min(results, key=lambda x: x["avg_load_time_ms"])
        smallest = min(results, key=lambda x: x["file_size_kb"])
        
        print(f"🚀 Fastest: {fastest['name']} ({fastest['avg_load_time_ms']:.3f} ms)")
        print(f"💾 Smallest: {smallest['name']} ({smallest['file_size_kb']:.1f} KB)")


if __name__ == "__main__":
    main()

