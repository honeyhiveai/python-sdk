from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateEventBatchResponse200")


@_attrs_define
class CreateEventBatchResponse200:
    """
    Example:
        {'event_ids': ['7f22137a-6911-4ed3-bc36-110f1dde6b66', '7f22137a-6911-4ed3-bc36-110f1dde6b67'], 'session_id':
            'caf77ace-3417-4da4-944d-f4a0688f3c23', 'success': True}

    Attributes:
        event_ids (list[str] | Unset):
        session_id (str | Unset):
        success (bool | Unset):
    """

    event_ids: list[str] | Unset = UNSET
    session_id: str | Unset = UNSET
    success: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_ids: list[str] | Unset = UNSET
        if not isinstance(self.event_ids, Unset):
            event_ids = self.event_ids

        session_id = self.session_id

        success = self.success

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if event_ids is not UNSET:
            field_dict["event_ids"] = event_ids
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if success is not UNSET:
            field_dict["success"] = success

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        event_ids = cast(list[str], d.pop("event_ids", UNSET))

        session_id = d.pop("session_id", UNSET)

        success = d.pop("success", UNSET)

        create_event_batch_response_200 = cls(
            event_ids=event_ids,
            session_id=session_id,
            success=success,
        )

        create_event_batch_response_200.additional_properties = d
        return create_event_batch_response_200

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
