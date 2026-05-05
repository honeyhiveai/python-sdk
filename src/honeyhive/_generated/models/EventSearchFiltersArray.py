from typing import List, TypeAlias

from .EventSearchFilter import EventSearchFilter

__all__ = ["EventSearchFiltersArray"]

EventSearchFiltersArray: TypeAlias = List[EventSearchFilter]
