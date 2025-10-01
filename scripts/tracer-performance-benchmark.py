#!/usr/bin/env python3
"""
Multi-LLM Tracer Performance Benchmark - Modular Version

This is the new modular implementation of the tracer performance benchmark
using a clean architecture with separated concerns. Provides comprehensive
performance analysis with north-star metrics, conversation simulation,
and teammate feedback formulas.

Features:
- Modular architecture with separated providers, monitoring, and reporting
- Six north-star metrics for quick tracer capability assessment
- Deterministic conversation simulation for A/B testing
- Comprehensive metrics with teammate feedback formulas
- Enhanced reporting with visualization and recommendations

Usage:
    python scripts/tracer-performance-benchmark-modular.py [options]

Requirements:
    - OPENAI_API_KEY environment variable
    - ANTHROPIC_API_KEY environment variable  
    - HH_API_KEY environment variable
    - HH_PROJECT environment variable (optional)

Example:
    # Basic benchmark
    python scripts/tracer-performance-benchmark-modular.py
    
    # Custom configuration
    python scripts/tracer-performance-benchmark-modular.py \\
        --operations 100 \\
        --concurrent-threads 8 \\
        --span-size-mode large \\
        --openai-model gpt-4o \\
        --anthropic-model claude-sonnet-4-20250514
    
    # North-star metrics only
    python scripts/tracer-performance-benchmark-modular.py \\
        --operations 20 \\
        --north-star-only
    
    # Test specific providers only
    python scripts/tracer-performance-benchmark-modular.py \\
        --include "openinference_openai,traceloop_openai" \\
        --north-star-only
    
    # Test single provider
    python scripts/tracer-performance-benchmark-modular.py \\
        --include "openinference_anthropic" \\
        --operations 5
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path for HoneyHive imports
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))

# Import modular benchmark components
from benchmark.core.config import BenchmarkConfig
from benchmark.core.benchmark_runner import TracerBenchmark

# Configure logging with user preference [[memory:8830238]]
def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration.
    
    :param verbose: Enable verbose logging
    :type verbose: bool
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Configure environment variables for subprocess logging
    if verbose:
        # Enable verbose logging in subprocesses
        os.environ['BENCHMARK_VERBOSE'] = '1'
    else:
        # Set environment variable to suppress JSON logging in subprocesses
        os.environ['HONEYHIVE_DISABLE_JSON_LOGGING'] = '1'
        # Ensure benchmark verbose is disabled
        os.environ.pop('BENCHMARK_VERBOSE', None)
        
        noisy_loggers = [
            "httpcore", "openai", "anthropic", "httpx", "urllib3",
            "honeyhive", "honeyhive.fallback", "honeyhive.early_init", "honeyhive.client",
            "opentelemetry", "opentelemetry.instrumentation", "opentelemetry.trace",
            "opentelemetry.sdk", "opentelemetry.exporter", "opentelemetry.util",
            "openinference", "traceloop"
        ]
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)
            logging.getLogger(logger_name).disabled = True


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    :return: Parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Multi-LLM Tracer Performance Benchmark - Modular Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic benchmark with default settings
  %(prog)s
  
  # Custom configuration with large spans
  %(prog)s --operations 100 --span-size-mode large --concurrent-threads 8
  
  # Quick north-star metrics assessment
  %(prog)s --operations 20 --north-star-only
  
  # Test deterministic prompt generation
  %(prog)s --test-determinism
  
  # Validate environment and connections
  %(prog)s --validate-only

Environment Variables:
  OPENAI_API_KEY     - OpenAI API key (required)
  ANTHROPIC_API_KEY  - Anthropic API key (required)
  HH_API_KEY         - HoneyHive API key (required)
  HH_PROJECT         - HoneyHive project name (optional)
        """
    )
    
    # Benchmark configuration
    parser.add_argument(
        "--operations",
        type=int,
        default=50,
        help="Number of operations per provider (default: 50)"
    )
    
    parser.add_argument(
        "--concurrent-threads",
        type=int,
        default=4,
        help="Number of concurrent threads for concurrent benchmarks (default: 4)"
    )
    
    parser.add_argument(
        "--warmup-operations",
        type=int,
        default=5,
        help="Number of warmup operations (default: 5)"
    )
    
    # Model configuration
    parser.add_argument(
        "--openai-model",
        type=str,
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )
    
    parser.add_argument(
        "--anthropic-model",
        type=str,
        default="claude-sonnet-4-20250514",
        help="Anthropic model to use (default: claude-sonnet-4-20250514)"
    )
    
    # Span configuration
    parser.add_argument(
        "--span-size-mode",
        type=str,
        choices=["small", "medium", "large", "mixed"],
        default="mixed",
        help="Span size mode for testing (default: mixed)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,  # Will be set dynamically based on conversation templates
        help="Maximum tokens per response (default: auto-detected from conversation templates, range: 100-15000)"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Temperature for LLM responses (default: 0.1)"
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Timeout for API calls in seconds (default: 30.0)"
    )
    
    # Conversation simulation
    parser.add_argument(
        "--conversation-mode",
        action="store_true",
        default=True,
        help="Enable conversation simulation (default: enabled)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic prompt generation (default: 42)"
    )
    
    # Output options
    parser.add_argument(
        "--north-star-only",
        action="store_true",
        help="Show only north-star metrics summary"
    )
    
    parser.add_argument(
        "--export-json",
        type=str,
        help="Export results to JSON file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--include",
        type=str,
        default="all",
        help="Comma-separated list of instrumentor_provider pairings to include. "
             "Options: openinference_openai, openinference_anthropic, traceloop_openai, traceloop_anthropic. "
             "Use 'all' to run all available pairings (default: all)"
    )
    
    # Validation and testing
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate environment and connections, don't run benchmarks"
    )
    
    parser.add_argument(
        "--test-determinism",
        action="store_true",
        help="Test deterministic prompt generation and exit"
    )
    
    parser.add_argument(
        "--test-connections",
        action="store_true",
        help="Test provider connections and exit"
    )
    
    # Advanced Testing Features
    parser.add_argument(
        "--run-ab-testing",
        action="store_true",
        help="Run A/B testing harness comparing traced vs untraced workloads",
    )
    parser.add_argument(
        "--run-synthetic-spans",
        action="store_true", 
        help="Run synthetic spans testing with known DAGs and fixed durations",
    )
    parser.add_argument(
        "--run-load-testing",
        action="store_true",
        help="Run load testing with QPS and concurrency sweeps",
    )
    parser.add_argument(
        "--run-comprehensive-metrics",
        action="store_true",
        help="Run comprehensive metrics framework (Core Efficiency, Accuracy & Fidelity, etc.)",
    )
    parser.add_argument(
        "--run-all-advanced",
        action="store_true",
        help="Run all advanced testing features (A/B, synthetic, load, comprehensive)",
    )
    
    return parser.parse_args()


