# Technical Specifications - Enhanced Compatibility Matrix

## Architecture Changes

### 1. Unified Test Infrastructure

#### Base Test Class
```python
class HoneyHiveCompatibilityTest:
    """Base class for all compatibility tests following Agent OS standards."""
    
    def setUp(self):
        """Set up test environment with proper API keys and configuration."""
        self.api_key = os.getenv("HH_API_KEY")
        self.project = "compatibility-matrix-test"
        self.source = "compatibility_test"
        
        if not self.api_key:
            pytest.skip("HH_API_KEY not available")
    
    def validate_full_feature_set(self, tracer, integration_type):
        """Validate all HoneyHive features work with integration."""
        self.validate_span_operations(tracer)
        self.validate_event_operations(tracer)
        self.validate_context_baggage(tracer)
        self.validate_session_management(tracer)
        self.validate_decorators(tracer)
        self.validate_performance_reliability(tracer)
```

#### Feature Validation Framework
```python
class FeatureValidator:
    """Validates HoneyHive features across integrations."""
    
    CORE_FEATURES = [
        "span_creation", "span_attributes", "span_context",
        "event_creation", "event_enrichment", "session_management",
        "baggage_propagation", "decorator_tracing", "async_support"
    ]
    
    def validate_feature(self, feature_name, tracer, integration_context):
        """Validate specific feature works correctly."""
        validator_method = getattr(self, f"_validate_{feature_name}")
        return validator_method(tracer, integration_context)
    
    def _validate_span_creation(self, tracer, context):
        """Test span creation and basic operations."""
        with tracer.start_span("test_span") as span:
            span.set_attribute("test_key", "test_value")
            assert span is not None
            return True
```

### 2. Instrumentor Integration Architecture

#### OpenInference Integration
```python
class TestOpenInferenceIntegration(HoneyHiveCompatibilityTest):
    """Test OpenInference instrumentor integration with HoneyHive tracing."""
    
    @pytest.mark.skipif(not OPENINFERENCE_AVAILABLE, reason="OpenInference not available")
    def test_openinference_openai_integration(self):
        """Test OpenInference OpenAI instrumentor with HoneyHive tracing."""
        
        # 1. Initialize OpenInference instrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        openai_instrumentor = OpenAIInstrumentor()
        
        # 2. Initialize HoneyHive tracer
        tracer = HoneyHiveTracer.init(
            api_key=self.api_key,
            project=self.project,
            source="openinference_openai"
        )
        
        # 3. Instrument with tracer provider (CORRECT BYOI PATTERN)
        openai_instrumentor.instrument(tracer_provider=tracer.provider)
        
        # Test OpenAI operations with tracing
        @trace(tracer=tracer, event_type="model", event_name="openai_completion")
        def test_openai_completion():
            """Test OpenAI completion with OpenInference tracing."""
            import openai
            client = openai.OpenAI()
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello, world!"}]
            )
            
            return response.choices[0].message.content
        
        # Execute test
        result = test_openai_completion()
        assert result is not None
        
        # Validate full feature set works with OpenInference
        self.validate_full_feature_set(tracer, "openinference_openai")
        
        # Validate OpenInference-specific features
        self.validate_openinference_features(tracer, "openai")
        
        # Cleanup
        openai_instrumentor.uninstrument()
    
    def validate_openinference_features(self, tracer, provider):
        """Validate OpenInference-specific tracing features."""
        
        # Test OpenInference span attributes
        with tracer.start_span("openinference_test") as span:
            span.set_attribute("openinference.provider", provider)
            span.set_attribute("llm.request.model", "gpt-3.5-turbo")
            span.set_attribute("llm.usage.prompt_tokens", 10)
            span.set_attribute("llm.usage.completion_tokens", 20)
        
        # Test OpenInference event creation
        event_id = tracer.create_event(
            event_name="openinference_llm_call",
            event_type="model",
            inputs={"messages": [{"role": "user", "content": "test"}]},
            outputs={"content": "response"},
            metadata={
                "provider": provider,
                "model": "gpt-3.5-turbo",
                "openinference_version": "0.1.0"
            }
        )
        assert event_id is not None
```

