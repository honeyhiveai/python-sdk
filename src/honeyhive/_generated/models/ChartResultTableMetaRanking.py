from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartResultTableMetaRanking"]


class ChartResultTableMetaRanking(BaseModel):
    """
    ChartResultTableMetaRanking model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    limit: float = Field(validation_alias="limit")

    total_categories: float = Field(validation_alias="total_categories")
