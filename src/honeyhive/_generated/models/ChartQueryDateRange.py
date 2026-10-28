from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartQueryDateRange"]


class ChartQueryDateRange(BaseModel):
    """
    ChartQueryDateRange model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    start_time: str = Field(validation_alias="start_time")

    end_time: str = Field(validation_alias="end_time")

    timezone: Optional[str] = Field(validation_alias="timezone", default=None)
