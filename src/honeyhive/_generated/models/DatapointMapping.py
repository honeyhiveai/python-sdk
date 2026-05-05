from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DatapointMapping"]


class DatapointMapping(BaseModel):
    """
    DatapointMapping model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    inputs: Optional[List[str]] = Field(validation_alias="inputs", default=None)

    history: Optional[List[str]] = Field(validation_alias="history", default=None)

    ground_truth: Optional[List[str]] = Field(
        validation_alias="ground_truth", default=None
    )
