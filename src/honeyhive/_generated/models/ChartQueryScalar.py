from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ChartQueryMeasure import ChartQueryMeasure
from .ChartQueryScalarComparison import ChartQueryScalarComparison
from .ChartQueryScalarSparkline import ChartQueryScalarSparkline

__all__ = ["ChartQueryScalar"]


class ChartQueryScalar(BaseModel):
    """
    ChartQueryScalar model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    kind: str = Field(validation_alias="kind")

    measure: ChartQueryMeasure = Field(validation_alias="measure")

    comparison: Optional[ChartQueryScalarComparison] = Field(
        validation_alias="comparison", default=None
    )

    sparkline: Optional[ChartQueryScalarSparkline] = Field(
        validation_alias="sparkline", default=None
    )
