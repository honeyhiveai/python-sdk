from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .CreateAnnotationQueueRequestFilters import CreateAnnotationQueueRequestFilters

__all__ = ["CreateAnnotationQueueRequest"]


class CreateAnnotationQueueRequest(BaseModel):
    """
    CreateAnnotationQueueRequest model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description", default=None)

    filters: Optional[CreateAnnotationQueueRequestFilters] = Field(
        validation_alias="filters", default=None
    )

    enabled: Optional[bool] = Field(validation_alias="enabled", default=None)

    event_ids: Optional[List[str]] = Field(validation_alias="event_ids", default=None)
