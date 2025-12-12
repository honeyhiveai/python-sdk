from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.create_tool_request_tool_type import CreateToolRequestToolType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateToolRequest")


@_attrs_define
class CreateToolRequest:
    """
    Attributes:
        name (str):
        description (str | Unset):
        parameters (Any | Unset):
        tool_type (CreateToolRequestToolType | Unset):
    """

    name: str
    description: str | Unset = UNSET
    parameters: Any | Unset = UNSET
    tool_type: CreateToolRequestToolType | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        parameters = self.parameters

        tool_type: str | Unset = UNSET
        if not isinstance(self.tool_type, Unset):
            tool_type = self.tool_type.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if tool_type is not UNSET:
            field_dict["tool_type"] = tool_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        parameters = d.pop("parameters", UNSET)

        _tool_type = d.pop("tool_type", UNSET)
        tool_type: CreateToolRequestToolType | Unset
        if isinstance(_tool_type, Unset):
            tool_type = UNSET
        else:
            tool_type = CreateToolRequestToolType(_tool_type)

        create_tool_request = cls(
            name=name,
            description=description,
            parameters=parameters,
            tool_type=tool_type,
        )

        return create_tool_request
