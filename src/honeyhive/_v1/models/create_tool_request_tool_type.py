from enum import Enum


class CreateToolRequestToolType(str, Enum):
    FUNCTION = "function"
    TOOL = "tool"

    def __str__(self) -> str:
        return str(self.value)
