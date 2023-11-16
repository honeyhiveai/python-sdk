# SessionEventQuery

The request object for querying session events


## Fields

| Field                                                 | Type                                                  | Required                                              | Description                                           |
| ----------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------- |
| `event_id`                                            | *Optional[str]*                                       | :heavy_minus_sign:                                    | The ID of the event                                   |
| `session_id`                                          | *Optional[str]*                                       | :heavy_minus_sign:                                    | The ID of the session                                 |
| `event_type`                                          | *Optional[str]*                                       | :heavy_minus_sign:                                    | The type of the event                                 |
| `project`                                             | *Optional[str]*                                       | :heavy_minus_sign:                                    | The project that the event belongs to                 |
| `event_name`                                          | *Optional[str]*                                       | :heavy_minus_sign:                                    | The name for the event                                |
| `config`                                              | Dict[str, *Any*]                                      | :heavy_minus_sign:                                    | The configuration of LLM, Tool or other for the event |
| `children`                                            | List[Dict[str, *Any*]]                                | :heavy_minus_sign:                                    | Child events                                          |
| `inputs`                                              | Dict[str, *Any*]                                      | :heavy_minus_sign:                                    | Inputs to the event                                   |
| `outputs`                                             | Dict[str, *Any*]                                      | :heavy_minus_sign:                                    | Outputs of the event                                  |
| `user_properties`                                     | Dict[str, *Any*]                                      | :heavy_minus_sign:                                    | User properties of the event                          |
| `error`                                               | *Optional[str]*                                       | :heavy_minus_sign:                                    | Error from the event                                  |
| `source`                                              | *Optional[str]*                                       | :heavy_minus_sign:                                    | Source of the event                                   |
| `start_time`                                          | *Optional[float]*                                     | :heavy_minus_sign:                                    | Start time of the event                               |
| `end_time`                                            | *Optional[float]*                                     | :heavy_minus_sign:                                    | End time of the event                                 |
| `duration`                                            | *Optional[float]*                                     | :heavy_minus_sign:                                    | Duration of the event                                 |
| `metadata`                                            | Dict[str, *Any*]                                      | :heavy_minus_sign:                                    | Metadata of the event                                 |
| `metrics`                                             | Dict[str, *Any*]                                      | :heavy_minus_sign:                                    | Metrics for the event                                 |
| `feedback`                                            | Dict[str, *Any*]                                      | :heavy_minus_sign:                                    | Feedback for the event                                |