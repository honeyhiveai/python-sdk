from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .GetAnnotationQueueByIdResponseFilters import GetAnnotationQueueByIdResponseFilters

__all__ = ["GetAnnotationQueueByIdResponse"]


class GetAnnotationQueueByIdResponse(BaseModel):
    """
    GetAnnotationQueueByIdResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    description: str = Field(validation_alias="description")

    filters: GetAnnotationQueueByIdResponseFilters = Field(validation_alias="filters")

    enabled: bool = Field(validation_alias="enabled")

    id: str = Field(validation_alias="id")

    scope_id: str = Field(validation_alias="scope_id")

    scope_type: str = Field(validation_alias="scope_type")

    is_active: bool = Field(validation_alias="is_active")

    created_at: str = Field(validation_alias="created_at")

    updated_at: Optional[datetime] = Field(validation_alias="updated_at")
