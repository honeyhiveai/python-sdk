"""Code generated by Speakeasy (https://speakeasyapi.dev). DO NOT EDIT."""

from __future__ import annotations
import dataclasses
import requests as requests_http
from ...models.components import evaluationupdaterequest as components_evaluationupdaterequest
from ...models.components import updateresponse as components_updateresponse
from typing import Optional


@dataclasses.dataclass
class PutEvaluationsIDRequest:
    id: str = dataclasses.field(metadata={'path_param': { 'field_name': 'id', 'style': 'simple', 'explode': False }})
    evaluation_update_request: Optional[components_evaluationupdaterequest.EvaluationUpdateRequest] = dataclasses.field(default=None, metadata={'request': { 'media_type': 'application/json' }})
    



@dataclasses.dataclass
class PutEvaluationsIDResponse:
    content_type: str = dataclasses.field()
    r"""HTTP response content type for this operation"""
    raw_response: requests_http.Response = dataclasses.field()
    r"""Raw HTTP response; suitable for custom response parsing"""
    status_code: int = dataclasses.field()
    r"""HTTP response status code for this operation"""
    update_response: Optional[components_updateresponse.UpdateResponse] = dataclasses.field(default=None)
    r"""OK"""
    

