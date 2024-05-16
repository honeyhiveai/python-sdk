# CreateDatapointRequest


## Fields

| Field                                                         | Type                                                          | Required                                                      | Description                                                   |
| ------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------- |
| `project`                                                     | *str*                                                         | :heavy_check_mark:                                            | UUID for the project to which the datapoint belongs           |
| `inputs`                                                      | Dict[str, *Any*]                                              | :heavy_check_mark:                                            | Arbitrary JSON object containing the inputs for the datapoint |
| `history`                                                     | List[Dict[str, *Any*]]                                        | :heavy_minus_sign:                                            | Conversation history associated with the datapoint            |
| `ground_truth`                                                | Dict[str, *Any*]                                              | :heavy_minus_sign:                                            | Expected output JSON object for the datapoint                 |
| `linked_event`                                                | *Optional[str]*                                               | :heavy_minus_sign:                                            | Event id for the event from which the datapoint was created   |
| `linked_datasets`                                             | List[*str*]                                                   | :heavy_minus_sign:                                            | Ids of all datasets that include the datapoint                |
| `metadata`                                                    | Dict[str, *Any*]                                              | :heavy_minus_sign:                                            | Any additional metadata for the datapoint                     |