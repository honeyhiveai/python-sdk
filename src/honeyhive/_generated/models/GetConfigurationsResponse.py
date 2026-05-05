from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .ConfigurationItem import ConfigurationItem

__all__ = ["GetConfigurationsResponse"]


class GetConfigurationsResponse(BaseModel):
    """
    GetConfigurationsResponse model
        Response for GET /configurations
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    configurations: List[ConfigurationItem] = Field(validation_alias="configurations")
