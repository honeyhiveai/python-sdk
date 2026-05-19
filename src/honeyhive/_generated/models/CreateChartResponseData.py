from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["CreateChartResponseData"]


class CreateChartResponseData(BaseModel):
    """
    CreateChartResponseData model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: str = Field(validation_alias="id")

    name: str = Field(validation_alias="name")

    description: Optional[str] = Field(validation_alias="description")

    metric: str = Field(validation_alias="metric")

    func: Optional[str] = Field(validation_alias="func")

    groupBy: Optional[str] = Field(validation_alias="groupBy")

    bucketing: str = Field(validation_alias="bucketing")

    dateRange: Optional[Dict[str, Any]] = Field(validation_alias="dateRange")

    query: Optional[List[Any]] = Field(validation_alias="query")

    owner_id: Optional[str] = Field(validation_alias="owner_id")

    owner_profile: Optional[Dict[str, Any]] = Field(
        validation_alias="owner_profile", default=None
    )

    is_active: bool = Field(validation_alias="is_active")

    created_at: Union[str, str] = Field(validation_alias="created_at")

    updated_at: Union[str, str, None] = Field(validation_alias="updated_at")
