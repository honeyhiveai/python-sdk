from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.todo_schema import TODOSchema


T = TypeVar("T", bound="CreateEventBody")


@_attrs_define
class CreateEventBody:
    """
    Attributes:
        event (TODOSchema | Unset): TODO: This is a placeholder schema. Proper Zod schemas need to be created in @hive-
            kube/core-ts for: Sessions, Events, Projects, and Experiment comparison/result endpoints.
    """

    event: TODOSchema | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event: dict[str, Any] | Unset = UNSET
        if not isinstance(self.event, Unset):
            event = self.event.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if event is not UNSET:
            field_dict["event"] = event

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.todo_schema import TODOSchema

        d = dict(src_dict)
        _event = d.pop("event", UNSET)
        event: TODOSchema | Unset
        if isinstance(_event, Unset):
            event = UNSET
        else:
            event = TODOSchema.from_dict(_event)

        create_event_body = cls(
            event=event,
        )

        create_event_body.additional_properties = d
        return create_event_body

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
