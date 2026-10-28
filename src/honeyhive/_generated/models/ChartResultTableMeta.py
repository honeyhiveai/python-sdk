from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultTableMetaRanking import ChartResultTableMetaRanking
from .ChartResultWarning import ChartResultWarning

__all__ = ["ChartResultTableMeta"]


class ChartResultTableMeta(BaseModel):
    """
    ChartResultTableMeta model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    matched_event_count: float = Field(validation_alias="matched_event_count")

    warnings: List[ChartResultWarning] = Field(validation_alias="warnings")

    ranking: ChartResultTableMetaRanking = Field(validation_alias="ranking")
