from enum import Enum


class UpdateToolRequestToolType(str, Enum):
    FUNCTION = "function"
    TOOL = "tool"

    def __str__(self) -> str:
        return str(self.value)
