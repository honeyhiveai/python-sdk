# Multi-LLM Tracer Performance Benchmark

This comprehensive benchmark suite establishes performance baselines for HoneyHive tracers across multiple LLM providers and instrumentor combinations with truly independent tracer instances.

## Features

- **Multi-Instrumentor Support**: Tests both OpenInference and Traceloop instrumentors
- **Multi-LLM Setup**: Creates truly independent tracer instances for OpenAI and Anthropic
- **Real Performance Measurement**: Uses actual OTLP export latency and span processing times
- **Modular Architecture**: Clean separation of concerns with dedicated modules for providers, monitoring, and reporting
- **Comprehensive Metrics**: Six north-star metrics covering cost, fidelity, and reliability
- **Process Isolation**: True memory isolation using multiprocessing for accurate measurements
- **Conversation Simulation**: Realistic conversation scenarios with deterministic prompt generation
- **Flexible Provider Selection**: Target specific instrumentor/provider combinations

## Prerequisites

### Environment Variables

Set the following environment variables before running the benchmark:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export HH_API_KEY="your-honeyhive-api-key"
export HH_PROJECT="your-project-name"  # Optional, defaults to benchmark project names
```

### Dependencies

The script requires the following packages (already included in the project):
- `openai` - OpenAI Python client
- `anthropic` - Anthropic Python client
- `openinference-instrumentation-openai` - OpenAI instrumentation
- `openinference-instrumentation-anthropic` - Anthropic instrumentation
- `traceloop-sdk` - Traceloop instrumentors (optional)
- `psutil` - System and process monitoring
- `honeyhive` - HoneyHive Python SDK

## Usage

### Basic Usage

```bash
# Run comprehensive benchmark with all available instrumentor/provider pairings
python scripts/tracer-performance-benchmark.py

# Quick north-star metrics assessment
python scripts/tracer-performance-benchmark.py --operations 20 --north-star-only
```

### Advanced Usage

```bash
# Customize benchmark parameters
python scripts/tracer-performance-benchmark.py \
    --operations 100 \
    --concurrent-threads 8 \
    --warmup-operations 10 \
    --span-size-mode large \
    --max-tokens 1000

# Target specific instrumentor/provider combinations
python scripts/tracer-performance-benchmark.py \
    --include "openinference_openai,traceloop_anthropic" \
    --operations 50

# Test with different models
python scripts/tracer-performance-benchmark.py \
    --openai-model gpt-4 \
    --anthropic-model claude-3-opus-20240229 \
    --operations 30

# Export results to JSON
python scripts/tracer-performance-benchmark.py \
    --operations 50 \
    --export-json benchmark-results.json
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--operations` | Number of operations per provider | 50 |
| `--concurrent-threads` | Number of concurrent threads | 4 |
| `--warmup-operations` | Number of warmup operations | 5 |
| `--openai-model` | OpenAI model to use | gpt-4o |
| `--anthropic-model` | Anthropic model to use | claude-sonnet-4-20250514 |
| `--span-size-mode` | Span size category (small/medium/large/mixed) | mixed |
| `--max-tokens` | Maximum tokens per response | 500 |
| `--temperature` | Temperature for LLM responses | 0.1 |
| `--include` | Comma-separated provider list or 'all' | all |
| `--north-star-only` | Show only north-star metrics table | false |
| `--export-json` | Export results to JSON file | none |
| `--verbose` | Enable verbose logging | false |
| `--validate-only` | Only validate environment, don't run benchmarks | false |

### Provider Selection

The `--include` argument supports flexible provider targeting:

```bash
# All available providers (default)
--include "all"

# Specific instrumentor/provider combinations
--include "openinference_openai,traceloop_anthropic"

# Single provider for focused testing
--include "traceloop_openai"

# Available combinations:
# - openinference_openai
# - openinference_anthropic  
# - traceloop_openai
# - traceloop_anthropic
```

## Architecture

The benchmark uses a modular architecture with clear separation of concerns:

```
scripts/benchmark/
├── core/                    # Core configuration and orchestration
│   ├── benchmark_runner.py  # Main benchmark orchestrator
│   ├── config.py           # Configuration dataclasses
│   └── metrics.py          # Performance metrics dataclasses
├── providers/              # LLM provider implementations
│   ├── base_provider.py    # Abstract base provider
│   ├── openinference_*.py  # OpenInference providers
│   └── traceloop_*.py      # Traceloop providers
├── monitoring/             # Performance monitoring components
│   ├── memory_profiler.py  # Memory usage tracking
│   ├── real_export_monitor.py # Real OTLP export measurement
│   ├── span_interceptor.py # Span interception for validation
│   └── trace_validator.py  # Trace coverage validation
├── scenarios/              # Test scenario generation
│   ├── conversation_templates.py # Realistic conversation scenarios
│   └── prompt_generator.py # Deterministic prompt generation
└── reporting/              # Results formatting and analysis
    ├── metrics_calculator.py # Comprehensive metrics calculation
    └── formatter.py        # Report formatting and visualization
