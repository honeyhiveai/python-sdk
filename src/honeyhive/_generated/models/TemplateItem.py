from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["TemplateItem"]


class TemplateItem(BaseModel):
    """
    TemplateItem model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    role: str = Field(validation_alias="role")

    content: str = Field(validation_alias="content")
