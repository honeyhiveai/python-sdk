"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import configuration as components_configuration
from enum import Enum
from typing import List, Optional

class Env(str, Enum):
    r"""Environment - \\"dev\\", \\"staging\\" or \\"prod\\" """
    DEV = 'dev'
    STAGING = 'staging'
    PROD = 'prod'


@dataclasses.dataclass
class GetConfigurationsRequest:
    project: str = dataclasses.field(metadata={'query_param': { 'field_name': 'project', 'style': 'form', 'explode': True }})
    r"""Project name for configuration like `Example Project`"""
    env: Optional[Env] = dataclasses.field(default=None, metadata={'query_param': { 'field_name': 'env', 'style': 'form', 'explode': True }})
    r"""Environment - \\"dev\\", \\"staging\\" or \\"prod\\" """
    name: Optional[str] = dataclasses.field(default=None, metadata={'query_param': { 'field_name': 'name', 'style': 'form', 'explode': True }})
    r"""The name of the configuration like `v0`"""
    



@dataclasses.dataclass
class GetConfigurationsResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    configurations: Optional[List[components_configuration.Configuration]] = dataclasses.field(default=None)
    r"""An array of configurations"""
    

