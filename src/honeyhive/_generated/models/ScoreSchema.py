from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

__all__ = ["ScoreSchema"]


class ScoreSchema(BaseModel):
    """
    ScoreSchema model
        A Draft 2020-12 schema document. Further safety restrictions will apply.
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }
