# FeedbackQuery

The request object for providing feedback


## Fields

| Field                                                          | Type                                                           | Required                                                       | Description                                                    |
| -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- |
| `task`                                                         | *str*                                                          | :heavy_check_mark:                                             | The task for which the feedback is being submitted             |
| `generation_id`                                                | *str*                                                          | :heavy_check_mark:                                             | The ID of the generation for which feedback is being submitted |
| `feedback_json`                                                | Dict[str, *Any*]                                               | :heavy_minus_sign:                                             | The feedback JSON with one or many feedback items              |
| `ground_truth`                                                 | *Optional[str]*                                                | :heavy_minus_sign:                                             | The ground truth for the generation                            |