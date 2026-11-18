from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["EvaluatorLLMExecution"]


class EvaluatorLLMExecution(BaseModel):
    """
    EvaluatorLLMExecution model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    system_prompt: str = Field(validation_alias="system_prompt")
