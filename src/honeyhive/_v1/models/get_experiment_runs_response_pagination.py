from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetExperimentRunsResponsePagination")


@_attrs_define
class GetExperimentRunsResponsePagination:
    """
    Attributes:
        page (int):
        limit (int):
        total (int):
        total_unfiltered (int):
        total_pages (int):
        has_next (bool):
        has_prev (bool):
    """

    page: int
    limit: int
    total: int
    total_unfiltered: int
    total_pages: int
    has_next: bool
    has_prev: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page = self.page

        limit = self.limit

        total = self.total

        total_unfiltered = self.total_unfiltered

        total_pages = self.total_pages

        has_next = self.has_next

        has_prev = self.has_prev

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "page": page,
                "limit": limit,
                "total": total,
                "total_unfiltered": total_unfiltered,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        page = d.pop("page")

        limit = d.pop("limit")

        total = d.pop("total")

        total_unfiltered = d.pop("total_unfiltered")

        total_pages = d.pop("total_pages")

        has_next = d.pop("has_next")

        has_prev = d.pop("has_prev")

        get_experiment_runs_response_pagination = cls(
            page=page,
            limit=limit,
            total=total,
            total_unfiltered=total_unfiltered,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        )

        get_experiment_runs_response_pagination.additional_properties = d
        return get_experiment_runs_response_pagination

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
