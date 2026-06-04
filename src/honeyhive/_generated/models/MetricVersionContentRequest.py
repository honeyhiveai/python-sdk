from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .MetricVersionContentRequestFilters import MetricVersionContentRequestFilters

__all__ = ["MetricVersionContentRequest"]


class MetricVersionContentRequest(BaseModel):
    """
        MetricVersionContentRequest model
            Metric definition snapshot accepted by POST /v1/metrics/{metric_id}/versions.
    Six fields are optional and fall back to server-side defaults when omitted:
    - `description` → `&#34;&#34;`
    - `return_type` → `&#34;float&#34;`
    - `enabled_in_prod` → `true` for HUMAN metrics, `false` otherwise
    - `needs_ground_truth` → `false`
    - `sampling_percentage` → `10`
    - `filters` → `{ &#34;filterArray&#34;: [] }`
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    type: str = Field(validation_alias="type")

    criteria: str = Field(validation_alias="criteria")

    description: Optional[str] = Field(validation_alias="description", default=None)

    return_type: Optional[str] = Field(validation_alias="return_type", default=None)

    enabled_in_prod: Optional[bool] = Field(
        validation_alias="enabled_in_prod", default=None
    )

    needs_ground_truth: Optional[bool] = Field(
        validation_alias="needs_ground_truth", default=None
    )

    sampling_percentage: Optional[float] = Field(
        validation_alias="sampling_percentage", default=None
    )

    model_provider: Optional[str] = Field(
        validation_alias="model_provider", default=None
    )

    model_name: Optional[str] = Field(validation_alias="model_name", default=None)

    scale: Optional[int] = Field(validation_alias="scale", default=None)

    threshold: Optional[Dict[str, Any]] = Field(
        validation_alias="threshold", default=None
    )

    categories: Optional[List[Any]] = Field(validation_alias="categories", default=None)

    child_metrics: Optional[List[Any]] = Field(
        validation_alias="child_metrics", default=None
    )

    filters: Optional[MetricVersionContentRequestFilters] = Field(
        validation_alias="filters", default=None
    )
