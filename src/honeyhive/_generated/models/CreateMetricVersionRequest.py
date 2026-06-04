from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .MetricVersionContentRequest import MetricVersionContentRequest

__all__ = ["CreateMetricVersionRequest"]


class CreateMetricVersionRequest(BaseModel):
    """
    CreateMetricVersionRequest model
        Request body for POST /v1/metrics/{metric_id}/versions
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    message: str = Field(validation_alias="message")

    content: MetricVersionContentRequest = Field(validation_alias="content")

    deploy_immediately: Optional[bool] = Field(
        validation_alias="deploy_immediately", default=None
    )
