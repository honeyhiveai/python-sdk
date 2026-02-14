from typing import *

from pydantic import BaseModel, Field

from .Dataset import Dataset


class GetDatasetsResponse(BaseModel):
    """
    GetDatasetsResponse model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    testcases: Optional[List[Optional[Dataset]]] = Field(
        validation_alias="testcases", default=None
    )
