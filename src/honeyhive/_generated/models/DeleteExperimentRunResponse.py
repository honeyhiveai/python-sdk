from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DeleteExperimentRunResponse"]


class DeleteExperimentRunResponse(BaseModel):
    """
    DeleteExperimentRunResponse model
        Response for DELETE /runs/{run_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: str = Field(validation_alias="id")

    deleted: bool = Field(validation_alias="deleted")
