from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartQueryProductFilters"]


class ChartQueryProductFilters(BaseModel):
    """
    ChartQueryProductFilters model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    experiment_run_id: Optional[str] = Field(
        validation_alias="experiment_run_id", default=None
    )

    only_experiments: Optional[bool] = Field(
        validation_alias="only_experiments", default=None
    )
