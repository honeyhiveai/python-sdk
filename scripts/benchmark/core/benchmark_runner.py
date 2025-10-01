"""
Benchmark Runner Module

This module provides the main TracerBenchmark class that orchestrates
comprehensive performance benchmarks using the modular architecture.
Follows Agent OS production code standards.
"""

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple
import multiprocessing as mp
from ..core.config import BenchmarkConfig
from ..core.metrics import PerformanceMetrics
from ..monitoring.memory_profiler import MemoryProfiler
from ..monitoring.real_export_monitor import RealExportLatencyMonitor
from ..monitoring.trace_validator import TraceValidator
from ..monitoring.span_interceptor import BenchmarkSpanInterceptor
from ..scenarios.conversation_templates import ConversationTemplates
from ..scenarios.prompt_generator import PromptGenerator
from ..providers.openinference_openai_provider import OpenInferenceOpenAIProvider
from ..providers.openinference_anthropic_provider import OpenInferenceAnthropicProvider
from ..providers.base_provider import BaseProvider, ProviderResponse
from ..reporting.metrics_calculator import MetricsCalculator
from ..reporting.formatter import ReportFormatter

# HoneyHive imports
from honeyhive import HoneyHiveTracer
from honeyhive.tracer.registry import register_tracer

logger = logging.getLogger(__name__)


