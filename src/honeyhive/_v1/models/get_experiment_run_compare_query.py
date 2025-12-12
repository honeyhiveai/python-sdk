from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetExperimentRunCompareQuery")


@_attrs_define
class GetExperimentRunCompareQuery:
    """
    Attributes:
        aggregate_function (str | Unset):  Default: 'average'.
        filters (list[Any] | str | Unset):
    """

    aggregate_function: str | Unset = "average"
    filters: list[Any] | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        aggregate_function = self.aggregate_function

        filters: list[Any] | str | Unset
        if isinstance(self.filters, Unset):
            filters = UNSET
        elif isinstance(self.filters, list):
            filters = self.filters

        else:
            filters = self.filters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if aggregate_function is not UNSET:
            field_dict["aggregate_function"] = aggregate_function
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        aggregate_function = d.pop("aggregate_function", UNSET)

        def _parse_filters(data: object) -> list[Any] | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filters_type_1 = cast(list[Any], data)

                return filters_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[Any] | str | Unset, data)

        filters = _parse_filters(d.pop("filters", UNSET))

        get_experiment_run_compare_query = cls(
            aggregate_function=aggregate_function,
            filters=filters,
        )

        get_experiment_run_compare_query.additional_properties = d
        return get_experiment_run_compare_query

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
