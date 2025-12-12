from enum import Enum


class UpdateConfigurationRequestType(str, Enum):
    LLM = "LLM"
    PIPELINE = "pipeline"

    def __str__(self) -> str:
        return str(self.value)
