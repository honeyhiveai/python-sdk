from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ChartResultTableDataRowsItem"]


class ChartResultTableDataRowsItem(BaseModel):
    """
    ChartResultTableDataRowsItem model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    key: str = Field(validation_alias="key")

    label: str = Field(validation_alias="label")

    dimensions: Dict[str, Any] = Field(validation_alias="dimensions")

    values: Dict[str, Any] = Field(validation_alias="values")
