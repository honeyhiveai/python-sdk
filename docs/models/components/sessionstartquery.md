# SessionStartQuery

The request object for starting a session


## Fields

| Field                               | Type                                | Required                            | Description                         |
| ----------------------------------- | ----------------------------------- | ----------------------------------- | ----------------------------------- |
| `session_id`                        | *Optional[str]*                     | :heavy_minus_sign:                  | The ID of the session               |
| `project`                           | *Optional[str]*                     | :heavy_minus_sign:                  | The project name for the session    |
| `source`                            | *Optional[str]*                     | :heavy_minus_sign:                  | The source of the session           |
| `session_name`                      | *Optional[str]*                     | :heavy_minus_sign:                  | The name for the session            |
| `user_properties`                   | Dict[str, *Any*]                    | :heavy_minus_sign:                  | The user properties for the session |