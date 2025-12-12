from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.update_datapoint_response_result import UpdateDatapointResponseResult


T = TypeVar("T", bound="UpdateDatapointResponse")


@_attrs_define
class UpdateDatapointResponse:
    """
    Attributes:
        updated (bool):
        result (UpdateDatapointResponseResult):
    """

    updated: bool
    result: UpdateDatapointResponseResult
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        updated = self.updated

        result = self.result.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "updated": updated,
                "result": result,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_datapoint_response_result import (
            UpdateDatapointResponseResult,
        )

        d = dict(src_dict)
        updated = d.pop("updated")

        result = UpdateDatapointResponseResult.from_dict(d.pop("result"))

        update_datapoint_response = cls(
            updated=updated,
            result=result,
        )

        update_datapoint_response.additional_properties = d
        return update_datapoint_response

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
