from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_experiment_run_compare_events_query_filter_type_1 import (
        GetExperimentRunCompareEventsQueryFilterType1,
    )


T = TypeVar("T", bound="GetExperimentRunCompareEventsQuery")


@_attrs_define
class GetExperimentRunCompareEventsQuery:
    """
    Attributes:
        run_id_1 (str):
        run_id_2 (str):
        event_name (str | Unset):
        event_type (str | Unset):
        filter_ (GetExperimentRunCompareEventsQueryFilterType1 | str | Unset):
        limit (int | Unset):  Default: 1000.
        page (int | Unset):  Default: 1.
    """

    run_id_1: str
    run_id_2: str
    event_name: str | Unset = UNSET
    event_type: str | Unset = UNSET
    filter_: GetExperimentRunCompareEventsQueryFilterType1 | str | Unset = UNSET
    limit: int | Unset = 1000
    page: int | Unset = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_experiment_run_compare_events_query_filter_type_1 import (
            GetExperimentRunCompareEventsQueryFilterType1,
        )

        run_id_1 = self.run_id_1

        run_id_2 = self.run_id_2

        event_name = self.event_name

        event_type = self.event_type

        filter_: dict[str, Any] | str | Unset
        if isinstance(self.filter_, Unset):
            filter_ = UNSET
        elif isinstance(self.filter_, GetExperimentRunCompareEventsQueryFilterType1):
            filter_ = self.filter_.to_dict()
        else:
            filter_ = self.filter_

        limit = self.limit

        page = self.page

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "run_id_1": run_id_1,
                "run_id_2": run_id_2,
            }
        )
        if event_name is not UNSET:
            field_dict["event_name"] = event_name
        if event_type is not UNSET:
            field_dict["event_type"] = event_type
        if filter_ is not UNSET:
            field_dict["filter"] = filter_
        if limit is not UNSET:
            field_dict["limit"] = limit
        if page is not UNSET:
            field_dict["page"] = page

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_experiment_run_compare_events_query_filter_type_1 import (
            GetExperimentRunCompareEventsQueryFilterType1,
        )

        d = dict(src_dict)
        run_id_1 = d.pop("run_id_1")

        run_id_2 = d.pop("run_id_2")

        event_name = d.pop("event_name", UNSET)

        event_type = d.pop("event_type", UNSET)

        def _parse_filter_(
            data: object,
        ) -> GetExperimentRunCompareEventsQueryFilterType1 | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                filter_type_1 = GetExperimentRunCompareEventsQueryFilterType1.from_dict(
                    data
                )

                return filter_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                GetExperimentRunCompareEventsQueryFilterType1 | str | Unset, data
            )

        filter_ = _parse_filter_(d.pop("filter", UNSET))

        limit = d.pop("limit", UNSET)

        page = d.pop("page", UNSET)

        get_experiment_run_compare_events_query = cls(
            run_id_1=run_id_1,
            run_id_2=run_id_2,
            event_name=event_name,
            event_type=event_type,
            filter_=filter_,
            limit=limit,
            page=page,
        )

        get_experiment_run_compare_events_query.additional_properties = d
        return get_experiment_run_compare_events_query

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
