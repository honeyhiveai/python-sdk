=== FINAL CORRECTED ANALYSIS - INDIVIDUAL FILE APPROACH ===
Running Pylint and MyPy on each individual file...

Found 58 production files to analyze
Found 67 unit test files
Starting individual file analysis...


# FINAL CORRECTED Analysis - Individual File Results

| Production File | Test File | Has Test | Coverage % | Covered Lines | Total Lines | Missing Lines | Pylint Score | Pylint Violations | MyPy Errors |
|----------------|-----------|----------|------------|---------------|-------------|---------------|--------------|-------------------|-------------|
| `honeyhive/api/datapoints.py` | `test_api_datapoints.py` | ✅ | 🔴 50.0% | 42 | 84 | 42 | 10.0/10 | 0 | 0 |
| `honeyhive/api/base.py` | `test_api_base.py` | ✅ | 🔴 51.1% | 23 | 45 | 22 | 10.0/10 | 0 | 0 |
| `honeyhive/api/events.py` | `test_api_events.py` | ✅ | 🔴 55.7% | 83 | 149 | 66 | 10.0/10 | 0 | 0 |
| `honeyhive/api/datasets.py` | `test_api_datasets.py` | ✅ | 🔴 57.5% | 46 | 80 | 34 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/processing/otlp_profiles.py` | `test_tracer_processing_otlp_profiles.py` | ✅ | 🟡 61.7% | 92 | 149 | 57 | 10.0/10 | 0 | 0 |
| `honeyhive/api/metrics.py` | `test_api_metrics.py` | ✅ | 🟡 61.8% | 42 | 68 | 26 | 10.0/10 | 0 | 0 |
| `honeyhive/utils/retry.py` | `❌ MISSING` | ❌ | 🟡 62.5% | 35 | 56 | 21 | 10.0/10 | 0 | 0 |
| `honeyhive/api/tools.py` | `test_api_tools.py` | ✅ | 🟡 62.9% | 44 | 70 | 26 | 10.0/10 | 0 | 0 |
| `honeyhive/api/configurations.py` | `test_api_configurations.py` | ✅ | 🟡 63.8% | 51 | 80 | 29 | 10.0/10 | 0 | 0 |
| `honeyhive/api/projects.py` | `test_api_projects.py` | ✅ | 🟡 64.1% | 41 | 64 | 23 | 10.0/10 | 0 | 0 |
| `honeyhive/api/session.py` | `test_api_session.py` | ✅ | 🟡 70.0% | 56 | 80 | 24 | 10.0/10 | 0 | 0 |
| `honeyhive/utils/logger.py` | `test_utils_logger.py` | ✅ | 🟡 70.9% | 112 | 158 | 46 | 9.9/10 | 1 | 0 |
| `honeyhive/tracer/infra/resources.py` | `❌ MISSING` | ❌ | 🟡 76.5% | 39 | 51 | 12 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/infra/environment.py` | `❌ MISSING` | ❌ | 🟡 78.1% | 225 | 288 | 63 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/core/context.py` | `test_tracer_core_context.py` | ✅ | 🟡 78.7% | 133 | 169 | 36 | 9.9/10 | 2 | 0 |
| `honeyhive/evaluation/evaluators.py` | `test_evaluation_evaluators.py` | ✅ | 🟢 84.2% | 266 | 316 | 50 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/instrumentation/initialization.py` | `test_tracer_instrumentation_initialization.py` | ✅ | 🟢 85.2% | 230 | 270 | 40 | 10.0/10 | 1 | 0 |
| `honeyhive/tracer/integration/detection.py` | `test_tracer_integration_detection.py` | ✅ | 🟢 85.5% | 200 | 234 | 34 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/core/tracer.py` | `test_tracer_core_base_minimal.py` | ✅ | 🟢 85.7% | 6 | 7 | 1 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/core/operations.py` | `test_tracer_core_operations.py` | ✅ | 🟢 86.6% | 246 | 284 | 38 | 10.0/10 | 0 | 0 |
| `honeyhive/utils/connection_pool.py` | `test_utils_connection_pool.py` | ✅ | 🟢 86.9% | 370 | 426 | 56 | 10.0/10 | 0 | 0 |
| `honeyhive/utils/cache.py` | `test_utils_cache.py` | ✅ | 🟢 87.8% | 216 | 246 | 30 | 10.0/10 | 0 | 0 |
| `honeyhive/api/client.py` | `test_api_client.py` | ✅ | 🟢 87.9% | 175 | 199 | 24 | 10.0/10 | 0 | 0 |
| `honeyhive/config/utils.py` | `test_config_utils.py` | ✅ | 🟢 90.0% | 54 | 60 | 6 | 5.0/10 | 6 | 0 |
| `honeyhive/utils/error_handler.py` | `test_utils_error_handler.py` | ✅ | 🟢 90.8% | 128 | 141 | 13 | 10.0/10 | 0 | 0 |
| `honeyhive/cli/main.py` | `test_cli_main.py` | ✅ | 🟢 91.5% | 300 | 328 | 28 | 10.0/10 | 1 | 0 |
| `honeyhive/tracer/processing/span_processor.py` | `test_tracer_processing_span_processor.py` | ✅ | 🟢 92.5% | 258 | 279 | 21 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/utils/general.py` | `test_tracer_utils_general.py` | ✅ | 🟢 92.7% | 127 | 137 | 10 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/integration/error_handling.py` | `test_tracer_integration_error_handling.py` | ✅ | 🟢 93.2% | 178 | 191 | 13 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/processing/otlp_session.py` | `test_tracer_processing_otlp_session.py` | ✅ | 🟢 94.0% | 158 | 168 | 10 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/instrumentation/decorators.py` | `test_tracer_instrumentation_decorators.py` | ✅ | 🟢 94.3% | 233 | 247 | 14 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/core/config_interface.py` | `test_tracer_core_config_interface.py` | ✅ | 🟢 94.4% | 201 | 213 | 12 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/core/base.py` | `test_tracer_core_base_minimal.py` | ✅ | 🟢 94.9% | 260 | 274 | 14 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/integration/http.py` | `test_tracer_integration_http.py` | ✅ | 🟢 95.4% | 188 | 197 | 9 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/lifecycle/shutdown.py` | `test_tracer_lifecycle_shutdown.py` | ✅ | 🟢 95.6% | 153 | 160 | 7 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/utils/session.py` | `test_tracer_utils_session.py` | ✅ | 🟢 96.8% | 120 | 124 | 4 | 10.0/10 | 0 | 0 |
| `honeyhive/models/tracing.py` | `test_models_tracing.py` | ✅ | 🟢 97.1% | 33 | 34 | 1 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/utils/git.py` | `test_tracer_utils_git.py` | ✅ | 🟢 97.1% | 133 | 137 | 4 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/utils/propagation.py` | `test_tracer_utils_propagation.py` | ✅ | 🟢 97.6% | 83 | 85 | 2 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/processing/context.py` | `test_tracer_processing_context.py` | ✅ | 🟢 98.1% | 156 | 159 | 3 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/registry.py` | `test_tracer_registry.py` | ✅ | 🟢 98.2% | 54 | 55 | 1 | 10.0/10 | 0 | 0 |
| `honeyhive/config/models/tracer.py` | `test_config_models_tracer.py` | ✅ | 🟢 98.7% | 77 | 78 | 1 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/utils/event_type.py` | `test_tracer_utils_event_type.py` | ✅ | 🟢 99.1% | 112 | 113 | 1 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/integration/processor.py` | `test_tracer_integration_processor.py` | ✅ | 🟢 99.3% | 137 | 138 | 1 | 10.0/10 | 0 | 0 |
| `honeyhive/api/evaluations.py` | `test_api_evaluations.py` | ✅ | 🟢 100.0% | 96 | 96 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/config/models/api_client.py` | `test_config_models_api_client.py` | ✅ | 🟢 100.0% | 14 | 14 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/config/models/base.py` | `test_config_models_base.py` | ✅ | 🟢 100.0% | 72 | 72 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/config/models/experiment.py` | `test_config_models_experiment.py` | ✅ | 🟢 100.0% | 49 | 49 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/config/models/http_client.py` | `test_config_models_http_client.py` | ✅ | 🟢 100.0% | 78 | 78 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/config/models/otlp.py` | `test_config_models_otlp.py` | ✅ | 🟢 100.0% | 108 | 108 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/models/generated.py` | `test_models_generated.py` | ✅ | 🟢 100.0% | 490 | 490 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/instrumentation/enrichment.py` | `test_tracer_instrumentation_enrichment.py` | ✅ | 🟢 100.0% | 74 | 74 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/integration/compatibility.py` | `test_tracer_integration_compatibility.py` | ✅ | 🟢 100.0% | 91 | 91 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/lifecycle/core.py` | `test_tracer_lifecycle_core.py` | ✅ | 🟢 100.0% | 75 | 75 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/lifecycle/flush.py` | `test_tracer_lifecycle_flush.py` | ✅ | 🟢 100.0% | 84 | 84 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/tracer/processing/otlp_exporter.py` | `test_tracer_processing_otlp_exporter.py` | ✅ | 🟢 100.0% | 65 | 65 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/utils/baggage_dict.py` | `test_utils_baggage_dict.py` | ✅ | 🟢 100.0% | 64 | 64 | 0 | 10.0/10 | 0 | 0 |
| `honeyhive/utils/dotdict.py` | `test_utils_dotdict.py` | ✅ | 🟢 100.0% | 76 | 76 | 0 | 10.0/10 | 0 | 0 |

## REAL Quality Summary (Individual File Analysis)
- **Average Pylint Score:** 9.91/10
- **Files with Perfect Pylint (10.0/10):** 53
- **Files with Pylint Issues (<10.0):** 5
- **Total Pylint Violations:** 11
- **Total MyPy Violations:** 0
- **Files with MyPy Violations:** 0
- **Files Analyzed:** 58

## Data Structure Approach Used:
1. ✅ Individual file iteration (as you suggested)
2. ✅ List of dictionaries for data storage
3. ✅ sort() with key function for coverage sorting
4. ✅ Iterate over list and join with | for table generation
5. ✅ Native string processing (no regex)
6. ✅ Correct Pylint violation detection
