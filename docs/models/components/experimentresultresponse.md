# ExperimentResultResponse


## Fields

| Field                                                                | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `status`                                                             | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | N/A                                                                  |
| `success`                                                            | *Optional[bool]*                                                     | :heavy_minus_sign:                                                   | N/A                                                                  |
| `passed`                                                             | List[*str*]                                                          | :heavy_minus_sign:                                                   | N/A                                                                  |
| `failed`                                                             | List[*str*]                                                          | :heavy_minus_sign:                                                   | N/A                                                                  |
| `metrics`                                                            | [Optional[components.Metrics]](../../models/components/metrics.md)   | :heavy_minus_sign:                                                   | N/A                                                                  |
| `datapoints`                                                         | List[[components.Datapoints](../../models/components/datapoints.md)] | :heavy_minus_sign:                                                   | N/A                                                                  |