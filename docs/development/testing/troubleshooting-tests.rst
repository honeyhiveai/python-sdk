Troubleshooting Test Issues
===========================

.. note::
   **Problem-solving guide for debugging HoneyHive SDK test issues**
   
   Practical solutions for diagnosing and fixing common testing problems with step-by-step troubleshooting approaches.

When tests fail or behave unexpectedly, systematic troubleshooting helps identify and resolve issues quickly.

Quick Diagnostics
-----------------

**Problem**: My HoneyHive tests are failing and I need to quickly identify the issue.

**Solution - Quick Diagnostic Checklist**:

.. code-block:: bash

   # 1. Check test environment
   echo "Python version: $(python --version)"
   echo "HoneyHive SDK version: $(pip show honeyhive | grep Version)"
   echo "Test mode: $HH_TEST_MODE"
   echo "API key set: ${HH_API_KEY:+YES}"
   
   # 2. Run single test with verbose output
   pytest tests/test_specific.py::test_failing_function -v -s --tb=long
   
   # 3. Check for import issues
   python -c "from honeyhive import HoneyHiveTracer; print('Import successful')"
   
   # 4. Verify test dependencies
   pip list | grep -E "(pytest|honeyhive|mock)"
   
   # 5. Check test isolation
   pytest tests/test_specific.py -v --tb=short
   
   # 6. Validate CLI functionality
   honeyhive --version
   honeyhive project list --limit 1
   
   # 7. Test SSL connectivity
   curl -v https://api.honeyhive.ai/health

Common Test Failures
--------------------

**Problem**: ImportError when importing HoneyHive SDK.

**Solution - Import Issue Debugging**:

.. code-block:: python

   """Debug import issues systematically."""
   
   import sys
   import os
   
   def debug_import_issues():
       """Systematic import debugging."""
       print("=== Import Debugging ===")
       
       # Check Python path
       print(f"Python executable: {sys.executable}")
       print(f"Python path: {sys.path}")
       
       # Check if HoneyHive is installed
       try:
           import honeyhive
           print(f"✅ HoneyHive imported successfully")
           print(f"HoneyHive version: {honeyhive.__version__}")
           print(f"HoneyHive location: {honeyhive.__file__}")
       except ImportError as e:
           print(f"❌ Failed to import HoneyHive: {e}")
           
           # Check if it's installed
           import subprocess
           result = subprocess.run(['pip', 'show', 'honeyhive'], 
                                 capture_output=True, text=True)
           if result.returncode == 0:
               print("HoneyHive is installed but not importable")
               print(result.stdout)
           else:
               print("HoneyHive is not installed")
               print("Run: pip install honeyhive")
       
       # Check individual component imports
       components = [
           'honeyhive.tracer',
           'honeyhive.api.client',
           'honeyhive.evaluation',
           'honeyhive.utils'
       ]
       
       for component in components:
           try:
               __import__(component)
               print(f"✅ {component} imported successfully")
           except ImportError as e:
               print(f"❌ Failed to import {component}: {e}")
       
       # Check for conflicting packages
       print("\n=== Checking for conflicts ===")
       import pkg_resources
       installed_packages = [d.project_name for d in pkg_resources.working_set]
       
       potential_conflicts = ['honeyhive-dev', 'honeyhive-test']
       for package in potential_conflicts:
           if package in installed_packages:
               print(f"⚠️ Potential conflict: {package} is installed")

**Usage**:

.. code-block:: python

   # Run import debugging
   debug_import_issues()

**Problem**: Tests pass individually but fail when run together.

**Solution - Test Isolation Issues**:

