from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchCreateDatapointsRequestDateRange")


@_attrs_define
class BatchCreateDatapointsRequestDateRange:
    """
    Attributes:
        gte (str | Unset):
        lte (str | Unset):
    """

    gte: str | Unset = UNSET
    lte: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        gte = self.gte

        lte = self.lte

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if gte is not UNSET:
            field_dict["$gte"] = gte
        if lte is not UNSET:
            field_dict["$lte"] = lte

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        gte = d.pop("$gte", UNSET)

        lte = d.pop("$lte", UNSET)

        batch_create_datapoints_request_date_range = cls(
            gte=gte,
            lte=lte,
        )

        batch_create_datapoints_request_date_range.additional_properties = d
        return batch_create_datapoints_request_date_range

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
