"""Test utilities for HoneyHive Python SDK."""

# pylint: disable=duplicate-code

# Import from the parent utils.py file
import sys
from pathlib import Path
from typing import Any

from honeyhive.models.generated import SessionStartRequest

# Add parent directory to path to import from utils.py
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import all utility modules at the top
from .backend_verification import (  # pylint: disable=wrong-import-position
    verify_backend_event,
)
from .env_enforcement import (  # pylint: disable=wrong-import-position
    EnvFileNotFoundError,
    EnvironmentEnforcer,
    MissingCredentialsError,
    enforce_integration_credentials,
    enforce_local_env_file,
    get_llm_credentials,
    print_env_status,
)
from .otel_reset import (  # pylint: disable=wrong-import-position
    debug_otel_state,
    ensure_clean_otel_state,
    get_otel_provider_info,
    reset_otel_to_clean_sdk,
    reset_otel_to_functioning_sdk,
    reset_otel_to_noop,
    reset_otel_to_provider,
    restore_otel_state,
    save_otel_state,
)
from .validation_helpers import (  # pylint: disable=wrong-import-position
    ValidationError,
    generate_span_id,
    generate_test_id,
    verify_configuration_creation,
    verify_datapoint_creation,
    verify_event_creation,
    verify_session_creation,
    verify_span_export,
    verify_tracer_span,
)

try:
    from utils import (  # type: ignore[import-not-found]
        cleanup_test_environment,
        create_openai_config_request,
        create_session_request,
        mock_api_error_response,
        mock_success_response,
        setup_test_environment,
        test_error_handling_common,
    )
except ImportError:
    # Fallback implementations if utils.py not available
    def setup_test_environment() -> None:
        """Setup test environment variables."""

    def cleanup_test_environment() -> None:
        """Cleanup test environment variables."""

    def create_openai_config_request(
        _: str = "test-project", __: str = "test-config"  # project, name not used
    ) -> Any:
        """Fallback implementation."""
        return None

    def create_session_request(
        project: str = "test-project",
        session_name: str = "test-session",
        source: str = "test",
    ) -> Any:
        """Fallback implementation."""
        try:

            return SessionStartRequest(
                project=project,
                session_name=session_name,
                source=source,
                session_id=None,
                children_ids=None,
                config={},
                inputs={},
                outputs={},
                error=None,
                duration=None,
                user_properties={},
                metrics={},
                feedback={},
                metadata={},
                start_time=None,
                end_time=None,
            )
        except Exception as e:
            print(f"Fallback create_session_request failed: {e}")
            return None

    def mock_api_error_response(
        _: str = "API Error",  # exception_message not used in fallback
    ) -> Any:
        """Fallback implementation."""
        return None

    def mock_success_response(_: Any) -> Any:  # data not used in fallback
        """Fallback implementation."""
        return None

    def test_error_handling_common(
        _: Any, __: str = "API Error"  # integration_client, test_name not used
    ) -> Any:
        """Fallback implementation."""


__all__ = [
    "EnvironmentEnforcer",
    "EnvFileNotFoundError",
    "MissingCredentialsError",
    "enforce_local_env_file",
    "enforce_integration_credentials",
    "get_llm_credentials",
    "print_env_status",
    "setup_test_environment",
    "cleanup_test_environment",
    "create_openai_config_request",
    "create_session_request",
    "mock_api_error_response",
    "mock_success_response",
    "test_error_handling_common",
    "reset_otel_to_provider",
    "reset_otel_to_noop",
    "reset_otel_to_clean_sdk",
    "reset_otel_to_functioning_sdk",
    "save_otel_state",
    "restore_otel_state",
    "get_otel_provider_info",
    "ensure_clean_otel_state",
    "debug_otel_state",
    # Validation helpers
    "ValidationError",
    "generate_span_id",
    "generate_test_id",
    "verify_configuration_creation",
    "verify_datapoint_creation",
    "verify_event_creation",
    "verify_session_creation",
    "verify_span_export",
    "verify_tracer_span",
    "verify_backend_event",
]