.. code-block:: python

   """Debug test isolation problems."""
   
   import pytest
   from honeyhive import HoneyHiveTracer
   
   # Common cause: Global state contamination
   class TestIsolationDebugger:
       """Debug test isolation issues."""
       
       @pytest.fixture(autouse=True)
       def debug_test_state(self, request):
           """Automatically debug test state before/after each test."""
           test_name = request.node.name
           
           print(f"\n=== Before {test_name} ===")
           self._print_global_state()
           
           yield
           
           print(f"\n=== After {test_name} ===")
           self._print_global_state()
       
       def _print_global_state(self):
           """Print relevant global state."""
           import honeyhive
           
           # Check for module-level state
           if hasattr(honeyhive, '_global_tracer'):
               print(f"Global tracer: {honeyhive._global_tracer}")
           
           # Check environment variables
           import os
           env_vars = ['HH_API_KEY', 'HH_PROJECT', 'HH_TEST_MODE']
           for var in env_vars:
               value = os.environ.get(var, 'NOT_SET')
               print(f"{var}: {value}")
           
           # Check active threads
           import threading
           active_threads = threading.active_count()
           print(f"Active threads: {active_threads}")
       
       def test_isolation_example_1(self):
           """Test that might affect global state."""
           tracer = HoneyHiveTracer.init(
               api_key="test-1",        # Or set HH_API_KEY environment variable
               project="test-project",  # Or set HH_PROJECT environment variable
               test_mode=True           # Or set HH_TEST_MODE=true
           )
           # Test logic here
       
       def test_isolation_example_2(self):
           """Test that might be affected by previous test."""
           tracer = HoneyHiveTracer.init(
               api_key="test-2",               test_mode=True
           )
           # This test might fail if previous test contaminated state

**Solution - Proper Test Isolation**:

.. code-block:: python

   """Ensure proper test isolation."""
   
   import pytest
   import os
   from unittest.mock import patch
   
   @pytest.fixture
   def isolated_environment():
       """Fixture for isolated test environment."""
       # Save original environment
       original_env = {}
       honeyhive_vars = [k for k in os.environ.keys() if k.startswith('HH_')]
       
       for var in honeyhive_vars:
           original_env[var] = os.environ[var]
           del os.environ[var]
       
       yield
       
       # Restore original environment
       for var, value in original_env.items():
           os.environ[var] = value
   
   @pytest.fixture
   def clean_imports():
       """Fixture to clean module imports between tests."""
       import sys
       
       # Save modules related to honeyhive
       honeyhive_modules = [name for name in sys.modules.keys() 
                           if name.startswith('honeyhive')]
       saved_modules = {}
       
       for module_name in honeyhive_modules:
           saved_modules[module_name] = sys.modules[module_name]
       
       yield
       
       # Clean up any new modules
       current_modules = [name for name in sys.modules.keys() 
                         if name.startswith('honeyhive')]
       
       for module_name in current_modules:
           if module_name not in saved_modules:
               del sys.modules[module_name]
   
   def test_with_isolation(isolated_environment, clean_imports):
       """Test with proper isolation."""
       # This test runs in a clean environment
       from honeyhive import HoneyHiveTracer
       
       tracer = HoneyHiveTracer.init(
           api_key="isolated-test",           test_mode=True
       )
       
       # Test logic here

**Problem**: Mock objects not working as expected.

**Solution - Mock Debugging**:

