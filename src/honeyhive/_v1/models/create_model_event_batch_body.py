from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.todo_schema import TODOSchema


T = TypeVar("T", bound="CreateModelEventBatchBody")


@_attrs_define
class CreateModelEventBatchBody:
    """
    Attributes:
        model_events (list[TODOSchema] | Unset):
        is_single_session (bool | Unset): Default is false. If true, all events will be associated with the same session
        session_properties (TODOSchema | Unset): TODO: This is a placeholder schema. Proper Zod schemas need to be
            created in @hive-kube/core-ts for: Sessions, Events, Projects, and Experiment comparison/result endpoints.
    """

    model_events: list[TODOSchema] | Unset = UNSET
    is_single_session: bool | Unset = UNSET
    session_properties: TODOSchema | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        model_events: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.model_events, Unset):
            model_events = []
            for model_events_item_data in self.model_events:
                model_events_item = model_events_item_data.to_dict()
                model_events.append(model_events_item)

        is_single_session = self.is_single_session

        session_properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.session_properties, Unset):
            session_properties = self.session_properties.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if model_events is not UNSET:
            field_dict["model_events"] = model_events
        if is_single_session is not UNSET:
            field_dict["is_single_session"] = is_single_session
        if session_properties is not UNSET:
            field_dict["session_properties"] = session_properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.todo_schema import TODOSchema

        d = dict(src_dict)
        _model_events = d.pop("model_events", UNSET)
        model_events: list[TODOSchema] | Unset = UNSET
        if _model_events is not UNSET:
            model_events = []
            for model_events_item_data in _model_events:
                model_events_item = TODOSchema.from_dict(model_events_item_data)

                model_events.append(model_events_item)

        is_single_session = d.pop("is_single_session", UNSET)

        _session_properties = d.pop("session_properties", UNSET)
        session_properties: TODOSchema | Unset
        if isinstance(_session_properties, Unset):
            session_properties = UNSET
        else:
            session_properties = TODOSchema.from_dict(_session_properties)

        create_model_event_batch_body = cls(
            model_events=model_events,
            is_single_session=is_single_session,
            session_properties=session_properties,
        )

        create_model_event_batch_body.additional_properties = d
        return create_model_event_batch_body

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
