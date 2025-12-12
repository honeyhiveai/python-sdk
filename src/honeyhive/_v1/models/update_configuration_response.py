from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UpdateConfigurationResponse")


@_attrs_define
class UpdateConfigurationResponse:
    """
    Attributes:
        acknowledged (bool):
        modified_count (float):
        upserted_id (None):
        upserted_count (float):
        matched_count (float):
    """

    acknowledged: bool
    modified_count: float
    upserted_id: None
    upserted_count: float
    matched_count: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        acknowledged = self.acknowledged

        modified_count = self.modified_count

        upserted_id = self.upserted_id

        upserted_count = self.upserted_count

        matched_count = self.matched_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "acknowledged": acknowledged,
                "modifiedCount": modified_count,
                "upsertedId": upserted_id,
                "upsertedCount": upserted_count,
                "matchedCount": matched_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        acknowledged = d.pop("acknowledged")

        modified_count = d.pop("modifiedCount")

        upserted_id = d.pop("upsertedId")

        upserted_count = d.pop("upsertedCount")

        matched_count = d.pop("matchedCount")

        update_configuration_response = cls(
            acknowledged=acknowledged,
            modified_count=modified_count,
            upserted_id=upserted_id,
            upserted_count=upserted_count,
            matched_count=matched_count,
        )

        update_configuration_response.additional_properties = d
        return update_configuration_response

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
