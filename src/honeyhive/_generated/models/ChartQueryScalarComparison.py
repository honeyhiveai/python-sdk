from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartQueryScalarComparison"]


class ChartQueryScalarComparison(BaseModel):
    """
    ChartQueryScalarComparison model
        Delta baseline; default none
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    mode: str = Field(validation_alias="mode")
