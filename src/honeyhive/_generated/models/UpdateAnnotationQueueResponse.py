from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .UpdateAnnotationQueueResponseQueue import UpdateAnnotationQueueResponseQueue

__all__ = ["UpdateAnnotationQueueResponse"]


class UpdateAnnotationQueueResponse(BaseModel):
    """
    UpdateAnnotationQueueResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    queue: UpdateAnnotationQueueResponseQueue = Field(validation_alias="queue")

    message: str = Field(validation_alias="message")
