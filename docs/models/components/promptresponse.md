# PromptResponse

The response object for a prompt


## Fields

| Field                                                                | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `name`                                                               | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The unique name of the prompt                                        |
| `version`                                                            | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The version of the prompt                                            |
| `task`                                                               | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The task for which the prompt is being created                       |
| `text`                                                               | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The text of the prompt                                               |
| `input_variables`                                                    | List[*str*]                                                          | :heavy_minus_sign:                                                   | The input variables to feed into the prompt                          |
| `model`                                                              | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The model to be used for the prompt                                  |
| `hyperparameters`                                                    | Dict[str, *Any*]                                                     | :heavy_minus_sign:                                                   | The hyperparameters for the prompt                                   |
| `is_deployed`                                                        | *Optional[bool]*                                                     | :heavy_minus_sign:                                                   | Flag indicating if the prompt is deployed                            |
| `few_shot_examples`                                                  | List[Dict[str, *Any*]]                                               | :heavy_minus_sign:                                                   | The few shot examples for the prompt                                 |
| `created_at`                                                         | [date](https://docs.python.org/3/library/datetime.html#date-objects) | :heavy_minus_sign:                                                   | The timestamp of when the prompt was created                         |
| `updated_at`                                                         | [date](https://docs.python.org/3/library/datetime.html#date-objects) | :heavy_minus_sign:                                                   | The timestamp of when the prompt was last updated                    |