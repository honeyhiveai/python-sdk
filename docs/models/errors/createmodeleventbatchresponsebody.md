# CreateModelEventBatchResponseBody

Model events partially created


## Fields

| Field                                                                                 | Type                                                                                  | Required                                                                              | Description                                                                           |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `event_ids`                                                                           | List[*str*]                                                                           | :heavy_minus_sign:                                                                    | N/A                                                                                   |
| `errors`                                                                              | List[*str*]                                                                           | :heavy_minus_sign:                                                                    | N/A                                                                                   |
| `success`                                                                             | *Optional[bool]*                                                                      | :heavy_minus_sign:                                                                    | N/A                                                                                   |
| `raw_response`                                                                        | [requests.Response](https://requests.readthedocs.io/en/latest/api/#requests.Response) | :heavy_minus_sign:                                                                    | Raw HTTP response; suitable for custom response parsing                               |