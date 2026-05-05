from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["LegacyExportEventsRequestDateRange"]


class LegacyExportEventsRequestDateRange(BaseModel):
    """
    LegacyExportEventsRequestDateRange model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    gte: str = Field(validation_alias="$gte")

    lte: str = Field(validation_alias="$lte")
