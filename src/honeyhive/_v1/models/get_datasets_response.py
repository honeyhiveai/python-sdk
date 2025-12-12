from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_datasets_response_datapoints_item import (
        GetDatasetsResponseDatapointsItem,
    )


T = TypeVar("T", bound="GetDatasetsResponse")


@_attrs_define
class GetDatasetsResponse:
    """
    Attributes:
        datapoints (list[GetDatasetsResponseDatapointsItem]):
    """

    datapoints: list[GetDatasetsResponseDatapointsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        datapoints = []
        for datapoints_item_data in self.datapoints:
            datapoints_item = datapoints_item_data.to_dict()
            datapoints.append(datapoints_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "datapoints": datapoints,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_datasets_response_datapoints_item import (
            GetDatasetsResponseDatapointsItem,
        )

        d = dict(src_dict)
        datapoints = []
        _datapoints = d.pop("datapoints")
        for datapoints_item_data in _datapoints:
            datapoints_item = GetDatasetsResponseDatapointsItem.from_dict(
                datapoints_item_data
            )

            datapoints.append(datapoints_item)

        get_datasets_response = cls(
            datapoints=datapoints,
        )

        get_datasets_response.additional_properties = d
        return get_datasets_response

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
