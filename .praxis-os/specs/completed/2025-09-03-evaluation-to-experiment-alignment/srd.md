# Spec Requirements Document - Evaluation to Experiment Framework Alignment

**Date**: 2025-09-04  
**Last Updated**: 2025-10-02 (v2.0)  
**Status**: Specification Updated - Implementation Ready  
**Priority**: High  
**Branch**: complete-refactor  
**Version**: 2.0

> **Version 2.0 Update**: Specification updated based on comprehensive backend code analysis, tracer architecture review, and generated models validation. See `CHANGELOG.md` for detailed changes.

## Overview

Align the current HoneyHive Python SDK evaluation implementation with the official HoneyHive experiment framework to provide consistent terminology, comprehensive metadata linking, enhanced experiment management capabilities, and leverage backend aggregation services.

## Business Requirements

### Core Business Objectives
- **User Experience Consistency**: Align SDK terminology with official HoneyHive platform
- **Feature Completeness**: Provide full experiment workflow capabilities leveraging backend services
- **Developer Productivity**: Reduce friction in experiment setup and execution
- **Platform Integration**: Enable seamless integration with HoneyHive experiment features
- **Performance Efficiency**: Leverage backend aggregation instead of client-side computation

### Performance Requirements
- **Backward Compatibility**: 100% compatibility with existing evaluation code
- **Performance**: No degradation in existing evaluation performance
- **Scalability**: Support large datasets via backend aggregation
- **Reliability**: Graceful degradation and comprehensive error handling
- **Network Efficiency**: Minimize data transfer by using backend result endpoints

## User Stories

### As a Data Scientist
- I want to use "experiment" terminology that matches the HoneyHive platform
- So that there's no confusion between SDK and platform concepts
- And I can leverage the full power of HoneyHive's experiment features
- **And I can get aggregated results computed by backend** (v2.0 update)

### As an ML Engineer
- I want proper metadata linking between my code executions and experiment runs
- So that I can trace all events back to specific experiments and datapoints
- And I can debug issues in my experiment pipeline effectively
- **And metadata propagates automatically via tracer configuration** (v2.0 update)

### As a Research Engineer  
- I want to use external datasets with my own IDs
- So that I can integrate with my existing data infrastructure
- And maintain consistency across different experiment tools
- **And SDK automatically handles EXT- prefix transformation** (v2.0 update)

### As a Platform Engineer
- I want automated experiment runs triggered from GitHub
- So that I can detect performance regressions in CI/CD
- And maintain quality gates for model deployments
- **And I can compare runs using backend comparison endpoints** (v2.0 update)

## Functional Requirements

### 1. Terminology Alignment
- Replace "evaluation" terminology with "experiment" throughout SDK
- Maintain backward compatibility through aliases
- Update all class names, function names, and module names
- Align with official HoneyHive platform terminology
- **Use type aliases (ExperimentRun = EvaluationRun) instead of duplicating models** (v2.0)

### 2. Metadata Linking (v2.0 Updated)
- Include `run_id`, `dataset_id`, `datapoint_id`, `source` on all traced events
- **All four fields are REQUIRED in session metadata** (corrected from v1.0)
- Set `source="evaluation"` for all experiment-related events  
- **Leverage tracer's built-in experiment metadata functionality** (v2.0)
- **Use `is_evaluation=True` in TracerConfig to enable automatic metadata propagation** (v2.0)
- Support experiment context propagation across async operations
- Validate metadata presence and format

### 3. External Dataset Support (v2.0 Updated)
- Generate client-side dataset IDs with `EXT-` prefix
- **Transform EXT- datasets: store in `metadata.offline_dataset_id`, clear `dataset_id` field** (v2.0)
- Support custom dataset and datapoint IDs
- Handle dataset validation and error cases
- Maintain ID consistency across experiment runs
- **Prevent foreign key constraint errors for external datasets** (v2.0)

