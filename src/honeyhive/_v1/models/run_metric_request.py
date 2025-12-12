from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_metric_request_metric import RunMetricRequestMetric


T = TypeVar("T", bound="RunMetricRequest")


@_attrs_define
class RunMetricRequest:
    """
    Attributes:
        metric (RunMetricRequestMetric):
        event (Any | Unset):
    """

    metric: RunMetricRequestMetric
    event: Any | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        metric = self.metric.to_dict()

        event = self.event

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metric": metric,
            }
        )
        if event is not UNSET:
            field_dict["event"] = event

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_metric_request_metric import RunMetricRequestMetric

        d = dict(src_dict)
        metric = RunMetricRequestMetric.from_dict(d.pop("metric"))

        event = d.pop("event", UNSET)

        run_metric_request = cls(
            metric=metric,
            event=event,
        )

        run_metric_request.additional_properties = d
        return run_metric_request

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
