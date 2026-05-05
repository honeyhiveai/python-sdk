from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ExperimentSchemaField import ExperimentSchemaField

__all__ = ["GetEventsSchemaResponse"]


class GetEventsSchemaResponse(BaseModel):
    """
    GetEventsSchemaResponse model
        Response for GET /events/schema
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    fields: List[ExperimentSchemaField] = Field(validation_alias="fields")

    datasets: List[str] = Field(validation_alias="datasets")

    mappings: Dict[str, Any] = Field(validation_alias="mappings")
