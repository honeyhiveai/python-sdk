"""Tracing-related models for HoneyHive SDK.

This module contains models used for tracing functionality that are
separated from the main tracer implementation to avoid cyclic imports.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class TracingParams(BaseModel):
    """Model for tracing decorator parameters using existing Pydantic models.

    This model is separated from the tracer implementation to avoid
    cyclic imports between the models and tracer modules.
    """

    event_type: Optional[str] = None
    event_name: Optional[str] = None
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    feedback: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    event_id: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
