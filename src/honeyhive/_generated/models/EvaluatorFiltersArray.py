from typing import List, TypeAlias

from .SingleFilter import SingleFilter

__all__ = ["EvaluatorFiltersArray"]

EvaluatorFiltersArray: TypeAlias = List[SingleFilter]
