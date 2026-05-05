from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["DateRange"]


class DateRange(BaseModel):
    """
    DateRange model
        Date range filter
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }
