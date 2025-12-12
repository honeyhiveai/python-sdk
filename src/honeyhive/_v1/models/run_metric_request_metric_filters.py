from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.run_metric_request_metric_filters_filter_array_item import (
        RunMetricRequestMetricFiltersFilterArrayItem,
    )


T = TypeVar("T", bound="RunMetricRequestMetricFilters")


@_attrs_define
class RunMetricRequestMetricFilters:
    """
    Attributes:
        filter_array (list[RunMetricRequestMetricFiltersFilterArrayItem]):
    """

    filter_array: list[RunMetricRequestMetricFiltersFilterArrayItem]

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
        from ..models.run_metric_request_metric_filters_filter_array_item import (
            RunMetricRequestMetricFiltersFilterArrayItem,
        )

        d = dict(src_dict)
        filter_array = []
        _filter_array = d.pop("filterArray")
        for filter_array_item_data in _filter_array:
            filter_array_item = RunMetricRequestMetricFiltersFilterArrayItem.from_dict(
                filter_array_item_data
            )

            filter_array.append(filter_array_item)

        run_metric_request_metric_filters = cls(
            filter_array=filter_array,
        )

        return run_metric_request_metric_filters
