from enum import Enum


class GetMetricsResponseItemFiltersFilterArrayItemType(str, Enum):
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    NUMBER = "number"
    STRING = "string"

    def __str__(self) -> str:
        return str(self.value)
