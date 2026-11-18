from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .EvaluatorFiltersArray import EvaluatorFiltersArray

__all__ = ["EvaluatorFilters"]


class EvaluatorFilters(BaseModel):
    """
    EvaluatorFilters model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    filterArray: EvaluatorFiltersArray = Field(validation_alias="filterArray")
