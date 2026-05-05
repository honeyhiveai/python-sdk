from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["Pagination"]


class Pagination(BaseModel):
    """
    Pagination model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    page: int = Field(validation_alias="page")

    limit: int = Field(validation_alias="limit")

    total: int = Field(validation_alias="total")

    total_unfiltered: int = Field(validation_alias="total_unfiltered")

    total_pages: int = Field(validation_alias="total_pages")

    has_next: bool = Field(validation_alias="has_next")

    has_prev: bool = Field(validation_alias="has_prev")
