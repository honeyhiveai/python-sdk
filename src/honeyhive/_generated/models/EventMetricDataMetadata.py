from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["EventMetricDataMetadata"]


class EventMetricDataMetadata(BaseModel):
    """
    EventMetricDataMetadata model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    datapoint_id: Optional[str] = Field(validation_alias="datapoint_id", default=None)
