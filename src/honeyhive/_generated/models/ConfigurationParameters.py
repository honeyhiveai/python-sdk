from typing import *

from pydantic import BaseModel, Field

from .ResponseFormat import ResponseFormat
from .SelectedFunction import SelectedFunction
from .TemplateItem import TemplateItem


class ConfigurationParameters(BaseModel):
    """
    ConfigurationParameters model
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    call_type: str = Field(validation_alias="call_type")

    model: str = Field(validation_alias="model")

    hyperparameters: Optional[Dict[str, Any]] = Field(validation_alias="hyperparameters", default=None)

    responseFormat: Optional[ResponseFormat] = Field(validation_alias="responseFormat", default=None)

    selectedFunctions: Optional[List[Optional[SelectedFunction]]] = Field(
        validation_alias="selectedFunctions", default=None
    )

    functionCallParams: Optional[str] = Field(validation_alias="functionCallParams", default=None)

    forceFunction: Optional[Dict[str, Any]] = Field(validation_alias="forceFunction", default=None)

    template: Optional[Union[List[TemplateItem], str]] = Field(validation_alias="template", default=None)
