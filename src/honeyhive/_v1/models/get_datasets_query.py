from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDatasetsQuery")


@_attrs_define
class GetDatasetsQuery:
    """
    Attributes:
        dataset_id (str | Unset):
        name (str | Unset):
        include_datapoints (bool | str | Unset):
    """

    dataset_id: str | Unset = UNSET
    name: str | Unset = UNSET
    include_datapoints: bool | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dataset_id = self.dataset_id

        name = self.name

        include_datapoints: bool | str | Unset
        if isinstance(self.include_datapoints, Unset):
            include_datapoints = UNSET
        else:
            include_datapoints = self.include_datapoints

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dataset_id is not UNSET:
            field_dict["dataset_id"] = dataset_id
        if name is not UNSET:
            field_dict["name"] = name
        if include_datapoints is not UNSET:
            field_dict["include_datapoints"] = include_datapoints

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dataset_id = d.pop("dataset_id", UNSET)

        name = d.pop("name", UNSET)

        def _parse_include_datapoints(data: object) -> bool | str | Unset:
            if isinstance(data, Unset):
                return data
            return cast(bool | str | Unset, data)

        include_datapoints = _parse_include_datapoints(
            d.pop("include_datapoints", UNSET)
        )

        get_datasets_query = cls(
            dataset_id=dataset_id,
            name=name,
            include_datapoints=include_datapoints,
        )

        get_datasets_query.additional_properties = d
        return get_datasets_query

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
