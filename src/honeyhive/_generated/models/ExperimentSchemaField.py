from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ExperimentSchemaField"]


class ExperimentSchemaField(BaseModel):
    """
    ExperimentSchemaField model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    event_type: str = Field(validation_alias="event_type")
