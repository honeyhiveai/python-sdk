from enum import Enum


class GetConfigurationsResponseItemParametersFunctionCallParams(str, Enum):
    AUTO = "auto"
    FORCE = "force"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
