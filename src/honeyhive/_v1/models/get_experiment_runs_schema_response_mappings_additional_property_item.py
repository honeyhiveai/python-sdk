from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetExperimentRunsSchemaResponseMappingsAdditionalPropertyItem")


@_attrs_define
class GetExperimentRunsSchemaResponseMappingsAdditionalPropertyItem:
    """
    Attributes:
        field_name (str):
        event_type (str):
    """

    field_name: str
    event_type: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_name = self.field_name

        event_type = self.event_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field_name": field_name,
                "event_type": event_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field_name = d.pop("field_name")

        event_type = d.pop("event_type")

        get_experiment_runs_schema_response_mappings_additional_property_item = cls(
            field_name=field_name,
            event_type=event_type,
        )

        get_experiment_runs_schema_response_mappings_additional_property_item.additional_properties = (
            d
        )
        return get_experiment_runs_schema_response_mappings_additional_property_item

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
