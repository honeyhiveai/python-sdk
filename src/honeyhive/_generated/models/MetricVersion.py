from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .MetricVersionContent import MetricVersionContent

__all__ = ["MetricVersion"]


class MetricVersion(BaseModel):
    """
    MetricVersion model
        A versioned snapshot of a metric definition.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    full_sha: str = Field(validation_alias="full_sha")

    message: str = Field(validation_alias="message")

    date: str = Field(validation_alias="date")

    deployed: bool = Field(validation_alias="deployed")

    content: MetricVersionContent = Field(validation_alias="content")
