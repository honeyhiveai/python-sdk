from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .CreateAnnotationQueueResponseQueue import CreateAnnotationQueueResponseQueue

__all__ = ["CreateAnnotationQueueResponse"]


class CreateAnnotationQueueResponse(BaseModel):
    """
    CreateAnnotationQueueResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    queue: CreateAnnotationQueueResponseQueue = Field(validation_alias="queue")

    message: str = Field(validation_alias="message")
