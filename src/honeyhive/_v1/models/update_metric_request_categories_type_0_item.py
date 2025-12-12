from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="UpdateMetricRequestCategoriesType0Item")


@_attrs_define
class UpdateMetricRequestCategoriesType0Item:
    """
    Attributes:
        category (str):
        score (float | None):
    """

    category: str
    score: float | None

    def to_dict(self) -> dict[str, Any]:
        category = self.category

        score: float | None
        score = self.score

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "category": category,
                "score": score,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        category = d.pop("category")

        def _parse_score(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        score = _parse_score(d.pop("score"))

        update_metric_request_categories_type_0_item = cls(
            category=category,
            score=score,
        )

        return update_metric_request_categories_type_0_item
