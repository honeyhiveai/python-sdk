from enum import Enum


class FilterFieldType(str, Enum):

    STRING = "string"

    NUMBER = "number"

    BOOLEAN = "boolean"

    DATETIME = "datetime"
