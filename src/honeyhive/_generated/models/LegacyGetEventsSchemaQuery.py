from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .AbsoluteDateRange import AbsoluteDateRange

__all__ = ["LegacyGetEventsSchemaQuery"]


class LegacyGetEventsSchemaQuery(BaseModel):
    """
    LegacyGetEventsSchemaQuery model
        Query parameters for GET /events/schema (deprecated — use GET /runs/{run_id}/schema or GET /runs/schema)
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
