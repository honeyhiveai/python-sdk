from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .Evaluator import Evaluator

__all__ = ["DeleteEvaluatorResponse"]


class DeleteEvaluatorResponse(BaseModel):
    """
    DeleteEvaluatorResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: Literal[True] = Field(validation_alias="success")

    data: Evaluator = Field(validation_alias="data")
