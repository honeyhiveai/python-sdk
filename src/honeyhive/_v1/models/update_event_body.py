from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_event_body_config import UpdateEventBodyConfig
    from ..models.update_event_body_feedback import UpdateEventBodyFeedback
    from ..models.update_event_body_metadata import UpdateEventBodyMetadata
    from ..models.update_event_body_metrics import UpdateEventBodyMetrics
    from ..models.update_event_body_outputs import UpdateEventBodyOutputs
    from ..models.update_event_body_user_properties import UpdateEventBodyUserProperties


T = TypeVar("T", bound="UpdateEventBody")


@_attrs_define
class UpdateEventBody:
    """
    Attributes:
        event_id (str):
        metadata (UpdateEventBodyMetadata | Unset):
        feedback (UpdateEventBodyFeedback | Unset):
        metrics (UpdateEventBodyMetrics | Unset):
        outputs (UpdateEventBodyOutputs | Unset):
        config (UpdateEventBodyConfig | Unset):
        user_properties (UpdateEventBodyUserProperties | Unset):
        duration (float | Unset):
    """

    event_id: str
    metadata: UpdateEventBodyMetadata | Unset = UNSET
    feedback: UpdateEventBodyFeedback | Unset = UNSET
    metrics: UpdateEventBodyMetrics | Unset = UNSET
    outputs: UpdateEventBodyOutputs | Unset = UNSET
    config: UpdateEventBodyConfig | Unset = UNSET
    user_properties: UpdateEventBodyUserProperties | Unset = UNSET
    duration: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_id = self.event_id

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        feedback: dict[str, Any] | Unset = UNSET
        if not isinstance(self.feedback, Unset):
            feedback = self.feedback.to_dict()

        metrics: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = self.metrics.to_dict()

        outputs: dict[str, Any] | Unset = UNSET
        if not isinstance(self.outputs, Unset):
            outputs = self.outputs.to_dict()

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        user_properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user_properties, Unset):
            user_properties = self.user_properties.to_dict()

        duration = self.duration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event_id": event_id,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if feedback is not UNSET:
            field_dict["feedback"] = feedback
        if metrics is not UNSET:
            field_dict["metrics"] = metrics
        if outputs is not UNSET:
            field_dict["outputs"] = outputs
        if config is not UNSET:
            field_dict["config"] = config
        if user_properties is not UNSET:
            field_dict["user_properties"] = user_properties
        if duration is not UNSET:
            field_dict["duration"] = duration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_event_body_config import UpdateEventBodyConfig
        from ..models.update_event_body_feedback import UpdateEventBodyFeedback
        from ..models.update_event_body_metadata import UpdateEventBodyMetadata
        from ..models.update_event_body_metrics import UpdateEventBodyMetrics
        from ..models.update_event_body_outputs import UpdateEventBodyOutputs
        from ..models.update_event_body_user_properties import (
            UpdateEventBodyUserProperties,
        )

        d = dict(src_dict)
        event_id = d.pop("event_id")

        _metadata = d.pop("metadata", UNSET)
        metadata: UpdateEventBodyMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UpdateEventBodyMetadata.from_dict(_metadata)

        _feedback = d.pop("feedback", UNSET)
        feedback: UpdateEventBodyFeedback | Unset
        if isinstance(_feedback, Unset):
            feedback = UNSET
        else:
            feedback = UpdateEventBodyFeedback.from_dict(_feedback)

        _metrics = d.pop("metrics", UNSET)
        metrics: UpdateEventBodyMetrics | Unset
        if isinstance(_metrics, Unset):
            metrics = UNSET
        else:
            metrics = UpdateEventBodyMetrics.from_dict(_metrics)

        _outputs = d.pop("outputs", UNSET)
        outputs: UpdateEventBodyOutputs | Unset
        if isinstance(_outputs, Unset):
            outputs = UNSET
        else:
            outputs = UpdateEventBodyOutputs.from_dict(_outputs)

        _config = d.pop("config", UNSET)
        config: UpdateEventBodyConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = UpdateEventBodyConfig.from_dict(_config)

        _user_properties = d.pop("user_properties", UNSET)
        user_properties: UpdateEventBodyUserProperties | Unset
        if isinstance(_user_properties, Unset):
            user_properties = UNSET
        else:
            user_properties = UpdateEventBodyUserProperties.from_dict(_user_properties)

        duration = d.pop("duration", UNSET)

        update_event_body = cls(
            event_id=event_id,
            metadata=metadata,
            feedback=feedback,
            metrics=metrics,
            outputs=outputs,
            config=config,
            user_properties=user_properties,
            duration=duration,
        )

        update_event_body.additional_properties = d
        return update_event_body

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
