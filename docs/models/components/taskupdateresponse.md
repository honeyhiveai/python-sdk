# TaskUpdateResponse


## Fields

| Field                                                            | Type                                                             | Required                                                         | Description                                                      |
| ---------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- |
| `acknowledged`                                                   | *Optional[bool]*                                                 | :heavy_minus_sign:                                               | Boolean flag representing if the update operation was successful |
| `modified_count`                                                 | *Optional[int]*                                                  | :heavy_minus_sign:                                               | Number of modified tasks                                         |
| `upserted_id`                                                    | *Optional[str]*                                                  | :heavy_minus_sign:                                               | The upserted ID of the task, if id has been changed              |
| `upserted_count`                                                 | *Optional[int]*                                                  | :heavy_minus_sign:                                               | Number of upserted tasks                                         |
| `matched_count`                                                  | *Optional[int]*                                                  | :heavy_minus_sign:                                               | Number of modified tasks                                         |