# HoneyHive Python SDK Documentation

## Overview

The HoneyHive Python SDK is a comprehensive tool for AI/ML observability, tracing, evaluation, and experimentation. It provides developers with the capability to monitor, trace, and evaluate AI applications with built-in support for popular frameworks like OpenAI, LangChain, and LlamaIndex.

## Project Structure

```
honeyhive/
├── __init__.py                 # Main SDK exports and public API
├── sdk.py                      # Core HoneyHive SDK class
├── basesdk.py                  # Base SDK functionality
├── sdkconfiguration.py         # SDK configuration management
├── httpclient.py               # HTTP client implementations
├── tracer/                     # Tracing and observability
│   ├── __init__.py            # HoneyHiveTracer main class
│   ├── custom.py              # Custom tracing decorators (@trace, @atrace)
│   └── asyncio_tracer.py      # Async tracing support
├── evaluation/                 # Evaluation framework
│   ├── __init__.py            # Evaluation runner and decorators
│   └── evaluators.py          # Evaluator decorators and utilities
├── cli/                       # Command-line interface
│   ├── __main__.py            # CLI entry point
│   └── eval.py                # CLI evaluation commands
├── models/                    # Data models and API schemas
│   ├── components/            # Component models (Session, Event, etc.)
│   ├── operations/            # API operation models
│   └── errors/                # Error handling models
├── utils/                     # Utility modules
│   ├── config.py              # Configuration management
│   ├── dotdict.py             # Dictionary utilities
│   ├── baggage_dict.py        # OpenTelemetry baggage handling
│   ├── langchain_tracer.py    # LangChain integration
│   ├── llamaindex_tracer.py   # LlamaIndex integration
│   └── telemetry.py           # Telemetry collection
└── [api_modules]/             # API endpoint modules
    ├── configurations.py      # Configuration management API
    ├── datapoints.py          # Dataset datapoint operations
    ├── datasets.py            # Dataset management
    ├── events.py              # Event logging and retrieval
    ├── experiments.py         # Experiment/run management
    ├── metrics.py             # Custom metrics
    ├── projects.py            # Project management
    ├── session.py             # Session management
    └── tools.py               # Tool definitions
```

## Core Components
