from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="UpdateConfigurationParams")


@_attrs_define
class UpdateConfigurationParams:
    """
    Attributes:
        config_id (str):
    """

    config_id: str

    def to_dict(self) -> dict[str, Any]:
        config_id = self.config_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "configId": config_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        config_id = d.pop("configId")

        update_configuration_params = cls(
            config_id=config_id,
        )

        return update_configuration_params
