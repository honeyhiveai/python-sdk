from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .EvaluatorMetadata import EvaluatorMetadata
from .EvaluatorTestCriteria import EvaluatorTestCriteria
from .ScoreSchema import ScoreSchema

__all__ = ["HumanEvaluatorConfig"]


class HumanEvaluatorConfig(BaseModel):
    """
    HumanEvaluatorConfig model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    metadata: EvaluatorMetadata = Field(validation_alias="metadata")

    score_schema: ScoreSchema = Field(validation_alias="score_schema")

    test_criteria: Optional[EvaluatorTestCriteria] = Field(
        validation_alias="test_criteria", default=None
    )
