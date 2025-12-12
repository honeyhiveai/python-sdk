from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_metrics_response_item_filters_filter_array_item import (
        GetMetricsResponseItemFiltersFilterArrayItem,
    )


T = TypeVar("T", bound="GetMetricsResponseItemFilters")


@_attrs_define
class GetMetricsResponseItemFilters:
    """
    Attributes:
        filter_array (list[GetMetricsResponseItemFiltersFilterArrayItem]):
    """

    filter_array: list[GetMetricsResponseItemFiltersFilterArrayItem]

    def to_dict(self) -> dict[str, Any]:
        filter_array = []
        for filter_array_item_data in self.filter_array:
            filter_array_item = filter_array_item_data.to_dict()
            filter_array.append(filter_array_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "filterArray": filter_array,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_metrics_response_item_filters_filter_array_item import (
            GetMetricsResponseItemFiltersFilterArrayItem,
        )

        d = dict(src_dict)
        filter_array = []
        _filter_array = d.pop("filterArray")
        for filter_array_item_data in _filter_array:
            filter_array_item = GetMetricsResponseItemFiltersFilterArrayItem.from_dict(
                filter_array_item_data
            )

            filter_array.append(filter_array_item)

        get_metrics_response_item_filters = cls(
            filter_array=filter_array,
        )

        return get_metrics_response_item_filters
