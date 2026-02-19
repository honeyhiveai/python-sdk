from typing import *

from ..api_config import APIConfig, HTTPException, _make_request
from ..models import *


def getProjects(
    api_config_override: Optional[APIConfig] = None, *, name: Optional[str] = None
) -> List[Project]:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/projects"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"name": name}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(api_config, "get", path, headers, params=query_params)

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"getProjects failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return [Project(**item) for item in body]


def createProject(
    api_config_override: Optional[APIConfig] = None, *, data: CreateProjectRequest
) -> Project:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/projects"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(
        api_config,
        "post",
        path,
        headers,
        params=query_params,
        json=data.model_dump(exclude_none=True),
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"createProject failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return Project(**body) if body is not None else Project()


def updateProject(
    api_config_override: Optional[APIConfig] = None, *, data: UpdateProjectRequest
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/projects"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(
        api_config,
        "put",
        path,
        headers,
        params=query_params,
        json=data.model_dump(exclude_none=True),
    )

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"updateProject failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None


def deleteProject(
    api_config_override: Optional[APIConfig] = None, *, name: str
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    path = f"/projects"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"name": name}

    query_params = {
        key: value for (key, value) in query_params.items() if value is not None
    }

    response = _make_request(api_config, "delete", path, headers, params=query_params)

    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"deleteProject failed with status code: {response.status_code}. Response: {response.text[:500]}",
        )
    else:
        body = None if 200 == 204 else response.json()

    return None
