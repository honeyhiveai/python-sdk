# ChatCompletionRequest


## Fields

| Field                    | Type                     | Required                 | Description              |
| ------------------------ | ------------------------ | ------------------------ | ------------------------ |
| `project`                | *str*                    | :heavy_check_mark:       | The project ID           |
| `version`                | *Optional[str]*          | :heavy_minus_sign:       | The version of the chat  |
| `messages`               | List[Dict[str, *Any*]]   | :heavy_check_mark:       | The chat history         |
| `model`                  | *str*                    | :heavy_check_mark:       | The model to use         |
| `provider`               | *Optional[str]*          | :heavy_minus_sign:       | The provider             |
| `hyperparameters`        | Dict[str, *Any*]         | :heavy_minus_sign:       | N/A                      |
| `functions`              | List[Dict[str, *Any*]]   | :heavy_minus_sign:       | N/A                      |
| `function_call`          | *Optional[str]*          | :heavy_minus_sign:       | The function call method |
| `num_samples`            | *Optional[int]*          | :heavy_minus_sign:       | The number of samples    |
| `stream`                 | *Optional[bool]*         | :heavy_minus_sign:       | Whether to stream output |