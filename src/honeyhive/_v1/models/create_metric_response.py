from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateMetricResponse")


@_attrs_define
class CreateMetricResponse:
    """
    Attributes:
        inserted (bool):
        metric_id (str):
    """

    inserted: bool
    metric_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        inserted = self.inserted

        metric_id = self.metric_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inserted": inserted,
                "metric_id": metric_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        inserted = d.pop("inserted")

        metric_id = d.pop("metric_id")

        create_metric_response = cls(
            inserted=inserted,
            metric_id=metric_id,
        )

        create_metric_response.additional_properties = d
        return create_metric_response

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
