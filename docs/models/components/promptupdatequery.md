# PromptUpdateQuery

The request object for updating a prompt


## Fields

| Field                                       | Type                                        | Required                                    | Description                                 |
| ------------------------------------------- | ------------------------------------------- | ------------------------------------------- | ------------------------------------------- |
| `id`                                        | *Optional[str]*                             | :heavy_minus_sign:                          | The ID of the prompt                        |
| `version`                                   | *Optional[str]*                             | :heavy_minus_sign:                          | The version of the prompt                   |
| `input_variables`                           | List[*str*]                                 | :heavy_minus_sign:                          | The input variables to feed into the prompt |
| `model`                                     | *Optional[str]*                             | :heavy_minus_sign:                          | The model to be used for the prompt         |
| `hyperparameters`                           | Dict[str, *Any*]                            | :heavy_minus_sign:                          | The hyperparameters for the prompt          |
| `is_deployed`                               | *Optional[bool]*                            | :heavy_minus_sign:                          | Flag indicating if the prompt is deployed   |
| `few_shot_examples`                         | List[Dict[str, *Any*]]                      | :heavy_minus_sign:                          | The few shot examples for the prompt        |