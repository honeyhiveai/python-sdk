from enum import Enum


class GetMetricsResponseItemFiltersFilterArrayItemOperatorType0(str, Enum):
    CONTAINS = "contains"
    EXISTS = "exists"
    IS = "is"
    IS_NOT = "is not"
    NOT_CONTAINS = "not contains"
    NOT_EXISTS = "not exists"

    def __str__(self) -> str:
        return str(self.value)
