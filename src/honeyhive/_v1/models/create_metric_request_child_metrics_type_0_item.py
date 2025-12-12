from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateMetricRequestChildMetricsType0Item")


@_attrs_define
class CreateMetricRequestChildMetricsType0Item:
    """
    Attributes:
        name (str):
        weight (float):
        id (str | Unset):
        scale (int | None | Unset):
    """

    name: str
    weight: float
    id: str | Unset = UNSET
    scale: int | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        weight = self.weight

        id = self.id

        scale: int | None | Unset
        if isinstance(self.scale, Unset):
            scale = UNSET
        else:
            scale = self.scale

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "weight": weight,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if scale is not UNSET:
            field_dict["scale"] = scale

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        weight = d.pop("weight")

        id = d.pop("id", UNSET)

        def _parse_scale(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        scale = _parse_scale(d.pop("scale", UNSET))

        create_metric_request_child_metrics_type_0_item = cls(
            name=name,
            weight=weight,
            id=id,
            scale=scale,
        )

        return create_metric_request_child_metrics_type_0_item
