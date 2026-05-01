from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["GetExperimentRunParams"]


class GetExperimentRunParams(BaseModel):
    """
    GetExperimentRunParams model
        Path parameters for GET /runs/{run_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    run_id: str = Field(validation_alias="run_id")
