from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ExperimentSchemaMappingEntry"]


class ExperimentSchemaMappingEntry(BaseModel):
    """
    ExperimentSchemaMappingEntry model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    field_name: str = Field(validation_alias="field_name")

    event_type: str = Field(validation_alias="event_type")
