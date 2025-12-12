from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_events_body_date_range import GetEventsBodyDateRange
    from ..models.todo_schema import TODOSchema


T = TypeVar("T", bound="GetEventsBody")


@_attrs_define
class GetEventsBody:
    """
    Attributes:
        project (str): Name of the project associated with the event like `New Project`
        filters (list[TODOSchema]):
        date_range (GetEventsBodyDateRange | Unset):
        projections (list[str] | Unset): Fields to include in the response
        limit (float | Unset): Limit number of results to speed up query (default is 1000, max is 7500)
        page (float | Unset): Page number of results (default is 1)
    """

    project: str
    filters: list[TODOSchema]
    date_range: GetEventsBodyDateRange | Unset = UNSET
    projections: list[str] | Unset = UNSET
    limit: float | Unset = UNSET
    page: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project

        filters = []
        for filters_item_data in self.filters:
            filters_item = filters_item_data.to_dict()
            filters.append(filters_item)

        date_range: dict[str, Any] | Unset = UNSET
        if not isinstance(self.date_range, Unset):
            date_range = self.date_range.to_dict()

        projections: list[str] | Unset = UNSET
        if not isinstance(self.projections, Unset):
            projections = self.projections

        limit = self.limit

        page = self.page

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "filters": filters,
            }
        )
        if date_range is not UNSET:
            field_dict["dateRange"] = date_range
        if projections is not UNSET:
            field_dict["projections"] = projections
        if limit is not UNSET:
            field_dict["limit"] = limit
        if page is not UNSET:
            field_dict["page"] = page

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_events_body_date_range import GetEventsBodyDateRange
        from ..models.todo_schema import TODOSchema

        d = dict(src_dict)
        project = d.pop("project")

        filters = []
        _filters = d.pop("filters")
        for filters_item_data in _filters:
            filters_item = TODOSchema.from_dict(filters_item_data)

            filters.append(filters_item)

        _date_range = d.pop("dateRange", UNSET)
        date_range: GetEventsBodyDateRange | Unset
        if isinstance(_date_range, Unset):
            date_range = UNSET
        else:
            date_range = GetEventsBodyDateRange.from_dict(_date_range)

        projections = cast(list[str], d.pop("projections", UNSET))

        limit = d.pop("limit", UNSET)

        page = d.pop("page", UNSET)

        get_events_body = cls(
            project=project,
            filters=filters,
            date_range=date_range,
            projections=projections,
            limit=limit,
            page=page,
        )

        get_events_body.additional_properties = d
        return get_events_body

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
