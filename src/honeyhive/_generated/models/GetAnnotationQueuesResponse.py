from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .GetAnnotationQueuesResponseQueuesItem import GetAnnotationQueuesResponseQueuesItem

__all__ = ["GetAnnotationQueuesResponse"]


class GetAnnotationQueuesResponse(BaseModel):
    """
    GetAnnotationQueuesResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    queues: List[GetAnnotationQueuesResponseQueuesItem] = Field(
        validation_alias="queues"
    )
