from enum import Enum


class UpdateConfigurationRequestParametersCallType(str, Enum):
    CHAT = "chat"
    COMPLETION = "completion"

    def __str__(self) -> str:
        return str(self.value)
