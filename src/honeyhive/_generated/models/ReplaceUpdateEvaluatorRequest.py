from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .EvaluatorDefinition import EvaluatorDefinition

__all__ = ["ReplaceUpdateEvaluatorRequest"]


class ReplaceUpdateEvaluatorRequest(BaseModel):
    """
    ReplaceUpdateEvaluatorRequest model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    definition: EvaluatorDefinition = Field(validation_alias="definition")

    message: Optional[str] = Field(validation_alias="message", default=None)

    publish: Optional[bool] = Field(validation_alias="publish", default=None)
