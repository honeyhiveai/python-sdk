from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["PostSessionRequestFeedback"]


class PostSessionRequestFeedback(BaseModel):
    """
    PostSessionRequestFeedback model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    ground_truth: Optional[Any] = Field(validation_alias="ground_truth", default=None)
