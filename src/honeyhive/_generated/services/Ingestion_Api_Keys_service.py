from typing import *

import httpx

from ..api_config import (
    APIConfig,
    HTTPException,
    _raise_http_exception,
    _serialize_query_params,
)
from ..models import *


def createIngestionApiKey(
    api_config_override: Optional[APIConfig] = None,
    *,
    project_id: str,
    data: CreateIngestionApiKeyRequest,
) -> CreateIngestionApiKeyResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/v1/projects/{project_id}/ingestion_api_keys"
    headers = api_config.get_default_headers()
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    with httpx.Client(
        base_url=base_path, verify=api_config.verify, timeout=api_config.timeout
    ) as client:
        response = client.request(
            "post",
            httpx.URL(path),
            headers=headers,
            params=_serialize_query_params(query_params),
            json=data.model_dump(exclude_none=True),
        )

    if response.status_code != 200:
        _raise_http_exception("createIngestionApiKey", response)
    else:
        body = None if 200 == 204 else response.json()

    return (
        CreateIngestionApiKeyResponse(**body)
        if body is not None
        else CreateIngestionApiKeyResponse()
    )
