# Multi-LLM Tracer Performance Benchmark - Modular Version

A comprehensive, modular benchmark suite for HoneyHive tracer performance testing across multiple LLM providers. Implements teammate feedback requirements including north-star metrics, conversation simulation, and A/B testing harness.

## 🎯 Features

### **Core Capabilities**
- **Multi-LLM Support**: Independent tracer instances for OpenAI and Anthropic
- **Modular Architecture**: Clean separation of concerns with testable components
- **Six North-Star Metrics**: Complete teammate feedback implementation
- **Conversation Simulation**: Deterministic prompt generation for A/B testing
- **Comprehensive Analysis**: Memory, network, and trace validation monitoring

### **Advanced Features**
- **Span Size Testing**: Small (50-200), medium (200-500), large (500+) token scenarios
- **Trace Coverage**: Percentage of requests with complete root spans
- **Attribute Completeness**: Validation of required span attributes
- **Mathematical Formulas**: All calculations use teammate feedback equations
- **Enhanced Reporting**: Tables, assessments, and actionable recommendations

## 🏗️ Architecture

```
benchmark/
├── core/                    # Core configuration and orchestration
│   ├── config.py           # BenchmarkConfig dataclass
│   ├── metrics.py          # PerformanceMetrics dataclass  
│   └── benchmark_runner.py # Main TracerBenchmark class
├── providers/              # LLM provider implementations
│   ├── base_provider.py    # Abstract BaseProvider class
│   ├── openai_provider.py  # OpenAI implementation
│   └── anthropic_provider.py # Anthropic implementation
├── monitoring/             # Performance monitoring components
│   ├── memory_profiler.py  # Memory usage tracking
│   ├── network_monitor.py  # Network I/O monitoring
│   └── trace_validator.py  # Trace coverage & completeness
├── scenarios/              # Conversation simulation
│   ├── conversation_templates.py # Realistic conversation scenarios
│   └── prompt_generator.py # Deterministic prompt generation
└── reporting/              # Metrics calculation and formatting
    ├── metrics_calculator.py # Comprehensive metrics with formulas
    └── formatter.py        # Enhanced report generation
```

## 🚀 Quick Start

### **Basic Usage**

```bash
# Basic benchmark with default settings
python scripts/tracer-performance-benchmark-modular.py

# Quick north-star metrics assessment  
python scripts/tracer-performance-benchmark-modular.py --operations 20 --north-star-only

# Custom configuration with large spans
python scripts/tracer-performance-benchmark-modular.py \
    --operations 100 \
    --span-size-mode large \
    --concurrent-threads 8
```

### **Environment Setup**

Required environment variables:
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"  
export HH_API_KEY="your-honeyhive-key"
export HH_PROJECT="your-project-name"  # Optional
```

### **Validation & Testing**

```bash
# Validate environment and connections
python scripts/tracer-performance-benchmark-modular.py --validate-only

# Test deterministic prompt generation
python scripts/tracer-performance-benchmark-modular.py --test-determinism

# Test provider connections
python scripts/tracer-performance-benchmark-modular.py --test-connections
```

## 📊 North-Star Metrics

The benchmark implements six north-star metrics for quick tracer capability assessment:

| Metric | Formula | Description |
|--------|---------|-------------|
| **Overhead Latency** | `Δlat = mean(lat_traced − lat_untraced)` | Extra time added by tracing (%) |
| **Dropped Span Rate** | `% = dropped / (exported + dropped)` | Spans lost before storage (%) |
| **Export Latency** | `P95 span enqueue→ACK` | Time to export telemetry (ms) |
| **Trace Coverage** | `% = traced_requests / total_requests` | Requests with complete root span (%) |
| **Attribute Completeness** | `% = spans_with_all_required / total_spans` | Spans with required fields (%) |
| **Memory Overhead** | `% = (RSS_traced − RSS_untraced) / RSS_untraced` | Extra memory footprint (%) |

### **Assessment Categories**

- **Cost of Tracing**: Overhead Latency + Memory Overhead
- **Fidelity of Data**: Trace Coverage + Attribute Completeness  
- **Reliability of Pipeline**: Dropped Span Rate + Export Latency

## 🎲 Conversation Simulation

### **Deterministic A/B Testing**

The benchmark uses seeded randomness to ensure identical conversation flows across different LLM providers for fair comparison:

```python
# Same operation_id always generates identical prompts
generator = PromptGenerator(seed=42)
prompt_openai, scenario = generator.generate_prompt(operation_id=123, span_size_mode="mixed")
prompt_anthropic, scenario = generator.generate_prompt(operation_id=123, span_size_mode="mixed")
# prompt_openai == prompt_anthropic (guaranteed identical)
```

### **Conversation Domains**

- **Technical**: Code review, debugging, architecture discussions
- **Creative**: Writing, brainstorming, content generation
- **Factual**: Research, data analysis, information retrieval
- **Analytical**: Problem solving, decision making, planning
- **Troubleshooting**: Error diagnosis, system debugging

### **Span Size Categories**

- **Small (50-200 tokens)**: Quick queries, simple responses
- **Medium (200-500 tokens)**: Detailed explanations, code examples
- **Large (500+ tokens)**: Complex analysis, comprehensive responses

## 📈 Advanced Configuration

### **Span Size Testing**

```bash
# Test specific span sizes
python scripts/tracer-performance-benchmark-modular.py --span-size-mode small
python scripts/tracer-performance-benchmark-modular.py --span-size-mode medium  
python scripts/tracer-performance-benchmark-modular.py --span-size-mode large

