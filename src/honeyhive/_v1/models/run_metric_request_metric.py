from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.run_metric_request_metric_return_type import (
    RunMetricRequestMetricReturnType,
)
from ..models.run_metric_request_metric_type import RunMetricRequestMetricType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_metric_request_metric_categories_type_0_item import (
        RunMetricRequestMetricCategoriesType0Item,
    )
    from ..models.run_metric_request_metric_child_metrics_type_0_item import (
        RunMetricRequestMetricChildMetricsType0Item,
    )
    from ..models.run_metric_request_metric_filters import RunMetricRequestMetricFilters
    from ..models.run_metric_request_metric_threshold_type_0 import (
        RunMetricRequestMetricThresholdType0,
    )


T = TypeVar("T", bound="RunMetricRequestMetric")


@_attrs_define
class RunMetricRequestMetric:
    """
    Attributes:
        name (str):
        type_ (RunMetricRequestMetricType):
        criteria (str):
        description (str | Unset):  Default: ''.
        return_type (RunMetricRequestMetricReturnType | Unset):  Default: RunMetricRequestMetricReturnType.FLOAT.
        enabled_in_prod (bool | Unset):  Default: False.
        needs_ground_truth (bool | Unset):  Default: False.
        sampling_percentage (float | Unset):  Default: 100.0.
        model_provider (None | str | Unset):
        model_name (None | str | Unset):
        scale (int | None | Unset):
        threshold (None | RunMetricRequestMetricThresholdType0 | Unset):
        categories (list[RunMetricRequestMetricCategoriesType0Item] | None | Unset):
        child_metrics (list[RunMetricRequestMetricChildMetricsType0Item] | None | Unset):
        filters (RunMetricRequestMetricFilters | Unset):
    """

    name: str
    type_: RunMetricRequestMetricType
    criteria: str
    description: str | Unset = ""
    return_type: RunMetricRequestMetricReturnType | Unset = (
        RunMetricRequestMetricReturnType.FLOAT
    )
    enabled_in_prod: bool | Unset = False
    needs_ground_truth: bool | Unset = False
    sampling_percentage: float | Unset = 100.0
    model_provider: None | str | Unset = UNSET
    model_name: None | str | Unset = UNSET
    scale: int | None | Unset = UNSET
    threshold: None | RunMetricRequestMetricThresholdType0 | Unset = UNSET
    categories: list[RunMetricRequestMetricCategoriesType0Item] | None | Unset = UNSET
    child_metrics: list[RunMetricRequestMetricChildMetricsType0Item] | None | Unset = (
        UNSET
    )
    filters: RunMetricRequestMetricFilters | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.run_metric_request_metric_threshold_type_0 import (
            RunMetricRequestMetricThresholdType0,
        )

        name = self.name

        type_ = self.type_.value

        criteria = self.criteria

        description = self.description

        return_type: str | Unset = UNSET
        if not isinstance(self.return_type, Unset):
            return_type = self.return_type.value

        enabled_in_prod = self.enabled_in_prod

        needs_ground_truth = self.needs_ground_truth

        sampling_percentage = self.sampling_percentage

        model_provider: None | str | Unset
        if isinstance(self.model_provider, Unset):
            model_provider = UNSET
        else:
            model_provider = self.model_provider

        model_name: None | str | Unset
        if isinstance(self.model_name, Unset):
            model_name = UNSET
        else:
            model_name = self.model_name

        scale: int | None | Unset
        if isinstance(self.scale, Unset):
            scale = UNSET
        else:
            scale = self.scale

        threshold: dict[str, Any] | None | Unset
        if isinstance(self.threshold, Unset):
            threshold = UNSET
        elif isinstance(self.threshold, RunMetricRequestMetricThresholdType0):
            threshold = self.threshold.to_dict()
        else:
            threshold = self.threshold

        categories: list[dict[str, Any]] | None | Unset
        if isinstance(self.categories, Unset):
            categories = UNSET
        elif isinstance(self.categories, list):
            categories = []
            for categories_type_0_item_data in self.categories:
                categories_type_0_item = categories_type_0_item_data.to_dict()
                categories.append(categories_type_0_item)

        else:
            categories = self.categories

        child_metrics: list[dict[str, Any]] | None | Unset
        if isinstance(self.child_metrics, Unset):
            child_metrics = UNSET
        elif isinstance(self.child_metrics, list):
            child_metrics = []
            for child_metrics_type_0_item_data in self.child_metrics:
                child_metrics_type_0_item = child_metrics_type_0_item_data.to_dict()
                child_metrics.append(child_metrics_type_0_item)

        else:
            child_metrics = self.child_metrics

        filters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "type": type_,
                "criteria": criteria,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if return_type is not UNSET:
            field_dict["return_type"] = return_type
        if enabled_in_prod is not UNSET:
            field_dict["enabled_in_prod"] = enabled_in_prod
        if needs_ground_truth is not UNSET:
            field_dict["needs_ground_truth"] = needs_ground_truth
        if sampling_percentage is not UNSET:
            field_dict["sampling_percentage"] = sampling_percentage
        if model_provider is not UNSET:
            field_dict["model_provider"] = model_provider
        if model_name is not UNSET:
            field_dict["model_name"] = model_name
        if scale is not UNSET:
            field_dict["scale"] = scale
        if threshold is not UNSET:
            field_dict["threshold"] = threshold
        if categories is not UNSET:
            field_dict["categories"] = categories
        if child_metrics is not UNSET:
            field_dict["child_metrics"] = child_metrics
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_metric_request_metric_categories_type_0_item import (
            RunMetricRequestMetricCategoriesType0Item,
        )
        from ..models.run_metric_request_metric_child_metrics_type_0_item import (
            RunMetricRequestMetricChildMetricsType0Item,
        )
        from ..models.run_metric_request_metric_filters import (
            RunMetricRequestMetricFilters,
        )
        from ..models.run_metric_request_metric_threshold_type_0 import (
            RunMetricRequestMetricThresholdType0,
        )

        d = dict(src_dict)
        name = d.pop("name")

        type_ = RunMetricRequestMetricType(d.pop("type"))

        criteria = d.pop("criteria")

        description = d.pop("description", UNSET)

        _return_type = d.pop("return_type", UNSET)
        return_type: RunMetricRequestMetricReturnType | Unset
        if isinstance(_return_type, Unset):
            return_type = UNSET
        else:
            return_type = RunMetricRequestMetricReturnType(_return_type)

        enabled_in_prod = d.pop("enabled_in_prod", UNSET)

        needs_ground_truth = d.pop("needs_ground_truth", UNSET)

        sampling_percentage = d.pop("sampling_percentage", UNSET)

        def _parse_model_provider(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        model_provider = _parse_model_provider(d.pop("model_provider", UNSET))

        def _parse_model_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        model_name = _parse_model_name(d.pop("model_name", UNSET))

        def _parse_scale(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        scale = _parse_scale(d.pop("scale", UNSET))

        def _parse_threshold(
            data: object,
        ) -> None | RunMetricRequestMetricThresholdType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                threshold_type_0 = RunMetricRequestMetricThresholdType0.from_dict(data)

                return threshold_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RunMetricRequestMetricThresholdType0 | Unset, data)

        threshold = _parse_threshold(d.pop("threshold", UNSET))

        def _parse_categories(
            data: object,
        ) -> list[RunMetricRequestMetricCategoriesType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                categories_type_0 = []
                _categories_type_0 = data
                for categories_type_0_item_data in _categories_type_0:
                    categories_type_0_item = (
                        RunMetricRequestMetricCategoriesType0Item.from_dict(
                            categories_type_0_item_data
                        )
                    )

                    categories_type_0.append(categories_type_0_item)

                return categories_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                list[RunMetricRequestMetricCategoriesType0Item] | None | Unset, data
            )

        categories = _parse_categories(d.pop("categories", UNSET))

        def _parse_child_metrics(
            data: object,
        ) -> list[RunMetricRequestMetricChildMetricsType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                child_metrics_type_0 = []
                _child_metrics_type_0 = data
                for child_metrics_type_0_item_data in _child_metrics_type_0:
                    child_metrics_type_0_item = (
                        RunMetricRequestMetricChildMetricsType0Item.from_dict(
                            child_metrics_type_0_item_data
                        )
                    )

                    child_metrics_type_0.append(child_metrics_type_0_item)

                return child_metrics_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                list[RunMetricRequestMetricChildMetricsType0Item] | None | Unset, data
            )

        child_metrics = _parse_child_metrics(d.pop("child_metrics", UNSET))

        _filters = d.pop("filters", UNSET)
        filters: RunMetricRequestMetricFilters | Unset
        if isinstance(_filters, Unset):
            filters = UNSET
        else:
            filters = RunMetricRequestMetricFilters.from_dict(_filters)

        run_metric_request_metric = cls(
            name=name,
            type_=type_,
            criteria=criteria,
            description=description,
            return_type=return_type,
            enabled_in_prod=enabled_in_prod,
            needs_ground_truth=needs_ground_truth,
            sampling_percentage=sampling_percentage,
            model_provider=model_provider,
            model_name=model_name,
            scale=scale,
            threshold=threshold,
            categories=categories,
            child_metrics=child_metrics,
            filters=filters,
        )

        return run_metric_request_metric
