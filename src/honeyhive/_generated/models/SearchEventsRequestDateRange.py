from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["SearchEventsRequestDateRange"]


class SearchEventsRequestDateRange(BaseModel):
    """
    SearchEventsRequestDateRange model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    start_time: str = Field(validation_alias="start_time")

    end_time: str = Field(validation_alias="end_time")
