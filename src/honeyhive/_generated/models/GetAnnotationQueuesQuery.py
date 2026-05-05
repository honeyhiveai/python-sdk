from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["GetAnnotationQueuesQuery"]


class GetAnnotationQueuesQuery(BaseModel):
    """
    GetAnnotationQueuesQuery model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    enabled: Optional[bool] = Field(validation_alias="enabled", default=None)
