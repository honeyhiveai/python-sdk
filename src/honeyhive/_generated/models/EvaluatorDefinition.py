from typing import Annotated, TypeAlias, Union

from pydantic import Field

from .HumanEvaluatorDefinition import HumanEvaluatorDefinition
from .LLMEvaluatorDefinition import LLMEvaluatorDefinition
from .PythonEvaluatorDefinition import PythonEvaluatorDefinition

__all__ = ["EvaluatorDefinition"]

EvaluatorDefinition: TypeAlias = Annotated[
    Union[PythonEvaluatorDefinition, LLMEvaluatorDefinition, HumanEvaluatorDefinition],
    Field(discriminator="type"),
]
