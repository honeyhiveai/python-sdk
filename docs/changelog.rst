Changelog
=========

.. note::
   **Release History and Updates**
   
   This changelog documents all notable changes to the HoneyHive Python SDK. For the complete, up-to-date changelog, see the `CHANGELOG.md file <https://github.com/honeyhiveai/python-sdk/blob/main/CHANGELOG.md>`_ in the repository.

.. important::
   **Format**: This project follows `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_ format and adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Latest Release Notes
--------------------

**For the complete and always up-to-date changelog, see:** `CHANGELOG.md <https://github.com/honeyhiveai/python-sdk/blob/main/CHANGELOG.md>`_

Current Version Highlights
~~~~~~~~~~~~~~~~~~~~~~~~~~

**🐛 FIXED: Metrics Table Printing Empty Values (Unreleased)**

* **Root Cause**: SDK expected metrics as dynamic top-level keys but backend returns them in a ``details`` array format per OpenAPI spec
* **New Typed Models**: Added ``MetricDetail``, ``DatapointResult``, ``DatapointMetric``, ``MetricDatapoints`` Pydantic models with proper type hints
* **Updated AggregatedMetrics**: Now uses ``details: List[MetricDetail]`` field to match backend response format
* **Updated print_table()**: Iterates over ``details`` array and extracts ``aggregate`` values from ``MetricDetail`` objects
* **Backward Compatible**: ``get_metric()``, ``list_metrics()``, ``get_all_metrics()`` support both new ``details`` array format and legacy ``model_extra`` format
* **Test Coverage**: Added 19 unit tests for typed models and integration test against real API
* **Files**: ``src/honeyhive/experiments/models.py``, ``src/honeyhive/experiments/results.py``

**🐛 FIXED: enrich_session() Metadata Requirement (Unreleased)**

* **Flexible Enrichment**: ``enrich_session()`` now works correctly even when no parameters (metadata, inputs, outputs, etc.) are explicitly provided
* **Bug Fix**: Previously, calling ``enrich_session()`` without parameters would silently fail due to empty ``update_params`` check
* **Improved Behavior**: Session enrichment now proceeds when a valid session_id is available, regardless of whether enrichment data is provided
* **Files**: ``src/honeyhive/tracer/core/context.py``

**🐛 FIXED: Session ID Initialization (Dec 2025)**

* **Backend Sync**: Sessions are now always initialized in backend, even when session_id is explicitly provided
* **Bug Prevention**: Prevents backend bug where inputs/outputs would be auto-populated from the first event if session didn't exist
* **UUID Validation**: Added automatic UUID format validation with fallback to new UUID if invalid
* **Session Preservation**: Properly preserves explicitly provided session IDs through the session creation process

**✨ NEW: Enhanced API Schemas & Filtering (Dec 2, 2025)**

* **Metric Schema Updates**: Updated to match backend with new enum values (PYTHON/LLM/HUMAN/COMPOSITE), added sampling_percentage, scale, categories, filters, timestamps
* **Datapoints Filtering**: Added dataset_id and dataset_name parameters, removed limit parameter (not in API spec), auto-detects ID vs name for legacy dataset parameter
* **EventFilter Convenience**: list_events() now accepts single EventFilter or List[EventFilter] with automatic conversion
* **UUIDType Display**: Added __str__ and __repr__ methods for proper string representation in logs
* **Metric Deletion**: Now raises AuthenticationError - users must use webapp to delete metrics
* **Test Fixes**: Fixed all unit test failures after model regeneration (enum name changes, UUID validation, AsyncMock issues)
* **Integration Test Fixes**: Updated backend_verification.py to use event_filters parameter, removed limit from list_datapoints calls, fixed invalid UUID strings
* **Files Modified**: 17 files (+492/-503 lines) with comprehensive test coverage

**🛡️ NEW: Configurable Span Limits & Core Attribute Preservation (Nov 18, 2025)**

