from enum import Enum


class CreateMetricRequestFiltersFilterArrayItemOperatorType3(str, Enum):
    AFTER = "after"
    BEFORE = "before"
    EXISTS = "exists"
    IS = "is"
    IS_NOT = "is not"
    NOT_EXISTS = "not exists"

    def __str__(self) -> str:
        return str(self.value)