### 4. Main Evaluate Function (v2.0 Updated)
- Execute user-provided functions against datasets
- **Use tracer multi-instance architecture (one tracer per datapoint)** (v2.0)
- **ThreadPoolExecutor for I/O-bound concurrent execution** (v2.0)
- Collect and validate function outputs  
- Run evaluators against function outputs
- **Flush each tracer instance after datapoint execution** (v2.0)

### 5. Result Aggregation (v2.0 NEW - Critical)
- **Use backend GET /runs/:run_id/result endpoint for aggregation** (v2.0)
- **DO NOT compute aggregates client-side** (v2.0)
- Support multiple aggregation functions (average, sum, min, max)
- **Backend handles: pass/fail determination, composite metrics, metric aggregation** (v2.0)
- Retrieve results using `ExperimentResultResponse` model
- **Use fixed Metrics model with ConfigDict(extra="allow") for dynamic keys** (v2.0)

### 6. Run Comparison (v2.0 NEW)
- **Use backend GET /runs/:new_run_id/compare-with/:old_run_id endpoint** (v2.0)
- Compare multiple experiment runs using `ExperimentComparisonResponse` model
- **Backend computes deltas and percent changes** (v2.0)
- Detect performance improvements/regressions
- Identify common datapoints between runs

### 7. Enhanced Experiment Management Using Generated Models
- Create complete experiment run workflows using `EvaluationRun` model
- **Extend Status enum with missing values: running, failed, cancelled** (v2.0)
- Retrieve experiment results using `ExperimentResultResponse` model  
- Compare multiple experiment runs using `ExperimentComparisonResponse` model
- Set and validate performance thresholds
- **Key Technical Approach**: Leverage existing generated models (85% usable) with minor extensions

### 8. GitHub Integration
- Generate GitHub Actions workflow templates
- Support automated experiment triggering
- Detect performance regressions automatically
- Provide CLI tools for experiment management

## Non-Functional Requirements

### Performance
- Maintain existing multi-threading performance (5x improvement)
- **Leverage backend aggregation for better performance** (v2.0)
- Function execution overhead: <10ms per datapoint
- **Memory usage: Minimal (backend computes aggregates)** (v2.0)
- Thread safety: Support concurrent experiment execution with isolated tracers

### Reliability
- Graceful degradation when HoneyHive API unavailable
- Comprehensive error handling and logging
- Data validation and sanitization
- Recovery from partial failures
- **Automatic tracer flush in finally blocks** (v2.0)

### Maintainability
- 100% backward compatibility maintained
- Clear migration path for existing users
- Comprehensive documentation and examples
- Test coverage >90% for new functionality
- **Minimal custom code (use backend services)** (v2.0)

## Technical Constraints

### Compatibility Requirements
- Python 3.11+ support required
- OpenTelemetry compliance maintained
- No breaking changes to existing APIs
- Existing evaluation decorators must continue working
- **Generated Models**: Use models from `honeyhive.models.generated` (85% coverage)
- **Model Extensions**: Create extensions in experiments/models.py for remaining 15%

### Integration Requirements (v2.0 Updated)
- HoneyHive platform API compatibility
- OpenAPI specification alignment
- **Backend Result Endpoints**: Use GET /runs/:run_id/result for aggregation
- **Backend Comparison Endpoints**: Use comparison endpoints, not manual computation
- **Tracer Multi-Instance Architecture**: One tracer per datapoint for isolation
- **Type Aliases**: Simple aliases like `ExperimentRun = EvaluationRun` for terminology alignment
- GitHub Actions ecosystem integration

### Backend Integration Requirements (v2.0 NEW)
- **External Dataset Transformation**: EXT- prefix → metadata.offline_dataset_id
- **Result Aggregation**: Backend-side only, never client-side
- **Merge Behavior**: Backend merges metadata/results/configuration on updates
- **Field Name Mapping**: Backend returns "evaluation" field, map to "experiment_run"

## Success Criteria

