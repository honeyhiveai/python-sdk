from typing import *

from pydantic import BaseModel, Field


class InsertResult(BaseModel):
    """
    InsertResult model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    insertedId: Optional[str] = Field(validation_alias="insertedId", default=None)
