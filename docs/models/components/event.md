# Event


## Fields

| Field                                                                                      | Type                                                                                       | Required                                                                                   | Description                                                                                |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `children_ids`                                                                             | List[*str*]                                                                                | :heavy_minus_sign:                                                                         | Id of events that are nested within the event                                              |
| `config`                                                                                   | [Optional[components.EventConfig]](../../models/components/eventconfig.md)                 | :heavy_minus_sign:                                                                         | Associated configuration for the event - model, provider, etc                              |
| `duration`                                                                                 | *Optional[float]*                                                                          | :heavy_minus_sign:                                                                         | How long the event took in milliseconds                                                    |
| `end_time`                                                                                 | *Optional[int]*                                                                            | :heavy_minus_sign:                                                                         | UTC timestamp (in milliseconds) for the event end                                          |
| `error`                                                                                    | *Optional[str]*                                                                            | :heavy_minus_sign:                                                                         | Any error description if the event failed                                                  |
| `event_id`                                                                                 | *Optional[str]*                                                                            | :heavy_minus_sign:                                                                         | Unique id of the event, if not set, it will be auto-generated                              |
| `event_name`                                                                               | *Optional[str]*                                                                            | :heavy_minus_sign:                                                                         | Name of the event                                                                          |
| `event_type`                                                                               | [Optional[components.EventEventType]](../../models/components/eventeventtype.md)           | :heavy_minus_sign:                                                                         | Specify whether the event is of "model", "tool", "session" or "chain" type                 |
| `feedback`                                                                                 | [Optional[components.EventFeedback]](../../models/components/eventfeedback.md)             | :heavy_minus_sign:                                                                         | Any user feedback provided for the event output                                            |
| `inputs`                                                                                   | [Optional[components.EventInputs]](../../models/components/eventinputs.md)                 | :heavy_minus_sign:                                                                         | Input object passed to the event - user query, text blob, etc                              |
| `metadata`                                                                                 | [Optional[components.EventMetadata]](../../models/components/eventmetadata.md)             | :heavy_minus_sign:                                                                         | Any system or application metadata associated with the event                               |
| `metrics`                                                                                  | [Optional[components.EventMetrics]](../../models/components/eventmetrics.md)               | :heavy_minus_sign:                                                                         | Any values computed over the output of the event                                           |
| `outputs`                                                                                  | [Optional[components.EventOutputs]](../../models/components/eventoutputs.md)               | :heavy_minus_sign:                                                                         | Final output of the event - completion, chunks, etc                                        |
| `parent_id`                                                                                | *Optional[str]*                                                                            | :heavy_minus_sign:                                                                         | Id of the parent event if nested                                                           |
| `project`                                                                                  | *Optional[str]*                                                                            | :heavy_minus_sign:                                                                         | Project associated with the event                                                          |
| `session_id`                                                                               | *Optional[str]*                                                                            | :heavy_minus_sign:                                                                         | Unique id of the session associated with the event                                         |
| `source`                                                                                   | *Optional[str]*                                                                            | :heavy_minus_sign:                                                                         | Source of the event - production, staging, etc                                             |
| `start_time`                                                                               | *Optional[float]*                                                                          | :heavy_minus_sign:                                                                         | UTC timestamp (in milliseconds) for the event start                                        |
| `user_properties`                                                                          | [Optional[components.EventUserProperties]](../../models/components/eventuserproperties.md) | :heavy_minus_sign:                                                                         | Any user properties associated with the event                                              |