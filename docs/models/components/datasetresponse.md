# DatasetResponse

The response object for a dataset


## Fields

| Field                                                                | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `name`                                                               | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The name of the dataset file                                         |
| `purpose`                                                            | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The purpose of the dataset                                           |
| `file`                                                               | List[Dict[str, *Any*]]                                               | :heavy_minus_sign:                                                   | The file in the dataset                                              |
| `bytes`                                                              | *Optional[int]*                                                      | :heavy_minus_sign:                                                   | The size of the dataset in bytes                                     |
| `description`                                                        | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The description of the dataset                                       |
| `created_at`                                                         | [date](https://docs.python.org/3/library/datetime.html#date-objects) | :heavy_minus_sign:                                                   | The timestamp of when the dataset was created                        |
| `updated_at`                                                         | [date](https://docs.python.org/3/library/datetime.html#date-objects) | :heavy_minus_sign:                                                   | The timestamp of when the dataset was last updated                   |
| `task`                                                               | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The task related to the dataset                                      |
| `prompt`                                                             | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The prompt related to the dataset                                    |
| `tenant`                                                             | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The tenant that this dataset belongs to                              |
| `id`                                                                 | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The id of this dataset                                               |