#### Traceloop Integration
```python
class TestTraceloopIntegration(HoneyHiveCompatibilityTest):
    """Test Traceloop (OpenLLMetry) instrumentor integration with HoneyHive tracing."""
    
    @pytest.mark.skipif(not TRACELOOP_AVAILABLE, reason="Traceloop not available")
    def test_traceloop_openai_integration(self):
        """Test Traceloop OpenAI instrumentor with HoneyHive tracing."""
        
        # 1. Initialize Traceloop instrumentor
        from opentelemetry.instrumentation.openai import OpenAIInstrumentor
        openai_instrumentor = OpenAIInstrumentor()
        
        # 2. Initialize HoneyHive tracer
        tracer = HoneyHiveTracer.init(
            api_key=self.api_key,
            project=self.project,
            source="traceloop_openai"
        )
        
        # 3. Instrument with tracer provider (CORRECT BYOI PATTERN)
        openai_instrumentor.instrument(tracer_provider=tracer.provider)
        
        # Test OpenAI operations with Traceloop tracing
        @trace(tracer=tracer, event_type="model", event_name="traceloop_completion")
        def test_traceloop_completion():
            """Test OpenAI completion with Traceloop tracing."""
            import openai
            client = openai.OpenAI()
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello from Traceloop!"}]
            )
            
            return response.choices[0].message.content
        
        # Execute test
        result = test_traceloop_completion()
        assert result is not None
        
        # Validate full feature set works with Traceloop
        self.validate_full_feature_set(tracer, "traceloop_openai")
        
        # Validate Traceloop-specific features
        self.validate_traceloop_features(tracer, "openai")
        
        # Cleanup
        openai_instrumentor.uninstrument()
    
    def validate_traceloop_features(self, tracer, provider):
        """Validate Traceloop-specific tracing features."""
        
        # Test Traceloop span attributes
        with tracer.start_span("traceloop_test") as span:
            span.set_attribute("traceloop.provider", provider)
            span.set_attribute("llm.request.type", "chat")
            span.set_attribute("llm.request.model", "gpt-3.5-turbo")
            span.set_attribute("llm.response.model", "gpt-3.5-turbo")
            span.set_attribute("llm.usage.total_tokens", 30)
        
        # Test Traceloop event creation with OpenLLMetry attributes
        event_id = tracer.create_event(
            event_name="traceloop_llm_call",
            event_type="model",
            inputs={"messages": [{"role": "user", "content": "test"}]},
            outputs={"content": "response"},
            metadata={
                "provider": provider,
                "model": "gpt-3.5-turbo",
                "traceloop_version": "0.1.0",
                "openllmetry_integration": True
            }
        )
        assert event_id is not None
```

### 3. AI Framework Integration Architecture

#### AWS Strands Integration
```python
class TestAWSStrandsIntegration(HoneyHiveCompatibilityTest):
    """Test AWS Strands integration with HoneyHive tracing."""
    
    @pytest.mark.skipif(not STRANDS_AVAILABLE, reason="AWS Strands not available")
    def test_strands_agent_workflow(self):
        """Test Strands agent workflow with HoneyHive tracing."""
        
        # Initialize HoneyHive tracer
        tracer = HoneyHiveTracer.init(
            api_key=self.api_key,
            project=self.project,
            source="aws_strands"
        )
        
        # Test Strands agent with HoneyHive tracing
        @trace(tracer=tracer, event_type="chain", event_name="strands_agent")
        async def run_strands_agent(query: str):
            """Run AWS Strands agent with tracing."""
            
            # Initialize Strands agent
            agent = StrandsAgent(
                name="test-agent",
                instructions="You are a helpful assistant"
            )
            
            # Trace conversation steps
            with tracer.start_span("strands_conversation") as span:
                span.set_attribute("query", query)
                
                # Run agent conversation
                response = await agent.run(query)
                
                span.set_attribute("response", response.content)
                span.set_attribute("tool_calls", len(response.tool_calls))
                
                return response
        
        # Execute test
        response = asyncio.run(run_strands_agent("Test query"))
        
        # Validate full feature set
        self.validate_full_feature_set(tracer, "aws_strands")
        
        # Validate Strands-specific features
        self.validate_strands_features(tracer, response)
```

