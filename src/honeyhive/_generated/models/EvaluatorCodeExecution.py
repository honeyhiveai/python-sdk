from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["EvaluatorCodeExecution"]


class EvaluatorCodeExecution(BaseModel):
    """
    EvaluatorCodeExecution model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    code_snippet: str = Field(validation_alias="code_snippet")
