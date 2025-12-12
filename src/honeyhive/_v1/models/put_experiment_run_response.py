from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PutExperimentRunResponse")


@_attrs_define
class PutExperimentRunResponse:
    """
    Attributes:
        evaluation (Any | Unset):
        warning (str | Unset):
    """

    evaluation: Any | Unset = UNSET
    warning: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        evaluation = self.evaluation

        warning = self.warning

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if evaluation is not UNSET:
            field_dict["evaluation"] = evaluation
        if warning is not UNSET:
            field_dict["warning"] = warning

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        evaluation = d.pop("evaluation", UNSET)

        warning = d.pop("warning", UNSET)

        put_experiment_run_response = cls(
            evaluation=evaluation,
            warning=warning,
        )

        put_experiment_run_response.additional_properties = d
        return put_experiment_run_response

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
