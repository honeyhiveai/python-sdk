from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartResultTableDataRowsItem import ChartResultTableDataRowsItem

__all__ = ["ChartResultTableData"]


class ChartResultTableData(BaseModel):
    """
    ChartResultTableData model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    rows: List[ChartResultTableDataRowsItem] = Field(validation_alias="rows")
