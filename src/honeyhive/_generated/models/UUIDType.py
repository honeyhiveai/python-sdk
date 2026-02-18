from typing import *

from pydantic import BaseModel, Field, model_serializer, model_validator


class UUIDType(BaseModel):
    """
    UUIDType model - represents a UUID that may come as a plain string from the backend.
    Serializes back to a plain string so API requests send strings, not objects.
    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    value: Optional[str] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def _accept_string(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"value": data}
        return data

    @model_serializer
    def _serialize_as_string(self) -> Optional[str]:
        """Serialize as a plain string so API requests send UUID strings, not objects."""
        return self.value

    def __str__(self) -> str:
        return self.value or ""

    def __repr__(self) -> str:
        return f"UUIDType(value={self.value!r})"