### Functional Success
- [ ] All experiment terminology properly implemented using type aliases
- [ ] Metadata linking working on all traced events (run_id, dataset_id, datapoint_id, source)
- [ ] Client-side dataset support functional with `EXT-` prefix transformation
- [ ] Main evaluate function executes user functions with tracer multi-instance pattern
- [ ] **Result aggregation uses backend GET /runs/:run_id/result endpoint** (v2.0)
- [ ] **Run comparison uses backend comparison endpoints** (v2.0)
- [ ] Experiment run management complete using `EvaluationRun` model
- [ ] **Generated models integration**: 85% direct usage, 15% extended
- [ ] **Zero client-side aggregation**: All stats computed by backend
- [ ] **EXT- prefix handling**: Automatic transformation for external datasets
- [ ] GitHub integration working (nice-to-have)

### Quality Success
- [ ] 100% backward compatibility maintained
- [ ] All existing tests continue passing
- [ ] New functionality has >90% test coverage
- [ ] Performance benchmarks met (backend aggregation improves performance)
- [ ] Documentation complete and accurate
- [ ] **Tracer flush properly handled in finally blocks**
- [ ] **ThreadPoolExecutor pattern validated for concurrent execution**

### User Experience Success
- [ ] Smooth migration path for existing users
- [ ] Clear examples and tutorials available
- [ ] Intuitive API design maintained
- [ ] Comprehensive error messages provided
- [ ] **Results retrieved from backend (no manual computation)**
- [ ] **External datasets work transparently**

## Out of Scope

### Phase 1 Exclusions
- Advanced experiment comparison algorithms (backend provides basic comparison)
- Real-time experiment monitoring dashboards
- Custom evaluator marketplace integration
- Advanced statistical analysis features
- **Custom Data Models**: No new dataclasses - use generated models only
- **Client-Side Aggregation**: Backend handles all aggregation
- **Multiprocessing**: ThreadPoolExecutor sufficient for I/O-bound operations

### Future Considerations
- Machine learning model registry integration
- Advanced experiment scheduling
- Cross-platform experiment execution
- Enterprise authentication features
- **Model Enhancements**: Extensions to generated models (modify OpenAPI spec if needed)
- **Advanced Aggregation Functions**: Additional aggregate_function options

## Risks & Mitigations

### High Risk Items
- **Breaking Changes**: Potential for breaking existing integrations
  - **Mitigation**: Phased implementation with comprehensive backward compatibility
- **Performance Impact**: Metadata injection on all events
  - **Mitigation**: Performance testing and tracer optimization
  - **v2.0 Note**: Tracer handles metadata automatically, minimal overhead
- **Complexity**: Increased complexity of experiment management
  - **Mitigation**: User feedback and early access program
  - **v2.0 Note**: Backend handles aggregation, SDK simpler than v1.0 design
- **Function Execution**: Ensuring user functions execute safely
  - **Mitigation**: Sandboxed execution and comprehensive error handling
  - **v2.0 Note**: Tracer multi-instance ensures isolation

### Medium Risk Items
- **API Changes**: HoneyHive platform API modifications
  - **Mitigation**: Version compatibility checking and graceful degradation
- **User Adoption**: Users may be slow to adopt new terminology
  - **Mitigation**: Clear migration guide and backward compatibility
- **External Dataset Handling**: EXT- prefix transformation complexity
  - **Mitigation**: Backend handles transformation, SDK validates format
  - **v2.0 Note**: Backend code already implements EXT- logic

### Low Risk Items (v2.0)
- **Generated Model Issues**: Some fields might be missing
  - **Mitigation**: 85% coverage validated, extend remaining 15% as needed
- **Metrics Structure**: Dynamic keys in Metrics model
  - **Mitigation**: Use ConfigDict(extra="allow") for flexible field access

## Dependencies

### Internal Dependencies
- Tracer framework with experiment context support
- **Tracer multi-instance architecture** (v2.0)
- API client enhancements for result endpoints
- **Generated model integration**: Imports from `honeyhive.models.generated` (85% coverage)
- **Extended models**: Create experiments/models.py for remaining 15%
- Test framework updates for new functionality