# Mixed distribution (40% small, 40% medium, 20% large)
python scripts/tracer-performance-benchmark-modular.py --span-size-mode mixed
```

### **Model Configuration**

```bash
# Use specific models
python scripts/tracer-performance-benchmark-modular.py \
    --openai-model gpt-4o \
    --anthropic-model claude-sonnet-4-20250514
```

### **Performance Tuning**

```bash
# High-throughput testing
python scripts/tracer-performance-benchmark-modular.py \
    --operations 200 \
    --concurrent-threads 16 \
    --warmup-operations 10

# Low-latency testing  
python scripts/tracer-performance-benchmark-modular.py \
    --operations 50 \
    --concurrent-threads 2 \
    --timeout 10.0
```

## 📊 Output Formats

### **North-Star Table**

```
Provider | Mode       | Overhead | Drops | Export | Coverage | Complete | Memory
---------|------------|----------|-------|--------|----------|----------|-------
openai   | sequential |     0.1% |  0.0% |   65ms |   100.0% |    95.0% |   1.5%
anthropic| sequential |     0.2% |  0.0% |   70ms |   100.0% |    97.0% |   1.8%
```

### **Comprehensive Report**

- Configuration summary
- Performance results table
- Detailed analysis per provider/mode
- Performance assessment (pass/fail criteria)
- Actionable recommendations
- Additional statistics

### **JSON Export**

```bash
# Export structured data for analysis
python scripts/tracer-performance-benchmark-modular.py \
    --export-json benchmark_results.json
```

## 🔧 Development

### **Adding New Providers**

1. Create provider class inheriting from `BaseProvider`
2. Implement required methods: `make_call`, `initialize_client`, `initialize_instrumentor`
3. Add to `benchmark_runner.py` initialization
4. Update CLI configuration options

### **Adding New Metrics**

1. Add fields to `PerformanceMetrics` dataclass
2. Implement calculation in `MetricsCalculator`
3. Update `ReportFormatter` for display
4. Add to north-star metrics if applicable

### **Extending Conversation Templates**

1. Add new domains to `ConversationDomain` enum
2. Create scenarios in `CONVERSATION_TEMPLATES`
3. Update prompt generation logic if needed
4. Test determinism with new scenarios

## 🧪 Testing

### **Unit Tests** (Planned)

```bash
# Run unit tests for all modules
python -m pytest tests/benchmark/

# Test specific components
python -m pytest tests/benchmark/test_providers.py
python -m pytest tests/benchmark/test_metrics_calculator.py
```

### **Integration Tests**

```bash
# Minimal integration test
python scripts/tracer-performance-benchmark-modular.py --operations 2 --warmup-operations 1

# Determinism validation
python scripts/tracer-performance-benchmark-modular.py --test-determinism
```

## 📋 Performance Criteria

### **Pass/Fail Thresholds**

- **Success Rate**: ≥99% (✅), ≥95% (⚠️), <95% (❌)
- **P95 Latency**: ≤5000ms (✅), ≤10000ms (⚠️), >10000ms (❌)  
- **Memory Overhead**: ≤5% (✅), ≤10% (⚠️), >10% (❌)
- **Tracer Overhead**: ≤2% (✅), ≤5% (⚠️), >5% (❌)

### **Recommendations**

The benchmark provides actionable recommendations based on results:

- High latency detection and optimization suggestions
- Memory leak investigation guidance  
- Error handling improvement recommendations
- Performance optimization strategies
- Production deployment considerations

## 🤝 Contributing

This modular architecture follows Agent OS production standards:

- **Type Safety**: 100% type annotations
- **Documentation**: Sphinx-compatible docstrings with examples
- **Error Handling**: Graceful degradation patterns
- **Logging**: Structured logging (no print statements)
- **Modularity**: Clean separation of concerns
- **Testing**: Comprehensive unit and integration tests

## 📚 Related Documentation

- [Original Benchmark Script](../tracer-performance-benchmark.py) - Legacy monolithic version
- [praxis OS Standards](../../.praxis-os/standards/) - Development guidelines
- [HoneyHive SDK Documentation](../../docs/) - SDK usage and examples
- [Performance Test Suite](../../tests/performance/) - Existing performance tests
