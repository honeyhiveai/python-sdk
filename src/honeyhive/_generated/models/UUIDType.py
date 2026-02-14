from typing import *

from pydantic import BaseModel, Field


class UUIDType(BaseModel):
    """
    UUIDType model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}
