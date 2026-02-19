from typing import *

from pydantic import BaseModel, Field


class DeleteRunResponse(BaseModel):
    """
    DeleteRunResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    deleted: Optional[bool] = Field(validation_alias="deleted", default=None)
