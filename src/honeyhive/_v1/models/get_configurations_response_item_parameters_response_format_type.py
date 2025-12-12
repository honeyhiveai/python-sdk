from enum import Enum


class GetConfigurationsResponseItemParametersResponseFormatType(str, Enum):
    JSON_OBJECT = "json_object"
    TEXT = "text"

    def __str__(self) -> str:
        return str(self.value)
