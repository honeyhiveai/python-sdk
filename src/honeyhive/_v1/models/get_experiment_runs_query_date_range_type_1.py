from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetExperimentRunsQueryDateRangeType1")


@_attrs_define
class GetExperimentRunsQueryDateRangeType1:
    """
    Attributes:
        gte (float | str):
        lte (float | str):
    """

    gte: float | str
    lte: float | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        gte: float | str
        gte = self.gte

        lte: float | str
        lte = self.lte

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "$gte": gte,
                "$lte": lte,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_gte(data: object) -> float | str:
            return cast(float | str, data)

        gte = _parse_gte(d.pop("$gte"))

        def _parse_lte(data: object) -> float | str:
            return cast(float | str, data)

        lte = _parse_lte(d.pop("$lte"))

        get_experiment_runs_query_date_range_type_1 = cls(
            gte=gte,
            lte=lte,
        )

        get_experiment_runs_query_date_range_type_1.additional_properties = d
        return get_experiment_runs_query_date_range_type_1

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
