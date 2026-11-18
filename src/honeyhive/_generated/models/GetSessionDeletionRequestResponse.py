from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .SessionDeletionRequest import SessionDeletionRequest

__all__ = ["GetSessionDeletionRequestResponse"]


class GetSessionDeletionRequestResponse(BaseModel):
    """
    GetSessionDeletionRequestResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: Literal[True] = Field(validation_alias="success")

    data: SessionDeletionRequest = Field(validation_alias="data")
