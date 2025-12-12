from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.create_configuration_request_env_item import (
    CreateConfigurationRequestEnvItem,
)
from ..models.create_configuration_request_type import CreateConfigurationRequestType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_configuration_request_parameters import (
        CreateConfigurationRequestParameters,
    )
    from ..models.create_configuration_request_user_properties_type_0 import (
        CreateConfigurationRequestUserPropertiesType0,
    )


T = TypeVar("T", bound="CreateConfigurationRequest")


@_attrs_define
class CreateConfigurationRequest:
    """
    Attributes:
        name (str):
        provider (str):
        parameters (CreateConfigurationRequestParameters):
        type_ (CreateConfigurationRequestType | Unset):  Default: CreateConfigurationRequestType.LLM.
        env (list[CreateConfigurationRequestEnvItem] | Unset):
        tags (list[str] | Unset):
        user_properties (CreateConfigurationRequestUserPropertiesType0 | None | Unset):
    """

    name: str
    provider: str
    parameters: CreateConfigurationRequestParameters
    type_: CreateConfigurationRequestType | Unset = CreateConfigurationRequestType.LLM
    env: list[CreateConfigurationRequestEnvItem] | Unset = UNSET
    tags: list[str] | Unset = UNSET
    user_properties: CreateConfigurationRequestUserPropertiesType0 | None | Unset = (
        UNSET
    )

    def to_dict(self) -> dict[str, Any]:
        from ..models.create_configuration_request_user_properties_type_0 import (
            CreateConfigurationRequestUserPropertiesType0,
        )

        name = self.name

        provider = self.provider

        parameters = self.parameters.to_dict()

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

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
            self.user_properties, CreateConfigurationRequestUserPropertiesType0
        ):
            user_properties = self.user_properties.to_dict()
        else:
            user_properties = self.user_properties

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "provider": provider,
                "parameters": parameters,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if env is not UNSET:
            field_dict["env"] = env
        if tags is not UNSET:
            field_dict["tags"] = tags
        if user_properties is not UNSET:
            field_dict["user_properties"] = user_properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_configuration_request_parameters import (
            CreateConfigurationRequestParameters,
        )
        from ..models.create_configuration_request_user_properties_type_0 import (
            CreateConfigurationRequestUserPropertiesType0,
        )

        d = dict(src_dict)
        name = d.pop("name")

        provider = d.pop("provider")

        parameters = CreateConfigurationRequestParameters.from_dict(d.pop("parameters"))

        _type_ = d.pop("type", UNSET)
        type_: CreateConfigurationRequestType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = CreateConfigurationRequestType(_type_)

        _env = d.pop("env", UNSET)
        env: list[CreateConfigurationRequestEnvItem] | Unset = UNSET
        if _env is not UNSET:
            env = []
            for env_item_data in _env:
                env_item = CreateConfigurationRequestEnvItem(env_item_data)

                env.append(env_item)

        tags = cast(list[str], d.pop("tags", UNSET))

        def _parse_user_properties(
            data: object,
        ) -> CreateConfigurationRequestUserPropertiesType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_properties_type_0 = (
                    CreateConfigurationRequestUserPropertiesType0.from_dict(data)
                )

                return user_properties_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                CreateConfigurationRequestUserPropertiesType0 | None | Unset, data
            )

        user_properties = _parse_user_properties(d.pop("user_properties", UNSET))

        create_configuration_request = cls(
            name=name,
            provider=provider,
            parameters=parameters,
            type_=type_,
            env=env,
            tags=tags,
            user_properties=user_properties,
        )

        return create_configuration_request
