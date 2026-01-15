from typing import *

from pydantic import BaseModel, Field


class CheckState(BaseModel):
    """
    CheckState model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}
