# Mapping

Mapping of keys in the data object to be used as inputs, ground truth, and history, everything else goes into metadata


## Fields

| Field                                                                                       | Type                                                                                        | Required                                                                                    | Description                                                                                 |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `inputs`                                                                                    | List[*str*]                                                                                 | :heavy_check_mark:                                                                          | List of keys in the data object to be used as inputs                                        |
| `ground_truth`                                                                              | List[*str*]                                                                                 | :heavy_check_mark:                                                                          | List of keys in the data object to be used as ground truth                                  |
| `history`                                                                                   | List[*str*]                                                                                 | :heavy_check_mark:                                                                          | List of keys in the data object to be used as chat history, can be empty list if not needed |