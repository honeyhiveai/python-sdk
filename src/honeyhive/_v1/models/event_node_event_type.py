from enum import Enum


class EventNodeEventType(str, Enum):
    CHAIN = "chain"
    MODEL = "model"
    SESSION = "session"
    TOOL = "tool"

    def __str__(self) -> str:
        return str(self.value)
