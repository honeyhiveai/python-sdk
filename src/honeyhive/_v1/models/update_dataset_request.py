from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateDatasetRequest")


@_attrs_define
class UpdateDatasetRequest:
    """
    Attributes:
        dataset_id (str):
        name (str | Unset):
        description (str | Unset):
        datapoints (list[str] | Unset):
    """

    dataset_id: str
    name: str | Unset = UNSET
    description: str | Unset = UNSET
    datapoints: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dataset_id = self.dataset_id

        name = self.name

        description = self.description

        datapoints: list[str] | Unset = UNSET
        if not isinstance(self.datapoints, Unset):
            datapoints = self.datapoints

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_id": dataset_id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if datapoints is not UNSET:
            field_dict["datapoints"] = datapoints

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dataset_id = d.pop("dataset_id")

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        datapoints = cast(list[str], d.pop("datapoints", UNSET))

        update_dataset_request = cls(
            dataset_id=dataset_id,
            name=name,
            description=description,
            datapoints=datapoints,
        )

        update_dataset_request.additional_properties = d
        return update_dataset_request

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
