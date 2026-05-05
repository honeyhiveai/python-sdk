from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .AbsoluteDateRange import AbsoluteDateRange

__all__ = ["GetEventsSchemaQuery"]


class GetEventsSchemaQuery(BaseModel):
    """
    GetEventsSchemaQuery model
        Query parameters for GET /events/schema
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    dateRange: Optional[Union[str, AbsoluteDateRange]] = Field(
        validation_alias="dateRange", default=None
    )

    evaluation_id: Optional[str] = Field(validation_alias="evaluation_id", default=None)
