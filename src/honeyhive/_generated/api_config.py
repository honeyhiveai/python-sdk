from typing import Optional, Union

from pydantic import BaseModel, Field


class APIConfig(BaseModel):
    model_config = {"validate_assignment": True}

    base_path: str = "https://api.honeyhive.ai"
    cp_base_path: Optional[str] = None  # Control Plane URL for query endpoints
    verify: Union[bool, str] = True
    access_token: Optional[str] = None

    def get_access_token(self) -> Optional[str]:
        return self.access_token

    def set_access_token(self, value: str):
        self.access_token = value

    def get_cp_base_path(self) -> str:
        """Get Control Plane base path, defaults to base_path if not set."""
        return self.cp_base_path or self.base_path


class HTTPException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"{status_code} {message}")

    def __str__(self):
        return f"{self.status_code} {self.message}"
