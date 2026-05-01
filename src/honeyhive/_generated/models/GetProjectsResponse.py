from typing import List, TypeAlias

from .ProjectItem import ProjectItem

__all__ = ["GetProjectsResponse"]

GetProjectsResponse: TypeAlias = List[ProjectItem]
