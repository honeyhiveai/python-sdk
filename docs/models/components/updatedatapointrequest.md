# UpdateDatapointRequest


## Fields

| Field                                                         | Type                                                          | Required                                                      | Description                                                   |
| ------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------- |
| `inputs`                                                      | Dict[str, *Any*]                                              | :heavy_minus_sign:                                            | Arbitrary JSON object containing the inputs for the datapoint |
| `history`                                                     | List[Dict[str, *Any*]]                                        | :heavy_minus_sign:                                            | Conversation history associated with the datapoint            |
| `ground_truth`                                                | Dict[str, *Any*]                                              | :heavy_minus_sign:                                            | Expected output JSON object for the datapoint                 |
| `linked_evals`                                                | List[*str*]                                                   | :heavy_minus_sign:                                            | Ids of evaluations where the datapoint is included            |
| `linked_datasets`                                             | List[*str*]                                                   | :heavy_minus_sign:                                            | Ids of all datasets that include the datapoint                |
| `metadata`                                                    | Dict[str, *Any*]                                              | :heavy_minus_sign:                                            | Any additional metadata for the datapoint                     |