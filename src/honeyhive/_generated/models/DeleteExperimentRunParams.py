from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DeleteExperimentRunParams"]


class DeleteExperimentRunParams(BaseModel):
    """
    DeleteExperimentRunParams model
        Path parameters for DELETE /runs/{run_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    run_id: str = Field(validation_alias="run_id")
