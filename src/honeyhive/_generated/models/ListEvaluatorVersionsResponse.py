from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .Evaluator import Evaluator
from .Pagination import Pagination

__all__ = ["ListEvaluatorVersionsResponse"]


class ListEvaluatorVersionsResponse(BaseModel):
    """
    ListEvaluatorVersionsResponse model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    success: Literal[True] = Field(validation_alias="success")

    data: List[Evaluator] = Field(validation_alias="data")

    pagination: Pagination = Field(validation_alias="pagination")
