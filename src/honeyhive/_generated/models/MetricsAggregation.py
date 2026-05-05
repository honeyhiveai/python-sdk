from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .MetricDetail import MetricDetail

__all__ = ["MetricsAggregation"]


class MetricsAggregation(BaseModel):
    """
    MetricsAggregation model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    aggregation_function: Optional[str] = Field(
        validation_alias="aggregation_function", default=None
    )

    details: Optional[List[Optional[MetricDetail]]] = Field(
        validation_alias="details", default=None
    )
