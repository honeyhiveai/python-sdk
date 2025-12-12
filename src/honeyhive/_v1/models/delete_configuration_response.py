from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeleteConfigurationResponse")


@_attrs_define
class DeleteConfigurationResponse:
    """
    Attributes:
        acknowledged (bool):
        deleted_count (float):
    """

    acknowledged: bool
    deleted_count: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        acknowledged = self.acknowledged

        deleted_count = self.deleted_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "acknowledged": acknowledged,
                "deletedCount": deleted_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        acknowledged = d.pop("acknowledged")

        deleted_count = d.pop("deletedCount")

        delete_configuration_response = cls(
            acknowledged=acknowledged,
            deleted_count=deleted_count,
        )

        delete_configuration_response.additional_properties = d
        return delete_configuration_response

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
