# PromptCreationQuery

The request object for creating a prompt


## Fields

| Field                                          | Type                                           | Required                                       | Description                                    |
| ---------------------------------------------- | ---------------------------------------------- | ---------------------------------------------- | ---------------------------------------------- |
| `task`                                         | *Optional[str]*                                | :heavy_minus_sign:                             | The task for which the prompt is being created |
| `version`                                      | *Optional[str]*                                | :heavy_minus_sign:                             | The version of the prompt                      |
| `model`                                        | *Optional[str]*                                | :heavy_minus_sign:                             | The model to be used for the prompt            |
| `text`                                         | *Optional[str]*                                | :heavy_minus_sign:                             | The text of the prompt                         |
| `chat`                                         | *Optional[str]*                                | :heavy_minus_sign:                             | The text of the chat prompt                    |
| `hyperparameters`                              | Dict[str, *Any*]                               | :heavy_minus_sign:                             | The hyperparameters for the prompt             |
| `provider`                                     | *Optional[str]*                                | :heavy_minus_sign:                             | The model provider                             |
| `is_deployed`                                  | *Optional[bool]*                               | :heavy_minus_sign:                             | Flag indicating if the prompt is deployed      |
| `few_shot_examples`                            | List[Dict[str, *Any*]]                         | :heavy_minus_sign:                             | The few shot examples for the prompt           |