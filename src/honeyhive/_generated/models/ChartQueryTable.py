from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartQueryMeasure import ChartQueryMeasure
from .ChartQueryTableOrderBy import ChartQueryTableOrderBy

__all__ = ["ChartQueryTable"]


class ChartQueryTable(BaseModel):
    """
    ChartQueryTable model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    group_by: List[str] = Field(validation_alias="group_by")

    measures: List[ChartQueryMeasure] = Field(validation_alias="measures")

    order_by: Optional[ChartQueryTableOrderBy] = Field(
        validation_alias="order_by", default=None
    )

    limit: Optional[int] = Field(validation_alias="limit", default=None)
