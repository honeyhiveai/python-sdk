from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .LLMEvaluatorConfig import LLMEvaluatorConfig

__all__ = ["LLMEvaluatorDefinition"]


class LLMEvaluatorDefinition(BaseModel):
    """
    LLMEvaluatorDefinition model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    type: Literal["llm"] = Field(validation_alias="type")

    llm: LLMEvaluatorConfig = Field(validation_alias="llm")
