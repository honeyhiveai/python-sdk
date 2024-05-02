# Tool


## Fields

| Field                                                                | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `name`                                                               | *str*                                                                | :heavy_check_mark:                                                   | N/A                                                                  |
| `parameters`                                                         | Dict[str, *Any*]                                                     | :heavy_check_mark:                                                   | These can be function call params or plugin call params              |
| `task`                                                               | *str*                                                                | :heavy_check_mark:                                                   | Name of the project associated with this tool                        |
| `id`                                                                 | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | N/A                                                                  |
| `description`                                                        | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | N/A                                                                  |
| `tool_type`                                                          | [Optional[components.ToolType]](../../models/components/tooltype.md) | :heavy_minus_sign:                                                   | N/A                                                                  |