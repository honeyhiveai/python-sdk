"""Experiment configuration models for HoneyHive SDK.

This module provides Pydantic models for experiment and evaluation configuration
including A/B testing, feature flags, and experimental features. Supports
multiple experiment tracking platforms (MLflow, W&B, Comet, etc.).
"""

# pylint: disable=duplicate-code
# Note: Environment variable utility functions (_get_env_*) are intentionally
# duplicated across config modules to keep each module self-contained and
# avoid unnecessary coupling. These are simple, stable utility functions.

import json
import logging
import os
from typing import Any, Dict, Optional

from pydantic import Field, field_validator

from .base import BaseHoneyHiveConfig, _safe_validate_string


def _get_env_json(key: str, default: Optional[dict] = None) -> Optional[dict]:
    """Get JSON value from environment variable."""
    value = os.getenv(key)
    if not value:
        return default
    try:
        result = json.loads(value)
        if isinstance(result, dict):
            return result
        return default
    except (json.JSONDecodeError, TypeError):
        return default


class ExperimentConfig(BaseHoneyHiveConfig):
    """Experiment and evaluation configuration settings.

    This class extends BaseHoneyHiveConfig with experiment-specific settings
    for A/B testing, feature flags, and experimental features. Supports
    multiple experiment tracking platforms (MLflow, W&B, Comet, etc.).

    Example:
        >>> config = ExperimentConfig(
        ...     experiment_id="exp_12345",
        ...     experiment_name="model-comparison",
        ...     experiment_variant="baseline",
        ...     experiment_group="control"
        ... )
        >>> # Or load from environment variables:
        >>> # export HH_EXPERIMENT_ID=exp_12345
        >>> # export MLFLOW_EXPERIMENT_NAME=model-comparison
        >>> config = ExperimentConfig()
    """

    # Experiment identification
    experiment_id: Optional[str] = Field(
        default=None,
        description="Unique experiment identifier",
        examples=["exp_12345", "experiment-2024-01-15"],
    )

    experiment_name: Optional[str] = Field(
        default=None,
        description="Human-readable experiment name",
        examples=["model-comparison", "baseline-vs-optimized"],
    )

    # Experiment variants and groups
    experiment_variant: Optional[str] = Field(
        default=None,
        description="Experiment variant/treatment identifier",
        examples=["baseline", "treatment_a", "optimized"],
    )

    experiment_group: Optional[str] = Field(
        default=None,
        description="Experiment group/cohort identifier",
        examples=["control", "test", "cohort_1"],
    )

    # Experiment metadata
    experiment_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Experiment metadata and tags",
        examples=[{"model_type": "gpt-4", "temperature": 0.7}],
    )

    def __init__(self, **data: Any) -> None:
        """Load this class's fields from the environment before validation.

        Init kwargs outrank the pydantic-settings environment source, so the
        HH_ names read here are what populate the fields declared on this
        class; the inherited fields still come through env_prefix. Reading
        them here also honours the bare EXPERIMENT_* names and the MLflow,
        Weights & Biases and Comet variables, and falls back to the default on
        a malformed value instead of raising.
        """
        # Load from environment variables with fallbacks to standard platforms
        env_data = {
            # Experiment ID with multiple fallbacks
            "experiment_id": (
                os.getenv("HH_EXPERIMENT_ID")
                or os.getenv("EXPERIMENT_ID")
                or os.getenv("MLFLOW_EXPERIMENT_ID")
                or os.getenv("WANDB_RUN_ID")
                or os.getenv("COMET_EXPERIMENT_KEY")
            ),
            # Experiment name with multiple fallbacks
            "experiment_name": (
                os.getenv("HH_EXPERIMENT_NAME")
                or os.getenv("EXPERIMENT_NAME")
                or os.getenv("MLFLOW_EXPERIMENT_NAME")
                or os.getenv("WANDB_PROJECT")
                or os.getenv("COMET_PROJECT_NAME")
            ),
            # Experiment variant with multiple fallbacks
            "experiment_variant": (
                os.getenv("HH_EXPERIMENT_VARIANT")
                or os.getenv("EXPERIMENT_VARIANT")
                or os.getenv("VARIANT")
                or os.getenv("AB_TEST_VARIANT")
                or os.getenv("TREATMENT")
            ),
            # Experiment group with multiple fallbacks
            "experiment_group": (
                os.getenv("HH_EXPERIMENT_GROUP")
                or os.getenv("EXPERIMENT_GROUP")
                or os.getenv("GROUP")
                or os.getenv("AB_TEST_GROUP")
                or os.getenv("COHORT")
            ),
            # Experiment metadata with multiple fallbacks
            "experiment_metadata": (
                _get_env_json("HH_EXPERIMENT_METADATA")
                or _get_env_json("EXPERIMENT_METADATA")
                or _get_env_json("MLFLOW_TAGS")
                or _get_env_json("WANDB_TAGS")
                or _get_env_json("COMET_TAGS")
            ),
        }

        # Merge environment data with provided data (provided data takes precedence)
        merged_data = {**env_data, **data}
        super().__init__(**merged_data)

    @field_validator(
        "experiment_id",
        "experiment_name",
        "experiment_variant",
        "experiment_group",
        mode="before",
    )
    @classmethod
    def validate_experiment_strings(cls, v: Optional[str]) -> Optional[str]:
        """Validate experiment string fields with graceful degradation."""

        return _safe_validate_string(
            v, "experiment field", allow_none=True, default=None
        )

    @field_validator("experiment_metadata", mode="before")
    @classmethod
    def validate_experiment_metadata(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate experiment metadata format with graceful degradation."""
        if v is not None:
            if not isinstance(v, dict):
                logger = logging.getLogger(__name__)
                logger.warning(
                    ("Invalid experiment_metadata: expected dict, got %s. Using None."),
                    type(v).__name__,
                    extra={"honeyhive_data": {"metadata_type": type(v).__name__}},
                )
                return None

            # Ensure all keys are strings - filter out invalid keys
            valid_metadata = {}
            for key, value in v.items():
                if isinstance(key, str):
                    valid_metadata[key] = value
                else:
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        (
                            "Invalid experiment_metadata key: expected string, "
                            "got %s. Skipping key."
                        ),
                        type(key).__name__,
                        extra={
                            "honeyhive_data": {
                                "key_type": type(key).__name__,
                                "key": str(key),
                            }
                        },
                    )
            return valid_metadata if valid_metadata else None
        return v
