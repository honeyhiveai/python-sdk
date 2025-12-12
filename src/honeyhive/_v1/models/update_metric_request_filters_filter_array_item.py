from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_metric_request_filters_filter_array_item_operator_type_0 import (
    UpdateMetricRequestFiltersFilterArrayItemOperatorType0,
)
from ..models.update_metric_request_filters_filter_array_item_operator_type_1 import (
    UpdateMetricRequestFiltersFilterArrayItemOperatorType1,
)
from ..models.update_metric_request_filters_filter_array_item_operator_type_2 import (
    UpdateMetricRequestFiltersFilterArrayItemOperatorType2,
)
from ..models.update_metric_request_filters_filter_array_item_operator_type_3 import (
    UpdateMetricRequestFiltersFilterArrayItemOperatorType3,
)
from ..models.update_metric_request_filters_filter_array_item_type import (
    UpdateMetricRequestFiltersFilterArrayItemType,
)

T = TypeVar("T", bound="UpdateMetricRequestFiltersFilterArrayItem")


@_attrs_define
class UpdateMetricRequestFiltersFilterArrayItem:
    """
    Attributes:
        field (str):
        operator (UpdateMetricRequestFiltersFilterArrayItemOperatorType0 |
            UpdateMetricRequestFiltersFilterArrayItemOperatorType1 | UpdateMetricRequestFiltersFilterArrayItemOperatorType2
            | UpdateMetricRequestFiltersFilterArrayItemOperatorType3):
        value (bool | float | None | str):
        type_ (UpdateMetricRequestFiltersFilterArrayItemType):
    """

    field: str
    operator: (
        UpdateMetricRequestFiltersFilterArrayItemOperatorType0
        | UpdateMetricRequestFiltersFilterArrayItemOperatorType1
        | UpdateMetricRequestFiltersFilterArrayItemOperatorType2
        | UpdateMetricRequestFiltersFilterArrayItemOperatorType3
    )
    value: bool | float | None | str
    type_: UpdateMetricRequestFiltersFilterArrayItemType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field = self.field

        operator: str
        if isinstance(
            self.operator, UpdateMetricRequestFiltersFilterArrayItemOperatorType0
        ):
            operator = self.operator.value
        elif isinstance(
            self.operator, UpdateMetricRequestFiltersFilterArrayItemOperatorType1
        ):
            operator = self.operator.value
        elif isinstance(
            self.operator, UpdateMetricRequestFiltersFilterArrayItemOperatorType2
        ):
            operator = self.operator.value
        else:
            operator = self.operator.value

        value: bool | float | None | str
        value = self.value

        type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
                "operator": operator,
                "value": value,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field = d.pop("field")

        def _parse_operator(
            data: object,
        ) -> (
            UpdateMetricRequestFiltersFilterArrayItemOperatorType0
            | UpdateMetricRequestFiltersFilterArrayItemOperatorType1
            | UpdateMetricRequestFiltersFilterArrayItemOperatorType2
            | UpdateMetricRequestFiltersFilterArrayItemOperatorType3
        ):
            try:
                if not isinstance(data, str):
                    raise TypeError()
                operator_type_0 = (
                    UpdateMetricRequestFiltersFilterArrayItemOperatorType0(data)
                )

                return operator_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                operator_type_1 = (
                    UpdateMetricRequestFiltersFilterArrayItemOperatorType1(data)
                )

                return operator_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                operator_type_2 = (
                    UpdateMetricRequestFiltersFilterArrayItemOperatorType2(data)
                )

                return operator_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, str):
                raise TypeError()
            operator_type_3 = UpdateMetricRequestFiltersFilterArrayItemOperatorType3(
                data
            )

            return operator_type_3

        operator = _parse_operator(d.pop("operator"))

        def _parse_value(data: object) -> bool | float | None | str:
            if data is None:
                return data
            return cast(bool | float | None | str, data)

        value = _parse_value(d.pop("value"))

        type_ = UpdateMetricRequestFiltersFilterArrayItemType(d.pop("type"))

        update_metric_request_filters_filter_array_item = cls(
            field=field,
            operator=operator,
            value=value,
            type_=type_,
        )

        update_metric_request_filters_filter_array_item.additional_properties = d
        return update_metric_request_filters_filter_array_item

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
