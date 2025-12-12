from enum import Enum


class GetConfigurationsResponseItemType(str, Enum):
    LLM = "LLM"
    PIPELINE = "pipeline"

    def __str__(self) -> str:
        return str(self.value)
