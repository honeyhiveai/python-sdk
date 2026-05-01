from typing import List, TypeAlias

from .SingleFilter import SingleFilter

__all__ = ["FiltersArray"]

FiltersArray: TypeAlias = List[SingleFilter]
