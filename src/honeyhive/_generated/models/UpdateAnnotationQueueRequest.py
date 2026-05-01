from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .UpdateAnnotationQueueRequestFilters import UpdateAnnotationQueueRequestFilters

__all__ = ["UpdateAnnotationQueueRequest"]


class UpdateAnnotationQueueRequest(BaseModel):
    """
    UpdateAnnotationQueueRequest model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    filters: Optional[UpdateAnnotationQueueRequestFilters] = Field(
        validation_alias="filters", default=None
    )

    enabled: Optional[bool] = Field(validation_alias="enabled", default=None)

    id: str = Field(validation_alias="id")

    add_event_ids: Optional[List[str]] = Field(
        validation_alias="add_event_ids", default=None
    )

    remove_event_ids: Optional[List[str]] = Field(
        validation_alias="remove_event_ids", default=None
    )
