from enum import Enum


class RunMetricRequestMetricType(str, Enum):
    COMPOSITE = "COMPOSITE"
    HUMAN = "HUMAN"
    LLM = "LLM"
    PYTHON = "PYTHON"

    def __str__(self) -> str:
        return str(self.value)
