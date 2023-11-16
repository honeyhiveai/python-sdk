# UploadDataset

The request object for uploading a dataset


## Fields

| Field                             | Type                              | Required                          | Description                       |
| --------------------------------- | --------------------------------- | --------------------------------- | --------------------------------- |
| `name`                            | *Optional[str]*                   | :heavy_minus_sign:                | The name of the dataset           |
| `task`                            | *Optional[str]*                   | :heavy_minus_sign:                | The task related to the dataset   |
| `prompt`                          | *Optional[str]*                   | :heavy_minus_sign:                | The prompt related to the dataset |
| `purpose`                         | *Optional[str]*                   | :heavy_minus_sign:                | The purpose of the dataset        |
| `description`                     | *Optional[str]*                   | :heavy_minus_sign:                | The description of the dataset    |
| `file`                            | List[Dict[str, *Any*]]            | :heavy_minus_sign:                | N/A                               |