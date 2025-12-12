from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_experiment_runs_schema_query_date_range_type_1 import (
        GetExperimentRunsSchemaQueryDateRangeType1,
    )


T = TypeVar("T", bound="GetExperimentRunsSchemaQuery")


@_attrs_define
class GetExperimentRunsSchemaQuery:
    """
    Attributes:
        date_range (GetExperimentRunsSchemaQueryDateRangeType1 | str | Unset):
        evaluation_id (str | Unset):
    """

    date_range: GetExperimentRunsSchemaQueryDateRangeType1 | str | Unset = UNSET
    evaluation_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_experiment_runs_schema_query_date_range_type_1 import (
            GetExperimentRunsSchemaQueryDateRangeType1,
        )

        date_range: dict[str, Any] | str | Unset
        if isinstance(self.date_range, Unset):
            date_range = UNSET
        elif isinstance(self.date_range, GetExperimentRunsSchemaQueryDateRangeType1):
            date_range = self.date_range.to_dict()
        else:
            date_range = self.date_range

        evaluation_id = self.evaluation_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if date_range is not UNSET:
            field_dict["dateRange"] = date_range
        if evaluation_id is not UNSET:
            field_dict["evaluation_id"] = evaluation_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_experiment_runs_schema_query_date_range_type_1 import (
            GetExperimentRunsSchemaQueryDateRangeType1,
        )

        d = dict(src_dict)

        def _parse_date_range(
            data: object,
        ) -> GetExperimentRunsSchemaQueryDateRangeType1 | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                date_range_type_1 = (
                    GetExperimentRunsSchemaQueryDateRangeType1.from_dict(data)
                )

                return date_range_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GetExperimentRunsSchemaQueryDateRangeType1 | str | Unset, data)

        date_range = _parse_date_range(d.pop("dateRange", UNSET))

        evaluation_id = d.pop("evaluation_id", UNSET)

        get_experiment_runs_schema_query = cls(
            date_range=date_range,
            evaluation_id=evaluation_id,
        )

        get_experiment_runs_schema_query.additional_properties = d
        return get_experiment_runs_schema_query

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
