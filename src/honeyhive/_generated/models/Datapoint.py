from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["Datapoint"]


class Datapoint(BaseModel):
    """
    Datapoint model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: str = Field(validation_alias="id")

    inputs: Dict[str, Any] = Field(validation_alias="inputs")

    history: List[Dict[str, Any]] = Field(validation_alias="history")

    ground_truth: Optional[Dict[str, Any]] = Field(validation_alias="ground_truth")

    metadata: Optional[Dict[str, Any]] = Field(validation_alias="metadata")

    linked_event: Union[str, None] = Field(validation_alias="linked_event")

    created_at: str = Field(validation_alias="created_at")

    updated_at: Optional[str] = Field(validation_alias="updated_at", default=None)

    linked_datasets: Optional[List[str]] = Field(
        validation_alias="linked_datasets", default=None
    )
