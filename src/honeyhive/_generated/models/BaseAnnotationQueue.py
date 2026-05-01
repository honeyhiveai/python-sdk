from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .BaseAnnotationQueueFilters import BaseAnnotationQueueFilters

__all__ = ["BaseAnnotationQueue"]


class BaseAnnotationQueue(BaseModel):
    """
    BaseAnnotationQueue model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    description: str = Field(validation_alias="description")

    filters: BaseAnnotationQueueFilters = Field(validation_alias="filters")

    enabled: bool = Field(validation_alias="enabled")
