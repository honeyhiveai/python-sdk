from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_datapoint_request_ground_truth import (
        UpdateDatapointRequestGroundTruth,
    )
    from ..models.update_datapoint_request_history_item import (
        UpdateDatapointRequestHistoryItem,
    )
    from ..models.update_datapoint_request_inputs import UpdateDatapointRequestInputs
    from ..models.update_datapoint_request_metadata import (
        UpdateDatapointRequestMetadata,
    )


T = TypeVar("T", bound="UpdateDatapointRequest")


@_attrs_define
class UpdateDatapointRequest:
    """
    Attributes:
        inputs (UpdateDatapointRequestInputs | Unset):
        history (list[UpdateDatapointRequestHistoryItem] | Unset):
        ground_truth (UpdateDatapointRequestGroundTruth | Unset):
        metadata (UpdateDatapointRequestMetadata | Unset):
        linked_event (str | Unset):
        linked_datasets (list[str] | Unset):
    """

    inputs: UpdateDatapointRequestInputs | Unset = UNSET
    history: list[UpdateDatapointRequestHistoryItem] | Unset = UNSET
    ground_truth: UpdateDatapointRequestGroundTruth | Unset = UNSET
    metadata: UpdateDatapointRequestMetadata | Unset = UNSET
    linked_event: str | Unset = UNSET
    linked_datasets: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        inputs: dict[str, Any] | Unset = UNSET
        if not isinstance(self.inputs, Unset):
            inputs = self.inputs.to_dict()

        history: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.history, Unset):
            history = []
            for history_item_data in self.history:
                history_item = history_item_data.to_dict()
                history.append(history_item)

        ground_truth: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ground_truth, Unset):
            ground_truth = self.ground_truth.to_dict()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        linked_event = self.linked_event

        linked_datasets: list[str] | Unset = UNSET
        if not isinstance(self.linked_datasets, Unset):
            linked_datasets = self.linked_datasets

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if inputs is not UNSET:
            field_dict["inputs"] = inputs
        if history is not UNSET:
            field_dict["history"] = history
        if ground_truth is not UNSET:
            field_dict["ground_truth"] = ground_truth
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if linked_event is not UNSET:
            field_dict["linked_event"] = linked_event
        if linked_datasets is not UNSET:
            field_dict["linked_datasets"] = linked_datasets

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_datapoint_request_ground_truth import (
            UpdateDatapointRequestGroundTruth,
        )
        from ..models.update_datapoint_request_history_item import (
            UpdateDatapointRequestHistoryItem,
        )
        from ..models.update_datapoint_request_inputs import (
            UpdateDatapointRequestInputs,
        )
        from ..models.update_datapoint_request_metadata import (
            UpdateDatapointRequestMetadata,
        )

        d = dict(src_dict)
        _inputs = d.pop("inputs", UNSET)
        inputs: UpdateDatapointRequestInputs | Unset
        if isinstance(_inputs, Unset):
            inputs = UNSET
        else:
            inputs = UpdateDatapointRequestInputs.from_dict(_inputs)

        _history = d.pop("history", UNSET)
        history: list[UpdateDatapointRequestHistoryItem] | Unset = UNSET
        if _history is not UNSET:
            history = []
            for history_item_data in _history:
                history_item = UpdateDatapointRequestHistoryItem.from_dict(
                    history_item_data
                )

                history.append(history_item)

        _ground_truth = d.pop("ground_truth", UNSET)
        ground_truth: UpdateDatapointRequestGroundTruth | Unset
        if isinstance(_ground_truth, Unset):
            ground_truth = UNSET
        else:
            ground_truth = UpdateDatapointRequestGroundTruth.from_dict(_ground_truth)

        _metadata = d.pop("metadata", UNSET)
        metadata: UpdateDatapointRequestMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UpdateDatapointRequestMetadata.from_dict(_metadata)

        linked_event = d.pop("linked_event", UNSET)

        linked_datasets = cast(list[str], d.pop("linked_datasets", UNSET))

        update_datapoint_request = cls(
            inputs=inputs,
            history=history,
            ground_truth=ground_truth,
            metadata=metadata,
            linked_event=linked_event,
            linked_datasets=linked_datasets,
        )

        update_datapoint_request.additional_properties = d
        return update_datapoint_request

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
