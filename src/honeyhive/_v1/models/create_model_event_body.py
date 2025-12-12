from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.todo_schema import TODOSchema


T = TypeVar("T", bound="CreateModelEventBody")


@_attrs_define
class CreateModelEventBody:
    """
    Attributes:
        model_event (TODOSchema | Unset): TODO: This is a placeholder schema. Proper Zod schemas need to be created in
            @hive-kube/core-ts for: Sessions, Events, Projects, and Experiment comparison/result endpoints.
    """

    model_event: TODOSchema | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        model_event: dict[str, Any] | Unset = UNSET
        if not isinstance(self.model_event, Unset):
            model_event = self.model_event.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if model_event is not UNSET:
            field_dict["model_event"] = model_event

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.todo_schema import TODOSchema

        d = dict(src_dict)
        _model_event = d.pop("model_event", UNSET)
        model_event: TODOSchema | Unset
        if isinstance(_model_event, Unset):
            model_event = UNSET
        else:
            model_event = TODOSchema.from_dict(_model_event)

        create_model_event_body = cls(
            model_event=model_event,
        )

        create_model_event_body.additional_properties = d
        return create_model_event_body

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