def run_provider_benchmark_process(provider_config: Dict[str, Any]) -> PerformanceMetrics:
    """Run a single provider benchmark in a separate process for true isolation.
    
    This function is designed to be run in a separate process to ensure complete
    isolation of memory usage, tracer state, and monitoring resources.
    
    :param provider_config: Configuration dictionary containing all necessary data
    :type provider_config: Dict[str, Any]
    :return: Performance metrics for the provider
    :rtype: PerformanceMetrics
    """
    # CRITICAL: Record true untraced baseline BEFORE any imports or initialization
    # This follows OpenTelemetry best practices for measuring RSS_untraced
    import psutil
    import os
    untraced_baseline_mb = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    
    # Configure logging for this subprocess to suppress HoneyHive spam
    import logging
    
    # Set up logging configuration for subprocess
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Aggressively suppress HoneyHive and OpenTelemetry logs in subprocess, but keep benchmark logs
    noisy_loggers = [
        "honeyhive", "honeyhive.fallback", "honeyhive.early_init", "honeyhive.client",
        "opentelemetry", "opentelemetry.instrumentation", "opentelemetry.trace",
        "opentelemetry.sdk", "opentelemetry.exporter", "opentelemetry.util",
        "openinference", "traceloop", "httpcore", "openai", "anthropic", "httpx", "urllib3"
    ]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)
        logging.getLogger(logger_name).disabled = True
    
    # Ensure benchmark loggers are enabled at appropriate level
    # Use INFO level by default, DEBUG only if explicitly requested via environment
    benchmark_level = logging.DEBUG if os.environ.get('BENCHMARK_VERBOSE') == '1' else logging.INFO
    logging.getLogger("benchmark").setLevel(benchmark_level)
    
    # Extract configuration
    provider_name = provider_config["provider_name"]
    mode = provider_config["mode"]
    config = provider_config["config"]
    
    # Import here to avoid import issues in multiprocessing
    from ..core.config import BenchmarkConfig
    from ..monitoring.memory_profiler import MemoryProfiler
    from ..monitoring.real_export_monitor import RealExportLatencyMonitor
    from ..monitoring.trace_validator import TraceValidator
    from ..monitoring.span_interceptor import BenchmarkSpanInterceptor
    from ..scenarios.prompt_generator import PromptGenerator
    from ..reporting.metrics_calculator import MetricsCalculator
    
    # Initialize HoneyHive tracer in this process
    import sys
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from honeyhive import HoneyHiveTracer
    from honeyhive.tracer.registry import register_tracer
    
    # Initialize tracer for this provider
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project=os.getenv("HH_PROJECT", f"tracer-benchmark-{provider_name}"),
        source=f"benchmark-{provider_name}-{mode}"
    )
    
    # Initialize span interceptor
    span_interceptor = BenchmarkSpanInterceptor()
    tracer.provider.add_span_processor(span_interceptor)
    
    # Initialize provider based on type
    if provider_name.startswith("openinference_openai"):
        from ..providers.openinference_openai_provider import OpenInferenceOpenAIProvider
        provider = OpenInferenceOpenAIProvider(config, tracer)
    elif provider_name.startswith("openinference_anthropic"):
        from ..providers.openinference_anthropic_provider import OpenInferenceAnthropicProvider
        provider = OpenInferenceAnthropicProvider(config, tracer)
    elif provider_name.startswith("traceloop_openai"):
        from ..providers.traceloop_openai_provider import TraceloopOpenAIProvider
        provider = TraceloopOpenAIProvider(config, tracer)
    elif provider_name.startswith("traceloop_anthropic"):
        from ..providers.traceloop_anthropic_provider import TraceloopAnthropicProvider
        provider = TraceloopAnthropicProvider(config, tracer)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    # Initialize provider
    provider.initialize_client()
    provider.initialize_instrumentor()
    
    # Initialize monitoring (process-local, no conflicts!)
    memory_profiler = MemoryProfiler()
    export_monitor = RealExportLatencyMonitor()
    trace_validator = TraceValidator()
    prompt_generator = PromptGenerator(config.seed)
    metrics_calculator = MetricsCalculator()
    
    # Initialize network analyzer for LLM and tracer I/O analysis
    from ..monitoring.network_analyzer import NetworkIOAnalyzer
    network_analyzer = NetworkIOAnalyzer()
    logger.debug(f"🌐 NetworkIOAnalyzer initialized in subprocess for {provider_name}")
    
    # Use the true untraced baseline from the beginning of the process
    logger.debug(f"🧠 Using true untraced baseline: {untraced_baseline_mb:.1f}MB")
    
    # Wrap the OTLP exporter for real export latency measurement
    if hasattr(tracer, 'otlp_exporter') and tracer.otlp_exporter:  # type: ignore[attr-defined]
        export_monitor.wrap_exporter(tracer.otlp_exporter)  # type: ignore[attr-defined]
        logger.debug(f"🌐 Wrapped OTLP exporter for {provider_name}")
    
    try:
        # Start monitoring and override with our true untraced baseline
        memory_profiler.start_monitoring()
        memory_profiler.baseline_memory = untraced_baseline_mb
        export_monitor.start_monitoring()
        trace_validator.start_validation()
        span_interceptor.start_interception()
        network_analyzer.start_monitoring()
        
        # Wrap OTLP exporter for tracer network I/O monitoring
        if hasattr(tracer, 'otlp_exporter') and tracer.otlp_exporter:  # type: ignore[attr-defined]
            network_analyzer.wrap_exporter(tracer.otlp_exporter)  # type: ignore[attr-defined]
            logger.debug(f"🌐 Wrapped OTLP exporter for network analysis")
        
        # Generate prompts
        prompts = prompt_generator.generate_prompt_batch(
            count=config.operations,
            span_size_mode=config.span_size_mode,
            start_id=1000
        )
        
        # Execute benchmark based on mode
        responses = []
        start_time = time.perf_counter()
        
        if mode == "sequential":
            # Sequential execution
            for i, (prompt, scenario) in enumerate(prompts):
                operation_id = 1000 + i
                memory_profiler.sample_memory(f"pre_operation_{operation_id}")
                
                # Set network analyzer on provider (avoid multiprocessing serialization issues)
                if hasattr(provider, 'set_network_analyzer'):
                    logger.debug(f"🌐 Setting network_analyzer on provider: {network_analyzer is not None}")
                    provider.set_network_analyzer(network_analyzer)
                else:
                    logger.debug(f"🌐 Provider {type(provider).__name__} does not have set_network_analyzer method")
                
                logger.debug(f"🌐 Calling make_call with network_analyzer available: {network_analyzer is not None}")
                response = provider.make_call(prompt, operation_id)
                responses.append(response)
                
                memory_profiler.sample_memory(f"post_operation_{operation_id}")
                # Real export latency is now measured automatically by wrapping the OTLP exporter
                trace_validator.record_request(has_complete_trace=response.success)
        
        else:  # concurrent
            # Concurrent execution within this process
            # Note: In multiprocessing mode, concurrent operations may complete too quickly
            # for meaningful memory sampling, resulting in 0.0% memory overhead (expected)
            
            # Sample memory before concurrent operations start
            memory_profiler.sample_memory("concurrent_start")
            
            # Set network analyzer on provider for concurrent operations
            if hasattr(provider, 'set_network_analyzer'):
                logger.debug(f"🌐 Setting network_analyzer on provider for concurrent: {network_analyzer is not None}")
                provider.set_network_analyzer(network_analyzer)
            else:
                logger.debug(f"🌐 Provider {type(provider).__name__} does not have set_network_analyzer method for concurrent")
            
            with ThreadPoolExecutor(max_workers=config.concurrent_threads) as executor:
                futures = []
                
                # Submit all futures and sample memory
                for i, (prompt, scenario) in enumerate(prompts):
                    operation_id = 1000 + i
                    logger.debug(f"🌐 Submitting concurrent make_call with network_analyzer available: {network_analyzer is not None}")
                    future = executor.submit(provider.make_call, prompt, operation_id)
                    futures.append(future)
                    
                    # Sample memory periodically during submission
                    if i == 0:  # After first submission
                        memory_profiler.sample_memory("concurrent_first_submit")
                
                # Sample memory after all submissions
                memory_profiler.sample_memory("concurrent_all_submitted")
                
                # Collect results
                for i, future in enumerate(as_completed(futures)):
                    response = future.result()
                    responses.append(response)
                    
                    # Sample memory after first and last completion
                    if i == 0:
                        memory_profiler.sample_memory("concurrent_first_complete")
                    elif i == len(futures) - 1:
                        memory_profiler.sample_memory("concurrent_last_complete")
                    
                    # Real export latency is now measured automatically by wrapping the OTLP exporter
                    trace_validator.record_request(has_complete_trace=response.success)
            
            # Sample memory after concurrent operations complete
            memory_profiler.sample_memory("concurrent_end")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Stop monitoring and collect data
        memory_stats = memory_profiler.stop_monitoring()
        export_stats = export_monitor.stop_monitoring()
        trace_stats = trace_validator.stop_validation()
        intercepted_spans, overhead_stats = span_interceptor.stop_interception()
        network_stats = network_analyzer.get_metrics_format()
        network_analyzer.stop_monitoring()
        network_analyzer.cleanup()
        
        # Update trace stats with real span data
        span_stats = span_interceptor.get_span_statistics()
        trace_stats.update({
            "trace_coverage_percent": span_stats.get("trace_coverage_percent", 0.0),
            "attribute_completeness_percent": span_stats.get("attribute_completeness_percent", 0.0)
        })
        
        # Calculate comprehensive metrics
        metrics = metrics_calculator.calculate_comprehensive_metrics(
            responses=responses,
            memory_stats=memory_stats,
            network_stats=export_stats,
            network_io_stats=network_stats,
            trace_validation_stats=trace_stats,
            overhead_stats=overhead_stats
        )
        
        # Set provider and mode manually since they're not passed to calculator
        metrics.provider = provider_name
        metrics.mode = mode
        return metrics
        
    finally:
        # Cleanup
        provider.cleanup_instrumentor()


