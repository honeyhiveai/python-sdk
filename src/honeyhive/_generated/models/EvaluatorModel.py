from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["EvaluatorModel"]


class EvaluatorModel(BaseModel):
    """
    EvaluatorModel model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    model_provider: str = Field(validation_alias="model_provider")

    model_name: str = Field(validation_alias="model_name")
