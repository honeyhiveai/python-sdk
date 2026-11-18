from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .EvaluatorDefinition import EvaluatorDefinition

__all__ = ["Evaluator"]


class Evaluator(BaseModel):
    """
    Evaluator model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    id: str = Field(validation_alias="id")

    slug: str = Field(validation_alias="slug")

    is_active: bool = Field(validation_alias="is_active")

    latest_version: int = Field(validation_alias="latest_version")

    published_version: Optional[int] = Field(validation_alias="published_version")

    version: int = Field(validation_alias="version")

    definition: EvaluatorDefinition = Field(validation_alias="definition")

    message: str = Field(validation_alias="message")

    evaluator_created_at: str = Field(validation_alias="evaluator_created_at")

    evaluator_updated_at: str = Field(validation_alias="evaluator_updated_at")

    version_created_at: str = Field(validation_alias="version_created_at")
