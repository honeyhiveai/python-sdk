from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartResultTimeSeriesMetaEffectiveBucket"]


class ChartResultTimeSeriesMetaEffectiveBucket(BaseModel):
    """
    ChartResultTimeSeriesMetaEffectiveBucket model
        What the server resolved; the UI cannot label the x-axis without it
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    interval: str = Field(validation_alias="interval")

    fill: str = Field(validation_alias="fill")
