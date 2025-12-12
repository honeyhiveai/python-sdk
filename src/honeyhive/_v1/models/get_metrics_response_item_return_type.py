from enum import Enum


class GetMetricsResponseItemReturnType(str, Enum):
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"
    FLOAT = "float"
    STRING = "string"

    def __str__(self) -> str:
        return str(self.value)
