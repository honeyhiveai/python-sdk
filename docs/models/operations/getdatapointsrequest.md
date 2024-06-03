# GetDatapointsRequest


## Fields

| Field                                      | Type                                       | Required                                   | Description                                |
| ------------------------------------------ | ------------------------------------------ | ------------------------------------------ | ------------------------------------------ |
| `project`                                  | *str*                                      | :heavy_check_mark:                         | Project name to filter datapoints          |
| `datapoint_ids`                            | List[*str*]                                | :heavy_minus_sign:                         | List of datapoint ids to fetch             |
| `dataset_name`                             | *Optional[str]*                            | :heavy_minus_sign:                         | Name of the dataset to get datapoints from |