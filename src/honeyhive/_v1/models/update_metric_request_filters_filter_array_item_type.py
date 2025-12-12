from enum import Enum


class UpdateMetricRequestFiltersFilterArrayItemType(str, Enum):
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    NUMBER = "number"
    STRING = "string"

    def __str__(self) -> str:
        return str(self.value)