.. code-block:: python

   """Debug mock-related issues."""
   
   from unittest.mock import Mock, patch, MagicMock
   import pytest
   
   def debug_mock_issues():
       """Debug common mock problems."""
       
       # Issue 1: Mock not being called
       def test_mock_not_called():
           mock_tracer = Mock()
           
           # If this fails, the mock wasn't called
           try:
               mock_tracer.trace.assert_called()
               print("✅ Mock was called")
           except AssertionError:
               print("❌ Mock was not called")
               print(f"Call count: {mock_tracer.trace.call_count}")
               print(f"Called with: {mock_tracer.trace.call_args_list}")
       
       # Issue 2: Mock called with unexpected arguments
       def test_mock_call_args():
           mock_tracer = Mock()
           mock_tracer.trace("test-span", event_type="test")
           
           # Debug call arguments
           print(f"Call args: {mock_tracer.trace.call_args}")
           print(f"Call args list: {mock_tracer.trace.call_args_list}")
           
           # More specific assertion
           mock_tracer.trace.assert_called_with("test-span", event_type="test")
       
       # Issue 3: Mock return value not configured
       def test_mock_return_value():
           mock_tracer = Mock()
           
           # Configure return value properly
           mock_span = Mock()
           mock_span.__enter__ = Mock(return_value=mock_span)
           mock_span.__exit__ = Mock(return_value=None)
           mock_tracer.trace.return_value = mock_span
           
           # Test the mock
           with mock_tracer.trace("test") as span:
               span.set_attribute("key", "value")
           
           # Verify interactions
           mock_tracer.trace.assert_called_once_with("test")
           mock_span.set_attribute.assert_called_once_with("key", "value")
       
       # Issue 4: Patching at wrong level
       def test_patch_location():
           # Wrong: patching at import level after import
           from honeyhive import HoneyHiveTracer
           
           with patch('honeyhive.HoneyHiveTracer') as mock_class:
               # This won't work because HoneyHiveTracer is already imported
               tracer = HoneyHiveTracer.init(api_key="test")
               # mock_class won't be called
           
           # Correct: patch where it's used
           with patch('your_module.HoneyHiveTracer') as mock_class:
               from your_module import function_that_uses_tracer
               function_that_uses_tracer()
               mock_class.init.assert_called()

**Problem**: Tests are slow or timing out.

**Solution - Performance Debugging**:

.. code-block:: python

   """Debug test performance issues."""
   
   import time
   import pytest
   from functools import wraps
   
   def time_test(func):
       """Decorator to time test execution."""
       @wraps(func)
       def wrapper(*args, **kwargs):
           start = time.time()
           try:
               result = func(*args, **kwargs)
               return result
           finally:
               end = time.time()
               duration = end - start
               print(f"Test {func.__name__} took {duration:.2f} seconds")
               
               if duration > 10:  # Warn for slow tests
                   print(f"⚠️ Slow test detected: {func.__name__}")
       
       return wrapper
   
   class TestPerformanceDebugging:
       """Debug test performance issues."""
       
       @time_test
       def test_potentially_slow(self):
           """Test that might be slow."""
           # Add debugging to find bottlenecks
           
           start = time.time()
           from honeyhive import HoneyHiveTracer
           import_time = time.time() - start
           print(f"Import time: {import_time:.3f}s")
           
           start = time.time()
           tracer = HoneyHiveTracer.init(
               api_key="perf-test",               test_mode=True
           )
           init_time = time.time() - start
           print(f"Init time: {init_time:.3f}s")
           
           start = time.time()
           with tracer.trace("perf-span") as span:
               span.set_attribute("test", "value")
           trace_time = time.time() - start
           print(f"Trace time: {trace_time:.3f}s")
       
       def test_network_timeout_debug(self):
           """Debug network-related timeouts."""
           import requests
           from unittest.mock import patch
           
           # Mock slow network calls
           with patch('requests.post') as mock_post:
               def slow_response(*args, **kwargs):
                   time.sleep(5)  # Simulate slow network
                   mock_response = Mock()
                   mock_response.status_code = 200
                   return mock_response
               
               mock_post.side_effect = slow_response
               
               # Your test code here - will be slow due to network
               # Consider mocking or reducing timeouts

Environment Issues
------------------

**Problem**: Tests behave differently in different environments.

**Solution - Environment Debugging**:

