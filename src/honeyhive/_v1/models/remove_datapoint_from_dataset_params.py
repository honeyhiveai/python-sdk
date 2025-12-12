from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RemoveDatapointFromDatasetParams")


@_attrs_define
class RemoveDatapointFromDatasetParams:
    """
    Attributes:
        dataset_id (str):
        datapoint_id (str):
    """

    dataset_id: str
    datapoint_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dataset_id = self.dataset_id

        datapoint_id = self.datapoint_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_id": dataset_id,
                "datapoint_id": datapoint_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dataset_id = d.pop("dataset_id")

        datapoint_id = d.pop("datapoint_id")

        remove_datapoint_from_dataset_params = cls(
            dataset_id=dataset_id,
            datapoint_id=datapoint_id,
        )

        remove_datapoint_from_dataset_params.additional_properties = d
        return remove_datapoint_from_dataset_params

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
