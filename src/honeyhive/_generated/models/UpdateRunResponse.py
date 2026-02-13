from typing import *

from pydantic import BaseModel, Field


class UpdateRunResponse(BaseModel):
    """
    UpdateRunResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    evaluation: Optional[Dict[str, Any]] = Field(
        validation_alias="evaluation", default=None
    )

    warning: Optional[str] = Field(validation_alias="warning", default=None)
