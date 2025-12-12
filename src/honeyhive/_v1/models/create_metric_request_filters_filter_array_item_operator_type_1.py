from enum import Enum


class CreateMetricRequestFiltersFilterArrayItemOperatorType1(str, Enum):
    EXISTS = "exists"
    GREATER_THAN = "greater than"
    IS = "is"
    IS_NOT = "is not"
    LESS_THAN = "less than"
    NOT_EXISTS = "not exists"

    def __str__(self) -> str:
        return str(self.value)