.. code-block:: python

   """Debug environment-specific issues."""
   
   import os
   import sys
   import platform
   
   def debug_environment():
       """Print comprehensive environment information."""
       print("=== Environment Debug Information ===")
       
       # Python environment
       print(f"Python version: {sys.version}")
       print(f"Python executable: {sys.executable}")
       print(f"Platform: {platform.platform()}")
       print(f"Architecture: {platform.architecture()}")
       
       # Package versions
       try:
           import honeyhive
           print(f"HoneyHive version: {honeyhive.__version__}")
       except ImportError:
           print("HoneyHive not installed")
       
       try:
           import pytest
           print(f"Pytest version: {pytest.__version__}")
       except ImportError:
           print("Pytest not installed")
       
       # Environment variables
       print("\n=== HoneyHive Environment Variables ===")
       honeyhive_vars = {k: v for k, v in os.environ.items() 
                        if k.startswith('HH_')}
       
       if honeyhive_vars:
           for key, value in honeyhive_vars.items():
               # Mask sensitive values
               if 'KEY' in key or 'SECRET' in key:
                   display_value = value[:4] + '***' if len(value) > 4 else '***'
               else:
                   display_value = value
               print(f"{key}: {display_value}")
       else:
           print("No HoneyHive environment variables set")
       
       # Working directory and paths
       print(f"\n=== Paths ===")
       print(f"Working directory: {os.getcwd()}")
       print(f"Python path: {sys.path[:3]}...")  # First 3 entries
       
       # Test-specific environment
       test_vars = ['CI', 'GITHUB_ACTIONS', 'GITLAB_CI', 'JENKINS_URL']
       ci_detected = []
       for var in test_vars:
           if os.environ.get(var):
               ci_detected.append(var)
       
       if ci_detected:
           print(f"CI environment detected: {', '.join(ci_detected)}")
       else:
           print("Local development environment")

**Problem**: Tests fail in CI but pass locally.

**Solution - CI-Specific Debugging**:

.. code-block:: python

   """Debug CI-specific test failures."""
   
   import os
   import pytest
   
   def is_ci_environment():
       """Detect if running in CI environment."""
       ci_indicators = [
           'CI', 'CONTINUOUS_INTEGRATION',
           'GITHUB_ACTIONS', 'GITLAB_CI', 'JENKINS_URL',
           'TRAVIS', 'CIRCLECI', 'BUILDKITE'
       ]
       return any(os.environ.get(indicator) for indicator in ci_indicators)
   
   def debug_ci_differences():
       """Debug differences between local and CI environments."""
       if is_ci_environment():
           print("Running in CI environment")
           
           # CI-specific debugging
           print(f"Available memory: {os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') // (1024**3)} GB")
           print(f"CPU count: {os.cpu_count()}")
           
           # Check for CI-specific limitations
           import tempfile
           temp_dir = tempfile.gettempdir()
           print(f"Temp directory: {temp_dir}")
           
           # Test network access
           try:
               import requests
               response = requests.get('https://httpbin.org/status/200', timeout=5)
               print(f"Network access: ✅ (status: {response.status_code})")
           except Exception as e:
               print(f"Network access: ❌ ({e})")
           
           # Check for specific CI limitations
           if os.environ.get('GITHUB_ACTIONS'):
               print("GitHub Actions specific checks:")
               print(f"Runner OS: {os.environ.get('RUNNER_OS')}")
               print(f"Workflow: {os.environ.get('GITHUB_WORKFLOW')}")
       else:
           print("Running in local environment")
   
   # Use conditional testing for CI differences
   @pytest.mark.skipif(is_ci_environment(), reason="Flaky in CI environment")
   def test_local_only():
       """Test that only runs locally."""
       pass
   
   @pytest.mark.skipif(not is_ci_environment(), reason="CI-specific test")
   def test_ci_only():
       """Test that only runs in CI."""
       pass
   
   def test_with_ci_timeout():
       """Test with CI-appropriate timeout."""
       import time
       
       # Longer timeout in CI
       timeout = 30 if is_ci_environment() else 10
       
       start = time.time()
       # Your test logic here
       elapsed = time.time() - start
       
       assert elapsed < timeout, f"Test took too long: {elapsed:.2f}s"

Debugging Test Data and Fixtures
--------------------------------

**Problem**: Test fixtures are not working correctly.

**Solution - Fixture Debugging**:

