# GetConfigurationsRequest


## Fields

| Field                                                        | Type                                                         | Required                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `project_name`                                               | *str*                                                        | :heavy_check_mark:                                           | Project name for configuration                               |
| `type`                                                       | [Optional[operations.Type]](../../models/operations/type.md) | :heavy_minus_sign:                                           | Configuration type - "LLM" or "pipeline" - default is "LLM"  |
| `env`                                                        | [Optional[operations.Env]](../../models/operations/env.md)   | :heavy_minus_sign:                                           | Environment - "dev", "staging" or "prod"                     |
| `name`                                                       | *Optional[str]*                                              | :heavy_minus_sign:                                           | The name of the configuration                                |