logger = logging.getLogger(__name__)


class TracerBenchmark:
    """Multi-LLM tracer performance benchmark suite with modular architecture.
    
    Orchestrates comprehensive performance benchmarks for HoneyHive tracers
    using multiple LLM providers with separate tracer instances. Implements
    all teammate feedback requirements including north-star metrics, conversation
    simulation, and A/B testing harness.
    
    :param config: Benchmark configuration parameters
    :type config: BenchmarkConfig
    
    Example:
        >>> config = BenchmarkConfig(operations=50, openai_model="gpt-4o")
        >>> benchmark = TracerBenchmark(config)
        >>> benchmark.run_full_benchmark()
        >>> print("Benchmark completed successfully!")
    """
    
    def __init__(self, config: BenchmarkConfig) -> None:
        """Initialize benchmark suite with modular components.
        
        :param config: Benchmark configuration parameters
        :type config: BenchmarkConfig
        """
        self.config = config
        
        # Initialize monitoring components
        self.memory_profiler = MemoryProfiler()
        self.export_monitor = RealExportLatencyMonitor()
        self.trace_validator = TraceValidator()
        self.span_interceptor = BenchmarkSpanInterceptor()
        
        # Initialize scenario generation
        self.conversation_templates = ConversationTemplates()
        self.prompt_generator = PromptGenerator(seed=config.seed)
        
        # Initialize metrics and reporting
        self.metrics_calculator = MetricsCalculator()
        self.report_formatter = ReportFormatter()
        
        # Provider instances
        self.providers: Dict[str, BaseProvider] = {}
        self.tracers: Dict[str, Any] = {}
        
        # Results storage
        self.results: List[PerformanceMetrics] = []
        
        logger.debug("🚀 TracerBenchmark initialized with modular architecture")
    
    def validate_environment(self) -> None:
        """Validate required environment variables and configuration.
        
        :raises ValueError: If required environment variables are missing
        """
        required_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "HH_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        # Validate configuration
        self.config.__post_init__()
        
        logger.info("✅ Environment validation passed")
    
    def initialize_tracers(self) -> None:
        """Initialize separate tracer instances for each enabled LLM provider.
        
        Creates truly independent tracer instances following the BYOI
        (Bring Your Own Instrumentor) pattern with proper multi-instance setup.
        Only initializes tracers for enabled providers.
        """
        logger.info("🔧 Initializing tracer instances...")
        
        # Get list of enabled providers (default to all if not specified)
        enabled_providers = self.config.enabled_providers or [
            "openinference_openai", "openinference_anthropic", 
            "traceloop_openai", "traceloop_anthropic"
        ]
        
        # Initialize OpenInference OpenAI tracer if enabled
        if "openinference_openai" in enabled_providers:
            self.tracers["openinference_openai"] = HoneyHiveTracer.init(
                api_key=os.getenv("HH_API_KEY"),
                project=os.getenv("HH_PROJECT", "tracer-benchmark-openinference-openai"),
                source="benchmark-openinference-openai"
            )
            openinference_openai_tracer_id = register_tracer(self.tracers["openinference_openai"])
            
            # Add span interceptor to OpenInference OpenAI tracer provider
            openinference_openai_provider = self.tracers["openinference_openai"].provider
            openinference_openai_provider.add_span_processor(self.span_interceptor)
            
            # Wrap OTLP exporter for real export latency measurement
            if hasattr(self.tracers["openinference_openai"], 'otlp_exporter') and self.tracers["openinference_openai"].otlp_exporter:  # type: ignore[attr-defined]
                self.export_monitor.wrap_exporter(self.tracers["openinference_openai"].otlp_exporter)  # type: ignore[attr-defined]
                logger.debug("🌐 Wrapped OpenInference OpenAI OTLP exporter")
            
            logger.info(f"✅ OpenInference OpenAI tracer initialized (ID: {openinference_openai_tracer_id}) with span interceptor and export monitor")
        
        # Initialize OpenInference Anthropic tracer if enabled
        if "openinference_anthropic" in enabled_providers:
            self.tracers["openinference_anthropic"] = HoneyHiveTracer.init(
                api_key=os.getenv("HH_API_KEY"),
                project=os.getenv("HH_PROJECT", "tracer-benchmark-openinference-anthropic"),
                source="benchmark-openinference-anthropic"
            )
            openinference_anthropic_tracer_id = register_tracer(self.tracers["openinference_anthropic"])
            
            # Add span interceptor to OpenInference Anthropic tracer provider
            openinference_anthropic_provider = self.tracers["openinference_anthropic"].provider
            openinference_anthropic_provider.add_span_processor(self.span_interceptor)
            
            # Wrap OTLP exporter for real export latency measurement
            if hasattr(self.tracers["openinference_anthropic"], 'otlp_exporter') and self.tracers["openinference_anthropic"].otlp_exporter:  # type: ignore[attr-defined]
                self.export_monitor.wrap_exporter(self.tracers["openinference_anthropic"].otlp_exporter)  # type: ignore[attr-defined]
                logger.debug("🌐 Wrapped OpenInference Anthropic OTLP exporter")
            
            logger.info(f"✅ OpenInference Anthropic tracer initialized (ID: {openinference_anthropic_tracer_id}) with span interceptor and export monitor")
        
        # Initialize Traceloop tracers if requested and enabled
        if self.config.include_traceloop:
            # Initialize Traceloop OpenAI tracer if enabled
            if "traceloop_openai" in enabled_providers:
                self.tracers["traceloop_openai"] = HoneyHiveTracer.init(
                    api_key=os.getenv("HH_API_KEY"),
                    project=os.getenv("HH_PROJECT", "tracer-benchmark-traceloop-openai"),
                    source="benchmark-traceloop-openai"
                )
                traceloop_openai_tracer_id = register_tracer(self.tracers["traceloop_openai"])
                
                # Add span interceptor to Traceloop OpenAI tracer provider
                traceloop_openai_provider = self.tracers["traceloop_openai"].provider
                traceloop_openai_provider.add_span_processor(self.span_interceptor)
                
                # Wrap OTLP exporter for real export latency measurement
                if hasattr(self.tracers["traceloop_openai"], 'otlp_exporter') and self.tracers["traceloop_openai"].otlp_exporter:  # type: ignore[attr-defined]
                    self.export_monitor.wrap_exporter(self.tracers["traceloop_openai"].otlp_exporter)  # type: ignore[attr-defined]
                    logger.debug("🌐 Wrapped Traceloop OpenAI OTLP exporter")
                
                logger.info(f"✅ Traceloop OpenAI tracer initialized (ID: {traceloop_openai_tracer_id}) with span interceptor and export monitor")
            
            # Initialize Traceloop Anthropic tracer if enabled
            if "traceloop_anthropic" in enabled_providers:
                self.tracers["traceloop_anthropic"] = HoneyHiveTracer.init(
                    api_key=os.getenv("HH_API_KEY"),
                    project=os.getenv("HH_PROJECT", "tracer-benchmark-traceloop-anthropic"),
                    source="benchmark-traceloop-anthropic"
                )
                traceloop_anthropic_tracer_id = register_tracer(self.tracers["traceloop_anthropic"])
                
                # Add span interceptor to Traceloop Anthropic tracer provider
                traceloop_anthropic_provider = self.tracers["traceloop_anthropic"].provider
                traceloop_anthropic_provider.add_span_processor(self.span_interceptor)
                
                # Wrap OTLP exporter for real export latency measurement
                if hasattr(self.tracers["traceloop_anthropic"], 'otlp_exporter') and self.tracers["traceloop_anthropic"].otlp_exporter:  # type: ignore[attr-defined]
                    self.export_monitor.wrap_exporter(self.tracers["traceloop_anthropic"].otlp_exporter)  # type: ignore[attr-defined]
                    logger.debug("🌐 Wrapped Traceloop Anthropic OTLP exporter")
                
                logger.info(f"✅ Traceloop Anthropic tracer initialized (ID: {traceloop_anthropic_tracer_id}) with span interceptor and export monitor")
            
        
        # Log summary of initialized tracers
        tracer_count = len(self.tracers)
        enabled_list = ", ".join(enabled_providers)
        logger.info(f"🎯 Created {tracer_count} independent tracer instances for: {enabled_list}")
    
    def initialize_providers(self) -> None:
        """Initialize LLM providers with their respective tracers and instrumentors."""
        logger.info("🤖 Initializing LLM providers...")
        
        # Initialize OpenAI provider (OpenInference) if enabled
        if "openinference_openai" in self.tracers:
            self.providers["openinference_openai"] = OpenInferenceOpenAIProvider(self.config, self.tracers["openinference_openai"])
            self.providers["openinference_openai"].initialize_client()
            self.providers["openinference_openai"].initialize_instrumentor()
            logger.info("✅ OpenInference OpenAI provider initialized")
        
        # Initialize Anthropic provider (OpenInference) if enabled
        if "openinference_anthropic" in self.tracers:
            self.providers["openinference_anthropic"] = OpenInferenceAnthropicProvider(self.config, self.tracers["openinference_anthropic"])
            self.providers["openinference_anthropic"].initialize_client()
            self.providers["openinference_anthropic"].initialize_instrumentor()
            logger.info("✅ OpenInference Anthropic provider initialized")
        
        # Initialize Traceloop providers if requested and enabled
        if self.config.include_traceloop:
            # Import Traceloop providers
            from ..providers.traceloop_openai_provider import TraceloopOpenAIProvider
            from ..providers.traceloop_anthropic_provider import TraceloopAnthropicProvider
            
            # Initialize Traceloop OpenAI provider if enabled
            if "traceloop_openai" in self.tracers:
                self.providers["traceloop_openai"] = TraceloopOpenAIProvider(
                    self.config, self.tracers["traceloop_openai"]
                )
                self.providers["traceloop_openai"].initialize_client()
                self.providers["traceloop_openai"].initialize_instrumentor()
                logger.info("✅ Traceloop OpenAI provider initialized")
            
            # Initialize Traceloop Anthropic provider if enabled
            if "traceloop_anthropic" in self.tracers:
                self.providers["traceloop_anthropic"] = TraceloopAnthropicProvider(
                    self.config, self.tracers["traceloop_anthropic"]
                )
                self.providers["traceloop_anthropic"].initialize_client()
                self.providers["traceloop_anthropic"].initialize_instrumentor()
                logger.info("✅ Traceloop Anthropic provider initialized")
    
    def cleanup_providers(self) -> None:
        """Clean up provider instrumentors."""
        for provider_name, provider in self.providers.items():
            provider.cleanup_instrumentor()
        logger.info("🧹 Providers cleaned up")
    
    def run_warmup(self) -> None:
        """Run warmup operations to stabilize performance measurements."""
        if self.config.warmup_operations <= 0:
            logger.info("🔥 Skipping warmup (0 operations)")
            return
        
        logger.info(f"🔥 Running warmup ({self.config.warmup_operations} operations)...")
        
        # Generate warmup prompts
        warmup_prompts = self.prompt_generator.generate_prompt_batch(
            count=self.config.warmup_operations,
            span_size_mode="small",  # Use small spans for warmup
            start_id=0
        )
        
        # Run warmup for each provider
        for provider_name, provider in self.providers.items():
            for i, (prompt, _) in enumerate(warmup_prompts):
                try:
                    provider.make_call(prompt, i)
                except Exception as e:
                    logger.warning(f"Warmup error for {provider_name}: {e}")
        
        logger.info("✅ Warmup completed")
    
    def run_sequential_benchmark(self, provider_name: str) -> PerformanceMetrics:
        """Run sequential benchmark for a specific provider.
        
        :param provider_name: Name of the provider to benchmark
        :type provider_name: str
        :return: Performance metrics for the sequential run
        :rtype: PerformanceMetrics
        """
        logger.info(f"📈 Running sequential benchmark for {provider_name}...")
        
        provider = self.providers[provider_name]
        
        # Start monitoring
        self.memory_profiler.start_monitoring()
        self.export_monitor.start_monitoring()
        self.trace_validator.start_validation()
        self.span_interceptor.start_interception()
        
        # Generate prompts using conversation simulation
        prompts = self.prompt_generator.generate_prompt_batch(
            count=self.config.operations,
            span_size_mode=self.config.span_size_mode,
            start_id=1000  # Offset to avoid warmup IDs
        )
        
        # Execute operations sequentially
        responses: List[ProviderResponse] = []
        start_time = time.perf_counter()
        
        for i, (prompt, scenario) in enumerate(prompts):
            operation_id = 1000 + i
            
            # Sample memory before operation
            self.memory_profiler.sample_memory(f"pre_operation_{operation_id}")
            
            # Record network operation
            operation_data = {
                "scenario_domain": scenario.domain.value,
                "scenario_complexity": scenario.complexity,
                "expected_tokens": scenario.expected_tokens[1],  # Use max expected
            }
            # Real export latency is now measured automatically by wrapping the OTLP exporter
            
            # Make the call
            response = provider.make_call(prompt, operation_id)
            responses.append(response)
            
            # Sample memory after operation
            self.memory_profiler.sample_memory(f"post_operation_{operation_id}")
            
            # Record trace validation
            self.trace_validator.record_request(has_complete_trace=response.success)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Stop monitoring and get span data
        memory_stats = self.memory_profiler.stop_monitoring()
        export_stats = self.export_monitor.stop_monitoring()
        trace_stats = self.trace_validator.stop_validation()
        intercepted_spans, overhead_stats = self.span_interceptor.stop_interception()
        
        # Update trace stats with real span data
        span_stats = self.span_interceptor.get_span_statistics()
        trace_stats.update({
            'trace_coverage_percent': span_stats['trace_coverage_percent'],
            'attribute_completeness_percent': span_stats['attribute_completeness_percent'],
        })
        
        # Calculate comprehensive metrics with real overhead data
        metrics = self.metrics_calculator.calculate_comprehensive_metrics(
            responses=responses,
            memory_stats=memory_stats,
            network_stats=export_stats,
            trace_validation_stats=trace_stats,
            overhead_stats=overhead_stats
        )
        
        # Update mode
        metrics.mode = "sequential"
        
        # Completion logged by parallel runner
        return metrics
    
    def run_concurrent_benchmark(self, provider_name: str) -> PerformanceMetrics:
        """Run concurrent benchmark for a specific provider.
        
        :param provider_name: Name of the provider to benchmark
        :type provider_name: str
        :return: Performance metrics for the concurrent run
        :rtype: PerformanceMetrics
        """
        logger.info(f"⚡ Running concurrent benchmark for {provider_name} with {self.config.concurrent_threads} threads...")
        
        provider = self.providers[provider_name]
        
        # Start monitoring
        self.memory_profiler.start_monitoring()
        self.export_monitor.start_monitoring()
        self.trace_validator.start_validation()
        self.span_interceptor.start_interception()
        
        # Generate prompts
        prompts = self.prompt_generator.generate_prompt_batch(
            count=self.config.operations,
            span_size_mode=self.config.span_size_mode,
            start_id=2000  # Different offset for concurrent
        )
        
        # Execute operations concurrently
        responses: List[ProviderResponse] = []
        start_time = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=self.config.concurrent_threads) as executor:
            # Submit all tasks
            futures = []
            for i, (prompt, scenario) in enumerate(prompts):
                operation_id = 2000 + i
                
                # Record network operation
                operation_data = {
                    "scenario_domain": scenario.domain.value,
                    "scenario_complexity": scenario.complexity,
                    "expected_tokens": scenario.expected_tokens[1],
                }
                # Real export latency is now measured automatically by wrapping the OTLP exporter
                
                future = executor.submit(provider.make_call, prompt, operation_id)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    response = future.result()
                    responses.append(response)
                    
                    # Sample memory after operation completion
                    self.memory_profiler.sample_memory(f"concurrent_operation_{response.operation_id}")
                    
                    # Record trace validation
                    self.trace_validator.record_request(has_complete_trace=response.success)
                except Exception as e:
                    logger.error(f"Concurrent operation failed: {e}")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Stop monitoring and get span data
        memory_stats = self.memory_profiler.stop_monitoring()
        export_stats = self.export_monitor.stop_monitoring()
        trace_stats = self.trace_validator.stop_validation()
        intercepted_spans, overhead_stats = self.span_interceptor.stop_interception()
        
        # Update trace stats with real span data
        span_stats = self.span_interceptor.get_span_statistics()
        trace_stats.update({
            'trace_coverage_percent': span_stats['trace_coverage_percent'],
            'attribute_completeness_percent': span_stats['attribute_completeness_percent'],
        })
        
        # Calculate comprehensive metrics with real overhead data
        metrics = self.metrics_calculator.calculate_comprehensive_metrics(
            responses=responses,
            memory_stats=memory_stats,
            network_stats=export_stats,
            trace_validation_stats=trace_stats,
            overhead_stats=overhead_stats
        )
        
        # Update mode
        metrics.mode = "concurrent"
        
        # Completion logged by parallel runner
        return metrics
    
    def run_full_benchmark(self) -> List[PerformanceMetrics]:
        """Run complete benchmark suite for all providers and modes.
        
        :return: List of performance metrics for all benchmark runs
        :rtype: List[PerformanceMetrics]
        
        Example:
            >>> benchmark = TracerBenchmark(config)
            >>> results = benchmark.run_full_benchmark()
            >>> print(f"Completed {len(results)} benchmark runs")
        """
        logger.info("🚀 Starting Multi-LLM Tracer Performance Benchmarks")
        logger.info("=" * 60)
        
        try:
            # Validation and initialization
            self.validate_environment()
            self.initialize_tracers()
            self.initialize_providers()
            
            # Warmup
            self.run_warmup()
            
            # Sequential benchmarks (run in parallel across providers)
            logger.info("📈 Running sequential benchmarks...")
            sequential_results = self._run_benchmarks_parallel("sequential")
            self.results.extend(sequential_results)
            
            # Concurrent benchmarks (run in parallel across providers)
            logger.info("⚡ Running concurrent benchmarks...")
            concurrent_results = self._run_benchmarks_parallel("concurrent")
            self.results.extend(concurrent_results)
            
            logger.info("✅ All benchmarks completed successfully")
            
        finally:
            # Always cleanup
            self.cleanup_providers()
        
        return self.results
    
    def _run_benchmarks_parallel(self, mode: str) -> List[PerformanceMetrics]:
        """Run benchmarks in parallel across all providers using multiprocessing for true isolation.
        
        :param mode: Benchmark mode ("sequential" or "concurrent")
        :type mode: str
        :return: List of performance metrics from all providers
        :rtype: List[PerformanceMetrics]
        """
        results = []
        
        # Prepare provider configurations for multiprocessing
        provider_configs = []
        for provider_name in self.providers.keys():
            provider_config = {
                "provider_name": provider_name,
                "mode": mode,
                "config": self.config
            }
            provider_configs.append(provider_config)
        
        # Use ProcessPoolExecutor for true isolation
        logger.info(f"🔄 Starting {len(provider_configs)} processes for {mode} benchmarks...")
        
        with ProcessPoolExecutor(max_workers=len(self.providers)) as executor:
            # Submit all provider benchmarks to separate processes
            future_to_provider = {}
            for provider_config in provider_configs:
                provider_name = provider_config["provider_name"]
                future = executor.submit(run_provider_benchmark_process, provider_config)
                future_to_provider[future] = provider_name
            
            # Collect results as they complete
            for future in as_completed(future_to_provider):
                provider_name = future_to_provider[future]
                try:
                    metrics = future.result()
                    results.append(metrics)
                    logger.info(f"✅ {mode.capitalize()} benchmark completed for {provider_name} (PID: {metrics.provider})")
                except Exception as e:
                    logger.error(f"❌ {mode.capitalize()} benchmark failed for {provider_name}: {e}")
                    import traceback
                    logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        return results
    
    def generate_report(self) -> str:
        """Generate comprehensive benchmark report.
        
        :return: Formatted benchmark report
        :rtype: str
        """
        if not self.results:
            return "No benchmark results available"
        
        return self.report_formatter.generate_comprehensive_report(
            metrics_list=self.results,
            config=self.config
        )
    
    def get_north_star_summary(self) -> str:
        """Get north-star metrics summary table.
        
        :return: Formatted north-star metrics table
        :rtype: str
        """
        if not self.results:
            return "No results available for north-star metrics"
        
        return self.report_formatter.generate_north_star_table(self.results)
    
    def export_results(self) -> Dict[str, Any]:
        """Export results as structured data.
        
        :return: Structured benchmark results
        :rtype: Dict[str, Any]
        """
        if not self.results:
            return {"error": "No results available"}
        
        return self.report_formatter.export_structured_data(self.results)
    
    def validate_determinism(self) -> bool:
        """Validate that prompt generation is deterministic for A/B testing.
        
        :return: True if prompt generation is deterministic
        :rtype: bool
        """
        return self.prompt_generator.validate_determinism(operation_id=12345, iterations=5)
    
    def get_conversation_statistics(self) -> Dict[str, Any]:
        """Get statistics about conversation template usage.
        
        :return: Conversation template statistics
        :rtype: Dict[str, Any]
        """
        return self.conversation_templates.get_scenario_statistics()
    
    def test_provider_connections(self) -> Dict[str, bool]:
        """Test connections to all configured providers.
        
        :return: Dictionary mapping provider names to connection status
        :rtype: Dict[str, bool]
        """
        results = {}
        for provider_name, provider in self.providers.items():
            try:
                results[provider_name] = provider.test_connection()
            except Exception as e:
                logger.error(f"Connection test failed for {provider_name}: {e}")
                results[provider_name] = False
        
        return results
