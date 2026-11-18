from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .EvaluatorDefinition import EvaluatorDefinition

__all__ = ["CreateEvaluatorRequest"]


class CreateEvaluatorRequest(BaseModel):
    """
    CreateEvaluatorRequest model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    slug: str = Field(validation_alias="slug")

    definition: EvaluatorDefinition = Field(validation_alias="definition")

    message: Optional[str] = Field(validation_alias="message", default=None)

    publish: Optional[bool] = Field(validation_alias="publish", default=None)
