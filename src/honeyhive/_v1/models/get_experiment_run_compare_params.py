from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetExperimentRunCompareParams")


@_attrs_define
class GetExperimentRunCompareParams:
    """
    Attributes:
        new_run_id (str):
        old_run_id (str):
    """

    new_run_id: str
    old_run_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_run_id = self.new_run_id

        old_run_id = self.old_run_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_run_id": new_run_id,
                "old_run_id": old_run_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        new_run_id = d.pop("new_run_id")

        old_run_id = d.pop("old_run_id")

        get_experiment_run_compare_params = cls(
            new_run_id=new_run_id,
            old_run_id=old_run_id,
        )

        get_experiment_run_compare_params.additional_properties = d
        return get_experiment_run_compare_params

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