```

## North-Star Metrics

The benchmark focuses on six critical metrics for production decision-making:

| Metric | Description | Target |
|--------|-------------|--------|
| **Overhead** | Additional latency added by tracing | < 5% |
| **Drops** | Percentage of spans lost before storage | 0% |
| **Export** | P95 latency for span export to backend | < 100ms |
| **Coverage** | Percentage of requests with complete traces | 100% |
| **Complete** | Percentage of spans with all required attributes | 100% |
| **Memory** | Additional memory overhead from tracing | < 5% |

## Benchmark Types

### 1. Sequential Benchmarks
- Tests each provider individually with sequential API calls
- Measures baseline performance and latency characteristics
- Tracks real tracer overhead through span processing time measurement

### 2. Concurrent Benchmarks  
- Tests each provider with multiple concurrent threads
- Measures throughput and scalability under load
- Uses process isolation for accurate memory measurement

### 3. Real Export Latency Measurement
- Intercepts actual OTLP exports from HoneyHive tracers
- Measures real network latency to telemetry backend
- Separates tracer overhead from benchmark measurement overhead

### 4. Comprehensive Span Validation
- Intercepts completed spans for attribute completeness analysis
- Validates trace coverage across all operations
- Supports multiple semantic convention formats (OpenInference, Traceloop, OpenLIT)

## Sample Output

```
========================================================================================================================
📊 NORTH-STAR METRICS SUMMARY
========================================================================================================================

🎯 BENCHMARK CONTEXT:

📋 What We're Testing:
  • Multi-instrumentor tracer performance comparison (OpenInference vs Traceloop)
  • Real-world conversation simulation with varied complexity and span sizes
  • True process isolation using multiprocessing for accurate memory measurement
  • Both sequential and concurrent execution patterns
  • Flexible provider selection for targeted performance analysis

Instrumentor    Provider   Mode         Overhead    Drops    Export     Coverage   Complete   Memory   
--------------------------------------------------------------------------------------------------------------------------
Openinference   OPENAI     sequential   4.90%       0.0%     105ms      100.0%     80.0%      7.91%    
Openinference   OPENAI     concurrent   4.92%       0.0%     76ms       100.0%     80.0%      8.72%    
Traceloop       OPENAI     sequential   4.95%       0.0%     104ms      100.0%     100.0%     1.41%    
Traceloop       OPENAI     concurrent   4.95%       0.0%     90ms       100.0%     100.0%     1.48%    
--------------------------------------------------------------------------------------------------------------------------

📋 Legend:
  • Overhead: Additional latency added by tracing (lower is better)
  • Drops: Percentage of spans lost before storage (0% is ideal)
  • Export: P95 latency for span export to backend (lower is better)
  • Coverage: Percentage of requests with complete traces (100% is ideal)
  • Complete: Percentage of spans with all required attributes (100% is ideal)
  • Memory: Additional memory overhead from tracing (lower is better)
```

## Performance Insights

The benchmark reveals actionable performance differences:

### Memory Efficiency Champions
- **Traceloop providers**: Consistently ~1.4% memory overhead
- **OpenInference providers**: Higher memory usage (7-9% for OpenAI)

### Export Performance Leaders  
- **Concurrent mode**: Generally faster export times (76-90ms vs 104-105ms)
- **Provider variation**: Real network conditions affect export latency

### Attribute Completeness Issues
- **OpenInference OpenAI**: Only 80% attribute completeness
- **All Traceloop providers**: 100% attribute completeness

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required environment variables are set
2. **Rate Limiting**: Reduce `--operations` if hitting API limits  
3. **Memory Issues**: Reduce `--concurrent-threads` for limited memory systems
4. **Import Errors**: Ensure Traceloop SDK is installed if using Traceloop providers

### Debug Mode

Enable verbose logging for detailed execution information:

```bash
python scripts/tracer-performance-benchmark.py --verbose
```

### Validation Mode

Test environment and connections without running benchmarks:

```bash
python scripts/tracer-performance-benchmark.py --validate-only
```

## Contributing

When modifying the benchmark:

1. Follow the modular architecture patterns
2. Maintain compatibility with Agent OS standards  
3. Add appropriate logging and error handling
4. Update tests and documentation for new features
5. Preserve the north-star metrics focus for production decisions

## Related Files

- `scripts/benchmark/` - Complete modular benchmark package
- `tests/performance/` - Core performance testing utilities  
- `examples/integrations/` - LLM integration examples
- `src/honeyhive/tracer/` - HoneyHive tracer implementation