.. code-block:: python

   """Debug pytest fixture issues."""
   
   import pytest
   from honeyhive import HoneyHiveTracer
   
   # Debug fixture scope issues
   @pytest.fixture(scope="function")  # Explicit scope
   def debug_tracer():
       """Debug tracer fixture with logging."""
       print("🔧 Creating debug tracer")
       
       tracer = HoneyHiveTracer.init(
           api_key="debug-test-key",           test_mode=True
       )
       
       print(f"✅ Tracer created: {tracer.session_id}")
       yield tracer
       
       print("🧹 Cleaning up debug tracer")
       tracer.close()
   
   # Debug fixture dependencies
   @pytest.fixture
   def debug_session(debug_tracer):
       """Fixture that depends on debug_tracer."""
       print(f"🔧 Creating session for tracer: {debug_tracer.session_id}")
       return debug_tracer.session_id
   
   # Debug fixture parameters
   @pytest.fixture(params=[256, 512, 1024])
   def memory_size(request):
       """Parameterized fixture for memory sizes."""
       print(f"🔧 Using memory size: {request.param}MB")
       return request.param
   
   def test_with_debug_fixtures(debug_tracer, debug_session, memory_size):
       """Test using debug fixtures."""
       print(f"🧪 Running test with:")
       print(f"  Tracer: {debug_tracer.session_id}")
       print(f"  Session: {debug_session}")
       print(f"  Memory: {memory_size}MB")
       
       assert debug_tracer.session_id == debug_session
   
   # Debug fixture cleanup issues
   @pytest.fixture
   def resource_with_cleanup():
       """Fixture that tracks cleanup."""
       resource = {"created": True, "cleaned": False}
       
       yield resource
       
       # Cleanup verification
       resource["cleaned"] = True
       print(f"🧹 Resource cleanup: {resource}")
       
       # Assert cleanup happened
       assert resource["cleaned"], "Resource was not properly cleaned up"

Async Test Debugging
--------------------

**Problem**: Async tests are failing or hanging.

**Solution - Async Test Debugging**:

.. code-block:: python

   """Debug async test issues."""
   
   import asyncio
   import pytest
   import time
   from honeyhive import HoneyHiveTracer
   
   # Debug async test timing
   @pytest.mark.asyncio
   async def test_async_with_timeout():
       """Async test with explicit timeout."""
       try:
           # Set a reasonable timeout
           async with asyncio.timeout(10):  # 10 second timeout
               tracer = HoneyHiveTracer.init(
                   api_key="async-test",
                   test_mode=True
               )
               
               # Your async test logic here
               await asyncio.sleep(0.1)  # Simulate async work
               
       except asyncio.TimeoutError:
           pytest.fail("Async test timed out after 10 seconds")
   
   # Debug event loop issues
   @pytest.mark.asyncio
   async def test_event_loop_debug():
       """Debug event loop state."""
       loop = asyncio.get_running_loop()
       print(f"Event loop: {loop}")
       print(f"Loop running: {loop.is_running()}")
       print(f"Loop closed: {loop.is_closed()}")
       
       # Check for pending tasks
       pending_tasks = [task for task in asyncio.all_tasks(loop) 
                       if not task.done()]
       print(f"Pending tasks: {len(pending_tasks)}")
       
       for task in pending_tasks[:5]:  # Show first 5
           print(f"  {task}")
   
   # Debug async mock issues
   @pytest.mark.asyncio
   async def test_async_mock_debug():
       """Debug async mocking issues."""
       from unittest.mock import AsyncMock, Mock
       
       # Correct async mock setup
       mock_tracer = Mock()
       mock_tracer.atrace = AsyncMock()
       
       # Configure async mock return value
       mock_span = Mock()
       mock_span.__aenter__ = AsyncMock(return_value=mock_span)
       mock_span.__aexit__ = AsyncMock(return_value=None)
       mock_tracer.atrace.return_value = mock_span
       
       # Test async mock
       async with mock_tracer.atrace("test") as span:
           span.set_attribute("async", True)
       
       # Verify async mock calls
       mock_tracer.atrace.assert_called_once_with("test")
       mock_span.set_attribute.assert_called_once_with("async", True)

Test Debugging Tools
--------------------

**Problem**: Need comprehensive debugging tools for test failures.

**Solution - Debug Utilities**:

