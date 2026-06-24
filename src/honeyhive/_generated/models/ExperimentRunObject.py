from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ExperimentRunObject"]


class ExperimentRunObject(BaseModel):
    """
    ExperimentRunObject model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: str = Field(validation_alias="id")

    run_id: str = Field(validation_alias="run_id")

    name: Optional[str] = Field(validation_alias="name", default=None)

    description: Optional[str] = Field(validation_alias="description", default=None)

    status: Optional[str] = Field(validation_alias="status", default=None)

    metadata: Dict[str, Any] = Field(validation_alias="metadata")

    results: Dict[str, Any] = Field(validation_alias="results")

    metrics: Optional[Dict[str, Any]] = Field(validation_alias="metrics", default=None)

    event_ids: List[str] = Field(validation_alias="event_ids")

    configuration: Dict[str, Any] = Field(validation_alias="configuration")

    is_active: bool = Field(validation_alias="is_active")

    created_at: Union[str, str] = Field(validation_alias="created_at")

    updated_at: Optional[Union[str, str, None]] = Field(
        validation_alias="updated_at", default=None
    )

    scope_type: str = Field(validation_alias="scope_type")

    scope_id: str = Field(validation_alias="scope_id")

    dataset_id: Optional[str] = Field(validation_alias="dataset_id", default=None)

    dataset_name: Optional[str] = Field(validation_alias="dataset_name", default=None)
