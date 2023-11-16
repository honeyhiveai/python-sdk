# Generation

The response object for a generation


## Fields

| Field                                                   | Type                                                    | Required                                                | Description                                             |
| ------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------- |
| `generation_id`                                         | *Optional[str]*                                         | :heavy_minus_sign:                                      | The unique ID of the generation                         |
| `version`                                               | *Optional[str]*                                         | :heavy_minus_sign:                                      | The unique ID of the prompt                             |
| `task`                                                  | *Optional[str]*                                         | :heavy_minus_sign:                                      | The task for which the generation is being requested    |
| `model`                                                 | *Optional[str]*                                         | :heavy_minus_sign:                                      | The model that was used to generate the text            |
| `hyperparameters`                                       | Dict[str, *Any*]                                        | :heavy_minus_sign:                                      | The hyperparameters that were used to generate the text |
| `generation`                                            | *Optional[str]*                                         | :heavy_minus_sign:                                      | The generated completion                                |
| `total_tokens`                                          | *Optional[int]*                                         | :heavy_minus_sign:                                      | The total number of tokens generated                    |
| `completion_tokens`                                     | *Optional[int]*                                         | :heavy_minus_sign:                                      | The number of tokens generated for the completion       |
| `cost`                                                  | *Optional[float]*                                       | :heavy_minus_sign:                                      | The cost of the generation                              |
| `latency`                                               | *Optional[float]*                                       | :heavy_minus_sign:                                      | The latency of the generation in milliseconds           |
| `source`                                                | *Optional[str]*                                         | :heavy_minus_sign:                                      | The source of the generation                            |
| `feedback`                                              | Dict[str, *Any*]                                        | :heavy_minus_sign:                                      | The feedback associated with this generation            |