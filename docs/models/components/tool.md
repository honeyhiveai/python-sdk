# Tool


## Fields

| Field                                                      | Type                                                       | Required                                                   | Description                                                |
| ---------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------- |
| `task`                                                     | *str*                                                      | :heavy_check_mark:                                         | Name of the project associated with this tool              |
| `name`                                                     | *str*                                                      | :heavy_check_mark:                                         | N/A                                                        |
| `parameters`                                               | Dict[str, *Any*]                                           | :heavy_check_mark:                                         | These can be function call params or plugin call params    |
| `tool_type`                                                | [components.ToolType](../../models/components/tooltype.md) | :heavy_check_mark:                                         | N/A                                                        |
| `id`                                                       | *Optional[str]*                                            | :heavy_minus_sign:                                         | N/A                                                        |
| `description`                                              | *Optional[str]*                                            | :heavy_minus_sign:                                         | N/A                                                        |