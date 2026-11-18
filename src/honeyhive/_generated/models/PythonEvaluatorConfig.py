from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .EvaluatorCodeExecution import EvaluatorCodeExecution
from .EvaluatorFilters import EvaluatorFilters
from .EvaluatorMetadata import EvaluatorMetadata
from .EvaluatorSampling import EvaluatorSampling
from .EvaluatorTestCriteria import EvaluatorTestCriteria
from .ScoreSchema import ScoreSchema

__all__ = ["PythonEvaluatorConfig"]


class PythonEvaluatorConfig(BaseModel):
    """
    PythonEvaluatorConfig model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    name: str = Field(validation_alias="name")

    metadata: EvaluatorMetadata = Field(validation_alias="metadata")

    sampling: EvaluatorSampling = Field(validation_alias="sampling")

    filters: EvaluatorFilters = Field(validation_alias="filters")

    score_schema: ScoreSchema = Field(validation_alias="score_schema")

    test_criteria: Optional[EvaluatorTestCriteria] = Field(
        validation_alias="test_criteria", default=None
    )

    code_execution: EvaluatorCodeExecution = Field(validation_alias="code_execution")
