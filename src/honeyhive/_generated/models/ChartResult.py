from typing import Annotated, TypeAlias, Union

from pydantic import Field

from .ChartResultCategorical import ChartResultCategorical
from .ChartResultHistogram import ChartResultHistogram
from .ChartResultScalar import ChartResultScalar
from .ChartResultScatter import ChartResultScatter
from .ChartResultTable import ChartResultTable
from .ChartResultTimeSeries import ChartResultTimeSeries

__all__ = ["ChartResult"]

ChartResult: TypeAlias = Annotated[
    Union[
        ChartResultTimeSeries,
        ChartResultCategorical,
        ChartResultScalar,
        ChartResultHistogram,
        ChartResultTable,
        ChartResultScatter,
    ],
    Field(discriminator="kind"),
]
