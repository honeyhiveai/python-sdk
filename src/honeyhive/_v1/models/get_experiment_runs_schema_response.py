from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_experiment_runs_schema_response_fields_item import (
        GetExperimentRunsSchemaResponseFieldsItem,
    )
    from ..models.get_experiment_runs_schema_response_mappings import (
        GetExperimentRunsSchemaResponseMappings,
    )


T = TypeVar("T", bound="GetExperimentRunsSchemaResponse")


@_attrs_define
class GetExperimentRunsSchemaResponse:
    """
    Attributes:
        fields (list[GetExperimentRunsSchemaResponseFieldsItem]):
        datasets (list[str]):
        mappings (GetExperimentRunsSchemaResponseMappings):
    """

    fields: list[GetExperimentRunsSchemaResponseFieldsItem]
    datasets: list[str]
    mappings: GetExperimentRunsSchemaResponseMappings
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fields = []
        for fields_item_data in self.fields:
            fields_item = fields_item_data.to_dict()
            fields.append(fields_item)

        datasets = self.datasets

        mappings = self.mappings.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fields": fields,
                "datasets": datasets,
                "mappings": mappings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_experiment_runs_schema_response_fields_item import (
            GetExperimentRunsSchemaResponseFieldsItem,
        )
        from ..models.get_experiment_runs_schema_response_mappings import (
            GetExperimentRunsSchemaResponseMappings,
        )

        d = dict(src_dict)
        fields = []
        _fields = d.pop("fields")
        for fields_item_data in _fields:
            fields_item = GetExperimentRunsSchemaResponseFieldsItem.from_dict(
                fields_item_data
            )

            fields.append(fields_item)

        datasets = cast(list[str], d.pop("datasets"))

        mappings = GetExperimentRunsSchemaResponseMappings.from_dict(d.pop("mappings"))

        get_experiment_runs_schema_response = cls(
            fields=fields,
            datasets=datasets,
            mappings=mappings,
        )

        get_experiment_runs_schema_response.additional_properties = d
        return get_experiment_runs_schema_response

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
