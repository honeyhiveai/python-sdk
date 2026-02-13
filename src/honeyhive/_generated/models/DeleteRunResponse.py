from typing import *

from pydantic import BaseModel, Field

from .UUIDType import UUIDType


class DeleteRunResponse(BaseModel):
    """
    DeleteRunResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[UUIDType] = Field(validation_alias="id", default=None)

    deleted: Optional[bool] = Field(validation_alias="deleted", default=None)