#### Pydantic AI Integration
```python
class TestPydanticAIIntegration(HoneyHiveCompatibilityTest):
    """Test Pydantic AI integration with HoneyHive tracing."""
    
    @pytest.mark.skipif(not PYDANTIC_AI_AVAILABLE, reason="Pydantic AI not available")
    def test_pydantic_ai_agent(self):
        """Test Pydantic AI agent with type-safe tracing."""
        
        # Initialize HoneyHive tracer
        tracer = HoneyHiveTracer.init(
            api_key=self.api_key,
            project=self.project,
            source="pydantic_ai"
        )
        
        # Define Pydantic models for structured outputs
        class WeatherResponse(BaseModel):
            temperature: float
            condition: str
            location: str
            confidence: float
        
        # Create Pydantic AI agent with tracing
        @trace(tracer=tracer, event_type="model", event_name="pydantic_ai_agent")
        async def run_pydantic_agent(query: str) -> WeatherResponse:
            """Run Pydantic AI agent with structured output."""
            
            agent = Agent(
                'openai:gpt-4',
                result_type=WeatherResponse,
                system_prompt="You are a weather assistant."
            )
            
            # Trace the agent run with structured validation
            with tracer.start_span("pydantic_ai_run") as span:
                span.set_attribute("query", query)
                span.set_attribute("result_type", "WeatherResponse")
                
                result = await agent.run(query)
                
                # Trace structured output validation
                span.set_attribute("validated_output", result.data.model_dump())
                span.set_attribute("validation_success", True)
                
                return result.data
        
        # Execute test
        response = asyncio.run(run_pydantic_agent("What's the weather in NYC?"))
        
        # Validate response structure
        assert isinstance(response, WeatherResponse)
        assert response.temperature is not None
        
        # Validate full feature set
        self.validate_full_feature_set(tracer, "pydantic_ai")
```

#### Microsoft Semantic Kernel Integration
```python
class TestSemanticKernelIntegration(HoneyHiveCompatibilityTest):
    """Test Microsoft Semantic Kernel integration."""
    
    @pytest.mark.skipif(not SEMANTIC_KERNEL_AVAILABLE, reason="Semantic Kernel not available")
    def test_semantic_kernel_workflow(self):
        """Test SK plugin workflow with tracing."""
        
        # Initialize HoneyHive tracer
        tracer = HoneyHiveTracer.init(
            api_key=self.api_key,
            project=self.project,
            source="semantic_kernel"
        )
        
        # Create Semantic Kernel with tracing
        @trace(tracer=tracer, event_type="chain", event_name="sk_workflow")
        async def run_sk_workflow(goal: str):
            """Run Semantic Kernel workflow with tracing."""
            
            # Initialize Semantic Kernel
            kernel = Kernel()
            
            # Add OpenAI service
            kernel.add_service(OpenAIChatCompletion(
                service_id="openai",
                ai_model_id="gpt-4"
            ))
            
            # Trace plugin execution
            with tracer.start_span("sk_plugin_execution") as span:
                span.set_attribute("goal", goal)
                
                # Load and execute plugins
                plugins = kernel.add_plugin_from_prompt_directory(
                    "plugins", "WriterPlugin"
                )
                
                # Execute function with tracing
                result = await kernel.invoke(
                    plugins["Brainstorm"],
                    input=goal
                )
                
                span.set_attribute("plugin_result", str(result))
                span.set_attribute("plugin_count", len(plugins))
                
                return result
        
        # Execute test
        result = asyncio.run(run_sk_workflow("Write a blog post about AI"))
        
        # Validate full feature set
        self.validate_full_feature_set(tracer, "semantic_kernel")
```

### 3. Correct BYOI Pattern Implementation

#### Standard BYOI Pattern
```python
def setup_instrumentor_integration(instrumentor_class, tracer):
    """Standard pattern for instrumentor integration."""
    
    # 1. Initialize instrumentor
    instrumentor = instrumentor_class()
    
    # 2. Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        api_key=api_key,
        project=project,
        source="integration_test"
    )
    
    # 3. Instrument with tracer provider (CORRECT BYOI PATTERN)
    instrumentor.instrument(tracer_provider=tracer.provider)
    
    return tracer, instrumentor
```

#### Deprecated Pattern Cleanup
```python
# ❌ DEPRECATED - Remove all instances of this pattern
def deprecated_pattern():
    """This pattern should be removed from all tests."""
    tracer = HoneyHiveTracer.init(
        api_key=api_key,
        project=project,
        instrumentors=[instrumentor]  # ❌ Remove this parameter
    )
```

