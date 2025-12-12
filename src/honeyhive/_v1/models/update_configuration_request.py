from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.update_configuration_request_env_item import (
    UpdateConfigurationRequestEnvItem,
)
from ..models.update_configuration_request_type import UpdateConfigurationRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_configuration_request_parameters import (
        UpdateConfigurationRequestParameters,
    )
    from ..models.update_configuration_request_user_properties_type_0 import (
        UpdateConfigurationRequestUserPropertiesType0,
    )


T = TypeVar("T", bound="UpdateConfigurationRequest")


@_attrs_define
class UpdateConfigurationRequest:
    """
    Attributes:
        name (str):
        type_ (UpdateConfigurationRequestType | Unset):  Default: UpdateConfigurationRequestType.LLM.
        provider (str | Unset):
        parameters (UpdateConfigurationRequestParameters | Unset):
        env (list[UpdateConfigurationRequestEnvItem] | Unset):
        tags (list[str] | Unset):
        user_properties (None | Unset | UpdateConfigurationRequestUserPropertiesType0):
    """

    name: str
    type_: UpdateConfigurationRequestType | Unset = UpdateConfigurationRequestType.LLM
    provider: str | Unset = UNSET
    parameters: UpdateConfigurationRequestParameters | Unset = UNSET
    env: list[UpdateConfigurationRequestEnvItem] | Unset = UNSET
    tags: list[str] | Unset = UNSET
    user_properties: None | Unset | UpdateConfigurationRequestUserPropertiesType0 = (
        UNSET
    )

    def to_dict(self) -> dict[str, Any]:
        from ..models.update_configuration_request_user_properties_type_0 import (
            UpdateConfigurationRequestUserPropertiesType0,
        )

        name = self.name

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        provider = self.provider

        parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        env: list[str] | Unset = UNSET
        if not isinstance(self.env, Unset):
            env = []
            for env_item_data in self.env:
                env_item = env_item_data.value
                env.append(env_item)

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        user_properties: dict[str, Any] | None | Unset
        if isinstance(self.user_properties, Unset):
            user_properties = UNSET
        elif isinstance(
            self.user_properties, UpdateConfigurationRequestUserPropertiesType0
        ):
            user_properties = self.user_properties.to_dict()
        else:
            user_properties = self.user_properties

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if provider is not UNSET:
            field_dict["provider"] = provider
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if env is not UNSET:
            field_dict["env"] = env
        if tags is not UNSET:
            field_dict["tags"] = tags
        if user_properties is not UNSET:
            field_dict["user_properties"] = user_properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_configuration_request_parameters import (
            UpdateConfigurationRequestParameters,
        )
        from ..models.update_configuration_request_user_properties_type_0 import (
            UpdateConfigurationRequestUserPropertiesType0,
        )

        d = dict(src_dict)
        name = d.pop("name")

        _type_ = d.pop("type", UNSET)
        type_: UpdateConfigurationRequestType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = UpdateConfigurationRequestType(_type_)

        provider = d.pop("provider", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: UpdateConfigurationRequestParameters | Unset
        if isinstance(_parameters, Unset):
            parameters = UNSET
        else:
            parameters = UpdateConfigurationRequestParameters.from_dict(_parameters)

        _env = d.pop("env", UNSET)
        env: list[UpdateConfigurationRequestEnvItem] | Unset = UNSET
        if _env is not UNSET:
            env = []
            for env_item_data in _env:
                env_item = UpdateConfigurationRequestEnvItem(env_item_data)

                env.append(env_item)

        tags = cast(list[str], d.pop("tags", UNSET))

        def _parse_user_properties(
            data: object,
        ) -> None | Unset | UpdateConfigurationRequestUserPropertiesType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_properties_type_0 = (
                    UpdateConfigurationRequestUserPropertiesType0.from_dict(data)
                )

                return user_properties_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | Unset | UpdateConfigurationRequestUserPropertiesType0, data
            )

        user_properties = _parse_user_properties(d.pop("user_properties", UNSET))

        update_configuration_request = cls(
            name=name,
            type_=type_,
            provider=provider,
            parameters=parameters,
            env=env,
            tags=tags,
            user_properties=user_properties,
        )

        return update_configuration_request
