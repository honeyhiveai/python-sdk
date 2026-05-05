from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["RunMetricResponse"]


class RunMetricResponse(BaseModel):
    """
    RunMetricResponse model
        Response for POST /metrics/run
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: bool = Field(validation_alias="success")

    loading: bool = Field(validation_alias="loading")

    result: Union[bool, float, str, None] = Field(validation_alias="result")

    explanation: Optional[str] = Field(validation_alias="explanation")
