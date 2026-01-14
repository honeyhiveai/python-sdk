from typing import *

from pydantic import BaseModel, Field


class TODOSchema(BaseModel):
    """
    TODOSchema model
        TODO: This is a placeholder schema. Proper Zod schemas need to be created in @hive-kube/core-ts for: Sessions, Events, Projects, and Experiment comparison/result endpoints.
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    message: str = Field(validation_alias="message")
