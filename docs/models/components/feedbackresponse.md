# FeedbackResponse

The response object for providing feedback


## Fields

| Field                                                                | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `task`                                                               | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The task for which the feedback was submitted                        |
| `generation_id`                                                      | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The ID of the generation for which feedback was submitted            |
| `feedback`                                                           | Dict[str, *Any*]                                                     | :heavy_minus_sign:                                                   | The feedback JSON with one or many feedback items                    |
| `ground_truth`                                                       | *Optional[str]*                                                      | :heavy_minus_sign:                                                   | The ground truth for the generation                                  |
| `created_at`                                                         | [date](https://docs.python.org/3/library/datetime.html#date-objects) | :heavy_minus_sign:                                                   | The timestamp of when the feedback was created                       |