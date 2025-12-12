from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_configuration_request_parameters_selected_functions_item_parameters import (
        CreateConfigurationRequestParametersSelectedFunctionsItemParameters,
    )


T = TypeVar("T", bound="CreateConfigurationRequestParametersSelectedFunctionsItem")


@_attrs_define
class CreateConfigurationRequestParametersSelectedFunctionsItem:
    """
    Attributes:
        id (str):
        name (str):
        description (str | Unset):
        parameters (CreateConfigurationRequestParametersSelectedFunctionsItemParameters | Unset):
    """

    id: str
    name: str
    description: str | Unset = UNSET
    parameters: (
        CreateConfigurationRequestParametersSelectedFunctionsItemParameters | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if parameters is not UNSET:
            field_dict["parameters"] = parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_configuration_request_parameters_selected_functions_item_parameters import (
            CreateConfigurationRequestParametersSelectedFunctionsItemParameters,
        )

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: (
            CreateConfigurationRequestParametersSelectedFunctionsItemParameters | Unset
        )
        if isinstance(_parameters, Unset):
            parameters = UNSET
        else:
            parameters = CreateConfigurationRequestParametersSelectedFunctionsItemParameters.from_dict(
                _parameters
            )

        create_configuration_request_parameters_selected_functions_item = cls(
            id=id,
            name=name,
            description=description,
            parameters=parameters,
        )

        create_configuration_request_parameters_selected_functions_item.additional_properties = (
            d
        )
        return create_configuration_request_parameters_selected_functions_item

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
