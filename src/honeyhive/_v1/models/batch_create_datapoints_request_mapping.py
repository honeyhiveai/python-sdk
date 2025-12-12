from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchCreateDatapointsRequestMapping")


@_attrs_define
class BatchCreateDatapointsRequestMapping:
    """
    Attributes:
        inputs (list[str] | Unset):
        history (list[str] | Unset):
        ground_truth (list[str] | Unset):
    """

    inputs: list[str] | Unset = UNSET
    history: list[str] | Unset = UNSET
    ground_truth: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        inputs: list[str] | Unset = UNSET
        if not isinstance(self.inputs, Unset):
            inputs = self.inputs

        history: list[str] | Unset = UNSET
        if not isinstance(self.history, Unset):
            history = self.history

        ground_truth: list[str] | Unset = UNSET
        if not isinstance(self.ground_truth, Unset):
            ground_truth = self.ground_truth

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if inputs is not UNSET:
            field_dict["inputs"] = inputs
        if history is not UNSET:
            field_dict["history"] = history
        if ground_truth is not UNSET:
            field_dict["ground_truth"] = ground_truth

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        inputs = cast(list[str], d.pop("inputs", UNSET))

        history = cast(list[str], d.pop("history", UNSET))

        ground_truth = cast(list[str], d.pop("ground_truth", UNSET))

        batch_create_datapoints_request_mapping = cls(
            inputs=inputs,
            history=history,
            ground_truth=ground_truth,
        )

        batch_create_datapoints_request_mapping.additional_properties = d
        return batch_create_datapoints_request_mapping

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
