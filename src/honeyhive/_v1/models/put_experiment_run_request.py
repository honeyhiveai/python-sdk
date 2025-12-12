from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.put_experiment_run_request_status import PutExperimentRunRequestStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.put_experiment_run_request_configuration import (
        PutExperimentRunRequestConfiguration,
    )
    from ..models.put_experiment_run_request_metadata import (
        PutExperimentRunRequestMetadata,
    )
    from ..models.put_experiment_run_request_passing_ranges import (
        PutExperimentRunRequestPassingRanges,
    )
    from ..models.put_experiment_run_request_results import (
        PutExperimentRunRequestResults,
    )


T = TypeVar("T", bound="PutExperimentRunRequest")


@_attrs_define
class PutExperimentRunRequest:
    """
    Attributes:
        name (str | Unset):
        description (str | Unset):
        status (PutExperimentRunRequestStatus | Unset):
        metadata (PutExperimentRunRequestMetadata | Unset):
        results (PutExperimentRunRequestResults | Unset):
        event_ids (list[str] | Unset):
        configuration (PutExperimentRunRequestConfiguration | Unset):
        evaluators (list[Any] | Unset):
        session_ids (list[str] | Unset):
        datapoint_ids (list[str] | Unset):
        passing_ranges (PutExperimentRunRequestPassingRanges | Unset):
    """

    name: str | Unset = UNSET
    description: str | Unset = UNSET
    status: PutExperimentRunRequestStatus | Unset = UNSET
    metadata: PutExperimentRunRequestMetadata | Unset = UNSET
    results: PutExperimentRunRequestResults | Unset = UNSET
    event_ids: list[str] | Unset = UNSET
    configuration: PutExperimentRunRequestConfiguration | Unset = UNSET
    evaluators: list[Any] | Unset = UNSET
    session_ids: list[str] | Unset = UNSET
    datapoint_ids: list[str] | Unset = UNSET
    passing_ranges: PutExperimentRunRequestPassingRanges | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        results: dict[str, Any] | Unset = UNSET
        if not isinstance(self.results, Unset):
            results = self.results.to_dict()

        event_ids: list[str] | Unset = UNSET
        if not isinstance(self.event_ids, Unset):
            event_ids = self.event_ids

        configuration: dict[str, Any] | Unset = UNSET
        if not isinstance(self.configuration, Unset):
            configuration = self.configuration.to_dict()

        evaluators: list[Any] | Unset = UNSET
        if not isinstance(self.evaluators, Unset):
            evaluators = self.evaluators

        session_ids: list[str] | Unset = UNSET
        if not isinstance(self.session_ids, Unset):
            session_ids = self.session_ids

        datapoint_ids: list[str] | Unset = UNSET
        if not isinstance(self.datapoint_ids, Unset):
            datapoint_ids = self.datapoint_ids

        passing_ranges: dict[str, Any] | Unset = UNSET
        if not isinstance(self.passing_ranges, Unset):
            passing_ranges = self.passing_ranges.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if status is not UNSET:
            field_dict["status"] = status
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if results is not UNSET:
            field_dict["results"] = results
        if event_ids is not UNSET:
            field_dict["event_ids"] = event_ids
        if configuration is not UNSET:
            field_dict["configuration"] = configuration
        if evaluators is not UNSET:
            field_dict["evaluators"] = evaluators
        if session_ids is not UNSET:
            field_dict["session_ids"] = session_ids
        if datapoint_ids is not UNSET:
            field_dict["datapoint_ids"] = datapoint_ids
        if passing_ranges is not UNSET:
            field_dict["passing_ranges"] = passing_ranges

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.put_experiment_run_request_configuration import (
            PutExperimentRunRequestConfiguration,
        )
        from ..models.put_experiment_run_request_metadata import (
            PutExperimentRunRequestMetadata,
        )
        from ..models.put_experiment_run_request_passing_ranges import (
            PutExperimentRunRequestPassingRanges,
        )
        from ..models.put_experiment_run_request_results import (
            PutExperimentRunRequestResults,
        )

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        _status = d.pop("status", UNSET)
        status: PutExperimentRunRequestStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = PutExperimentRunRequestStatus(_status)

        _metadata = d.pop("metadata", UNSET)
        metadata: PutExperimentRunRequestMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PutExperimentRunRequestMetadata.from_dict(_metadata)

        _results = d.pop("results", UNSET)
        results: PutExperimentRunRequestResults | Unset
        if isinstance(_results, Unset):
            results = UNSET
        else:
            results = PutExperimentRunRequestResults.from_dict(_results)

        event_ids = cast(list[str], d.pop("event_ids", UNSET))

        _configuration = d.pop("configuration", UNSET)
        configuration: PutExperimentRunRequestConfiguration | Unset
        if isinstance(_configuration, Unset):
            configuration = UNSET
        else:
            configuration = PutExperimentRunRequestConfiguration.from_dict(
                _configuration
            )

        evaluators = cast(list[Any], d.pop("evaluators", UNSET))

        session_ids = cast(list[str], d.pop("session_ids", UNSET))

        datapoint_ids = cast(list[str], d.pop("datapoint_ids", UNSET))

        _passing_ranges = d.pop("passing_ranges", UNSET)
        passing_ranges: PutExperimentRunRequestPassingRanges | Unset
        if isinstance(_passing_ranges, Unset):
            passing_ranges = UNSET
        else:
            passing_ranges = PutExperimentRunRequestPassingRanges.from_dict(
                _passing_ranges
            )

        put_experiment_run_request = cls(
            name=name,
            description=description,
            status=status,
            metadata=metadata,
            results=results,
            event_ids=event_ids,
            configuration=configuration,
            evaluators=evaluators,
            session_ids=session_ids,
            datapoint_ids=datapoint_ids,
            passing_ranges=passing_ranges,
        )

        put_experiment_run_request.additional_properties = d
        return put_experiment_run_request

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
