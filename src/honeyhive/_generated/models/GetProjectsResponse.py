from typing import *

from pydantic import BaseModel, Field


class GetProjectsResponse(BaseModel):
    """
    GetProjectsResponse model
        Array of projects
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}
