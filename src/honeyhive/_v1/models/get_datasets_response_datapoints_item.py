from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDatasetsResponseDatapointsItem")


@_attrs_define
class GetDatasetsResponseDatapointsItem:
    """
    Attributes:
        id (str):
        name (str):
        description (None | str | Unset):
        datapoints (list[str] | Unset):
        created_at (str | Unset):
        updated_at (str | Unset):
    """

    id: str
    name: str
    description: None | str | Unset = UNSET
    datapoints: list[str] | Unset = UNSET
    created_at: str | Unset = UNSET
    updated_at: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        datapoints: list[str] | Unset = UNSET
        if not isinstance(self.datapoints, Unset):
            datapoints = self.datapoints

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if datapoints is not UNSET:
            field_dict["datapoints"] = datapoints
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        datapoints = cast(list[str], d.pop("datapoints", UNSET))

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        get_datasets_response_datapoints_item = cls(
            id=id,
            name=name,
            description=description,
            datapoints=datapoints,
            created_at=created_at,
            updated_at=updated_at,
        )

        get_datasets_response_datapoints_item.additional_properties = d
        return get_datasets_response_datapoints_item

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
