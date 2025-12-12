from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_metrics_response_item_filters_filter_array_item_operator_type_0 import (
    GetMetricsResponseItemFiltersFilterArrayItemOperatorType0,
)
from ..models.get_metrics_response_item_filters_filter_array_item_operator_type_1 import (
    GetMetricsResponseItemFiltersFilterArrayItemOperatorType1,
)
from ..models.get_metrics_response_item_filters_filter_array_item_operator_type_2 import (
    GetMetricsResponseItemFiltersFilterArrayItemOperatorType2,
)
from ..models.get_metrics_response_item_filters_filter_array_item_operator_type_3 import (
    GetMetricsResponseItemFiltersFilterArrayItemOperatorType3,
)
from ..models.get_metrics_response_item_filters_filter_array_item_type import (
    GetMetricsResponseItemFiltersFilterArrayItemType,
)

T = TypeVar("T", bound="GetMetricsResponseItemFiltersFilterArrayItem")


@_attrs_define
class GetMetricsResponseItemFiltersFilterArrayItem:
    """
    Attributes:
        field (str):
        operator (GetMetricsResponseItemFiltersFilterArrayItemOperatorType0 |
            GetMetricsResponseItemFiltersFilterArrayItemOperatorType1 |
            GetMetricsResponseItemFiltersFilterArrayItemOperatorType2 |
            GetMetricsResponseItemFiltersFilterArrayItemOperatorType3):
        value (bool | float | None | str):
        type_ (GetMetricsResponseItemFiltersFilterArrayItemType):
    """

    field: str
    operator: (
        GetMetricsResponseItemFiltersFilterArrayItemOperatorType0
        | GetMetricsResponseItemFiltersFilterArrayItemOperatorType1
        | GetMetricsResponseItemFiltersFilterArrayItemOperatorType2
        | GetMetricsResponseItemFiltersFilterArrayItemOperatorType3
    )
    value: bool | float | None | str
    type_: GetMetricsResponseItemFiltersFilterArrayItemType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field = self.field

        operator: str
        if isinstance(
            self.operator, GetMetricsResponseItemFiltersFilterArrayItemOperatorType0
        ):
            operator = self.operator.value
        elif isinstance(
            self.operator, GetMetricsResponseItemFiltersFilterArrayItemOperatorType1
        ):
            operator = self.operator.value
        elif isinstance(
            self.operator, GetMetricsResponseItemFiltersFilterArrayItemOperatorType2
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
            GetMetricsResponseItemFiltersFilterArrayItemOperatorType0
            | GetMetricsResponseItemFiltersFilterArrayItemOperatorType1
            | GetMetricsResponseItemFiltersFilterArrayItemOperatorType2
            | GetMetricsResponseItemFiltersFilterArrayItemOperatorType3
        ):
            try:
                if not isinstance(data, str):
                    raise TypeError()
                operator_type_0 = (
                    GetMetricsResponseItemFiltersFilterArrayItemOperatorType0(data)
                )

                return operator_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                operator_type_1 = (
                    GetMetricsResponseItemFiltersFilterArrayItemOperatorType1(data)
                )

                return operator_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, str):
                    raise TypeError()
                operator_type_2 = (
                    GetMetricsResponseItemFiltersFilterArrayItemOperatorType2(data)
                )

                return operator_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, str):
                raise TypeError()
            operator_type_3 = GetMetricsResponseItemFiltersFilterArrayItemOperatorType3(
                data
            )

            return operator_type_3

        operator = _parse_operator(d.pop("operator"))

        def _parse_value(data: object) -> bool | float | None | str:
            if data is None:
                return data
            return cast(bool | float | None | str, data)

        value = _parse_value(d.pop("value"))

        type_ = GetMetricsResponseItemFiltersFilterArrayItemType(d.pop("type"))

        get_metrics_response_item_filters_filter_array_item = cls(
            field=field,
            operator=operator,
            value=value,
            type_=type_,
        )

        get_metrics_response_item_filters_filter_array_item.additional_properties = d
        return get_metrics_response_item_filters_filter_array_item

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
