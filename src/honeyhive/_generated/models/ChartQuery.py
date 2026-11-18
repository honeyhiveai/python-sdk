from typing import Annotated, TypeAlias, Union

from pydantic import Field

from .ChartQueryCategorical import ChartQueryCategorical
from .ChartQueryHistogram import ChartQueryHistogram
from .ChartQueryScalar import ChartQueryScalar
from .ChartQueryScatter import ChartQueryScatter
from .ChartQueryTable import ChartQueryTable
from .ChartQueryTimeSeries import ChartQueryTimeSeries

__all__ = ["ChartQuery"]

ChartQuery: TypeAlias = Annotated[
    Union[
        ChartQueryTimeSeries,
        ChartQueryCategorical,
        ChartQueryScalar,
        ChartQueryHistogram,
        ChartQueryTable,
        ChartQueryScatter,
    ],
    Field(discriminator="kind"),
]
