from enum import Enum


class CreateConfigurationRequestType(str, Enum):
    LLM = "LLM"
    PIPELINE = "pipeline"

    def __str__(self) -> str:
        return str(self.value)
