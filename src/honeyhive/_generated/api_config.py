import os
from typing import Optional, Union

from pydantic import BaseModel, Field


# Default production URLs
DEFAULT_BASE_URL = "https://api.honeyhive.ai"
DEFAULT_CP_BASE_URL = "https://api.honeyhive.ai"


class APIConfig(BaseModel):
    model_config = {"validate_assignment": True}

    base_path: str = DEFAULT_BASE_URL
    cp_base_path: Optional[str] = DEFAULT_CP_BASE_URL
    verify: Union[bool, str] = True
    access_token: Optional[str] = None

    @classmethod
    def from_env(
        cls,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        cp_base_url: Optional[str] = None,
    ) -> "APIConfig":
        """Create APIConfig from environment variables with overrides.

        Environment variables:
            HH_API_KEY: API key for authentication
            HH_API_URL: Base URL for Data Plane API
            HH_CP_API_URL: Base URL for Control Plane API (defaults to HH_API_URL)

        Args:
            api_key: Override for HH_API_KEY
            base_url: Override for HH_API_URL
            cp_base_url: Override for HH_CP_API_URL
        """
        resolved_api_key = api_key or os.environ.get("HH_API_KEY")
        resolved_base_url = (
            base_url or os.environ.get("HH_API_URL") or DEFAULT_BASE_URL
        )
        resolved_cp_base_url = (
            cp_base_url
            or os.environ.get("HH_CP_API_URL")
            or os.environ.get("HH_API_URL")
            or DEFAULT_CP_BASE_URL
        )

        return cls(
            base_path=resolved_base_url,
            cp_base_path=resolved_cp_base_url,
            access_token=resolved_api_key,
        )

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
