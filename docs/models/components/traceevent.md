# TraceEvent


## Fields

| Field                                       | Type                                        | Required                                    | Description                                 |
| ------------------------------------------- | ------------------------------------------- | ------------------------------------------- | ------------------------------------------- |
| `name`                                      | *str*                                       | :heavy_check_mark:                          | The name of the event.                      |
| `cat`                                       | *Optional[str]*                             | :heavy_minus_sign:                          | The category of the event.                  |
| `ph`                                        | *str*                                       | :heavy_check_mark:                          | The phase of the event.                     |
| `ts`                                        | *int*                                       | :heavy_check_mark:                          | The timestamp of the event in microseconds. |
| `pid`                                       | *int*                                       | :heavy_check_mark:                          | The process ID.                             |
| `tid`                                       | *int*                                       | :heavy_check_mark:                          | The thread ID.                              |
| `args`                                      | Dict[str, *Any*]                            | :heavy_minus_sign:                          | Arguments associated with the event.        |