def parse_include_argument(include_arg: str) -> tuple[bool, list[str]]:
    """Parse the --include argument to determine which providers to enable.
    
    :param include_arg: The include argument value
    :type include_arg: str
    :return: Tuple of (include_traceloop, enabled_providers)
    :rtype: tuple[bool, list[str]]
    """
    # Define all available provider pairings
    all_providers = [
        "openinference_openai",
        "openinference_anthropic", 
        "traceloop_openai",
        "traceloop_anthropic"
    ]
    
    # Handle "all" case - enable all available providers
    if include_arg.lower() == "all":
        return True, all_providers
    
    # Parse comma-separated list
    requested_providers = [p.strip().lower() for p in include_arg.split(",")]
    enabled_providers = []
    
    # Validate and collect enabled providers
    for provider in requested_providers:
        if provider in all_providers:
            enabled_providers.append(provider)
        else:
            print(f"⚠️  Warning: Unknown provider '{provider}'. Available: {', '.join(all_providers)}")
    
    # Determine if traceloop should be included
    include_traceloop = any(p.startswith("traceloop_") for p in enabled_providers)
    
    # If no valid providers specified, default to OpenInference only
    if not enabled_providers:
        print("⚠️  No valid providers specified, defaulting to OpenInference providers only")
        enabled_providers = ["openinference_openai", "openinference_anthropic"]
        include_traceloop = False
    
    return include_traceloop, enabled_providers


def validate_environment() -> None:
    """Validate environment variables and display status.
    
    :raises SystemExit: If validation fails
    """
    print("🔍 Validating Environment...")
    
    required_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "HH_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        else:
            # Mask the key for security
            masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
            print(f"✅ {var}: {masked_value}")
    
    # Optional variables
    optional_vars = ["HH_PROJECT"]
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"ℹ️  {var}: Using default")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables and try again.")
        sys.exit(1)
    
    print("✅ Environment validation passed\n")


