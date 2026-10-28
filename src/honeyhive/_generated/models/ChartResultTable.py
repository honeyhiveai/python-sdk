from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultMeasure import ChartResultMeasure
from .ChartResultTableData import ChartResultTableData
from .ChartResultTableMeta import ChartResultTableMeta

__all__ = ["ChartResultTable"]


class ChartResultTable(BaseModel):
    """
    ChartResultTable model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    meta: ChartResultTableMeta = Field(validation_alias="meta")

    measures: List[ChartResultMeasure] = Field(validation_alias="measures")

    data: ChartResultTableData = Field(validation_alias="data")
