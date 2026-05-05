from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["LegacyGetExperimentRunCompareParams"]


class LegacyGetExperimentRunCompareParams(BaseModel):
    """
    LegacyGetExperimentRunCompareParams model
        Path parameters for GET /runs/{new_run_id}/compare-with/{old_run_id} (deprecated — use GET /runs/{new_run_id}/compare/{old_run_id})
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    new_run_id: str = Field(validation_alias="new_run_id")

    old_run_id: str = Field(validation_alias="old_run_id")
