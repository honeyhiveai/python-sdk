from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["MetricDatapoints"]


class MetricDatapoints(BaseModel):
    """
    MetricDatapoints model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    passed: List[str] = Field(validation_alias="passed")

    failed: List[str] = Field(validation_alias="failed")