### 4. Integration Onboarding Framework

#### Instrumentor Onboarding Process
```python
# scripts/onboard_instrumentor.py
class InstrumentorOnboardingFramework:
    """Framework for onboarding new instrumentor integrations."""
    
    def onboard_instrumentor(self, config: InstrumentorConfig):
        """Complete onboarding process for new instrumentor."""
        
        # 1. Generate test files
        self.generate_compatibility_tests(config)
        
        # 2. Generate documentation
        self.generate_documentation(config)
        
        # 3. Generate example code
        self.generate_examples(config)
        
        # 4. Update compatibility matrix
        self.update_compatibility_matrix(config)
        
        # 5. Run validation
        self.validate_integration(config)
    
    def generate_compatibility_tests(self, config: InstrumentorConfig):
        """Generate comprehensive compatibility tests."""
        
        test_template = """
class Test{provider_name}Integration(HoneyHiveCompatibilityTest):
    \"\"\"Test {provider_name} instrumentor integration with HoneyHive tracing.\"\"\"
    
    @pytest.mark.skipif(not {provider_name.upper()}_AVAILABLE, reason="{provider_name} not available")
    def test_{provider_name.lower()}_integration(self):
        \"\"\"Test {provider_name} instrumentor with HoneyHive tracing.\"\"\"
        
        # 1. Initialize {instrumentor_type} instrumentor
        from {import_path} import {instrumentor_class}
        instrumentor = {instrumentor_class}()
        
        # 2. Initialize HoneyHive tracer
        tracer = HoneyHiveTracer.init(
            api_key=self.api_key,
            project=self.project,
            source="{provider_name.lower()}_integration"
        )
        
        # 3. Instrument with tracer provider (CORRECT BYOI PATTERN)
        instrumentor.instrument(tracer_provider=tracer.provider)
        
        # Test {provider_name} operations with tracing
        result = self.run_{provider_name.lower()}_test()
        assert result is not None
        
        # Validate full feature set
        self.validate_full_feature_set(tracer, "{provider_name.lower()}")
        
        # Validate {provider_name}-specific features
        self.validate_{provider_name.lower()}_features(tracer)
        
        # Cleanup
        instrumentor.uninstrument()
"""
        
        # Generate test file from template
        test_content = test_template.format(**config.template_vars)
        test_file_path = f"tests/compatibility_matrix/instrumentors/{config.instrumentor_type}/test_{config.provider_name.lower()}.py"
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
    
    def generate_documentation(self, config: InstrumentorConfig):
        """Generate RST documentation for the integration."""
        
        doc_template = """
{provider_name} Integration
{'=' * (len(config.provider_name) + 12)}

This guide shows how to integrate HoneyHive with {provider_name} using {instrumentor_type} instrumentors.

.. tabs::

   .. tab:: Installation
   
      Install the required packages:
      
      .. code-block:: bash
      
         pip install honeyhive[opentelemetry]
         pip install {instrumentor_package}
         pip install {provider_sdk}
   
   .. tab:: Basic Setup
   
      .. code-block:: python
      
         from honeyhive import HoneyHiveTracer
         from {import_path} import {instrumentor_class}
         
         # 1. Initialize instrumentor
         instrumentor = {instrumentor_class}()
         
         # 2. Initialize HoneyHive tracer
         tracer = HoneyHiveTracer.init(
             api_key="your-api-key",
             project="your-project"
         )
         
         # 3. Instrument with tracer provider
         instrumentor.instrument(tracer_provider=tracer.provider)
         
         # Your {provider_name} code will now be traced
         {basic_example}
   
   .. tab:: Advanced Usage
   
      .. code-block:: python
      
         # Advanced configuration and usage patterns
         {advanced_example}

Features Supported
------------------

✅ **Core HoneyHive Features**
- Span creation and attributes
- Event creation and enrichment  
- Session management
- Context propagation
- Decorator tracing

✅ **{provider_name}-Specific Features**
{provider_specific_features}

✅ **{instrumentor_type} Features**
{instrumentor_specific_features}

Troubleshooting
---------------

{troubleshooting_content}
"""
        
        # Generate documentation from template
        doc_content = doc_template.format(**config.template_vars)
        doc_file_path = f"docs/how-to/integrations/{config.provider_name.lower()}.rst"
        
        with open(doc_file_path, 'w') as f:
            f.write(doc_content)
    
    def generate_examples(self, config: InstrumentorConfig):
        """Generate example code for the integration."""
        
        example_template = """
\"\"\"
{provider_name} Integration Example

This example demonstrates how to use HoneyHive with {provider_name} 
using {instrumentor_type} instrumentors.
\"\"\"

import os
from honeyhive import HoneyHiveTracer, trace
from {import_path} import {instrumentor_class}

def main():
    \"\"\"Main example function.\"\"\"
    
    # 1. Initialize {instrumentor_type} instrumentor
    instrumentor = {instrumentor_class}()
    
    # 2. Initialize HoneyHive tracer
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        project="integration-examples",
        source="{provider_name.lower()}_example"
    )
    
    # 3. Instrument with tracer provider (CORRECT BYOI PATTERN)
    instrumentor.instrument(tracer_provider=tracer.provider)
    
    # Example usage with tracing
    {example_usage}
    
    # Cleanup
    instrumentor.uninstrument()

if __name__ == "__main__":
    main()
"""
        
        # Generate example from template
        example_content = example_template.format(**config.template_vars)
        example_file_path = f"examples/integrations/{config.provider_name.lower()}_example.py"
        
        with open(example_file_path, 'w') as f:
            f.write(example_content)
```

