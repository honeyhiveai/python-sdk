from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartQueryBucket"]


class ChartQueryBucket(BaseModel):
    """
    ChartQueryBucket model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    interval: Optional[str] = Field(validation_alias="interval", default=None)

    max_points: Optional[int] = Field(validation_alias="max_points", default=None)
