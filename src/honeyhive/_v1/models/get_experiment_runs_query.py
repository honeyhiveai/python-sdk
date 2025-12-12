from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_experiment_runs_query_sort_by import GetExperimentRunsQuerySortBy
from ..models.get_experiment_runs_query_sort_order import (
    GetExperimentRunsQuerySortOrder,
)
from ..models.get_experiment_runs_query_status import GetExperimentRunsQueryStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_experiment_runs_query_date_range_type_1 import (
        GetExperimentRunsQueryDateRangeType1,
    )


T = TypeVar("T", bound="GetExperimentRunsQuery")


@_attrs_define
class GetExperimentRunsQuery:
    """
    Attributes:
        dataset_id (str | Unset):
        page (int | Unset):  Default: 1.
        limit (int | Unset):  Default: 20.
        run_ids (list[str] | Unset):
        name (str | Unset):
        status (GetExperimentRunsQueryStatus | Unset):
        date_range (GetExperimentRunsQueryDateRangeType1 | str | Unset):
        sort_by (GetExperimentRunsQuerySortBy | Unset):  Default: GetExperimentRunsQuerySortBy.CREATED_AT.
        sort_order (GetExperimentRunsQuerySortOrder | Unset):  Default: GetExperimentRunsQuerySortOrder.DESC.
    """

    dataset_id: str | Unset = UNSET
    page: int | Unset = 1
    limit: int | Unset = 20
    run_ids: list[str] | Unset = UNSET
    name: str | Unset = UNSET
    status: GetExperimentRunsQueryStatus | Unset = UNSET
    date_range: GetExperimentRunsQueryDateRangeType1 | str | Unset = UNSET
    sort_by: GetExperimentRunsQuerySortBy | Unset = (
        GetExperimentRunsQuerySortBy.CREATED_AT
    )
    sort_order: GetExperimentRunsQuerySortOrder | Unset = (
        GetExperimentRunsQuerySortOrder.DESC
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_experiment_runs_query_date_range_type_1 import (
            GetExperimentRunsQueryDateRangeType1,
        )

        dataset_id = self.dataset_id

        page = self.page

        limit = self.limit

        run_ids: list[str] | Unset = UNSET
        if not isinstance(self.run_ids, Unset):
            run_ids = self.run_ids

        name = self.name

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        date_range: dict[str, Any] | str | Unset
        if isinstance(self.date_range, Unset):
            date_range = UNSET
        elif isinstance(self.date_range, GetExperimentRunsQueryDateRangeType1):
            date_range = self.date_range.to_dict()
        else:
            date_range = self.date_range

        sort_by: str | Unset = UNSET
        if not isinstance(self.sort_by, Unset):
            sort_by = self.sort_by.value

        sort_order: str | Unset = UNSET
        if not isinstance(self.sort_order, Unset):
            sort_order = self.sort_order.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dataset_id is not UNSET:
            field_dict["dataset_id"] = dataset_id
        if page is not UNSET:
            field_dict["page"] = page
        if limit is not UNSET:
            field_dict["limit"] = limit
        if run_ids is not UNSET:
            field_dict["run_ids"] = run_ids
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status
        if date_range is not UNSET:
            field_dict["dateRange"] = date_range
        if sort_by is not UNSET:
            field_dict["sort_by"] = sort_by
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_experiment_runs_query_date_range_type_1 import (
            GetExperimentRunsQueryDateRangeType1,
        )

        d = dict(src_dict)
        dataset_id = d.pop("dataset_id", UNSET)

        page = d.pop("page", UNSET)

        limit = d.pop("limit", UNSET)

        run_ids = cast(list[str], d.pop("run_ids", UNSET))

        name = d.pop("name", UNSET)

        _status = d.pop("status", UNSET)
        status: GetExperimentRunsQueryStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = GetExperimentRunsQueryStatus(_status)

        def _parse_date_range(
            data: object,
        ) -> GetExperimentRunsQueryDateRangeType1 | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                date_range_type_1 = GetExperimentRunsQueryDateRangeType1.from_dict(data)

                return date_range_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GetExperimentRunsQueryDateRangeType1 | str | Unset, data)

        date_range = _parse_date_range(d.pop("dateRange", UNSET))

        _sort_by = d.pop("sort_by", UNSET)
        sort_by: GetExperimentRunsQuerySortBy | Unset
        if isinstance(_sort_by, Unset):
            sort_by = UNSET
        else:
            sort_by = GetExperimentRunsQuerySortBy(_sort_by)

        _sort_order = d.pop("sort_order", UNSET)
        sort_order: GetExperimentRunsQuerySortOrder | Unset
        if isinstance(_sort_order, Unset):
            sort_order = UNSET
        else:
            sort_order = GetExperimentRunsQuerySortOrder(_sort_order)

        get_experiment_runs_query = cls(
            dataset_id=dataset_id,
            page=page,
            limit=limit,
            run_ids=run_ids,
            name=name,
            status=status,
            date_range=date_range,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        get_experiment_runs_query.additional_properties = d
        return get_experiment_runs_query

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
