from enum import Enum


class UpdateMetricRequestFiltersFilterArrayItemOperatorType2(str, Enum):
    EXISTS = "exists"
    IS = "is"
    NOT_EXISTS = "not exists"

    def __str__(self) -> str:
        return str(self.value)
