from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .AbsoluteDateRange import AbsoluteDateRange

__all__ = ["GetRunsSchemaQuery"]


class GetRunsSchemaQuery(BaseModel):
    """
    GetRunsSchemaQuery model
        Query parameters for GET /runs/schema
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