#### AI Framework Onboarding Process
```python
class AIFrameworkOnboardingFramework:
    """Framework for onboarding new AI framework integrations."""
    
    def onboard_ai_framework(self, config: AIFrameworkConfig):
        """Complete onboarding process for new AI framework."""
        
        # 1. Generate test files
        self.generate_compatibility_tests(config)
        
        # 2. Generate documentation
        self.generate_documentation(config)
        
        # 3. Generate example code
        self.generate_examples(config)
        
        # 4. Update compatibility matrix
        self.update_compatibility_matrix(config)
        
        # 5. Run validation
        self.validate_integration(config)
    
    def generate_compatibility_tests(self, config: AIFrameworkConfig):
        """Generate comprehensive compatibility tests for AI framework."""
        
        test_template = """
class Test{framework_name}Integration(HoneyHiveCompatibilityTest):
    \"\"\"Test {framework_name} integration with HoneyHive tracing.\"\"\"
    
    @pytest.mark.skipif(not {framework_name.upper()}_AVAILABLE, reason="{framework_name} not available")
    def test_{framework_name.lower()}_integration(self):
        \"\"\"Test {framework_name} with HoneyHive tracing.\"\"\"
        
        # Initialize HoneyHive tracer
        tracer = HoneyHiveTracer.init(
            api_key=self.api_key,
            project=self.project,
            source="{framework_name.lower()}_integration"
        )
        
        # Test {framework_name} operations with tracing
        @trace(tracer=tracer, event_type="chain", event_name="{framework_name.lower()}_workflow")
        async def run_{framework_name.lower()}_workflow():
            \"\"\"Run {framework_name} workflow with tracing.\"\"\"
            
            {framework_test_code}
        
        # Execute test
        result = await run_{framework_name.lower()}_workflow()
        assert result is not None
        
        # Validate full feature set
        self.validate_full_feature_set(tracer, "{framework_name.lower()}")
        
        # Validate {framework_name}-specific features
        self.validate_{framework_name.lower()}_features(tracer, result)
"""
        
        # Generate test file from template
        test_content = test_template.format(**config.template_vars)
        test_file_path = f"tests/compatibility_matrix/integrations/ai_frameworks/test_{config.framework_name.lower()}.py"
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
```

