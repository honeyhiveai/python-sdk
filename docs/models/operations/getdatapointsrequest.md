# GetDatapointsRequest


## Fields

| Field                                                                            | Type                                                                             | Required                                                                         | Description                                                                      |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `project`                                                                        | *str*                                                                            | :heavy_check_mark:                                                               | Project ID to filter datapoints                                                  |
| `type`                                                                           | [Optional[operations.QueryParamType]](../../models/operations/queryparamtype.md) | :heavy_minus_sign:                                                               | Type of data - "evaluation" or "event"                                           |
| `datapoint_ids`                                                                  | List[*str*]                                                                      | :heavy_minus_sign:                                                               | List of datapoint ids to fetch                                                   |