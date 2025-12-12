from enum import Enum


class UpdateConfigurationRequestParametersResponseFormatType(str, Enum):
    JSON_OBJECT = "json_object"
    TEXT = "text"

    def __str__(self) -> str:
        return str(self.value)
