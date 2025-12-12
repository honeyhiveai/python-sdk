from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="RunMetricRequestMetricThresholdType0")


@_attrs_define
class RunMetricRequestMetricThresholdType0:
    """
    Attributes:
        min_ (float | Unset):
        max_ (float | Unset):
        pass_when (bool | float | Unset):
        passing_categories (list[str] | Unset):
    """

    min_: float | Unset = UNSET
    max_: float | Unset = UNSET
    pass_when: bool | float | Unset = UNSET
    passing_categories: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        min_ = self.min_

        max_ = self.max_

        pass_when: bool | float | Unset
        if isinstance(self.pass_when, Unset):
            pass_when = UNSET
        else:
            pass_when = self.pass_when

        passing_categories: list[str] | Unset = UNSET
        if not isinstance(self.passing_categories, Unset):
            passing_categories = self.passing_categories

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if min_ is not UNSET:
            field_dict["min"] = min_
        if max_ is not UNSET:
            field_dict["max"] = max_
        if pass_when is not UNSET:
            field_dict["pass_when"] = pass_when
        if passing_categories is not UNSET:
            field_dict["passing_categories"] = passing_categories

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        min_ = d.pop("min", UNSET)

        max_ = d.pop("max", UNSET)

        def _parse_pass_when(data: object) -> bool | float | Unset:
            if isinstance(data, Unset):
                return data
            return cast(bool | float | Unset, data)

        pass_when = _parse_pass_when(d.pop("pass_when", UNSET))

        passing_categories = cast(list[str], d.pop("passing_categories", UNSET))

        run_metric_request_metric_threshold_type_0 = cls(
            min_=min_,
            max_=max_,
            pass_when=pass_when,
            passing_categories=passing_categories,
        )

        return run_metric_request_metric_threshold_type_0
