# GetConfigurationsRequest


## Fields

| Field                                                      | Type                                                       | Required                                                   | Description                                                |
| ---------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------- |
| `project`                                                  | *str*                                                      | :heavy_check_mark:                                         | Project name for configuration like `Example Project`      |
| `env`                                                      | [Optional[operations.Env]](../../models/operations/env.md) | :heavy_minus_sign:                                         | Environment - "dev", "staging" or "prod"                   |
| `name`                                                     | *Optional[str]*                                            | :heavy_minus_sign:                                         | The name of the configuration like `v0`                    |