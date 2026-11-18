from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .HumanEvaluatorConfig import HumanEvaluatorConfig

__all__ = ["HumanEvaluatorDefinition"]


class HumanEvaluatorDefinition(BaseModel):
    """
    HumanEvaluatorDefinition model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["human"] = Field(validation_alias="type")

    human: HumanEvaluatorConfig = Field(validation_alias="human")
