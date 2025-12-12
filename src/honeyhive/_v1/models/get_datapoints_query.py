from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDatapointsQuery")


@_attrs_define
class GetDatapointsQuery:
    """
    Attributes:
        datapoint_ids (list[str] | Unset):
        dataset_name (str | Unset):
    """

    datapoint_ids: list[str] | Unset = UNSET
    dataset_name: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        datapoint_ids: list[str] | Unset = UNSET
        if not isinstance(self.datapoint_ids, Unset):
            datapoint_ids = self.datapoint_ids

        dataset_name = self.dataset_name

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if datapoint_ids is not UNSET:
            field_dict["datapoint_ids"] = datapoint_ids
        if dataset_name is not UNSET:
            field_dict["dataset_name"] = dataset_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        datapoint_ids = cast(list[str], d.pop("datapoint_ids", UNSET))

        dataset_name = d.pop("dataset_name", UNSET)

        get_datapoints_query = cls(
            datapoint_ids=datapoint_ids,
            dataset_name=dataset_name,
        )

        return get_datapoints_query