#### Onboarding Configuration
```python
@dataclass
class InstrumentorConfig:
    """Configuration for instrumentor onboarding."""
    provider_name: str  # e.g., "OpenAI"
    instrumentor_type: str  # e.g., "openinference" or "traceloop"
    instrumentor_class: str  # e.g., "OpenAIInstrumentor"
    import_path: str  # e.g., "openinference.instrumentation.openai"
    instrumentor_package: str  # e.g., "openinference-instrumentation-openai"
    provider_sdk: str  # e.g., "openai>=1.0.0"
    basic_example: str  # Basic usage code
    advanced_example: str  # Advanced usage code
    provider_specific_features: List[str]  # Provider-specific features
    instrumentor_specific_features: List[str]  # Instrumentor-specific features
    troubleshooting_content: str  # Troubleshooting guide
    
    @property
    def template_vars(self) -> Dict[str, Any]:
        """Get template variables for code generation."""
        return {
            'provider_name': self.provider_name,
            'instrumentor_type': self.instrumentor_type,
            'instrumentor_class': self.instrumentor_class,
            'import_path': self.import_path,
            'instrumentor_package': self.instrumentor_package,
            'provider_sdk': self.provider_sdk,
            'basic_example': self.basic_example,
            'advanced_example': self.advanced_example,
            'provider_specific_features': '\n'.join(f'- {feature}' for feature in self.provider_specific_features),
            'instrumentor_specific_features': '\n'.join(f'- {feature}' for feature in self.instrumentor_specific_features),
            'troubleshooting_content': self.troubleshooting_content,
        }

@dataclass
class AIFrameworkConfig:
    """Configuration for AI framework onboarding."""
    framework_name: str  # e.g., "PydanticAI"
    framework_package: str  # e.g., "pydantic-ai>=0.0.1"
    import_path: str  # e.g., "pydantic_ai"
    framework_test_code: str  # Test code specific to framework
    basic_example: str  # Basic usage code
    advanced_example: str  # Advanced usage code
    framework_specific_features: List[str]  # Framework-specific features
    troubleshooting_content: str  # Troubleshooting guide
    
    @property
    def template_vars(self) -> Dict[str, Any]:
        """Get template variables for code generation."""
        return {
            'framework_name': self.framework_name,
            'framework_package': self.framework_package,
            'import_path': self.import_path,
            'framework_test_code': self.framework_test_code,
            'basic_example': self.basic_example,
            'advanced_example': self.advanced_example,
            'framework_specific_features': '\n'.join(f'- {feature}' for feature in self.framework_specific_features),
            'troubleshooting_content': self.troubleshooting_content,
        }
```

### 5. Test Directory Structure

```
tests/compatibility_matrix/
├── core/                           # Core feature tests (no instrumentors)
│   ├── test_tracer_initialization.py
│   ├── test_span_operations.py
│   ├── test_event_operations.py
│   ├── test_context_baggage.py
│   ├── test_session_management.py
│   ├── test_decorators.py
│   └── test_performance_reliability.py
│
├── instrumentors/                  # Third-party instrumentor tests
│   ├── openinference/
│   │   ├── test_openai.py
│   │   ├── test_anthropic.py
│   │   ├── test_bedrock.py
│   │   └── test_google_ai.py
│   │
│   ├── traceloop/
│   │   ├── test_openai.py
│   │   ├── test_anthropic.py
│   │   ├── test_bedrock.py
│   │   └── test_google_ai.py
│   │
│   └── custom/
│       └── test_custom_instrumentor.py
│
├── integrations/                   # Non-instrumentor integrations
│   ├── ai_frameworks/              # AI Agent Frameworks
│   │   ├── test_aws_strands.py
│   │   ├── test_pydantic_ai.py
│   │   └── test_semantic_kernel.py
│   │
│   ├── web_frameworks/
│   │   ├── test_fastapi.py
│   │   ├── test_django.py
│   │   └── test_flask.py
│   │
│   ├── manual/
│   │   ├── test_decorator_only.py
│   │   ├── test_manual_spans.py
│   │   └── test_session_only.py
│   │
│   └── async/
│       ├── test_asyncio.py
│       └── test_concurrent.py
│
├── scenarios/                      # End-to-end scenarios
│   ├── test_multi_provider.py     # Multiple LLM providers
│   ├── test_multi_instance.py     # Multiple tracer instances
│   ├── test_distributed.py        # Distributed tracing
│   ├── test_evaluation.py         # Evaluation workflows
│   └── test_agent_workflows.py    # Multi-step agent scenarios
│
├── infrastructure/                 # Test infrastructure
│   ├── base_test.py               # Base test class
│   ├── feature_validator.py       # Feature validation framework
│   ├── instrumentor_factory.py    # Instrumentor creation utilities
│   ├── framework_factory.py       # AI framework utilities
│   └── compatibility_runner.py    # Test execution engine
│
└── reports/                       # Generated reports
    ├── compatibility_matrix.md
    ├── feature_coverage.json
    └── performance_benchmarks.json
```

## Implementation Details

