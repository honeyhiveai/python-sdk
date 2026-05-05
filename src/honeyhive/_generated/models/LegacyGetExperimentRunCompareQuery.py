from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["LegacyGetExperimentRunCompareQuery"]


class LegacyGetExperimentRunCompareQuery(BaseModel):
    """
    LegacyGetExperimentRunCompareQuery model
        Query parameters for GET /runs/{new_run_id}/compare-with/{old_run_id} (deprecated — use GET /runs/{new_run_id}/compare/{old_run_id})
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    aggregate_function: Optional[str] = Field(
        validation_alias="aggregate_function", default=None
    )

    filters: Optional[Union[str, List[Any]]] = Field(
        validation_alias="filters", default=None
    )
