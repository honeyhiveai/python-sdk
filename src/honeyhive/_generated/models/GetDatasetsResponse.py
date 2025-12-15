from typing import *

from pydantic import BaseModel, Field


class GetDatasetsResponse(BaseModel):
    """
    GetDatasetsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    # Note: API returns datasets in a field called "datapoints" (confusing naming from backend)
    # We expose this as both 'datapoints' (for backwards compat) and 'datasets' (correct name)
    datapoints: List[Dict[str, Any]] = Field(validation_alias="datapoints")

    @property
    def datasets(self) -> List[Dict[str, Any]]:
        """Alias for datapoints field - returns the list of datasets."""
        return self.datapoints
