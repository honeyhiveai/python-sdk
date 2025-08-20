"""
Pytest configuration file for HoneyHive tracer tests.
This file ensures proper test isolation by resetting tracer state between all tests.
"""

import pytest
from honeyhive.tracer import reset_tracer_state


@pytest.fixture(autouse=True)
def reset_tracer_state_between_tests():
    """
    Automatically reset tracer state before and after each test.
    This ensures complete isolation between tests, even across different test classes.
    """
    # Reset before test
    reset_tracer_state()
    
    yield
    
    # Reset after test
    reset_tracer_state()
