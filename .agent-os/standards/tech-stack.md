# Technology Stack Standards - HoneyHive Python SDK

## Core Languages & Runtimes
- **Python**: 3.11+ (strict minimum requirement)
  - Supported versions: 3.11, 3.12, 3.13
  - Type hints required for ALL functions, methods, and class attributes
  - Modern Python features encouraged (match statements, union types, walrus operator)

## Build & Package Management
- **pyproject.toml**: PEP 621 compliant project configuration
- **hatchling**: Modern build backend
- **pip**: Package installation
- **Virtual Environment**: Required, named "python-sdk"
- **tox**: Multi-version testing orchestration

## Core SDK Dependencies
- **httpx**: >=0.24.0 - Modern async/sync HTTP client
- **pydantic**: >=2.0.0 - Data validation and models
- **opentelemetry-api**: >=1.20.0 - W3C standard tracing
- **opentelemetry-sdk**: >=1.20.0 - OTEL implementation
- **opentelemetry-exporter-otlp-proto-http**: >=1.20.0 - OTLP export
- **wrapt**: >=1.14.0 - Decorator utilities
- **click**: >=8.0.0 - CLI framework
- **python-dotenv**: >=1.0.0 - Environment management
- **pyyaml**: >=6.0 - YAML parsing

## Testing Framework
- **pytest**: >=7.0.0 - Primary testing framework
- **pytest-asyncio**: >=0.21.0 - Async test support
- **pytest-cov**: >=4.0.0 - Coverage reporting
- **pytest-mock**: >=3.10.0 - Mocking utilities
- **pytest-xdist**: >=3.0.0 - Parallel test execution
- **tox**: >=4.0.0 - Test environment management
- **psutil**: >=5.9.0 - System monitoring in tests

## Code Quality & Linting
- **black**: Line length 88, Python 3.11+ target
- **isort**: Black-compatible import sorting
- **flake8**: >=6.0.0 - Style guide enforcement
- **pylint**: Custom configuration, 9.99 score target
- **mypy**: >=1.0.0 - Static type checking (strict mode)
- **typeguard**: >=4.0.0 - Runtime type checking
- **yamllint**: >=1.37.0 - YAML syntax validation

## Documentation Tools
- **sphinx**: >=7.0.0 - Documentation generation
- **sphinx-rtd-theme**: >=1.3.0 - Documentation theme
- **myst-parser**: >=2.0.0 - Markdown support in Sphinx

## API Design Standards
- **OpenAPI**: 3.0 specification
- **REST**: RESTful API design principles
- **JSON**: Primary data interchange format
- **Pydantic Models**: Request/response validation
- **OpenTelemetry**: W3C trace context standard

## Observability Stack
- **OpenTelemetry**: Full OTEL compliance
- **OTLP**: OpenTelemetry Protocol for exports
- **W3C Baggage**: Context propagation
- **Structured Logging**: JSON-formatted logs
- **Metrics**: Prometheus-compatible format

## Environment & Configuration
- **Environment Variables**: HH_* prefix convention
- **python-dotenv**: .env file support
- **Configuration Hierarchy**: Constructor > Env > Defaults
- **Standard Env Support**: HTTP_*, EXPERIMENT_* compatibility

## Development & CI/CD Tools
- **GitHub CLI**: >=2.78.0 - GitHub Actions investigation and automation
- **Docker**: Container development and Lambda testing
- **tox**: Multi-environment testing automation

## Deployment Targets
- **Docker**: Container support
- **AWS Lambda**: Serverless functions
- **Kubernetes**: Cloud-native deployment
- **PyPI**: Package distribution
- **GitHub Actions**: CI/CD automation

## Integration Ecosystem
### LLM Providers
- OpenAI / Azure OpenAI
- Anthropic Claude
- Google Gemini
- AWS Bedrock
- Cohere, Groq, Mistral
- Ollama (local models)

### Vector Databases
- Pinecone, Chroma, Qdrant
- LanceDB, Marqo
- Zilliz/Milvus

### Frameworks
- LangChain / LangGraph
- LlamaIndex
- CrewAI
- LiteLLM
- Vercel AI SDK

### Experiment Platforms
- MLflow
- Weights & Biases
- Comet ML
