from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["EvaluatorSampling"]


class EvaluatorSampling(BaseModel):
    """
    EvaluatorSampling model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    sampling_percentage: float = Field(validation_alias="sampling_percentage")
