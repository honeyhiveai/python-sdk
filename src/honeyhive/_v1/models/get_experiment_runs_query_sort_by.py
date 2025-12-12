from enum import Enum


class GetExperimentRunsQuerySortBy(str, Enum):
    CREATED_AT = "created_at"
    NAME = "name"
    STATUS = "status"
    UPDATED_AT = "updated_at"

    def __str__(self) -> str:
        return str(self.value)
