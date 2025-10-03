"""
Performance Benchmark for Agent OS MCP/RAG System.

Validates performance requirements:
- Query latency < 100ms (NFR-1)
- Index build time < 60s (NFR-2)
- Throughput > 10 queries/sec (NFR-3)

100% AI-authored via human orchestration.
"""

import argparse
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add .agent-os to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.rag_engine import RAGEngine
from scripts.build_rag_index import IndexBuilder


class RAGBenchmark:
    """Benchmark suite for RAG performance."""

    def __init__(self, base_path: Path):
        """
        Initialize benchmark suite.

        Args:
            base_path: Path to .agent-os directory
        """
        self.base_path = Path(base_path)
        self.standards_path = self.base_path / "standards"
        self.index_path = self.base_path / ".cache" / "vector_index"
        self.results = {}

    def benchmark_index_build(self) -> Dict[str, Any]:
        """
        Benchmark vector index build time.

        Requirement: < 60s for full index build

        Returns:
            Dictionary with timing and chunk statistics
        """
        print("\n" + "=" * 70)
        print("BENCHMARK 1: Index Build Time")
        print("=" * 70)
        print(f"Target: < 60 seconds")
        print(f"Standards path: {self.standards_path}")
        print()

        # Clear existing index
        if self.index_path.exists():
            import shutil

            shutil.rmtree(self.index_path)
            print("✓ Cleared existing index")

        # Build index with timing
        builder = IndexBuilder(
            index_path=self.index_path,
            standards_path=self.standards_path,
            embedding_provider="openai",
        )

        start_time = time.time()
        builder.build_index()
        build_time = time.time() - start_time

        # Read metadata
        metadata_file = self.index_path / "index_metadata.json"
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        result = {
            "build_time_seconds": build_time,
            "chunk_count": metadata["chunk_count"],
            "file_count": metadata["file_count"],
            "passed": build_time < 60.0,
        }

        # Print results
        print(f"\n📊 Results:")
        print(f"  Build Time: {build_time:.2f}s")
        print(f"  Chunks: {metadata['chunk_count']}")
        print(f"  Files: {metadata['file_count']}")
        print(f"  Status: {'✅ PASS' if result['passed'] else '❌ FAIL'}")

        return result

    def benchmark_query_latency(self, n_queries: int = 50) -> Dict[str, Any]:
        """
        Benchmark query latency.

        Requirement: < 100ms per query

        Args:
            n_queries: Number of queries to test

        Returns:
            Dictionary with latency statistics
        """
        print("\n" + "=" * 70)
        print("BENCHMARK 2: Query Latency")
        print("=" * 70)
        print(f"Target: < 100ms per query")
        print(f"Queries: {n_queries}")
        print()

        # Initialize RAG engine
        rag_engine = RAGEngine(
            index_path=self.index_path, standards_path=self.standards_path
        )

        # Test queries covering different patterns
        test_queries = [
            "Phase 1 method verification requirements",
            "How to determine mocking boundaries",
            "Quality targets for test generation",
            "Checkpoint criteria for Phase 2",
            "Test generation framework overview",
            "Logging analysis requirements",
            "AST tools and commands",
            "Coverage requirements",
            "Production code standards",
            "Error handling patterns",
        ]

        # Extend to n_queries by cycling
        queries = (test_queries * (n_queries // len(test_queries) + 1))[:n_queries]

        # Benchmark queries
        latencies = []
        print("Running queries...", end=" ", flush=True)

        for i, query in enumerate(queries):
            start_time = time.time()
            rag_engine.search(query=query, n_results=5)
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)

            if (i + 1) % 10 == 0:
                print(f"{i + 1}", end=" ", flush=True)

        print("✓")

        # Calculate statistics
        result = {
            "query_count": n_queries,
            "mean_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "p95_latency_ms": sorted(latencies)[int(n_queries * 0.95)],
            "p99_latency_ms": sorted(latencies)[int(n_queries * 0.99)],
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "passed": statistics.mean(latencies) < 100.0,
        }

        # Print results
        print(f"\n📊 Results:")
        print(f"  Mean: {result['mean_latency_ms']:.2f}ms")
        print(f"  Median: {result['median_latency_ms']:.2f}ms")
        print(f"  P95: {result['p95_latency_ms']:.2f}ms")
        print(f"  P99: {result['p99_latency_ms']:.2f}ms")
        print(f"  Min: {result['min_latency_ms']:.2f}ms")
        print(f"  Max: {result['max_latency_ms']:.2f}ms")
        print(f"  Status: {'✅ PASS' if result['passed'] else '❌ FAIL'}")

        return result

    def benchmark_throughput(self, duration_seconds: int = 10) -> Dict[str, Any]:
        """
        Benchmark query throughput.

        Requirement: > 10 queries/second

        Args:
            duration_seconds: How long to run throughput test

        Returns:
            Dictionary with throughput statistics
        """
        print("\n" + "=" * 70)
        print("BENCHMARK 3: Query Throughput")
        print("=" * 70)
        print(f"Target: > 10 queries/second")
        print(f"Duration: {duration_seconds}s")
        print()

        # Initialize RAG engine
        rag_engine = RAGEngine(
            index_path=self.index_path, standards_path=self.standards_path
        )

        # Simple query for throughput testing
        query = "Phase 1 requirements"

        # Run queries for duration
        print("Running throughput test...", end=" ", flush=True)
        start_time = time.time()
        query_count = 0

        while time.time() - start_time < duration_seconds:
            rag_engine.search(query=query, n_results=5)
            query_count += 1

            if query_count % 50 == 0:
                print(".", end="", flush=True)

        elapsed_time = time.time() - start_time
        print(f" {query_count} queries in {elapsed_time:.2f}s")

        # Calculate throughput
        queries_per_second = query_count / elapsed_time

        result = {
            "total_queries": query_count,
            "elapsed_seconds": elapsed_time,
            "queries_per_second": queries_per_second,
            "passed": queries_per_second > 10.0,
        }

        # Print results
        print(f"\n📊 Results:")
        print(f"  Total Queries: {query_count}")
        print(f"  Elapsed Time: {elapsed_time:.2f}s")
        print(f"  Throughput: {queries_per_second:.2f} queries/sec")
        print(f"  Status: {'✅ PASS' if result['passed'] else '❌ FAIL'}")

        return result

    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """
        Benchmark memory usage of RAG engine.

        Requirement: < 500MB memory usage

        Returns:
            Dictionary with memory statistics
        """
        print("\n" + "=" * 70)
        print("BENCHMARK 4: Memory Usage")
        print("=" * 70)
        print(f"Target: < 500MB memory usage")
        print()

        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Get baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Initialize RAG engine
        rag_engine = RAGEngine(
            index_path=self.index_path, standards_path=self.standards_path
        )

        # Perform some queries
        for _ in range(10):
            rag_engine.search(query="test query", n_results=5)

        # Get peak memory
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = peak_memory - baseline_memory

        result = {
            "baseline_mb": baseline_memory,
            "peak_mb": peak_memory,
            "delta_mb": memory_delta,
            "passed": memory_delta < 500.0,
        }

        # Print results
        print(f"\n📊 Results:")
        print(f"  Baseline: {baseline_memory:.2f}MB")
        print(f"  Peak: {peak_memory:.2f}MB")
        print(f"  Delta: {memory_delta:.2f}MB")
        print(f"  Status: {'✅ PASS' if result['passed'] else '❌ FAIL'}")

        return result

    def run_all_benchmarks(self, skip_index_build: bool = False) -> Dict[str, Any]:
        """
        Run all benchmarks and generate report.

        Args:
            skip_index_build: Skip index build benchmark (use existing)

        Returns:
            Complete benchmark results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": {},
        }

        # Benchmark 1: Index build
        if not skip_index_build:
            results["benchmarks"]["index_build"] = self.benchmark_index_build()
        else:
            print("\n⏭️  Skipping index build benchmark (using existing index)")

        # Benchmark 2: Query latency
        results["benchmarks"]["query_latency"] = self.benchmark_query_latency(
            n_queries=50
        )

        # Benchmark 3: Throughput
        results["benchmarks"]["throughput"] = self.benchmark_throughput(
            duration_seconds=10
        )

        # Benchmark 4: Memory usage
        results["benchmarks"]["memory_usage"] = self.benchmark_memory_usage()

        # Summary
        print("\n" + "=" * 70)
        print("BENCHMARK SUMMARY")
        print("=" * 70)

        all_passed = all(
            b.get("passed", True) for b in results["benchmarks"].values()
        )

        for name, result in results["benchmarks"].items():
            status = "✅ PASS" if result.get("passed", True) else "❌ FAIL"
            print(f"  {name.replace('_', ' ').title()}: {status}")

        print()
        print(f"Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        print("=" * 70)

        results["all_passed"] = all_passed

        return results

    def save_results(self, results: Dict[str, Any], output_path: Path):
        """
        Save benchmark results to JSON.

        Args:
            results: Benchmark results
            output_path: Path to save results
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved to: {output_path}")


def main():
    """Entry point for benchmark script."""
    parser = argparse.ArgumentParser(
        description="Benchmark Agent OS MCP/RAG performance"
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Path to .agent-os directory",
    )
    parser.add_argument(
        "--skip-index-build",
        action="store_true",
        help="Skip index build benchmark (use existing index)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / ".cache" / "benchmark_results.json",
        help="Path to save results JSON",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("Agent OS MCP/RAG Performance Benchmark")
    print("=" * 70)
    print(f"Base Path: {args.base_path}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Check dependencies
    try:
        import psutil
    except ImportError:
        print("⚠️  Warning: psutil not installed, skipping memory benchmark")
        print("   Install with: pip install psutil")

    # Run benchmarks
    benchmark = RAGBenchmark(args.base_path)
    results = benchmark.run_all_benchmarks(skip_index_build=args.skip_index_build)

    # Save results
    benchmark.save_results(results, args.output)

    # Exit with appropriate code
    sys.exit(0 if results["all_passed"] else 1)


if __name__ == "__main__":
    main()

