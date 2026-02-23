from typing import *

from pydantic import BaseModel, Field


class TemplateItem(BaseModel):
    """
    TemplateItem model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    role: str = Field(validation_alias="role")

    content: str = Field(validation_alias="content")