### Phase 1: Infrastructure Setup
1. Create base test infrastructure (`HoneyHiveCompatibilityTest`, `FeatureValidator`)
2. Implement unified test directory structure
3. Set up test execution framework (`CompatibilityTestRunner`)
4. Create requirements and environment configuration

### Phase 2: Core Feature Tests
1. Implement core feature validation tests (no instrumentors)
2. Test span operations, event operations, context/baggage
3. Test session management, decorators, performance/reliability
4. Validate async support and error handling

### Phase 3: Instrumentor Integration Tests
1. Migrate existing OpenInference tests to new structure
2. Migrate existing Traceloop tests to new structure
3. Implement correct BYOI patterns across all instrumentor tests
4. Add comprehensive feature validation to each instrumentor test

### Phase 4: AI Framework Integration Tests
1. Implement AWS Strands integration tests
2. Implement Pydantic AI integration tests
3. Implement Microsoft Semantic Kernel integration tests
4. Test framework-specific features (structured outputs, async workflows, etc.)

### Phase 5: Scenario and Reporting
1. Implement end-to-end scenario tests
2. Create automated compatibility report generation
3. Add performance benchmarking across integrations
4. Implement distributed tracing validation

### Phase 6: Cleanup and Documentation
1. Remove all references to deprecated `instrumentors` parameter
2. Update documentation with correct BYOI patterns
3. Update examples to use new patterns
4. Create migration guide for users

## Configuration Changes

### New Environment Variables
```bash
# Compatibility Matrix Configuration
HH_COMPATIBILITY_MATRIX_PROJECT=compatibility-matrix-test
HH_COMPATIBILITY_MATRIX_SOURCE=compatibility_test

# AI Framework Flags
HH_TEST_AWS_STRANDS=true
HH_TEST_PYDANTIC_AI=true
HH_TEST_SEMANTIC_KERNEL=true

# Performance Configuration
HH_COMPATIBILITY_TEST_TIMEOUT=30
HH_COMPATIBILITY_PARALLEL_WORKERS=4
```

### Dependencies
```python
# Core requirements
honeyhive[opentelemetry]

# OpenInference Instrumentation
openinference-instrumentation-openai
openinference-instrumentation-anthropic
openinference-instrumentation-bedrock
openinference-instrumentation-google-generativeai

# Traceloop Instrumentation
opentelemetry-instrumentation-openai
opentelemetry-instrumentation-anthropic
opentelemetry-instrumentation-bedrock

# AI Agent Frameworks
pydantic-ai>=0.0.1
semantic-kernel>=1.0.0
# strands-ai>=0.1.0  # When available

# LLM Provider SDKs
openai>=1.0.0
anthropic>=0.20.0
boto3>=1.28.0
google-generativeai>=0.3.0

# Web Frameworks
fastapi>=0.100.0
django>=4.0.0
flask>=2.3.0

# Testing Infrastructure
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-timeout>=2.1.0
pytest-xdist>=3.0.0
```

## Testing Strategy

### Test Execution
```bash
# Run all compatibility tests
tox -e compatibility-matrix

# Run specific category
tox -e compatibility-matrix -- --category=ai_frameworks

# Run with coverage
tox -e compatibility-matrix-coverage

# Generate reports
tox -e compatibility-matrix-reports
```

### Continuous Integration
- Run compatibility matrix on all PRs
- Generate compatibility reports on main branch
- Performance regression detection
- Automated dependency updates with compatibility validation

## Migration Strategy

### Backwards Compatibility
- All changes to test infrastructure only
- No changes to HoneyHive SDK API
- Existing integration patterns continue working
- New patterns available alongside old ones

### Rollout Plan
1. Create new compatibility matrix structure
2. Migrate existing tests to new structure
3. Add AI framework integration tests
4. Remove deprecated parameter references
5. Update documentation and examples
6. Full rollout after validation

## Monitoring & Validation

### Success Metrics
- All HoneyHive features validated across all integration types
- AI agent frameworks fully supported with comprehensive tests
- Zero references to deprecated `instrumentors` parameter
- Consistent BYOI patterns used throughout
- Comprehensive test coverage (>90% for compatibility matrix)

### Quality Gates
- All tests pass across Python 3.11, 3.12, 3.13
- No test flakiness or race conditions
- Memory usage stays under 1GB during test execution
- Test suite completes in <10 minutes for full run
- Comprehensive error handling and edge case coverage
