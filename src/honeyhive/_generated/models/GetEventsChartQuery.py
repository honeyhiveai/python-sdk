from typing import *

from pydantic import BaseModel, Field

from .DateRange import DateRange
from .FiltersArray import FiltersArray


class GetEventsChartQuery(BaseModel):
    """
    GetEventsChartQuery model
        Query parameters for GET /events/chart
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    dateRange: Optional[DateRange] = Field(validation_alias="dateRange", default=None)

    filters: Optional[FiltersArray] = Field(validation_alias="filters", default=None)

    metric: Optional[str] = Field(validation_alias="metric", default=None)

    groupBy: Optional[str] = Field(validation_alias="groupBy", default=None)

    bucket: Optional[str] = Field(validation_alias="bucket", default=None)

    aggregation: Optional[str] = Field(validation_alias="aggregation", default=None)

    evaluation_id: Optional[str] = Field(validation_alias="evaluation_id", default=None)

    only_experiments: Optional[bool] = Field(validation_alias="only_experiments", default=None)
