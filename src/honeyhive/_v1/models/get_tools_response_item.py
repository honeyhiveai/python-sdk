from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_tools_response_item_tool_type import GetToolsResponseItemToolType
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetToolsResponseItem")


@_attrs_define
class GetToolsResponseItem:
    """
    Attributes:
        id (str):
        name (str):
        created_at (str):
        description (str | Unset):
        parameters (Any | Unset):
        tool_type (GetToolsResponseItemToolType | Unset):
        updated_at (None | str | Unset):
    """

    id: str
    name: str
    created_at: str
    description: str | Unset = UNSET
    parameters: Any | Unset = UNSET
    tool_type: GetToolsResponseItemToolType | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        created_at = self.created_at

        description = self.description

        parameters = self.parameters

        tool_type: str | Unset = UNSET
        if not isinstance(self.tool_type, Unset):
            tool_type = self.tool_type.value

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
                "created_at": created_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if tool_type is not UNSET:
            field_dict["tool_type"] = tool_type
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        created_at = d.pop("created_at")

        description = d.pop("description", UNSET)

        parameters = d.pop("parameters", UNSET)

        _tool_type = d.pop("tool_type", UNSET)
        tool_type: GetToolsResponseItemToolType | Unset
        if isinstance(_tool_type, Unset):
            tool_type = UNSET
        else:
            tool_type = GetToolsResponseItemToolType(_tool_type)

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        get_tools_response_item = cls(
            id=id,
            name=name,
            created_at=created_at,
            description=description,
            parameters=parameters,
            tool_type=tool_type,
            updated_at=updated_at,
        )

        get_tools_response_item.additional_properties = d
        return get_tools_response_item

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
