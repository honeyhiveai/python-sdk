from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.update_tool_request_tool_type import UpdateToolRequestToolType
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateToolRequest")


@_attrs_define
class UpdateToolRequest:
    """
    Attributes:
        id (str):
        name (str | Unset):
        description (str | Unset):
        parameters (Any | Unset):
        tool_type (UpdateToolRequestToolType | Unset):
    """

    id: str
    name: str | Unset = UNSET
    description: str | Unset = UNSET
    parameters: Any | Unset = UNSET
    tool_type: UpdateToolRequestToolType | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        parameters = self.parameters

        tool_type: str | Unset = UNSET
        if not isinstance(self.tool_type, Unset):
            tool_type = self.tool_type.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
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
        id = d.pop("id")

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        parameters = d.pop("parameters", UNSET)

        _tool_type = d.pop("tool_type", UNSET)
        tool_type: UpdateToolRequestToolType | Unset
        if isinstance(_tool_type, Unset):
            tool_type = UNSET
        else:
            tool_type = UpdateToolRequestToolType(_tool_type)

        update_tool_request = cls(
            id=id,
            name=name,
            description=description,
            parameters=parameters,
            tool_type=tool_type,
        )

        return update_tool_request