.. code-block:: python

   """Comprehensive test debugging utilities."""
   
   import pytest
   import sys
   import traceback
   import logging
   from contextlib import contextmanager
   
   class TestDebugger:
       """Comprehensive test debugging utilities."""
       
       def __init__(self):
           self.debug_enabled = True
           self.logs = []
       
       @contextmanager
       def debug_context(self, test_name):
           """Context manager for comprehensive test debugging."""
           print(f"\n{'='*50}")
           print(f"🐛 DEBUG: Starting {test_name}")
           print(f"{'='*50}")
           
           # Capture logs
           if self.debug_enabled:
               logging.basicConfig(level=logging.DEBUG)
           
           try:
               yield self
           except Exception as e:
               print(f"\n{'='*50}")
               print(f"❌ ERROR in {test_name}: {e}")
               print(f"{'='*50}")
               
               # Print full traceback
               traceback.print_exc()
               
               # Print debug information
               self.print_debug_info()
               raise
           finally:
               print(f"\n{'='*50}")
               print(f"🏁 DEBUG: Finished {test_name}")
               print(f"{'='*50}")
       
       def print_debug_info(self):
           """Print comprehensive debug information."""
           print("\n=== DEBUG INFORMATION ===")
           
           # Print captured logs
           if self.logs:
               print("Recent logs:")
               for log in self.logs[-10:]:  # Last 10 logs
                   print(f"  {log}")
           
           # Print system information
           print(f"Python version: {sys.version}")
           print(f"Working directory: {os.getcwd()}")
           
           # Print HoneyHive state if available
           try:
               import honeyhive
               print(f"HoneyHive version: {honeyhive.__version__}")
           except:
               print("HoneyHive not available")
       
       def add_debug_log(self, message):
           """Add debug log entry."""
           self.logs.append(f"{time.time()}: {message}")
   
   # Global debugger instance
   debugger = TestDebugger()
   
   def test_with_comprehensive_debugging():
       """Example test with comprehensive debugging."""
       with debugger.debug_context("test_with_comprehensive_debugging"):
           debugger.add_debug_log("Starting test setup")
           
           # Your test code here
           from honeyhive import HoneyHiveTracer
           
           debugger.add_debug_log("Creating tracer")
           tracer = HoneyHiveTracer.init(
               api_key="debug-test",
               test_mode=True
           )
           
           debugger.add_debug_log("Creating span")
           with tracer.trace("debug-span") as span:
               span.set_attribute("debug", True)
               debugger.add_debug_log("Span created successfully")
           
           debugger.add_debug_log("Test completed successfully")

**Debugging Commands**:

.. code-block:: bash

   # Run tests with maximum debugging information
   pytest tests/test_file.py::test_function -v -s --tb=long --capture=no
   
   # Run with Python debugger on failure
   pytest tests/test_file.py --pdb
   
   # Run with custom debugging
   pytest tests/test_file.py --debug-mode --log-level=DEBUG
   
   # Run single test with full output
   pytest tests/test_file.py::test_function -v -s --tb=line --no-header

CLI Validation in Tests
-----------------------

**Problem**: Need to validate HoneyHive CLI functionality in test environments.

**Solution - CLI Test Validation**:

.. code-block:: bash

   # Validate CLI installation in test environment
   honeyhive --version
   
   # Test API connectivity
   honeyhive project list --limit 1
   
   # Create test events with valid event_type values
   honeyhive event create \
     --project "test-project" \
     --event-type "model" \
     --event-name "cli-test-model" \
     --inputs '{"test": "model_validation"}'
   
   honeyhive event create \
     --project "test-project" \
     --event-type "tool" \
     --event-name "cli-test-tool" \
     --inputs '{"test": "tool_validation"}'
   
   honeyhive event create \
     --project "test-project" \
     --event-type "chain" \
     --event-name "cli-test-chain" \
     --inputs '{"test": "chain_validation"}'
   
   # Validate event_type filtering works correctly
   honeyhive event search --query "event_type:model" --limit 1
   honeyhive event search --query "event_type:tool" --limit 1
   honeyhive event search --query "event_type:chain" --limit 1
   
   # Test event_type combinations
   honeyhive event search --query "event_type:[model,tool]" --limit 5
   
   # Validate recent test events
   honeyhive event search \
     --query "event_name:cli-test-* AND start_time:>$(date -d '5 minutes ago' --iso-8601)" \
     --fields "event_id,event_type,event_name,start_time"

