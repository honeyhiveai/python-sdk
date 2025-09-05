# Technology Stack Standards - HoneyHive Python SDK

## Core Languages & Runtimes
- **Python**: 3.11+ (strict minimum requirement)
  - Supported versions: 3.11, 3.12, 3.13
  - Type hints required for ALL functions, methods, and class attributes
  - Modern Python features encouraged (match statements, union types, walrus operator)

### Type Safety Requirements
- **Enum Usage**: MANDATORY use of proper enum imports in all code
  ```python
  # ✅ CORRECT
  from honeyhive.models import EventType
  @trace(event_type=EventType.model)
  
  # ❌ INCORRECT
  @trace(event_type="model")  # Never use string literals
  ```
- **Import Validation**: All documentation examples must include complete imports
- **Type Checking**: All examples must pass mypy validation
- **Documentation Standards**: See `.agent-os/standards/best-practices.md` for full requirements

## Build & Package Management
- **pyproject.toml**: PEP 621 compliant project configuration
- **hatchling**: Modern build backend
- **pip**: Package installation
- **Virtual Environment**: Required, named "python-sdk"
- **tox**: Multi-version testing orchestration

## Testing Framework & Quality Assurance

### Testing Requirements - MANDATORY
- **Zero Failing Tests Policy**: ALL commits must have 100% passing tests
- **tox**: Primary testing orchestration tool
  ```bash
  tox -e unit           # Unit tests (MUST pass)
  tox -e integration    # Integration tests (MUST pass)
  tox -e py311 -e py312 -e py313  # All Python versions (MUST pass)
  ```
- **pytest**: Test framework with fixtures and async support
- **Coverage**: **Minimum 80% project-wide** (enforced), **70% individual files** (recommended)
- **Pre-commit validation**: Automated test execution before commits
- **Enhanced Quality Gates**: Unified documentation compliance validation including:
  - **Dual Changelog Sync**: Enforces CHANGELOG.md and docs/changelog.rst synchronization
  - **Content Style Preservation**: Maintains different purposes (technical vs user-facing)
  - **Changelog Updates**: Required for all significant changes (code, docs, config, tooling, Agent OS files)
  - **Documentation Compliance**: Mandatory for new features and large changesets (>5 files)
  - **AI Assistant Compliance**: Automatic enforcement with detailed feedback
  - **Comprehensive Coverage**: File pattern matching for docs, config, tooling, and Agent OS files

### Testing Architecture
- **Unit Tests**: Fast, isolated, mock external dependencies
- **Integration Tests**: Real API calls, external service validation
- **Performance Tests**: Latency and throughput validation
- **Compatibility Tests**: Cross-version Python and dependency validation

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

## Documentation Tools & Standards

### Core Documentation Stack
- **sphinx**: >=7.0.0 - Documentation generation engine
- **sphinx-rtd-theme**: >=1.3.0 - ReadTheDocs compatible theme
- **myst-parser**: >=2.0.0 - Markdown support in Sphinx
- **sphinxcontrib-mermaid**: >=0.9.2 - Diagram generation support

### Documentation Architecture - Divio System
Following the [Divio Documentation System](https://docs.divio.com/documentation-system/) for comprehensive user experience:

**🎯 Four Documentation Types**:
1. **TUTORIALS** (`tutorials/`) - Learning-oriented, step-by-step guides
2. **HOW-TO GUIDES** (`how-to/`) - Problem-oriented, specific solutions
3. **REFERENCE** (`reference/`) - Information-oriented, technical specifications
4. **EXPLANATION** (`explanation/`) - Understanding-oriented, conceptual background

### Documentation Quality Standards
```yaml
# Content Requirements by Type
tutorials:
  max_duration: "15-20 minutes"
  testing: "Verify with 3+ new users monthly"
  structure: "Objective → Prerequisites → Steps → Results → Next Steps"

how-to:
  title_format: "How to [solve specific problem]"
  structure: "Problem → Solution → Implementation → Verification"
  prerequisites: "Always clearly stated"

reference:
  coverage: "100% API documentation"
  examples: "Working code for every function"
  accuracy: "Automated testing of examples"

explanation:
  purpose: "Design rationale and conceptual understanding"
  cross_links: "Connect to practical tutorials and how-tos"
  depth: "Sufficient context for informed decisions"
```

### Content Validation Tools
```python
# Automated documentation testing
docs/utils/
├── audit-content.py          # Broken link detection
├── test-examples.py          # Code example verification
├── validate-structure.py     # Divio compliance checking
└── user-journey-test.py      # End-to-end tutorial testing
```

### Documentation Generation System
```python
# Automated template-based documentation generation
docs/_templates/
├── generate_provider_docs.py              # Generation script
├── multi_instrumentor_integration_formal_template.rst  # Base template
├── template_variables.md                  # Variable documentation
└── README.md                             # Usage instructions
```

**Generation Commands**:
```bash
# Generate single provider documentation
python docs/_templates/generate_provider_docs.py --provider openai

# Regenerate all integration documentation
for provider in openai anthropic google-ai google-adk bedrock azure-openai mcp; do
    python docs/_templates/generate_provider_docs.py --provider $provider
done
```

**See**: `.agent-os/standards/documentation-generation.md` for complete usage guide

### Documentation Deployment
- **GitHub Pages**: Primary hosting platform for documentation
- **Preview Builds**: Automatic PR previews for review using GitHub Actions
- **Multi-Version Support**: Sphinx versioning for releases
- **Search Integration**: Full-text search capability
- **Analytics**: User journey tracking and content optimization

### Visual Documentation Standards
- **Mermaid Diagrams**: Architecture and flow diagrams
- **Screenshots**: UI walkthrough captures (sanitized credentials)
- **Code Highlighting**: Syntax highlighting for all languages
- **Responsive Design**: Mobile-friendly documentation layout

### Cross-Platform Compatibility
- **Desktop**: Full navigation and content accessibility
- **Mobile**: Optimized reading experience
- **Print**: PDF generation capability for offline reference
- **Screen Readers**: WCAG 2.1 accessibility compliance

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
### Core CI/CD Infrastructure
- **GitHub Actions**: Primary CI/CD platform with multi-tier testing strategy
- **GitHub CLI**: >=2.78.0 - Workflow investigation, automation, and debugging
- **yamllint**: >=1.37.0 - YAML syntax validation with 120-character line length
- **Docker**: Container development, Lambda simulation, and testing environments
- **tox**: Multi-environment testing automation across Python versions

### Workflow Management
- **Composite Jobs**: Reduced PR interface clutter through workflow consolidation
- **Matrix Strategies**: Strategic parallelization for cross-platform testing
- **Conditional Logic**: Branch and commit message-based execution control
- **Artifact Management**: Comprehensive test result preservation and analysis

### Testing Infrastructure
- **Docker Simulation**: Complete AWS Lambda runtime simulation using official images
- **Performance Benchmarking**: Statistical measurement with 99.8% variance reduction
- **Real Environment Testing**: Production AWS Lambda validation on main branch
- **Cross-Platform Testing**: Ubuntu, Windows, macOS validation matrices

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
