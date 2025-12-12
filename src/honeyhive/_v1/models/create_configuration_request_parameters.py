from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_configuration_request_parameters_call_type import (
    CreateConfigurationRequestParametersCallType,
)
from ..models.create_configuration_request_parameters_function_call_params import (
    CreateConfigurationRequestParametersFunctionCallParams,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_configuration_request_parameters_force_function import (
        CreateConfigurationRequestParametersForceFunction,
    )
    from ..models.create_configuration_request_parameters_hyperparameters import (
        CreateConfigurationRequestParametersHyperparameters,
    )
    from ..models.create_configuration_request_parameters_response_format import (
        CreateConfigurationRequestParametersResponseFormat,
    )
    from ..models.create_configuration_request_parameters_selected_functions_item import (
        CreateConfigurationRequestParametersSelectedFunctionsItem,
    )
    from ..models.create_configuration_request_parameters_template_type_0_item import (
        CreateConfigurationRequestParametersTemplateType0Item,
    )


T = TypeVar("T", bound="CreateConfigurationRequestParameters")


@_attrs_define
class CreateConfigurationRequestParameters:
    """
    Attributes:
        call_type (CreateConfigurationRequestParametersCallType):
        model (str):
        hyperparameters (CreateConfigurationRequestParametersHyperparameters | Unset):
        response_format (CreateConfigurationRequestParametersResponseFormat | Unset):
        selected_functions (list[CreateConfigurationRequestParametersSelectedFunctionsItem] | Unset):
        function_call_params (CreateConfigurationRequestParametersFunctionCallParams | Unset):
        force_function (CreateConfigurationRequestParametersForceFunction | Unset):
        template (list[CreateConfigurationRequestParametersTemplateType0Item] | str | Unset):
    """

    call_type: CreateConfigurationRequestParametersCallType
    model: str
    hyperparameters: CreateConfigurationRequestParametersHyperparameters | Unset = UNSET
    response_format: CreateConfigurationRequestParametersResponseFormat | Unset = UNSET
    selected_functions: (
        list[CreateConfigurationRequestParametersSelectedFunctionsItem] | Unset
    ) = UNSET
    function_call_params: (
        CreateConfigurationRequestParametersFunctionCallParams | Unset
    ) = UNSET
    force_function: CreateConfigurationRequestParametersForceFunction | Unset = UNSET
    template: (
        list[CreateConfigurationRequestParametersTemplateType0Item] | str | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        call_type = self.call_type.value

        model = self.model

        hyperparameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.hyperparameters, Unset):
            hyperparameters = self.hyperparameters.to_dict()

        response_format: dict[str, Any] | Unset = UNSET
        if not isinstance(self.response_format, Unset):
            response_format = self.response_format.to_dict()

        selected_functions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.selected_functions, Unset):
            selected_functions = []
            for selected_functions_item_data in self.selected_functions:
                selected_functions_item = selected_functions_item_data.to_dict()
                selected_functions.append(selected_functions_item)

        function_call_params: str | Unset = UNSET
        if not isinstance(self.function_call_params, Unset):
            function_call_params = self.function_call_params.value

        force_function: dict[str, Any] | Unset = UNSET
        if not isinstance(self.force_function, Unset):
            force_function = self.force_function.to_dict()

        template: list[dict[str, Any]] | str | Unset
        if isinstance(self.template, Unset):
            template = UNSET
        elif isinstance(self.template, list):
            template = []
            for template_type_0_item_data in self.template:
                template_type_0_item = template_type_0_item_data.to_dict()
                template.append(template_type_0_item)

        else:
            template = self.template

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "call_type": call_type,
                "model": model,
            }
        )
        if hyperparameters is not UNSET:
            field_dict["hyperparameters"] = hyperparameters
        if response_format is not UNSET:
            field_dict["responseFormat"] = response_format
        if selected_functions is not UNSET:
            field_dict["selectedFunctions"] = selected_functions
        if function_call_params is not UNSET:
            field_dict["functionCallParams"] = function_call_params
        if force_function is not UNSET:
            field_dict["forceFunction"] = force_function
        if template is not UNSET:
            field_dict["template"] = template

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_configuration_request_parameters_force_function import (
            CreateConfigurationRequestParametersForceFunction,
        )
        from ..models.create_configuration_request_parameters_hyperparameters import (
            CreateConfigurationRequestParametersHyperparameters,
        )
        from ..models.create_configuration_request_parameters_response_format import (
            CreateConfigurationRequestParametersResponseFormat,
        )
        from ..models.create_configuration_request_parameters_selected_functions_item import (
            CreateConfigurationRequestParametersSelectedFunctionsItem,
        )
        from ..models.create_configuration_request_parameters_template_type_0_item import (
            CreateConfigurationRequestParametersTemplateType0Item,
        )

        d = dict(src_dict)
        call_type = CreateConfigurationRequestParametersCallType(d.pop("call_type"))

        model = d.pop("model")

        _hyperparameters = d.pop("hyperparameters", UNSET)
        hyperparameters: CreateConfigurationRequestParametersHyperparameters | Unset
        if isinstance(_hyperparameters, Unset):
            hyperparameters = UNSET
        else:
            hyperparameters = (
                CreateConfigurationRequestParametersHyperparameters.from_dict(
                    _hyperparameters
                )
            )

        _response_format = d.pop("responseFormat", UNSET)
        response_format: CreateConfigurationRequestParametersResponseFormat | Unset
        if isinstance(_response_format, Unset):
            response_format = UNSET
        else:
            response_format = (
                CreateConfigurationRequestParametersResponseFormat.from_dict(
                    _response_format
                )
            )

        _selected_functions = d.pop("selectedFunctions", UNSET)
        selected_functions: (
            list[CreateConfigurationRequestParametersSelectedFunctionsItem] | Unset
        ) = UNSET
        if _selected_functions is not UNSET:
            selected_functions = []
            for selected_functions_item_data in _selected_functions:
                selected_functions_item = (
                    CreateConfigurationRequestParametersSelectedFunctionsItem.from_dict(
                        selected_functions_item_data
                    )
                )

                selected_functions.append(selected_functions_item)

        _function_call_params = d.pop("functionCallParams", UNSET)
        function_call_params: (
            CreateConfigurationRequestParametersFunctionCallParams | Unset
        )
        if isinstance(_function_call_params, Unset):
            function_call_params = UNSET
        else:
            function_call_params = (
                CreateConfigurationRequestParametersFunctionCallParams(
                    _function_call_params
                )
            )

        _force_function = d.pop("forceFunction", UNSET)
        force_function: CreateConfigurationRequestParametersForceFunction | Unset
        if isinstance(_force_function, Unset):
            force_function = UNSET
        else:
            force_function = (
                CreateConfigurationRequestParametersForceFunction.from_dict(
                    _force_function
                )
            )

        def _parse_template(
            data: object,
        ) -> list[CreateConfigurationRequestParametersTemplateType0Item] | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                template_type_0 = []
                _template_type_0 = data
                for template_type_0_item_data in _template_type_0:
                    template_type_0_item = (
                        CreateConfigurationRequestParametersTemplateType0Item.from_dict(
                            template_type_0_item_data
                        )
                    )

                    template_type_0.append(template_type_0_item)

                return template_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                list[CreateConfigurationRequestParametersTemplateType0Item]
                | str
                | Unset,
                data,
            )

        template = _parse_template(d.pop("template", UNSET))

        create_configuration_request_parameters = cls(
            call_type=call_type,
            model=model,
            hyperparameters=hyperparameters,
            response_format=response_format,
            selected_functions=selected_functions,
            function_call_params=function_call_params,
            force_function=force_function,
            template=template,
        )

        create_configuration_request_parameters.additional_properties = d
        return create_configuration_request_parameters

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