* **Lazy-Activated Preservation**: Automatically preserves critical attributes (session_id, event_type, event_name, source) to prevent data loss when spans exceed attribute limits
* **Performance Optimized**: Only triggers for large spans (95%+ of limit), <0.001ms overhead for normal spans, ~0.5ms for large spans
* **Configurable Limits**: New span limit controls - max_attributes (1024, up from OTel's 128), max_events (1024), max_links (128), max_span_size (10MB)
* **Zero Configuration**: Works out of the box with sane defaults, fully configurable via TracerConfig or environment variables
* **Data Safety**: Prevents span rejection by backend when critical attributes are evicted by OpenTelemetry's FIFO policy

**🚀 INFRA: praxis OS Migration & Bug Fixes (Nov 14, 2025)**

* **✨ NEW: Pretty Table Output for Evaluations**: Added beautiful terminal table display for evaluate() results with color, emojis, and formatted metrics
* **AI Development Framework**: Migrated from Agent OS to praxis OS with MCP (Model Context Protocol) integration
* **Enhanced Tooling**: Added multi-repo code intelligence, advanced RAG search, and phase-gated workflows
* **Bug Fix**: Completed praxis OS pre-commit migration - fixed all hooks to use new .praxis-os/ paths (10 files, 43 references updated)
* **Bug Fix**: Fixed enrich_session inputs parameter causing 400 errors - now maps unsupported fields to metadata
* **Bug Fix**: Fixed OpenInference event type detection - ensures correct classification of instrumented spans (CHAIN, LLM, TOOL, etc.)
* **Bug Fix**: Enhanced error logging for 400 errors in experiment runs for better debugging
* **Bug Fix**: Corrected user_properties and metrics handling in enrich_span/enrich_session methods
* **Testing**: Added Google ADK instrumentation exercise script with rate limiting, callbacks, and comprehensive test scenarios
* **Breaking Change (Dev Only)**: AI development workflows now require praxis OS installation

**✨ NEW: DatasetsAPI Filtering - Find Datasets Efficiently (Nov 10, 2025)**

* **Server-Side Filtering**: Find datasets by name, type, or ID without fetching all datasets
* **Performance**: Much faster for large projects with 100+ datasets
* **New Parameters**: ``name``, ``dataset_type``, ``dataset_id``, ``include_datapoints``
* **Backward Compatible**: All parameters optional, existing code works unchanged
* **Customer Request**: Addresses scalability concerns as projects grow

**📚 IMPROVED: Strands Integration - Best Practices Pattern (Nov 6, 2025)**

* **Instance Method Pattern**: All examples now use ``tracer.enrich_span()`` instead of global ``enrich_span()``
* **Multi-Instance Safety**: Explicit tracer references work reliably in all environments
* **Future-Proof**: Avoids global function that will be deprecated in v2.0
* **Best Practices**: Documentation showcases recommended v1.0+ patterns
* **Explicit Context**: All ``@trace`` decorators include explicit ``tracer=tracer`` parameter

**🔧 NEW: Manual PyPI Publishing for Release Candidates (Nov 6, 2025)**

* **Manual Trigger**: Added workflow_dispatch to PyPI publishing workflow
* **RC Testing**: Can now publish release candidates (e.g., 1.0.0-rc3) from any branch
* **Pre-Merge Testing**: Enables user testing of RCs before merging to main
* **Automated**: Still performs all validation, integrity checks, and creates GitHub releases
* **Fixed**: Version extraction now uses sed to avoid Python import errors

**📚 UPDATED: AWS Strands Documentation with Current Model IDs (Nov 6, 2025)**

* **Version Bump**: Updated to 1.0.0-rc3 to reflect stable API
* **Model Access**: Clarified that AWS Bedrock models are now automatically available (no manual request)
* **Current Models**: Replaced deprecated Claude 3 models with Claude 4.5 series (Haiku 4.5, Sonnet 4.5)
* **EULA Info**: Added documentation about Anthropic EULA acceptance on first invocation
* **Verification**: All updates verified against official AWS Bedrock documentation

**✨ NEW: Automatic Span Capture for Evaluation Functions (Nov 3, 2025)**

* **Auto-Decoration**: User functions in `evaluate()` are now automatically wrapped with `@trace` decorator
* **Zero-Config Observability**: Automatic span capture with inputs/outputs without manual decorator application
* **Event Type**: Functions traced as "chain" type events for proper categorization
* **Transparent**: Works seamlessly with both functions that accept `tracer` parameter and those that don't

**✨ NEW: v1.0 Evaluation Enhancements (Oct 31, 2025)**

* **Smart Session Naming**: Experiments now use experiment name as default session name
* **Tracer Injection**: Auto-inject `tracer` parameter into evaluation functions for `enrich_session()` support
* **Ground Truth Tracking**: Automatic ground truth capture in session feedback
* **Auto-Input Tracking**: `@trace` decorator automatically captures function inputs (no manual enrichment needed)
* **Session Linking**: Propagate `run_id` through OpenTelemetry baggage for correct span association
* **Backward Compatible**: Functions without `tracer` parameter continue to work
* **New Tutorial**: "Run Your First Experiment" with evaluators and result comparison
* **Test Coverage**: 14 new tests with end-to-end backend verification

**🐛 CRITICAL FIX: Config Priority Bug (Oct 30, 2025)**

* **Issue**: `SessionConfig` and `EvaluationConfig` values not promoted to root, hidden in nested configs
* **Root Cause**: `create_unified_config()` didn't implement field promotion logic
* **Solution**: Added priority-aware promotion: individual params > SessionConfig > EvaluationConfig > TracerConfig
* **Impact**: 15 colliding fields now work correctly (`session_id`, `project`, `api_key`, `server_url`, etc.)
* **Tests**: Added 19 unit tests, 35 API integration tests, 10 backend verification tests

**🐛 CRITICAL FIX: Evaluation Metadata Propagation to Child Spans (Nov 3, 2025)**

* **Issue**: Evaluation context (`run_id`, `dataset_id`, `datapoint_id`) not propagating from `evaluate()` to child spans created by `@trace` decorators
* **Root Cause**: `HoneyHiveSpanProcessor` wasn't reading evaluation-specific baggage keys
* **Solution**: Added `_get_evaluation_attributes_from_baggage()` method to extract and apply evaluation metadata
* **Impact**: All spans created during `evaluate()` datapoint processing now inherit evaluation context
* **Tests**: Added 3 unit tests (all baggage scenarios) + 1 integration test for end-to-end validation

**🚨 BREAKING CHANGE: Ground Truth Field Name Migration (Nov 3, 2025)**

* **Breaking Change**: Migrated from `ground_truths` (plural) to `ground_truth` (singular) throughout SDK
* **Critical Bug Fixed**: Ground truth data was inaccessible to metrics, UI, and LLM evaluators
* **Root Cause**: SDK sent `feedback: {"ground_truths": {...}}` but backend expects `feedback: {"ground_truth": {...}}`
* **Impact Before Fix**: Metrics with `needs_ground_truth=true` failed, UI couldn't display ground truth, LLM evaluators couldn't access data
* **Migration Required**:
   - Dataset format: Change `"ground_truths"` → `"ground_truth"` in all datasets
   - Evaluator signatures: Change `ground_truths` parameter → `ground_truth` parameter
* **Before**: `dataset = [{"inputs": {...}, "ground_truths": {...}}]`
* **After**: `dataset = [{"inputs": {...}, "ground_truth": {...}}]`
* **Migration Time**: 15 minutes to 2 hours (simple find-replace operation)
* **Benefits**: Fixes broken metrics, enables UI display, enables LLM evaluator access, aligns with backend API and industry standards
* **Files Updated**: 15 files (1 source, 4 tests, 9 docs, 1 example) with 322 total line changes

**✨ NEW: Instance Method Pattern for Span/Session Enrichment (v1.0)**

* **Primary API**: `tracer.enrich_span()` and `tracer.enrich_session()` instance methods
* **Backward Compatible**: Free functions still work but deprecated
* **Multi-Instance Safe**: Proper tracer discovery via baggage propagation
* **Comprehensive Examples**: Updated all examples with new patterns

**🐛 CRITICAL FIX: Multi-Instance Context Isolation (Oct 29, 2025)**

* **Issue**: `project` and `source` leaked between tracer instances via global baggage
* **Root Cause**: `project`/`source` were in `SAFE_PROPAGATION_KEYS`, causing context pollution
* **Solution**: Removed from safe keys, prioritize tracer instance values in span processor
* **Result**: Each tracer instance maintains isolated context in multi-instance scenarios

**🐛 CRITICAL FIX: enrich_span() Immediate Execution (Oct 29, 2025)**

* **Issue**: `enrich_span(metadata={...})` returned lazy object instead of executing
* **Root Cause**: `UnifiedEnrichSpan.__call__()` deferred execution
* **Solution**: Modified to immediately execute `enrich_span_unified()`
* **Result**: Direct calls now work without context manager or boolean evaluation

**🐛 FIX: Decorator API Parameter Handling (Oct 29, 2025)**

* **Issue**: `@trace` decorator passed span object to `enrich_span_unified()`, polluting spans
* **Solution**: Removed erroneous span parameter from decorator enrichment calls
* **Result**: Spans no longer contain `honeyhive_metadata: "Span(...)"` pollution

**🐛 FIX: None Value Defense-in-Depth Filtering (Oct 29, 2025)**

* **Issue**: `None` values serialized to `"null"` strings in span attributes
* **Solution**: Two-layer filtering at decorator and attribute-setting levels
* **Result**: Spans no longer polluted with `"null"` string values

**🐛 CRITICAL FIX: evaluate() + enrich_span() Pattern**

* **Issue**: Span enrichment failed in evaluation workflows
* **Root Cause**: Baggage propagation was disabled to avoid session conflicts
* **Solution**: Selective baggage with safe keys (updated Oct 29: removed project/source)
* **Result**: Tracer discovery works while preventing multi-instance conflicts

**🧪 ADDED: Nested enrich_span() Backend Validation**

* **Comprehensive Test**: Validates nested function calls with enrich_span() in evaluate() workflows
* **Backend Verification**: Confirms enriched properties (metadata, metrics, config, feedback) persist
* **Pattern Coverage**: Parent function → nested helper function enrichment
* **Real Fixtures**: Uses real_project and integration_client for accurate validation
* **Zero False Positives**: CRITICAL assertions fail if enrichment not found in backend

**📚 ADDED: Strands Multi-Agent Integration Examples**

* **Swarm Collaboration**: Comprehensive example with researcher → coder → reviewer flow
* **Graph Workflow**: Parallel processing pattern with research → analysis/fact_check → report
* **Advanced Patterns**: Entry points, max handoffs/iterations, execution timeouts, node timeouts
* **Tracing Support**: Expected spans, agent collaboration flow, and agent-level metrics documented

**📋 ADDED: Integration Examples Requirements File**

* **Comprehensive Dependencies**: Added requirements.txt with all packages for integration examples
* **Organized by Category**: Core, LLM providers, OpenInference instrumentors, Traceloop instrumentors, and agent frameworks
* **Installation Commands**: Per-integration pip install commands for easy setup
* **Environment Variables**: Documentation of required credentials for each provider

**📚 ADDED: New Example Files**

* **Evaluation Example**: Simple demonstration of the ``evaluate()`` function with dataset evaluation and span enrichment
* **Legacy SDK Example**: Reference example showing basic tracer initialization and OpenAI integration

**🔧 FIXED: Session Enrichment in evaluate() Function**

* **Always Enriches Sessions**: Fixed bug where sessions weren't enriched when no evaluators were provided
* **Output Persistence**: Ensures outputs are always saved to backend regardless of evaluator presence
* **Better Logging**: Upgraded log level from debug to info for session enrichment visibility

**🔧 IMPROVED: Tracer Internal Cleanup**

* **Code Simplification**: Removed redundant experiment baggage code path
* **No User Impact**: Experiment tracking continues to work exactly as before
* **Performance**: Simplified baggage discovery logic

**🔧 FIXED: enrich_session() Backwards Compatibility Restored**

* **Legacy Parameters**: Restored `session_id` as optional positional parameter and `user_properties` support
* **Automatic Conversion**: User properties automatically merged into metadata with `user_properties.` prefix
* **Comprehensive Documentation**: Added 685-line documentation guide with 15+ examples and 5 common patterns
* **API Reference**: Complete function signature documentation with backwards compatibility examples
* **Regression Tests**: Added tests for legacy positional arguments and user_properties handling

**🔧 FIXED: enrich_span() Dynamic Tracer Discovery**

* **Automatic Resolution**: Added tracer discovery when not explicitly provided via `tracer_instance`
* **Priority-Based**: Explicit parameter → baggage context → global default tracer
* **Multi-Instance Safe**: Ensures correct tracer in multi-tracer applications
* **Regression Tests**: Added tests for auto-discovery, explicit tracer priority, and graceful degradation

**🔧 FIXED: Integration Examples Bug Fixes**

* **Google ADK**: Fixed LoopAgent parameter name (sub_agent → agent), disabled parallel workflow test
* **Strands**: Removed redundant global TracerProvider setting
* **Documentation**: Enhanced README with expanded links to all integration guides organized by category

**🔧 FIXED: enrich_span() Backwards Compatibility Restored**

* **Original Interface Restored**: Fixed `enrich_span()` to support main branch's reserved namespaces (`metadata`, `metrics`, `feedback`, `inputs`, `outputs`, `config`, `error`, `event_id`)
* **New Patterns Added**: Simple dictionary (routes to metadata), arbitrary kwargs (routes to metadata), and context manager support
* **Circular Import Resolved**: Extracted `_set_span_attributes()` to new `span_utils.py` module
* **100% Test Coverage**: Added 48 unit tests + 3 integration tests with backend verification
* **Documentation Updated**: Comprehensive updates to tutorials, how-to guides, and API reference with new examples

**🧪 NEW: Span Capture and Test Case Generation**

* **Span Recording**: Capture OpenTelemetry spans during integration runs
* **Test Generation**: Convert captured spans to unit test cases
* **Provider Coverage**: Generate tests for AutoGen, Google ADK, Semantic Kernel
* **Environment Flag**: Enable via CAPTURE_SPANS=true
* **Automated Workflow**: Complete guide for test case generation

**📚 NEW: AutoGen Integration Example**

* **Two-Agent Conversations**: User proxy and assistant agent collaboration
* **Group Chat**: Multiple specialized agents (writer, critic, planner)
* **Sequential Chat**: State-based transitions between agents
* **Nested Chat**: Complex task decomposition with agent hierarchies
* **Code Execution**: Automatic Docker-based code execution
* **Tool Registration**: Function calling with custom tools

**📚 NEW: DSPy Integration Example**

* **Signatures**: Declarative task definitions with input/output specifications
* **Chain of Thought**: CoT reasoning with assertions and validation
* **ReAct Pattern**: Agent-based reasoning with tool use
* **Optimization**: BootstrapFewShot for program optimization
* **Multi-Hop Reasoning**: Retrieve-then-read patterns for complex queries

**📚 NEW: AWS Bedrock Direct Integration Example**

* **Multi-Model Support**: Amazon Nova, Titan Text, and Anthropic Claude models
* **Converse API**: Unified interface for all Bedrock models
* **Streaming**: ConverseStream API for real-time responses
* **Document Understanding**: PDF, TXT, and DOC format support
* **Flexible Auth**: Multiple authentication methods (keys, session tokens, IAM roles)

**📚 NEW: Pydantic AI Integration Example**

* **Type-Safe Agents**: Complete Pydantic AI integration with structured outputs
* **Agent Tools**: Demonstrates @agent.tool decorator for function calling
* **Dynamic Prompts**: System prompt generation with @agent.system_prompt
* **Dependency Injection**: RunContext for passing dependencies to agents
* **Streaming Support**: Async iteration for streaming responses

**📚 NEW: LangGraph Integration Example**

* **State Graph Workflows**: Complete LangGraph integration with sequential node execution
* **Conditional Routing**: Demonstrates dynamic routing based on graph state
* **Multi-Step Agents**: Agent graphs with state management across nodes
* **Node Tracing**: Node-level tracing with @trace decorator integration
* **Automatic Instrumentation**: LangChain call tracing via OpenInference

**🔍 NEW: Raw Span Data Dumping for Debugging**

* **Comprehensive Span Extraction**: New `_dump_raw_span_data()` method captures all OpenTelemetry span properties
* **Full Context Capture**: Includes trace_id, span_id, parent spans, status, attributes, events, links
* **Resource Information**: Captures resource attributes and instrumentation info for complete observability
* **JSON Formatting**: Outputs pretty-printed JSON for easy debugging and troubleshooting

**🔧 CHANGED: Enhanced evaluate() Environment Variable Support**

* **Optional API Key**: api_key parameter now optional, reads from environment variables
* **Server URL Support**: Added server_url parameter with env var support
* **Dual Prefix Support**: Accepts both HONEYHIVE_* and HH_* environment variable prefixes
* **Better UX**: More flexible configuration without hardcoding credentials

**🔄 CHANGED: Updated Google ADK Integration with Async Support**

* **Modern API**: Updated to newer Google ADK API with LlmAgent, Runner, and InMemorySessionService
* **Async/Await**: Added full async support to all test functions for better performance
* **Simplified Auth**: Migrated from GOOGLE_ADK_API_KEY to standard GOOGLE_API_KEY environment variable
* **Session Management**: Improved session handling with explicit session service

**🔄 CHANGED: Refactored Strands Integration Example**

* **TracerProvider Pattern**: Updated AWS Strands integration to use recommended tracing pattern
* **6 Focused Test Cases**: Replaced complex workflow with targeted tests (basic invocation, tools, streaming, etc.)
* **AWS Bedrock Integration**: Switched from OpenAI to AWS Bedrock model implementation
* **Comprehensive Documentation**: Added detailed tracing expectations and GenAI semantic conventions

**🔧 NEW: MCP Server Upgrade (v0.1.0rc3)**

* **Agent OS Enhanced Architecture**: Upgraded from prototype to modular product architecture (+5,823 lines)
* **Workflow Engine**: Phase gating with evidence validation for controlled AI development
* **File Watcher**: Automatic incremental RAG index updates on content changes
* **Framework Generator**: Create new AI-assisted workflows programmatically
* **FastMCP Integration**: Modern server factory with automatic tool registration

**📦 Version Refactoring: Single Source of Truth (v0.1.0rc3)**

* **Consolidated Version Management**: Reduced from 5 hardcoded locations to 1
* **Dynamic Imports**: Late binding pattern following Agent OS standards
* **80% Less Maintenance**: Version updates now require editing only 1 file
* **MyPy Compliance**: Fixed circular import errors with proper import strategy

**📚 NEW: Restructured Evaluation Documentation**

* **Modular How-To Guides**: Created 9 focused problem-oriented guides following Divio Documentation System
* **Simplified Tutorial**: Redesigned 04-evaluation-basics.rst as a true 15-minute introductory guide
* **Question-Based Format**: All sections use questions as titles for better scannability (e.g., "How do I run experiments?")
* **Clear Navigation**: Updated index with toctree and quick links to common use cases
* **API Focus**: All guides prioritize ``evaluate()`` function over decorator-based approach

**🤖 NEW: Agent OS MCP/RAG Server (Dogfooding)**

* **Model Context Protocol Integration**: Complete MCP server implementation with 5 tools for AI-assisted development
* **90% Context Reduction**: RAG engine with LanceDB achieving semantic search over standards (50KB → 5KB)
* **Phase-Gated Workflows**: Workflow engine enforcing controlled AI development with checkpoint validation
* **HoneyHive Tracing**: Complete instrumentation with @trace decorators on all tools for observability dogfooding
* **Import Verification Standard**: New "2-Minute Rule" preventing import path hallucination in AI-generated code
* **Quality Excellence**: 28 unit tests with 10.0/10 Pylint score, full type annotations, and independent dependency management

**Development Tools**

- Improved pre-commit checks for Agent OS spec proposals

**v0.1.0+ (Development) - Major Architectural Refactor**

**🏗️ NEW: Modular Tracer Architecture**

* **Mixin-Based Design**: Complete rewrite with 6 core modules for better maintainability
* **Enhanced Multi-Instance**: True isolation between tracer instances with independent configurations
* **OpenTelemetry Compliance**: Full OTel standard adherence with enhanced provider strategies
* **35 New Files**: Comprehensive modular architecture across core, infra, instrumentation, integration, lifecycle, processing, and utils modules

**🔧 NEW: Hybrid Configuration System**

* **Type-Safe Config Objects**: New Pydantic models (TracerConfig, SessionConfig, APIClientConfig, etc.)
* **Three Initialization Patterns**: Traditional .init() (recommended), modern config objects, environment variables
* **100% Backwards Compatible**: All existing .init() usage continues to work unchanged
* **Dynamic Environment Mapping**: Flexible environment variable configuration with AliasChoices

**📚 NEW: Comprehensive Documentation**

* **Complete Migration Guide**: Zero-breaking-change upgrade paths with detailed examples
* **Architecture Reference**: Mixin composition patterns and multi-instance scenarios
* **Enhanced Tutorials**: Configuration patterns and best practices
* **API Reference Expansion**: Full documentation for all new Pydantic models

**🔧 QUALITY: Perfect Test Suite**

* **2,904 Total Tests**: 2,735 unit + 169 integration tests with 100% pass rate
* **94.13% Coverage**: Significantly exceeds 80% requirement
* **10.0/10 Pylint Score**: Perfect code quality with 0 MyPy errors
* **Enhanced Performance Testing**: Dynamic thresholds for parallel vs isolation execution

**v0.1.0rc2 (Development) - Full Backwards Compatibility and Environment Variable Fixes**

**🔄 NEW: Complete Backwards Compatibility Implementation**

* **All 16 Original Parameters**: Complete parameter compatibility with main branch HoneyHiveTracer
* **Context Association Properties**: Multi-tracer coordination support for complex deployments
* **Session ID Validation**: UUID validation with proper error handling for session linking
* **Server URL Override**: Custom deployment support with runtime URL configuration
* **Verbose Debug Control**: Granular output control throughout tracer initialization
* **Evaluation Workflows**: Full evaluation baggage support (run_id, dataset_id, datapoint_id)
* **Batch Processing Control**: disable_batch parameter controls SimpleSpanProcessor vs BatchSpanProcessor
* **Git Metadata Collection**: Automatic git information collection for session metadata
* **Context Propagation**: Link/unlink/inject methods for carrier-based context propagation
* **Session Enhancement**: Inputs and metadata support for enriched session creation

**🔧 FIXED: Runtime Environment Variable Support**

* **HH_API_URL Override**: Environment variables now properly picked up when set at runtime
* **Boolean Variables**: Fixed HH_VERIFY_SSL and HH_FOLLOW_REDIRECTS precedence logic
* **Fresh Config Loading**: API client and tracer use fresh config instances
* **API Key Precedence**: Fixed HH_API_KEY environment variable precedence over constructor parameters
* **HTTP Tracing Configuration**: Fixed disable_http_tracing environment variable handling for multi-instance support
* **Comprehensive Testing**: Added 17 backwards compatibility integration tests covering runtime behavior

**⚡ BREAKING: Structured Logging Infrastructure**

* **Production Ready**: Replaced all print statements with structured HoneyHive logging
* **Better Observability**: Structured logging with honeyhive_data for context
* **Proper Log Levels**: Debug, info, warning, and error levels for appropriate output
* **Maintained Compatibility**: Docstring examples still use print statements per Python conventions

**🚀 NEW: Pre-commit Test Suite Execution**

* **Zero Failing Tests Policy**: Automated test execution in pre-commit hooks
* **Unit Test Enforcement**: All unit tests must pass before commit
* **Basic Integration Tests**: Fast subset of integration tests with credential validation
* **Quality Gate Enhancement**: Comprehensive pre-commit validation pipeline

**🔧 FIXES: GitHub Actions Integration**

* **Workflow Environment Variables**: Fixed missing ``HH_PROJECT`` in GitHub Actions workflows
* **Tox Environment Configuration**: Fixed missing ``HH_PROJECT`` in local tox test environments
* **Integration Test Reliability**: Resolved authentication failures in both CI/CD and local testing
* **Lambda Test Compatibility**: Added proper environment configuration for AWS Lambda tests

**v0.1.0rc1 (2025-09-11) - Release Candidate with Performance Improvements**

**🚀 NEW: Performance Optimization Framework**

* **OTLP Performance Tuning**: Configurable batch sizes and flush intervals for production optimization
* **Environment Variables**: ``HH_BATCH_SIZE`` and ``HH_FLUSH_INTERVAL`` for fine-tuned performance control
* **Enhanced Span Processing**: Improved batching performance with configurable parameters
* **API Client Improvements**: Better error handling and configuration management
* **Documentation Navigation**: Comprehensive validation framework with 0 broken links across 69 URLs
* **Integration Testing**: Consolidated two-tier testing strategy with real API validation
* **RST Hierarchy**: Fixed documentation structure across all provider integration guides

**v0.1.0 (Development) - Major Architectural Refactor & Bug Fixes**

**🎯 NEW: Compatibility Matrix Framework (2025-09-05)**

* **Complete Testing Framework**: 13 provider compatibility tests with 100% success rate
* **Python Version Support**: Full validation across Python 3.11, 3.12, and 3.13
* **Dynamic Generation**: Automated maintenance reducing manual work by 75%
* **Official Documentation**: Integrated compatibility matrix in Sphinx docs with optimal UX
* **Systematic Workarounds**: Professional handling of upstream instrumentor bugs
* **Streamlined Architecture**: 25% file count reduction with consolidated documentation

This release represents a comprehensive modernization of the HoneyHive Python SDK with significant architectural improvements and enhanced developer experience.

**🔄 Breaking Changes**

- **Modernized Architecture**: ``HoneyHiveTracer`` now supports multiple independent instances
  
  - ``HoneyHiveTracer.init()`` method maintained for backwards compatibility
  - Direct constructor usage also available: ``HoneyHiveTracer(api_key="key")``
  - Each initialization creates a new independent tracer instance

**✨ Major Additions**

- **Examples Directory Restructure**: Organized provider examples into dedicated integrations/ subdirectory with 39% size reduction, improved navigation, and focused approach eliminating external dependencies

- **CSS-Based Dual-Theme System**: Automatic light/dark theme detection for Mermaid sequence diagrams with targeted styling for optimal readability across all browsers

- **Documentation Quality Prevention System**: Comprehensive error prevention and validation framework
  
  - Zero Build Warnings: Documentation now builds cleanly without any Sphinx warnings  
  - Automated RST Validation: Pre-commit hooks validate structure and formatting
  - Type Safety Enforcement: All code examples use proper ``EventType`` enums
  - Code Example Testing: Automated validation ensures correct syntax and imports

- **Documentation Content Improvements**: Major cleanup and standardization
  
  - Divio Architecture Compliance: Complete reorganization following Divio documentation system
  - Decorator-First Approach: Updated examples to emphasize ``@trace`` decorators
  - Type-Safe Examples: Replaced string literals with ``EventType`` enums
  - Backward Compatibility Documentation: Comprehensive guide for tracer auto-discovery

- **Automatic Tracer Discovery**: Enhanced decorator functionality
  
  - ``@trace`` decorator now works without explicit tracer parameter
  - OpenTelemetry baggage-based tracer discovery mechanism
  - ``set_default_tracer()`` function for global tracer configuration
  - Maintains backward compatibility with existing code

- **Enhanced Decorator Support**: Improved tracing capabilities
  
  - ``@trace_class`` decorator for automatic class-level tracing
  - ``enrich_span()`` utility function for adding context to active spans
  - Unified decorator behavior for both sync and async functions
  - Better error handling and span lifecycle management

**🔧 Improvements**

- **Testing Infrastructure**: Comprehensive test coverage improvements
  
  - Unit tests for registry and tracer discovery mechanisms
  - Integration tests for backward compatibility scenarios  
  - Performance testing for multi-instance scenarios
  - Mocking strategies for reliable test isolation

- **Developer Experience**: Enhanced tooling and workflows
  
  - Pre-commit hooks for code quality and documentation validation
  - Strict changelog enforcement for high-frequency development environments
  - Feature synchronization verification
  - Enhanced error messages and debugging information

**🐛 Fixes**

- **API Endpoint Corrections**: Fixed incorrect health check endpoints
- **Documentation Warnings**: Resolved 23+ Sphinx build warnings
- **Import Issues**: Fixed pylint ungrouped-imports warnings
- **Cross-Reference Links**: Corrected broken internal documentation links

.. note::
   **Staying Updated**
   
   - **GitHub Releases**: Watch the `releases page <https://github.com/honeyhiveai/python-sdk/releases>`_ for notifications
   - **PyPI Updates**: Monitor `honeyhive on PyPI <https://pypi.org/project/honeyhive/>`_ for new versions
   - **Breaking Changes**: Major version bumps indicate breaking changes - review the changelog carefully before upgrading

Version Upgrade Guide
---------------------

**Upgrading to Latest Version**

.. code-block:: bash

   # Upgrade to latest version
   pip install --upgrade honeyhive
   
   # Or specify a specific version
   pip install honeyhive==X.Y.Z

**Breaking Changes Checklist**

When upgrading across major versions, review:

1. **API Changes**: Check for deprecated or removed methods
2. **Configuration Changes**: Verify environment variable names and formats
3. **Dependency Updates**: Update any instrumentor packages if needed
4. **Import Changes**: Update import statements if package structure changed
5. **Behavior Changes**: Test critical paths for any behavioral differences

**Migration Support**

If you need help migrating between versions:

- **Migration Guides**: Check the :doc:`how-to/index` section for version-specific migration guides
- **GitHub Discussions**: Ask questions in `GitHub Discussions <https://github.com/honeyhiveai/python-sdk/discussions>`_
- **Discord Community**: Get help in our `Discord server <https://discord.gg/honeyhive>`_
- **Support Email**: Contact support@honeyhive.ai for enterprise migration assistance

Contributing to the Changelog
-----------------------------

**For Contributors**

When submitting pull requests, update the "Unreleased" section in `CHANGELOG.md`:

.. code-block:: markdown

   ## [Unreleased]
   
   ### Added
   - New feature description
   
   ### Changed
   - Changed behavior description
   
   ### Deprecated
   - Deprecated feature notice
   
   ### Removed
   - Removed feature description
   
   ### Fixed
   - Bug fix description
   
   ### Security
   - Security improvement description

**Change Categories**

- **Added**: New features
- **Changed**: Changes in existing functionality  
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

**Writing Good Changelog Entries**

- **Be specific**: "Fixed trace span duration calculation" vs "Fixed bug"
- **Include impact**: "Breaking Change: Removed deprecated `trace_event()` method"
- **Add context**: "Improved performance by 40% for large trace batches"
- **Reference issues**: "Fixed #123: Memory leak in async tracing"

Release Process
---------------

**For Maintainers**

The release process follows these steps:

1. **Update Version**: Bump version in `pyproject.toml`
2. **Update Changelog**: Move "Unreleased" items to new version section
3. **Create Release**: Tag and create GitHub release
4. **Publish Package**: Automated publishing to PyPI
5. **Update Documentation**: Deploy updated docs with new version

**Release Schedule**

- **Major Releases**: Quarterly (breaking changes, major features)
- **Minor Releases**: Monthly (new features, improvements)
- **Patch Releases**: As needed (bug fixes, security updates)
- **Pre-releases**: Beta versions for testing major changes

**Version Numbering**

Following Semantic Versioning:

- **Major**: Breaking changes (1.0.0 → 2.0.0)
- **Minor**: New features, backwards compatible (1.0.0 → 1.1.0)  
- **Patch**: Bug fixes, backwards compatible (1.0.0 → 1.0.1)
- **Pre-release**: Beta versions (1.1.0-beta.1)
