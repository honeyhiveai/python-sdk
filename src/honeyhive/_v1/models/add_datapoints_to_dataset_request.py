from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.add_datapoints_to_dataset_request_data_item import (
        AddDatapointsToDatasetRequestDataItem,
    )
    from ..models.add_datapoints_to_dataset_request_mapping import (
        AddDatapointsToDatasetRequestMapping,
    )


T = TypeVar("T", bound="AddDatapointsToDatasetRequest")


@_attrs_define
class AddDatapointsToDatasetRequest:
    """
    Attributes:
        data (list[AddDatapointsToDatasetRequestDataItem]):
        mapping (AddDatapointsToDatasetRequestMapping):
    """

    data: list[AddDatapointsToDatasetRequestDataItem]
    mapping: AddDatapointsToDatasetRequestMapping
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        mapping = self.mapping.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "mapping": mapping,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.add_datapoints_to_dataset_request_data_item import (
            AddDatapointsToDatasetRequestDataItem,
        )
        from ..models.add_datapoints_to_dataset_request_mapping import (
            AddDatapointsToDatasetRequestMapping,
        )

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = AddDatapointsToDatasetRequestDataItem.from_dict(data_item_data)

            data.append(data_item)

        mapping = AddDatapointsToDatasetRequestMapping.from_dict(d.pop("mapping"))

        add_datapoints_to_dataset_request = cls(
            data=data,
            mapping=mapping,
        )

        add_datapoints_to_dataset_request.additional_properties = d
        return add_datapoints_to_dataset_request

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
