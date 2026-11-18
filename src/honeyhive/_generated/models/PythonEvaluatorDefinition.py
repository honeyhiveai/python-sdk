from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .PythonEvaluatorConfig import PythonEvaluatorConfig

__all__ = ["PythonEvaluatorDefinition"]


class PythonEvaluatorDefinition(BaseModel):
    """
    PythonEvaluatorDefinition model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["python"] = Field(validation_alias="type")

    python: PythonEvaluatorConfig = Field(validation_alias="python")
