from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.batch_create_datapoints_request_check_state import (
        BatchCreateDatapointsRequestCheckState,
    )
    from ..models.batch_create_datapoints_request_date_range import (
        BatchCreateDatapointsRequestDateRange,
    )
    from ..models.batch_create_datapoints_request_filters_type_0 import (
        BatchCreateDatapointsRequestFiltersType0,
    )
    from ..models.batch_create_datapoints_request_filters_type_1_item import (
        BatchCreateDatapointsRequestFiltersType1Item,
    )
    from ..models.batch_create_datapoints_request_mapping import (
        BatchCreateDatapointsRequestMapping,
    )


T = TypeVar("T", bound="BatchCreateDatapointsRequest")


@_attrs_define
class BatchCreateDatapointsRequest:
    """
    Attributes:
        events (list[str] | Unset):
        mapping (BatchCreateDatapointsRequestMapping | Unset):
        filters (BatchCreateDatapointsRequestFiltersType0 | list[BatchCreateDatapointsRequestFiltersType1Item] | Unset):
        date_range (BatchCreateDatapointsRequestDateRange | Unset):
        check_state (BatchCreateDatapointsRequestCheckState | Unset):
        select_all (bool | Unset):
        dataset_id (str | Unset):
    """

    events: list[str] | Unset = UNSET
    mapping: BatchCreateDatapointsRequestMapping | Unset = UNSET
    filters: (
        BatchCreateDatapointsRequestFiltersType0
        | list[BatchCreateDatapointsRequestFiltersType1Item]
        | Unset
    ) = UNSET
    date_range: BatchCreateDatapointsRequestDateRange | Unset = UNSET
    check_state: BatchCreateDatapointsRequestCheckState | Unset = UNSET
    select_all: bool | Unset = UNSET
    dataset_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.batch_create_datapoints_request_filters_type_0 import (
            BatchCreateDatapointsRequestFiltersType0,
        )

        events: list[str] | Unset = UNSET
        if not isinstance(self.events, Unset):
            events = self.events

        mapping: dict[str, Any] | Unset = UNSET
        if not isinstance(self.mapping, Unset):
            mapping = self.mapping.to_dict()

        filters: dict[str, Any] | list[dict[str, Any]] | Unset
        if isinstance(self.filters, Unset):
            filters = UNSET
        elif isinstance(self.filters, BatchCreateDatapointsRequestFiltersType0):
            filters = self.filters.to_dict()
        else:
            filters = []
            for filters_type_1_item_data in self.filters:
                filters_type_1_item = filters_type_1_item_data.to_dict()
                filters.append(filters_type_1_item)

        date_range: dict[str, Any] | Unset = UNSET
        if not isinstance(self.date_range, Unset):
            date_range = self.date_range.to_dict()

        check_state: dict[str, Any] | Unset = UNSET
        if not isinstance(self.check_state, Unset):
            check_state = self.check_state.to_dict()

        select_all = self.select_all

        dataset_id = self.dataset_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if events is not UNSET:
            field_dict["events"] = events
        if mapping is not UNSET:
            field_dict["mapping"] = mapping
        if filters is not UNSET:
            field_dict["filters"] = filters
        if date_range is not UNSET:
            field_dict["dateRange"] = date_range
        if check_state is not UNSET:
            field_dict["checkState"] = check_state
        if select_all is not UNSET:
            field_dict["selectAll"] = select_all
        if dataset_id is not UNSET:
            field_dict["dataset_id"] = dataset_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_create_datapoints_request_check_state import (
            BatchCreateDatapointsRequestCheckState,
        )
        from ..models.batch_create_datapoints_request_date_range import (
            BatchCreateDatapointsRequestDateRange,
        )
        from ..models.batch_create_datapoints_request_filters_type_0 import (
            BatchCreateDatapointsRequestFiltersType0,
        )
        from ..models.batch_create_datapoints_request_filters_type_1_item import (
            BatchCreateDatapointsRequestFiltersType1Item,
        )
        from ..models.batch_create_datapoints_request_mapping import (
            BatchCreateDatapointsRequestMapping,
        )

        d = dict(src_dict)
        events = cast(list[str], d.pop("events", UNSET))

        _mapping = d.pop("mapping", UNSET)
        mapping: BatchCreateDatapointsRequestMapping | Unset
        if isinstance(_mapping, Unset):
            mapping = UNSET
        else:
            mapping = BatchCreateDatapointsRequestMapping.from_dict(_mapping)

        def _parse_filters(
            data: object,
        ) -> (
            BatchCreateDatapointsRequestFiltersType0
            | list[BatchCreateDatapointsRequestFiltersType1Item]
            | Unset
        ):
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                filters_type_0 = BatchCreateDatapointsRequestFiltersType0.from_dict(
                    data
                )

                return filters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, list):
                raise TypeError()
            filters_type_1 = []
            _filters_type_1 = data
            for filters_type_1_item_data in _filters_type_1:
                filters_type_1_item = (
                    BatchCreateDatapointsRequestFiltersType1Item.from_dict(
                        filters_type_1_item_data
                    )
                )

                filters_type_1.append(filters_type_1_item)

            return filters_type_1

        filters = _parse_filters(d.pop("filters", UNSET))

        _date_range = d.pop("dateRange", UNSET)
        date_range: BatchCreateDatapointsRequestDateRange | Unset
        if isinstance(_date_range, Unset):
            date_range = UNSET
        else:
            date_range = BatchCreateDatapointsRequestDateRange.from_dict(_date_range)

        _check_state = d.pop("checkState", UNSET)
        check_state: BatchCreateDatapointsRequestCheckState | Unset
        if isinstance(_check_state, Unset):
            check_state = UNSET
        else:
            check_state = BatchCreateDatapointsRequestCheckState.from_dict(_check_state)

        select_all = d.pop("selectAll", UNSET)

        dataset_id = d.pop("dataset_id", UNSET)

        batch_create_datapoints_request = cls(
            events=events,
            mapping=mapping,
            filters=filters,
            date_range=date_range,
            check_state=check_state,
            select_all=select_all,
            dataset_id=dataset_id,
        )

        batch_create_datapoints_request.additional_properties = d
        return batch_create_datapoints_request

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
