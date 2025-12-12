from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.session_start_request_config import SessionStartRequestConfig
    from ..models.session_start_request_feedback import SessionStartRequestFeedback
    from ..models.session_start_request_inputs import SessionStartRequestInputs
    from ..models.session_start_request_metadata import SessionStartRequestMetadata
    from ..models.session_start_request_metrics import SessionStartRequestMetrics
    from ..models.session_start_request_outputs import SessionStartRequestOutputs
    from ..models.session_start_request_user_properties import (
        SessionStartRequestUserProperties,
    )


T = TypeVar("T", bound="SessionStartRequest")


@_attrs_define
class SessionStartRequest:
    """
    Attributes:
        project (str): Project name associated with the session
        session_name (str | Unset): Name of the session
        source (str | Unset): Source of the session - production, staging, etc
        session_id (str | Unset): Unique id of the session, if not set, it will be auto-generated
        children_ids (list[str] | Unset): Id of events that are nested within the session
        config (SessionStartRequestConfig | Unset): Associated configuration for the session
        inputs (SessionStartRequestInputs | Unset): Input object passed to the session
        outputs (SessionStartRequestOutputs | Unset): Final output of the session
        error (str | Unset): Any error description if session failed
        duration (float | Unset): How long the session took in milliseconds
        user_properties (SessionStartRequestUserProperties | Unset): Any user properties associated with the session
        metrics (SessionStartRequestMetrics | Unset): Any values computed over the output of the session
        feedback (SessionStartRequestFeedback | Unset): User feedback for the session
        metadata (SessionStartRequestMetadata | Unset): Any metadata associated with the session
    """

    project: str
    session_name: str | Unset = UNSET
    source: str | Unset = UNSET
    session_id: str | Unset = UNSET
    children_ids: list[str] | Unset = UNSET
    config: SessionStartRequestConfig | Unset = UNSET
    inputs: SessionStartRequestInputs | Unset = UNSET
    outputs: SessionStartRequestOutputs | Unset = UNSET
    error: str | Unset = UNSET
    duration: float | Unset = UNSET
    user_properties: SessionStartRequestUserProperties | Unset = UNSET
    metrics: SessionStartRequestMetrics | Unset = UNSET
    feedback: SessionStartRequestFeedback | Unset = UNSET
    metadata: SessionStartRequestMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project

        session_name = self.session_name

        source = self.source

        session_id = self.session_id

        children_ids: list[str] | Unset = UNSET
        if not isinstance(self.children_ids, Unset):
            children_ids = self.children_ids

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        inputs: dict[str, Any] | Unset = UNSET
        if not isinstance(self.inputs, Unset):
            inputs = self.inputs.to_dict()

        outputs: dict[str, Any] | Unset = UNSET
        if not isinstance(self.outputs, Unset):
            outputs = self.outputs.to_dict()

        error = self.error

        duration = self.duration

        user_properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user_properties, Unset):
            user_properties = self.user_properties.to_dict()

        metrics: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = self.metrics.to_dict()

        feedback: dict[str, Any] | Unset = UNSET
        if not isinstance(self.feedback, Unset):
            feedback = self.feedback.to_dict()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
            }
        )
        if session_name is not UNSET:
            field_dict["session_name"] = session_name
        if source is not UNSET:
            field_dict["source"] = source
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if children_ids is not UNSET:
            field_dict["children_ids"] = children_ids
        if config is not UNSET:
            field_dict["config"] = config
        if inputs is not UNSET:
            field_dict["inputs"] = inputs
        if outputs is not UNSET:
            field_dict["outputs"] = outputs
        if error is not UNSET:
            field_dict["error"] = error
        if duration is not UNSET:
            field_dict["duration"] = duration
        if user_properties is not UNSET:
            field_dict["user_properties"] = user_properties
        if metrics is not UNSET:
            field_dict["metrics"] = metrics
        if feedback is not UNSET:
            field_dict["feedback"] = feedback
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.session_start_request_config import SessionStartRequestConfig
        from ..models.session_start_request_feedback import SessionStartRequestFeedback
        from ..models.session_start_request_inputs import SessionStartRequestInputs
        from ..models.session_start_request_metadata import SessionStartRequestMetadata
        from ..models.session_start_request_metrics import SessionStartRequestMetrics
        from ..models.session_start_request_outputs import SessionStartRequestOutputs
        from ..models.session_start_request_user_properties import (
            SessionStartRequestUserProperties,
        )

        d = dict(src_dict)
        project = d.pop("project")

        session_name = d.pop("session_name", UNSET)

        source = d.pop("source", UNSET)

        session_id = d.pop("session_id", UNSET)

        children_ids = cast(list[str], d.pop("children_ids", UNSET))

        _config = d.pop("config", UNSET)
        config: SessionStartRequestConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = SessionStartRequestConfig.from_dict(_config)

        _inputs = d.pop("inputs", UNSET)
        inputs: SessionStartRequestInputs | Unset
        if isinstance(_inputs, Unset):
            inputs = UNSET
        else:
            inputs = SessionStartRequestInputs.from_dict(_inputs)

        _outputs = d.pop("outputs", UNSET)
        outputs: SessionStartRequestOutputs | Unset
        if isinstance(_outputs, Unset):
            outputs = UNSET
        else:
            outputs = SessionStartRequestOutputs.from_dict(_outputs)

        error = d.pop("error", UNSET)

        duration = d.pop("duration", UNSET)

        _user_properties = d.pop("user_properties", UNSET)
        user_properties: SessionStartRequestUserProperties | Unset
        if isinstance(_user_properties, Unset):
            user_properties = UNSET
        else:
            user_properties = SessionStartRequestUserProperties.from_dict(
                _user_properties
            )

        _metrics = d.pop("metrics", UNSET)
        metrics: SessionStartRequestMetrics | Unset
        if isinstance(_metrics, Unset):
            metrics = UNSET
        else:
            metrics = SessionStartRequestMetrics.from_dict(_metrics)

        _feedback = d.pop("feedback", UNSET)
        feedback: SessionStartRequestFeedback | Unset
        if isinstance(_feedback, Unset):
            feedback = UNSET
        else:
            feedback = SessionStartRequestFeedback.from_dict(_feedback)

        _metadata = d.pop("metadata", UNSET)
        metadata: SessionStartRequestMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = SessionStartRequestMetadata.from_dict(_metadata)

        session_start_request = cls(
            project=project,
            session_name=session_name,
            source=source,
            session_id=session_id,
            children_ids=children_ids,
            config=config,
            inputs=inputs,
            outputs=outputs,
            error=error,
            duration=duration,
            user_properties=user_properties,
            metrics=metrics,
            feedback=feedback,
            metadata=metadata,
        )

        session_start_request.additional_properties = d
        return session_start_request

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