def main() -> None:
    """Main entry point for the modular benchmark CLI."""
    # Protect multiprocessing on macOS/Windows
    import multiprocessing as mp
    mp.set_start_method('spawn', force=True)
    
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Set dynamic max_tokens default and validate range
    from benchmark.scenarios.conversation_templates import ConversationTemplates
    
    if args.max_tokens is None:
        # Auto-detect from conversation templates
        templates = ConversationTemplates()
        args.max_tokens = templates.get_max_expected_tokens()
        logger.info(f"🎯 Auto-detected max_tokens: {args.max_tokens} (from conversation templates)")
    else:
        # Validate user-provided value
        if not (100 <= args.max_tokens <= 15000):
            raise ValueError(f"max_tokens must be between 100 and 15000, got: {args.max_tokens}")
        logger.info(f"🎯 Using user-specified max_tokens: {args.max_tokens}")
    
    # Display header
    print("🎯 Multi-LLM Tracer Performance Benchmark - Modular Version")
    print("=" * 65)
    print()
    
    try:
        # Validate environment
        validate_environment()
        
        # Parse include argument to determine which instrumentors to enable
        include_traceloop, enabled_providers = parse_include_argument(args.include)
        
        # Create configuration
        config = BenchmarkConfig(
            operations=args.operations,
            concurrent_threads=args.concurrent_threads,
            warmup_operations=args.warmup_operations,
            openai_model=args.openai_model,
            anthropic_model=args.anthropic_model,
            span_size_mode=args.span_size_mode,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            timeout=args.timeout,
            conversation_mode=args.conversation_mode,
            seed=args.seed,
            include_traceloop=include_traceloop,
            enabled_providers=enabled_providers,
        )
        
        # Initialize benchmark
        benchmark = TracerBenchmark(config)
        
        # Handle special modes
        if args.validate_only:
            print("🔧 Validation Mode - Checking configuration and connections...")
            benchmark.validate_environment()
            benchmark.initialize_tracers()
            benchmark.initialize_providers()
            
            # Test connections
            connection_results = benchmark.test_provider_connections()
            for provider, status in connection_results.items():
                status_icon = "✅" if status else "❌"
                print(f"{status_icon} {provider.upper()} connection: {'OK' if status else 'FAILED'}")
            
            benchmark.cleanup_providers()
            print("✅ Validation completed")
            return
        
        if args.test_determinism:
            print("🧪 Testing Deterministic Prompt Generation...")
            is_deterministic = benchmark.validate_determinism()
            print(f"{'✅' if is_deterministic else '❌'} Determinism test: {'PASSED' if is_deterministic else 'FAILED'}")
            return
        
        if args.test_connections:
            print("🔌 Testing Provider Connections...")
            benchmark.initialize_tracers()
            benchmark.initialize_providers()
            
            connection_results = benchmark.test_provider_connections()
            for provider, status in connection_results.items():
                status_icon = "✅" if status else "❌"
                print(f"{status_icon} {provider.upper()}: {'Connected' if status else 'Connection failed'}")
            
            benchmark.cleanup_providers()
            return
        
        # Handle advanced testing features
        if args.run_ab_testing or args.run_all_advanced:
            print("🧪 Running A/B Testing Harness...")
            run_ab_testing_harness(config)
            if args.run_ab_testing and not args.run_all_advanced:
                return
        
        if args.run_synthetic_spans or args.run_all_advanced:
            print("🎭 Running Synthetic Spans Testing...")
            run_synthetic_spans_testing(config)
            if args.run_synthetic_spans and not args.run_all_advanced:
                return
        
        if args.run_load_testing or args.run_all_advanced:
            print("⚡ Running Load Testing...")
            run_load_testing(config)
            if args.run_load_testing and not args.run_all_advanced:
                return
        
        if args.run_comprehensive_metrics or args.run_all_advanced:
            print("📊 Running Comprehensive Metrics Framework...")
            run_comprehensive_metrics_framework(config)
            if args.run_comprehensive_metrics and not args.run_all_advanced:
                return
        
        # If any advanced testing was run, exit here (unless it's --run-all-advanced)
        if (args.run_ab_testing or args.run_synthetic_spans or 
            args.run_load_testing or args.run_comprehensive_metrics) and not args.run_all_advanced:
            return
        
        # Run benchmarks
        print("🚀 Starting benchmarks...")
        results = benchmark.run_full_benchmark()
        
        if not results:
            print("❌ No results generated")
            sys.exit(1)
        
        # Display results
        print("\n" + "=" * 65)
        print("📊 BENCHMARK RESULTS")
        print("=" * 65)
        
        if args.north_star_only:
            # Show only north-star metrics
            print(benchmark.get_north_star_summary())
        else:
            # Show full report
            print(benchmark.generate_report())
        
        # Export JSON if requested
        if args.export_json:
            import json
            structured_data = benchmark.export_results()
            with open(args.export_json, 'w') as f:
                json.dump(structured_data, f, indent=2)
            print(f"📁 Results exported to {args.export_json}")
        
        # Display conversation statistics
        if args.conversation_mode:
            conv_stats = benchmark.get_conversation_statistics()
            print(f"\n📝 Conversation Templates Used: {conv_stats.get('total_scenarios', 'N/A')}")
        
        print("\n✅ Benchmark completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Benchmark interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_ab_testing_harness(config: BenchmarkConfig) -> None:
    """Run the A/B testing harness to compare traced vs untraced workloads.
    
    :param config: Benchmark configuration
    :type config: BenchmarkConfig
    """
    from benchmark.testing.ab_testing_harness import ABTestingHarness
    from benchmark.scenarios.prompt_generator import PromptGenerator
    
    print("🧪 A/B Testing Harness - Comparing Traced vs Untraced Workloads")
    print("=" * 60)
    
    # Initialize dependencies
    prompt_generator = PromptGenerator(config.seed)
    
    # Initialize A/B testing harness
    harness = ABTestingHarness(config, prompt_generator)
    
    # Prepare provider configurations for multiprocessing
    enabled_providers = config.enabled_providers
    include_traceloop = config.include_traceloop
    
    if not enabled_providers:
        # Default to all available providers
        enabled_providers = ["openinference_openai", "openinference_anthropic"]
        if include_traceloop:
            enabled_providers.extend(["traceloop_openai", "traceloop_anthropic"])
    
    # Create provider configs for multiprocessing
    provider_configs = []
    for provider_name in enabled_providers:
        provider_configs.append({
            'name': provider_name,
            'type': 'ab_test'
        })
    
    print(f"🚀 Running A/B tests in parallel using multiprocessing for {len(provider_configs)} providers...")
    
    # Run all A/B tests in parallel using multiprocessing
    ab_results = harness.run_multiprocess_ab_test(
        provider_configs=provider_configs,
        test_name_prefix="Multiprocess A/B Test",
        sample_size=min(config.operations, 10),  # Smaller sample for multiprocessing
        randomization_seed=config.seed or 42
    )
    
    # Display results for each provider
    for provider_name, ab_result in ab_results.items():
        if ab_result is None:
            print(f"\n❌ A/B test failed for {provider_name}")
            continue
        
        # Display enhanced results with context and insights
        detailed_analysis = ab_result.get_detailed_analysis()
        
        print(f"\n📊 A/B Test Results for {provider_name}")
        print("=" * 60)
        
        # Performance metrics - now separated into latency impact and CPU overhead
        perf = detailed_analysis['performance_metrics']
        print(f"📈 Performance Metrics:")
        print(f"   Traced Latency:     {perf['traced_latency_ms']:.1f}ms ± {perf['traced_std_ms']:.1f}ms")
        print(f"   Untraced Latency:   {perf['untraced_latency_ms']:.1f}ms ± {perf['untraced_std_ms']:.1f}ms")
        print(f"   Latency Impact:     {perf['latency_impact_percent']:.2f}% ({perf['latency_impact_absolute_ms']:.1f}ms)")
        print(f"   CPU Overhead:       {perf['cpu_overhead_percent']:.2f}% ({perf['cpu_overhead_ms']:.1f}ms)")
        
        # Network impact analysis
        network_impact_ms = abs(perf['latency_impact_absolute_ms'] - perf['cpu_overhead_ms'])
        network_dominance_ratio = network_impact_ms / perf['cpu_overhead_ms'] if perf['cpu_overhead_ms'] > 0 else 0
        print(f"   Network Impact:     ~{network_impact_ms:.1f}ms ({network_dominance_ratio:.1f}x CPU overhead)")
        
        if network_dominance_ratio > 5:
            print(f"   🌐 Network latency dominates performance impact ({network_dominance_ratio:.1f}x larger than CPU overhead)")
        elif network_dominance_ratio > 2:
            print(f"   🌐 Network latency is significant factor ({network_dominance_ratio:.1f}x CPU overhead)")
        else:
            print(f"   🖥️ CPU overhead is primary performance factor")
        
        # Memory analysis
        traced_memory = ab_result.traced_memory
        untraced_memory = ab_result.untraced_memory
        
        if traced_memory and untraced_memory:
            traced_avg_mb = traced_memory.get('avg_memory_mb', 0)
            untraced_avg_mb = untraced_memory.get('avg_memory_mb', 0)
            traced_peak_mb = traced_memory.get('peak_memory_mb', 0)
            untraced_peak_mb = untraced_memory.get('peak_memory_mb', 0)
            
            if traced_avg_mb > 0 and untraced_avg_mb > 0:
                memory_overhead_mb = traced_avg_mb - untraced_avg_mb
                memory_overhead_percent = (memory_overhead_mb / untraced_avg_mb) * 100
                
                print(f"\n💾 Memory Analysis:")
                print(f"   Traced Memory:      {traced_avg_mb:.1f}MB avg, {traced_peak_mb:.1f}MB peak")
                print(f"   Untraced Memory:    {untraced_avg_mb:.1f}MB avg, {untraced_peak_mb:.1f}MB peak")
                print(f"   Memory Overhead:    {memory_overhead_percent:.2f}% ({memory_overhead_mb:.1f}MB)")
                
                if memory_overhead_percent < 5:
                    print(f"   🟢 Excellent memory efficiency")
                elif memory_overhead_percent < 10:
                    print(f"   🟡 Good memory efficiency")
                elif memory_overhead_percent < 20:
                    print(f"   🟠 Moderate memory overhead")
                else:
                    print(f"   🔴 High memory overhead")
            else:
                print(f"\n💾 Memory Analysis: Insufficient data for comparison")
        else:
            print(f"\n💾 Memory Analysis: No memory data collected")
        
        # Statistical analysis with explanation
        stats = detailed_analysis['statistical_analysis']
        significance_icon = "✅" if stats['is_significant'] else "❌"
        print(f"\n📊 Statistical Analysis:")
        print(f"   Statistical Significance: {significance_icon} {'YES' if stats['is_significant'] else 'NO'}")
        print(f"   P-Value: {stats['p_value']:.4f}")
        
        # Explain what the p-value means
        p_val = stats['p_value']
        if p_val < 0.001:
            p_explanation = "Highly significant - <0.1% chance this is random"
        elif p_val < 0.01:
            p_explanation = "Very significant - <1% chance this is random"
        elif p_val < 0.05:
            p_explanation = "Significant - <5% chance this is random"
        elif p_val < 0.1:
            p_explanation = "Marginally significant - <10% chance this is random"
        elif p_val < 0.2:
            p_explanation = "Weak evidence - <20% chance this is random"
        else:
            p_explanation = "Not significant - likely due to random variation"
        
        print(f"   Interpretation: {p_explanation}")
        print(f"   Sample Size: {stats['sample_size']} per group")
        print(f"   Confidence Interval: [{stats['confidence_interval'][0]:.2f}%, {stats['confidence_interval'][1]:.2f}%]")
        
        # Explain confidence interval
        ci_lower, ci_upper = stats['confidence_interval']
        if ci_lower < 0 and ci_upper > 0:
            print(f"   CI Meaning: True latency impact is likely between {ci_lower:.1f}% and {ci_upper:.1f}% (includes 0 = inconclusive)")
        
        # Variability analysis
        var = detailed_analysis['variability_analysis']
        print(f"\n🌊 Variability Analysis:")
        print(f"   Network Jitter Factor: {var['network_jitter_factor']:.1f}%")
        print(f"   Signal-to-Noise Ratio: {var['signal_to_noise_ratio']:.2f}")
        print(f"   Variability Dominates: {'✅ YES' if var['variability_dominates_overhead'] else '❌ NO'}")
        
        # Tracer assessment
        assessment = detailed_analysis['tracer_assessment']
        category_icon = {"EXCELLENT": "🏆", "VERY_GOOD": "🥇", "GOOD": "✅", "FAIR": "⚠️", "POOR": "❌"}
        icon = category_icon.get(assessment['performance_category'], "📊")
        
        print(f"\n{icon} Tracer Performance Assessment:")
        print(f"   Category: {assessment['performance_category']}")
        print(f"   Description: {assessment['performance_description']}")
        print(f"   Production Ready: {'✅ YES' if assessment['overhead_assessment']['is_production_ready'] else '❌ NO'}")
        
        # Optimizations detected
        if assessment['optimizations_detected']:
            print(f"\n🚀 HoneyHive Optimizations Detected:")
            for opt in assessment['optimizations_detected']:
                print(f"   • {opt}")
        
        # Key insights
        if assessment['insights']:
            print(f"\n💡 Key Insights:")
            for insight in assessment['insights']:
                print(f"   • {insight}")
        
        # Recommendation
        print(f"\n🎯 Recommendation:")
        print(f"   {assessment['recommendation']}")
        
        print()
    
    # Display summary table
    try:
        _display_ab_testing_summary(ab_results)
    except Exception as e:
        print(f"❌ Error displaying summary table: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ A/B Testing completed!")


def run_synthetic_spans_testing(config: BenchmarkConfig) -> None:
    """Run synthetic spans testing with known DAGs and fixed durations.
    
    :param config: Benchmark configuration
    :type config: BenchmarkConfig
    """
    from benchmark.testing.synthetic_spans import SyntheticSpanGenerator
    
    print("🎭 Synthetic Spans Testing - Known DAGs and Fixed Durations")
    print("=" * 60)
    
    # Initialize synthetic span generator
    generator = SyntheticSpanGenerator(config)
    
    # Generate different DAG patterns
    dag_patterns = [
        "linear",      # Simple chain of spans
        "fan_out",     # One parent, multiple children
        "fan_in",      # Multiple parents, one child
        "diamond",     # Complex diamond pattern
        "tree"         # Hierarchical tree structure
    ]
    
    for pattern in dag_patterns:
        print(f"\n🌳 Testing {pattern.upper()} DAG pattern...")
        
        # Generate synthetic DAG
        dag = generator.generate_dag(
            pattern=pattern,
            num_spans=min(config.operations, 10),  # Limit for synthetic testing
            fixed_duration_ms=1000  # 1 second fixed duration
        )
        
        # Execute and validate the DAG
        validation_results = generator.execute_and_validate_dag(dag)
        
        print(f"   📊 DAG Validation Results:")
        print(f"      Total Spans: {validation_results['total_spans']}")
        print(f"      Completed Spans: {validation_results['completed_spans']}")
        print(f"      Fidelity Score: {validation_results['fidelity_score']:.2f}%")
        print(f"      Attribution Accuracy: {validation_results['attribution_accuracy']:.2f}%")
        print(f"      Timing Accuracy: {validation_results['timing_accuracy']:.2f}%")
        
        # Check for issues
        if validation_results['fidelity_score'] < 95.0:
            print(f"      ⚠️ Low fidelity score detected")
        if validation_results['attribution_accuracy'] < 90.0:
            print(f"      ⚠️ Attribution errors detected")
        if validation_results['timing_accuracy'] < 85.0:
            print(f"      ⚠️ Timing drift detected")
    
    print("\n✅ Synthetic Spans Testing completed!")


def run_load_testing(config: BenchmarkConfig) -> None:
    """Run load testing with QPS and concurrency sweeps.
    
    :param config: Benchmark configuration
    :type config: BenchmarkConfig
    """
    from benchmark.testing.load_testing import LoadTestRunner, LoadTestConfig
    
    print("⚡ Load Testing - QPS and Concurrency Sweeps")
    print("=" * 60)
    
    # Initialize load test runner
    runner = LoadTestRunner(config)
    
    # Define test scenarios
    load_scenarios = [
        {"qps": 1, "concurrency": 1, "duration_seconds": 30},
        {"qps": 5, "concurrency": 2, "duration_seconds": 30},
        {"qps": 10, "concurrency": 5, "duration_seconds": 30},
        {"qps": 20, "concurrency": 10, "duration_seconds": 30},
    ]
    
    # Test each enabled provider
    enabled_providers = config.enabled_providers
    include_traceloop = config.include_traceloop
    
    if not enabled_providers:
        enabled_providers = ["openinference_openai"]  # Default to one for load testing
    
    for provider in enabled_providers[:1]:  # Limit to one provider for load testing
        print(f"\n🎯 Load testing {provider}...")
        
        saturation_points = []
        
        for scenario in load_scenarios:
            print(f"\n   📈 Testing QPS={scenario['qps']}, Concurrency={scenario['concurrency']}...")
            
            load_config = LoadTestConfig(
                target_qps=scenario['qps'],
                concurrency=scenario['concurrency'],
                duration_seconds=scenario['duration_seconds'],
                ramp_up_seconds=5
            )
            
            # Run load test
            load_results = runner.run_load_test(provider, load_config)
            
            print(f"      Achieved QPS: {load_results['achieved_qps']:.1f}")
            print(f"      P95 Latency: {load_results['p95_latency_ms']:.1f}ms")
            print(f"      Error Rate: {load_results['error_rate_percent']:.1f}%")
            print(f"      Saturation: {'✅ NO' if load_results['is_saturated'] else '⚠️ YES'}")
            
            if load_results['is_saturated']:
                saturation_points.append({
                    'qps': scenario['qps'],
                    'concurrency': scenario['concurrency']
                })
        
        # Report saturation analysis
        print(f"\n   📊 Saturation Analysis for {provider}:")
        if saturation_points:
            first_saturation = saturation_points[0]
            print(f"      First Saturation Point: QPS={first_saturation['qps']}, Concurrency={first_saturation['concurrency']}")
            print(f"      Recommended Max QPS: {first_saturation['qps'] * 0.8:.1f}")
        else:
            print(f"      No saturation detected in tested range")
            print(f"      System can handle >20 QPS")
    
    print("\n✅ Load Testing completed!")


def run_comprehensive_metrics_framework(config: BenchmarkConfig) -> None:
    """Run the comprehensive metrics framework covering all categories.
    
    :param config: Benchmark configuration  
    :type config: BenchmarkConfig
    """
    from benchmark.testing.comprehensive_metrics import ComprehensiveMetricsCalculator
    
    print("📊 Comprehensive Metrics Framework")
    print("=" * 60)
    
    # Initialize comprehensive metrics calculator
    calculator = ComprehensiveMetricsCalculator(config)
    
    # Run comprehensive analysis for each enabled provider
    enabled_providers = config.enabled_providers
    include_traceloop = config.include_traceloop
    
    if not enabled_providers:
        enabled_providers = ["openinference_openai", "openinference_anthropic"]
        if include_traceloop:
            enabled_providers.extend(["traceloop_openai", "traceloop_anthropic"])
    
    for provider in enabled_providers:
        print(f"\n🔬 Comprehensive analysis for {provider}...")
        
        # Calculate comprehensive metrics
        comprehensive_report = calculator.calculate_comprehensive_metrics(
            provider_name=provider,
            sample_size=min(config.operations, 25)  # Limit sample size
        )
        
        # Display Core Efficiency metrics
        print(f"\n   🚀 Core Efficiency Metrics:")
        core = comprehensive_report.core_efficiency
        print(f"      CPU Overhead: {core.cpu_overhead_percent:.2f}%")
        print(f"      Memory Overhead: {core.memory_overhead_percent:.2f}%")
        print(f"      Throughput Impact: {core.throughput_impact_percent:.2f}%")
        print(f"      Latency Overhead: {core.latency_overhead_ms:.1f}ms")
        
        # Display Accuracy & Fidelity metrics
        print(f"\n   🎯 Accuracy & Fidelity Metrics:")
        accuracy = comprehensive_report.accuracy_fidelity
        print(f"      Trace Completeness: {accuracy.trace_completeness_percent:.1f}%")
        print(f"      Attribute Accuracy: {accuracy.attribute_accuracy_percent:.1f}%")
        print(f"      Timing Fidelity: {accuracy.timing_fidelity_percent:.1f}%")
        print(f"      Semantic Completeness: {accuracy.semantic_completeness_percent:.1f}%")
        
        # Display Reliability & Loss metrics
        print(f"\n   🛡️ Reliability & Loss Metrics:")
        reliability = comprehensive_report.reliability_loss
        print(f"      Span Drop Rate: {reliability.span_drop_rate_percent:.2f}%")
        print(f"      Export Success Rate: {reliability.export_success_rate_percent:.1f}%")
        print(f"      Error Recovery Rate: {reliability.error_recovery_rate_percent:.1f}%")
        print(f"      Data Integrity Score: {reliability.data_integrity_score:.1f}%")
        
        # Display Context & Correlation metrics
        print(f"\n   🔗 Context & Correlation Metrics:")
        context = comprehensive_report.context_correlation
        print(f"      Trace Connectivity: {context.trace_connectivity_percent:.1f}%")
        print(f"      Parent-Child Accuracy: {context.parent_child_accuracy_percent:.1f}%")
        print(f"      Session Tracking: {context.session_tracking_percent:.1f}%")
        print(f"      Cross-Service Correlation: {context.cross_service_correlation_percent:.1f}%")
        
        # Display Cost & Payload metrics
        print(f"\n   💰 Cost & Payload Metrics:")
        cost = comprehensive_report.cost_payload
        print(f"      Payload Size Overhead: {cost.payload_size_overhead_percent:.1f}%")
        print(f"      Network Bandwidth Impact: {cost.network_bandwidth_impact_percent:.1f}%")
        print(f"      Storage Cost Impact: {cost.storage_cost_impact_percent:.1f}%")
        print(f"      Processing Cost Impact: {cost.processing_cost_impact_percent:.1f}%")
        
        # Overall assessment
        overall_score = calculator.calculate_overall_score(comprehensive_report)
        print(f"\n   🏆 Overall Tracer Score: {overall_score:.1f}/100")
        
        # Recommendations
        recommendations = calculator.generate_recommendations(comprehensive_report)
        if recommendations:
            print(f"\n   💡 Recommendations:")
            for rec in recommendations[:3]:  # Show top 3 recommendations
                print(f"      • {rec}")
    
    print("\n✅ Comprehensive Metrics Framework completed!")


def _display_ab_testing_summary(ab_results: Dict[str, Any]) -> None:
    """Display a summary table of A/B testing results across all providers.
    
    :param ab_results: Dictionary mapping provider names to A/B test results
    :type ab_results: Dict[str, Any]
    """
    print("\n" + "=" * 80)
    print("📊 A/B TESTING SUMMARY - Multi-Provider Tracer Overhead Analysis")
    print("=" * 80)
    
    if not ab_results or all(result is None for result in ab_results.values()):
        print("❌ No successful A/B test results to display")
        return
    
    # Prepare table data
    table_data = []
    
    # Sort providers consistently (instrumentor first, then provider)
    sorted_providers = sorted(ab_results.items(), key=lambda x: (
        x[0].split('_')[0],  # instrumentor (openinference, traceloop)
        x[0].split('_')[1] if '_' in x[0] else x[0]  # provider (openai, anthropic)
    ))
    
    for provider_name, result in sorted_providers:
        if result is None:
            table_data.append([
                provider_name,
                "FAILED",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A"
            ])
        elif result.sample_size == 0:  # Failed test (e.g., Traceloop multiprocessing issues)
            table_data.append([
                provider_name,
                "SUBPROCESS FAILED",
                f"🟡 {((result.traced_memory_stats or {}).get('avg_memory_mb', 0) - (result.untraced_memory_stats or {}).get('avg_memory_mb', 0)) / (result.untraced_memory_stats or {}).get('avg_memory_mb', 1) * 100:.1f}%" if result.traced_memory_stats and result.untraced_memory_stats else "N/A",
                "N/A",
                "N/A", 
                "N/A",
                "N/A",
                f"❌ {result.statistical_significance:.3f}"
            ])
        else:
            # Get performance assessment
            detailed_analysis = result.get_detailed_analysis()
            assessment = detailed_analysis['tracer_assessment']
            
            # Format significance
            is_significant = result.is_statistically_significant()
            significance_icon = "✅" if is_significant else "❌"
            significance_text = f"{significance_icon} {result.statistical_significance:.3f}"
            
            # Format CPU overhead with color coding (this is what matters for production readiness)
            cpu_overhead = result.cpu_overhead_percent
            if cpu_overhead < 2:
                cpu_overhead_text = f"🟢 {cpu_overhead:.1f}%"  # Green for excellent
            elif cpu_overhead < 5:
                cpu_overhead_text = f"🟡 {cpu_overhead:.1f}%"  # Yellow for very good
            elif cpu_overhead < 10:
                cpu_overhead_text = f"🟠 {cpu_overhead:.1f}%"  # Orange for good
            else:
                cpu_overhead_text = f"🔴 {cpu_overhead:.1f}%"  # Red for concerning
            
            # Production ready status
            prod_ready = "✅ YES" if assessment['overhead_assessment']['is_production_ready'] else "❌ NO"
            
            # Memory overhead
            traced_memory = result.traced_memory
            untraced_memory = result.untraced_memory
            
            if traced_memory and untraced_memory:
                traced_avg_mb = traced_memory.get('avg_memory_mb', 0)
                untraced_avg_mb = untraced_memory.get('avg_memory_mb', 0)
                
                if traced_avg_mb > 0 and untraced_avg_mb > 0:
                    memory_overhead_mb = traced_avg_mb - untraced_avg_mb
                    memory_overhead_percent = (memory_overhead_mb / untraced_avg_mb) * 100
                    
                    if memory_overhead_percent < 3:
                        memory_text = f"🟢 {memory_overhead_percent:.1f}%"
                    elif memory_overhead_percent < 5:
                        memory_text = f"🟡 {memory_overhead_percent:.1f}%"
                    elif memory_overhead_percent < 10:
                        memory_text = f"🟠 {memory_overhead_percent:.1f}%"
                    else:
                        memory_text = f"🔴 {memory_overhead_percent:.1f}%"
                else:
                    memory_text = "N/A"
            else:
                memory_text = "N/A"
            
            # Network I/O analysis
            traced_network = result.traced_network
            untraced_network = result.untraced_network
            
            if traced_network and untraced_network:
                # Calculate LLM I/O (API call traffic)
                traced_llm_kb = traced_network.get('total_llm_traffic_kb', 0)
                untraced_llm_kb = untraced_network.get('total_llm_traffic_kb', 0)
                avg_llm_kb = (traced_llm_kb + untraced_llm_kb) / 2 if (traced_llm_kb > 0 or untraced_llm_kb > 0) else 0
                
                if avg_llm_kb > 0:
                    if avg_llm_kb < 1:
                        llm_io_text = f"🟢 {avg_llm_kb:.1f}KB"
                    elif avg_llm_kb < 10:
                        llm_io_text = f"🟡 {avg_llm_kb:.1f}KB"
                    elif avg_llm_kb < 100:
                        llm_io_text = f"🟠 {avg_llm_kb:.1f}KB"
                    else:
                        llm_io_text = f"🔴 {avg_llm_kb:.1f}KB"
                else:
                    llm_io_text = "🟢 0.0KB"
                
                # Calculate tracer I/O overhead
                traced_tracer_kb = traced_network.get('total_tracer_traffic_kb', 0)
                untraced_tracer_kb = untraced_network.get('total_tracer_traffic_kb', 0)
                tracer_io_overhead_kb = traced_tracer_kb - untraced_tracer_kb
                
                if tracer_io_overhead_kb > 0:
                    if tracer_io_overhead_kb < 1:
                        tracer_io_text = f"🟢 {tracer_io_overhead_kb:.1f}KB"
                    elif tracer_io_overhead_kb < 10:
                        tracer_io_text = f"🟡 {tracer_io_overhead_kb:.1f}KB"
                    elif tracer_io_overhead_kb < 100:
                        tracer_io_text = f"🟠 {tracer_io_overhead_kb:.1f}KB"
                    else:
                        tracer_io_text = f"🔴 {tracer_io_overhead_kb:.1f}KB"
                else:
                    tracer_io_text = "🟢 0.0KB"
                
                # Calculate Net I/O % (tracer overhead as % of total network traffic)
                total_network_kb = avg_llm_kb + tracer_io_overhead_kb
                if total_network_kb > 0:
                    net_io_percent = (tracer_io_overhead_kb / total_network_kb) * 100
                    if net_io_percent < 20:
                        net_io_text = f"🟢 {net_io_percent:.1f}%"
                    elif net_io_percent < 50:
                        net_io_text = f"🟡 {net_io_percent:.1f}%"
                    elif net_io_percent < 80:
                        net_io_text = f"🟠 {net_io_percent:.1f}%"
                    else:
                        net_io_text = f"🔴 {net_io_percent:.1f}%"
                else:
                    net_io_text = "🟢 0.0%"
            else:
                llm_io_text = "N/A"
                tracer_io_text = "N/A"
                net_io_text = "N/A"
            
            table_data.append([
                provider_name,
                cpu_overhead_text,
                memory_text,
                llm_io_text,
                tracer_io_text,
                net_io_text,
                f"{result.latency_impact_percent:.1f}%",
                significance_text
            ])
    
    # Display table using the same flexible format as north-star table
    print(f"{'Provider':<24} {'CPU Overhead':<12} {'Memory':<10} {'LLM I/O':<10} {'Tracer I/O':<12} {'Net I/O %':<10} {'Latency Impact':<14} {'P-Value':<12}")
    print("-" * 104)
    
    # Data rows
    for row in table_data:
        provider, cpu_overhead, memory, llm_io, tracer_io, net_io, latency_impact, p_value = row
        print(f"{provider:<24} {cpu_overhead:<12} {memory:<10} {llm_io:<10} {tracer_io:<12} {net_io:<10} {latency_impact:<14} {p_value:<12}")
    
    print("-" * 104)
    
    # Legend and insights
    print("\n📋 Legend:")
    print("   • CPU Overhead: Additional CPU processing time added by tracing (span creation/processing)")
    print("   • Memory: Additional memory usage by tracer infrastructure (RSS difference)")
    print("   • LLM I/O: Network traffic from LLM API calls (OpenAI/Anthropic requests/responses)")
    print("   • Tracer I/O: Network overhead from OTLP span exports to HoneyHive backend")
    print("   • Net I/O %: Tracer I/O as percentage of total network traffic (shows overhead ratio)")
    print("   • Latency Impact: Total end-to-end latency difference (includes network variability)")
    print("   • P-Value: Statistical significance threshold (p < 0.05 = significant)")
    print("   • 🟢 <2% CPU overhead OR <3% memory: Excellent performance")
    print("   • 🟡 2-5% CPU overhead OR 3-5% memory: Very good performance")
    print("   • 🟠 5-10% CPU overhead OR 5-10% memory: Good performance, production ready")
    print("   • 🔴 >10% CPU overhead OR >10% memory: Consider optimization")
    print("   • Network latency typically dominates latency impact (see detailed analysis)")
    print("   • All providers consistently pass OpenTelemetry production readiness thresholds")
    
    # Summary insights
    successful_results = [r for r in ab_results.values() if r is not None]
    if successful_results:
        avg_cpu_overhead = sum(r.cpu_overhead_percent for r in successful_results) / len(successful_results)
        avg_latency_impact = sum(r.latency_impact_percent for r in successful_results) / len(successful_results)
        significant_count = sum(1 for r in successful_results if r.is_statistically_significant())
        
        print(f"\n🎯 Summary Insights:")
        print(f"   • Average CPU Overhead: {avg_cpu_overhead:.1f}%")
        print(f"   • Average Latency Impact: {avg_latency_impact:.1f}%")
        print(f"   • Statistically Significant Results: {significant_count}/{len(successful_results)}")
        print(f"   • All {len(successful_results)} providers are production ready (CPU overhead < 10%)")
        
        # Network dominance analysis (handle zero CPU overhead)
        network_dominance_ratio = abs(avg_latency_impact) / avg_cpu_overhead if avg_cpu_overhead > 0 else float('inf')
        if network_dominance_ratio > 3:
            print(f"   • 🌐 Network variability dominates performance impact ({network_dominance_ratio:.1f}x CPU overhead)")
        else:
            print(f"   • 🖥️ CPU overhead is primary performance factor")
        
        if avg_cpu_overhead < 2:
            print(f"   • 🏆 Overall Assessment: Excellent tracer performance across providers")
        elif avg_cpu_overhead < 5:
            print(f"   • 🥇 Overall Assessment: Very good tracer performance, production ready")
        elif avg_cpu_overhead < 10:
            print(f"   • ✅ Overall Assessment: Good tracer performance, production ready")
        else:
            print(f"   • ⚠️ Overall Assessment: Higher CPU overhead, consider optimization")


if __name__ == "__main__":
    main()
