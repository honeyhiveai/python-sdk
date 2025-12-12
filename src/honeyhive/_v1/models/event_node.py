from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_node_event_type import EventNodeEventType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_node_metadata import EventNodeMetadata


T = TypeVar("T", bound="EventNode")


@_attrs_define
class EventNode:
    """Event node in session tree with nested children

    Attributes:
        event_id (str):
        event_type (EventNodeEventType):
        event_name (str):
        children (list[Any]):
        start_time (float):
        end_time (float):
        duration (float):
        metadata (EventNodeMetadata):
        parent_id (str | Unset):
        session_id (str | Unset):
        children_ids (list[str] | Unset):
    """

    event_id: str
    event_type: EventNodeEventType
    event_name: str
    children: list[Any]
    start_time: float
    end_time: float
    duration: float
    metadata: EventNodeMetadata
    parent_id: str | Unset = UNSET
    session_id: str | Unset = UNSET
    children_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_id = self.event_id

        event_type = self.event_type.value

        event_name = self.event_name

        children = self.children

        start_time = self.start_time

        end_time = self.end_time

        duration = self.duration

        metadata = self.metadata.to_dict()

        parent_id = self.parent_id

        session_id = self.session_id

        children_ids: list[str] | Unset = UNSET
        if not isinstance(self.children_ids, Unset):
            children_ids = self.children_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event_id": event_id,
                "event_type": event_type,
                "event_name": event_name,
                "children": children,
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
                "metadata": metadata,
            }
        )
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if children_ids is not UNSET:
            field_dict["children_ids"] = children_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_node_metadata import EventNodeMetadata

        d = dict(src_dict)
        event_id = d.pop("event_id")

        event_type = EventNodeEventType(d.pop("event_type"))

        event_name = d.pop("event_name")

        children = cast(list[Any], d.pop("children"))

        start_time = d.pop("start_time")

        end_time = d.pop("end_time")

        duration = d.pop("duration")

        metadata = EventNodeMetadata.from_dict(d.pop("metadata"))

        parent_id = d.pop("parent_id", UNSET)

        session_id = d.pop("session_id", UNSET)

        children_ids = cast(list[str], d.pop("children_ids", UNSET))

        event_node = cls(
            event_id=event_id,
            event_type=event_type,
            event_name=event_name,
            children=children,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            metadata=metadata,
            parent_id=parent_id,
            session_id=session_id,
            children_ids=children_ids,
        )

        event_node.additional_properties = d
        return event_node

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