**CLI Integration in Test Suite**:

.. code-block:: python

   """Integrate CLI validation into test suite."""
   
   import subprocess
   import pytest
   import json
   from datetime import datetime, timedelta
   
   class TestCLIValidation:
       """Test CLI functionality and event_type validation."""
       
       def test_cli_connectivity(self):
           """Test CLI can connect to HoneyHive API."""
           result = subprocess.run(
               ["honeyhive", "--version"],
               capture_output=True,
               text=True
           )
           assert result.returncode == 0, f"CLI not available: {result.stderr}"
           assert "honeyhive" in result.stdout.lower()
       
       @pytest.mark.parametrize("event_type", ["model", "tool", "chain"])
       def test_valid_event_types(self, event_type):
           """Test all valid event_type values work with CLI."""
           # Create test event
           create_result = subprocess.run([
               "honeyhive", "event", "create",
               "--project", "test-project",
               "--event-type", event_type,
               "--event-name", f"test-{event_type}-event",
               "--inputs", '{"test": "validation"}'
           ], capture_output=True, text=True)
           
           assert create_result.returncode == 0, f"Failed to create {event_type} event: {create_result.stderr}"
           
           # Verify event can be found
           search_result = subprocess.run([
               "honeyhive", "event", "search",
               "--query", f"event_type:{event_type}",
               "--limit", "1"
           ], capture_output=True, text=True)
           
           assert search_result.returncode == 0, f"Failed to search {event_type} events: {search_result.stderr}"
       
       def test_invalid_event_type_rejection(self):
           """Test that invalid event_type values are rejected."""
           invalid_types = ["llm", "evaluation", "custom", "invalid"]
           
           for invalid_type in invalid_types:
               result = subprocess.run([
                   "honeyhive", "event", "create",
                   "--project", "test-project", 
                   "--event-type", invalid_type,
                   "--event-name", f"test-invalid-{invalid_type}"
               ], capture_output=True, text=True)
               
               # Should fail with invalid event type
               assert result.returncode != 0, f"Invalid event_type '{invalid_type}' was accepted"
       
       def test_event_search_filtering(self):
           """Test event_type filtering in search."""
           # Search with specific event_type
           result = subprocess.run([
               "honeyhive", "event", "search",
               "--query", "event_type:model",
               "--fields", "event_id,event_type,event_name",
               "--limit", "5"
           ], capture_output=True, text=True)
           
           assert result.returncode == 0, f"Search failed: {result.stderr}"

**Environment Validation Script**:

.. code-block:: bash

   #!/bin/bash
   # validate_test_environment.sh
   
   echo "🔍 Validating HoneyHive test environment..."
   
   # Check CLI installation
   if command -v honeyhive &> /dev/null; then
       echo "✅ HoneyHive CLI installed: $(honeyhive --version)"
   else
       echo "❌ HoneyHive CLI not found"
       exit 1
   fi
   
   # Check API connectivity
   if honeyhive project list --limit 1 &> /dev/null; then
       echo "✅ API connectivity confirmed"
   else
       echo "❌ Cannot connect to HoneyHive API"
       exit 1
   fi
   
   # Validate event_type handling
   echo "🧪 Testing valid event types..."
   
   for event_type in model tool chain; do
       if honeyhive event create \
           --project "test-validation" \
           --event-type "$event_type" \
           --event-name "validation-$event_type" \
           --inputs '{"validation": true}' &> /dev/null; then
           echo "✅ Event type '$event_type' accepted"
       else
           echo "❌ Event type '$event_type' rejected"
       fi
   done
   
   echo "🎉 Environment validation complete"

See Also
--------

- :doc:`unit-testing` - Unit testing best practices
- :doc:`integration-testing` - Integration testing strategies
- :doc:`mocking-strategies` - Advanced mocking techniques
- :doc:`../../reference/api/tracer` - Tracer API reference for debugging
