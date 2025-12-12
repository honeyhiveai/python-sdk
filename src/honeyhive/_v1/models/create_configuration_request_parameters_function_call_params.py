from enum import Enum


class CreateConfigurationRequestParametersFunctionCallParams(str, Enum):
    AUTO = "auto"
    FORCE = "force"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
