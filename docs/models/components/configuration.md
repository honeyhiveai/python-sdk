# Configuration


## Fields

| Field                                                                            | Type                                                                             | Required                                                                         | Description                                                                      |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `project`                                                                        | *str*                                                                            | :heavy_check_mark:                                                               | ID of the project to which this configuration belongs                            |
| `name`                                                                           | *str*                                                                            | :heavy_check_mark:                                                               | Name of the configuration                                                        |
| `provider`                                                                       | *str*                                                                            | :heavy_check_mark:                                                               | Name of the provider - "openai", "anthropic", etc.                               |
| `type`                                                                           | [Optional[components.Type]](../../models/components/type.md)                     | :heavy_minus_sign:                                                               | Type of the configuration - "LLM" or "pipeline" - "LLM" by default               |
| `parameters`                                                                     | [Optional[components.Parameters]](../../models/components/parameters.md)         | :heavy_minus_sign:                                                               | N/A                                                                              |
| `user_properties`                                                                | [Optional[components.UserProperties]](../../models/components/userproperties.md) | :heavy_minus_sign:                                                               | Details of user who created the configuration                                    |