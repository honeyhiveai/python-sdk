from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_configurations_response_item_env_item import (
    GetConfigurationsResponseItemEnvItem,
)
from ..models.get_configurations_response_item_type import (
    GetConfigurationsResponseItemType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_configurations_response_item_parameters import (
        GetConfigurationsResponseItemParameters,
    )
    from ..models.get_configurations_response_item_user_properties_type_0 import (
        GetConfigurationsResponseItemUserPropertiesType0,
    )


T = TypeVar("T", bound="GetConfigurationsResponseItem")


@_attrs_define
class GetConfigurationsResponseItem:
    """
    Attributes:
        id (str):
        name (str):
        provider (str):
        parameters (GetConfigurationsResponseItemParameters):
        env (list[GetConfigurationsResponseItemEnvItem]):
        tags (list[str]):
        created_at (str):
        type_ (GetConfigurationsResponseItemType | Unset):  Default: GetConfigurationsResponseItemType.LLM.
        user_properties (GetConfigurationsResponseItemUserPropertiesType0 | None | Unset):
        updated_at (None | str | Unset):
    """

    id: str
    name: str
    provider: str
    parameters: GetConfigurationsResponseItemParameters
    env: list[GetConfigurationsResponseItemEnvItem]
    tags: list[str]
    created_at: str
    type_: GetConfigurationsResponseItemType | Unset = (
        GetConfigurationsResponseItemType.LLM
    )
    user_properties: GetConfigurationsResponseItemUserPropertiesType0 | None | Unset = (
        UNSET
    )
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_configurations_response_item_user_properties_type_0 import (
            GetConfigurationsResponseItemUserPropertiesType0,
        )

        id = self.id

        name = self.name

        provider = self.provider

        parameters = self.parameters.to_dict()

        env = []
        for env_item_data in self.env:
            env_item = env_item_data.value
            env.append(env_item)

        tags = self.tags

        created_at = self.created_at

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        user_properties: dict[str, Any] | None | Unset
        if isinstance(self.user_properties, Unset):
            user_properties = UNSET
        elif isinstance(
            self.user_properties, GetConfigurationsResponseItemUserPropertiesType0
        ):
            user_properties = self.user_properties.to_dict()
        else:
            user_properties = self.user_properties

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "provider": provider,
                "parameters": parameters,
                "env": env,
                "tags": tags,
                "created_at": created_at,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if user_properties is not UNSET:
            field_dict["user_properties"] = user_properties
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_configurations_response_item_parameters import (
            GetConfigurationsResponseItemParameters,
        )
        from ..models.get_configurations_response_item_user_properties_type_0 import (
            GetConfigurationsResponseItemUserPropertiesType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        provider = d.pop("provider")

        parameters = GetConfigurationsResponseItemParameters.from_dict(
            d.pop("parameters")
        )

        env = []
        _env = d.pop("env")
        for env_item_data in _env:
            env_item = GetConfigurationsResponseItemEnvItem(env_item_data)

            env.append(env_item)

        tags = cast(list[str], d.pop("tags"))

        created_at = d.pop("created_at")

        _type_ = d.pop("type", UNSET)
        type_: GetConfigurationsResponseItemType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = GetConfigurationsResponseItemType(_type_)

        def _parse_user_properties(
            data: object,
        ) -> GetConfigurationsResponseItemUserPropertiesType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_properties_type_0 = (
                    GetConfigurationsResponseItemUserPropertiesType0.from_dict(data)
                )

                return user_properties_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                GetConfigurationsResponseItemUserPropertiesType0 | None | Unset, data
            )

        user_properties = _parse_user_properties(d.pop("user_properties", UNSET))

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        get_configurations_response_item = cls(
            id=id,
            name=name,
            provider=provider,
            parameters=parameters,
            env=env,
            tags=tags,
            created_at=created_at,
            type_=type_,
            user_properties=user_properties,
            updated_at=updated_at,
        )

        get_configurations_response_item.additional_properties = d
        return get_configurations_response_item

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
