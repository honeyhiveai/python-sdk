from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ExperimentRunObject import ExperimentRunObject

__all__ = ["GetExperimentRunResponse"]


class GetExperimentRunResponse(BaseModel):
    """
    GetExperimentRunResponse model
        Response for GET /runs/{run_id}
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    evaluation: ExperimentRunObject = Field(validation_alias="evaluation")
