from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_node_metadata_scope import EventNodeMetadataScope


T = TypeVar("T", bound="EventNodeMetadata")


@_attrs_define
class EventNodeMetadata:
    """
    Attributes:
        num_events (float | Unset):
        num_model_events (float | Unset):
        has_feedback (bool | Unset):
        cost (float | Unset):
        total_tokens (float | Unset):
        prompt_tokens (float | Unset):
        completion_tokens (float | Unset):
        scope (EventNodeMetadataScope | Unset):
    """

    num_events: float | Unset = UNSET
    num_model_events: float | Unset = UNSET
    has_feedback: bool | Unset = UNSET
    cost: float | Unset = UNSET
    total_tokens: float | Unset = UNSET
    prompt_tokens: float | Unset = UNSET
    completion_tokens: float | Unset = UNSET
    scope: EventNodeMetadataScope | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        num_events = self.num_events

        num_model_events = self.num_model_events

        has_feedback = self.has_feedback

        cost = self.cost

        total_tokens = self.total_tokens

        prompt_tokens = self.prompt_tokens

        completion_tokens = self.completion_tokens

        scope: dict[str, Any] | Unset = UNSET
        if not isinstance(self.scope, Unset):
            scope = self.scope.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if num_events is not UNSET:
            field_dict["num_events"] = num_events
        if num_model_events is not UNSET:
            field_dict["num_model_events"] = num_model_events
        if has_feedback is not UNSET:
            field_dict["has_feedback"] = has_feedback
        if cost is not UNSET:
            field_dict["cost"] = cost
        if total_tokens is not UNSET:
            field_dict["total_tokens"] = total_tokens
        if prompt_tokens is not UNSET:
            field_dict["prompt_tokens"] = prompt_tokens
        if completion_tokens is not UNSET:
            field_dict["completion_tokens"] = completion_tokens
        if scope is not UNSET:
            field_dict["scope"] = scope

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_node_metadata_scope import EventNodeMetadataScope

        d = dict(src_dict)
        num_events = d.pop("num_events", UNSET)

        num_model_events = d.pop("num_model_events", UNSET)

        has_feedback = d.pop("has_feedback", UNSET)

        cost = d.pop("cost", UNSET)

        total_tokens = d.pop("total_tokens", UNSET)

        prompt_tokens = d.pop("prompt_tokens", UNSET)

        completion_tokens = d.pop("completion_tokens", UNSET)

        _scope = d.pop("scope", UNSET)
        scope: EventNodeMetadataScope | Unset
        if isinstance(_scope, Unset):
            scope = UNSET
        else:
            scope = EventNodeMetadataScope.from_dict(_scope)

        event_node_metadata = cls(
            num_events=num_events,
            num_model_events=num_model_events,
            has_feedback=has_feedback,
            cost=cost,
            total_tokens=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            scope=scope,
        )

        event_node_metadata.additional_properties = d
        return event_node_metadata

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
