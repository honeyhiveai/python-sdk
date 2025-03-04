# CreateEventBatchResponseBody

Events partially created


## Fields

| Field                                                        | Type                                                         | Required                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `event_ids`                                                  | List[*str*]                                                  | :heavy_minus_sign:                                           | N/A                                                          |
| `errors`                                                     | List[*str*]                                                  | :heavy_minus_sign:                                           | N/A                                                          |
| `success`                                                    | *Optional[bool]*                                             | :heavy_minus_sign:                                           | N/A                                                          |
| `raw_response`                                               | [httpx.Response](https://www.python-httpx.org/api/#response) | :heavy_minus_sign:                                           | Raw HTTP response; suitable for custom response parsing      |