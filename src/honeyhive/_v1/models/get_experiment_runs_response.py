from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_experiment_runs_response_pagination import (
        GetExperimentRunsResponsePagination,
    )


T = TypeVar("T", bound="GetExperimentRunsResponse")


@_attrs_define
class GetExperimentRunsResponse:
    """
    Attributes:
        evaluations (list[Any]):
        pagination (GetExperimentRunsResponsePagination):
        metrics (list[str]):
    """

    evaluations: list[Any]
    pagination: GetExperimentRunsResponsePagination
    metrics: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        evaluations = self.evaluations

        pagination = self.pagination.to_dict()

        metrics = self.metrics

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "evaluations": evaluations,
                "pagination": pagination,
                "metrics": metrics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_experiment_runs_response_pagination import (
            GetExperimentRunsResponsePagination,
        )

        d = dict(src_dict)
        evaluations = cast(list[Any], d.pop("evaluations"))

        pagination = GetExperimentRunsResponsePagination.from_dict(d.pop("pagination"))

        metrics = cast(list[str], d.pop("metrics"))

        get_experiment_runs_response = cls(
            evaluations=evaluations,
            pagination=pagination,
            metrics=metrics,
        )

        get_experiment_runs_response.additional_properties = d
        return get_experiment_runs_response

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
