from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.session_start_request import SessionStartRequest


T = TypeVar("T", bound="StartSessionBody")


@_attrs_define
class StartSessionBody:
    """
    Attributes:
        session (SessionStartRequest | Unset):
    """

    session: SessionStartRequest | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session: dict[str, Any] | Unset = UNSET
        if not isinstance(self.session, Unset):
            session = self.session.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if session is not UNSET:
            field_dict["session"] = session

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.session_start_request import SessionStartRequest

        d = dict(src_dict)
        _session = d.pop("session", UNSET)
        session: SessionStartRequest | Unset
        if isinstance(_session, Unset):
            session = UNSET
        else:
            session = SessionStartRequest.from_dict(_session)

        start_session_body = cls(
            session=session,
        )

        start_session_body.additional_properties = d
        return start_session_body

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
