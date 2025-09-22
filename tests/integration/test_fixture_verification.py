#!/usr/bin/env python3
"""Simple test to verify that integration test fixtures work correctly."""
# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Integration test file with fixture verification

from typing import Any

import pytest

from tests.utils import (  # pylint: disable=no-name-in-module
    generate_test_id,
    verify_tracer_span,
)


@pytest.mark.integration
@pytest.mark.tracer
def test_fixture_verification(
    integration_tracer: Any,
    integration_client: Any,
    real_project: Any,
    real_source: Any,  # pylint: disable=unused-argument
) -> None:
    """Test that fixtures provide correct values and spans are exported."""
    # Verify we have a valid project name
    assert real_project is not None, "Project should not be None"
    assert (
        len(real_project.strip()) > 0
    ), f"Project should not be empty: '{real_project}'"
    assert (
        integration_tracer.project == real_project
    ), f"Tracer project mismatch: {integration_tracer.project} != {real_project}"

    # Create span and verify using NEW standardized pattern

    span_name, unique_id = generate_test_id("fixture_test", "fixture_test")

    # Use NEW validation pattern - creates span AND verifies backend
    event = verify_tracer_span(
        tracer=integration_tracer,
        client=integration_client,
        project=real_project,
        span_name=span_name,
        unique_identifier=unique_id,
        span_attributes={
            "test.fixture_verification": "true",
            "test.type": "fixture_verification",
        },
    )

    # Validate fixture verification attribute
    assert event.metadata.get("test.fixture_verification") == "true"


if __name__ == "__main__":
    import os
    import sys

    sys.path.insert(0, "tests")

    # Load environment
    from dotenv import load_dotenv

    load_dotenv()

    # Create fixture values
    credentials = {
        "api_key": os.environ.get("HH_API_KEY"),
        "source": os.environ.get("HH_SOURCE", "pytest-integration"),
        "project": os.environ.get("HH_PROJECT"),
    }

    print(f"Environment project: {os.environ.get('HH_PROJECT')}")
    print(f"Credentials project: {credentials['project']}")

    # This would be called by pytest normally
    # test_fixture_verification(tracer, key, project, source)