### External Dependencies
- HoneyHive platform API compatibility
- **Backend result aggregation endpoints** (v2.0)
- **Backend comparison endpoints** (v2.0)
- GitHub Actions ecosystem stability
- OpenTelemetry specification alignment
- Official OpenAPI specification updates

### Backend Dependencies (v2.0 NEW)
- GET /runs/:run_id/result endpoint availability
- GET /runs/:new_run_id/compare-with/:old_run_id endpoint availability
- EXT- prefix handling in backend (already implemented)
- Metadata merge behavior in backend (already implemented)

## Timeline - Release Candidate Implementation

### Updated Implementation Schedule (v2.0)
**Target**: Complete implementation within 2 business days (revised from 1 day)

#### Day 1 - Core Implementation (9:00 AM - 5:00 PM)
- **Hours 0-2**: Module structure and extended models (Metrics, Status enum)
- **Hours 2-4**: Tracer integration with multi-instance pattern
- **Hours 4-6**: Main evaluate function with ThreadPoolExecutor
- **Hours 6-8**: External dataset EXT- prefix handling

#### Day 2 - Integration & Validation (9:00 AM - 5:00 PM)
- **Hours 0-2**: Result endpoint integration (get_run_result, compare_runs)
- **Hours 2-4**: Backward compatibility layer
- **Hours 4-6**: Comprehensive testing
- **Hours 6-8**: Documentation and examples

### Critical Milestones
- **Day 1, 12:00 PM**: Core evaluate function operational with tracer
- **Day 1, 5:00 PM**: External dataset handling complete
- **Day 2, 12:00 PM**: Result endpoints integrated
- **Day 2, 5:00 PM**: Release candidate ready

### Resource Requirements
- **Primary Developer**: 2 full days focused implementation
- **Testing Support**: Parallel testing during implementation
- **Documentation**: Real-time documentation updates
- **Backend Validation**: Access to backend codebase for reference

## Acceptance Criteria

### Technical Validation
- All existing evaluation code continues to work without changes
- New experiment functionality passes comprehensive test suite
- Performance benchmarks meet or exceed current performance
- Official HoneyHive data models integrated correctly
- **Backend result endpoints properly integrated** (v2.0)
- **Tracer multi-instance pattern validated** (v2.0)
- **EXT- prefix transformation working correctly** (v2.0)
- **No client-side aggregation code** (v2.0)

### User Validation
- Migration guide enables smooth transition for existing users
- New experiment features work as documented
- Error messages are clear and actionable
- Examples and tutorials are complete and accurate
- **Users can retrieve aggregated results from backend** (v2.0)
- **Users can compare runs using backend endpoints** (v2.0)
- **External datasets work transparently with EXT- prefix** (v2.0)

### Integration Validation (v2.0 NEW)
- Backend result endpoint returns correct ExperimentResultResponse structure
- Backend comparison endpoint returns correct comparison data
- Tracer propagates all required metadata (run_id, dataset_id, datapoint_id, source)
- External dataset IDs transformed correctly (EXT- → metadata.offline_dataset_id)
- Multiple concurrent tracers work without interference

---

## Document Change Log

### Version 2.0 - October 2, 2025
- Added backend result aggregation requirements
- Added EXT- prefix transformation requirements
- Updated metadata requirements (all four fields mandatory)
- Added tracer multi-instance pattern requirements
- Updated timeline to 2 days (more realistic)
- Added backend integration dependencies
- Updated success criteria with backend integration checks

### Version 1.0 - September 4, 2025
- Initial specification
- Basic requirements based on documentation

---

**Document Version**: 2.0  
**Last Updated**: 2025-10-02  
**Next Review**: After Phase 1 implementation  
**Specification Owner**: Development Team  
**Analysis Reference**: See CHANGELOG.md and analysis documents in this directory
