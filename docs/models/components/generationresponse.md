# GenerationResponse

The response object for a generation


## Fields

| Field                           | Type                            | Required                        | Description                     |
| ------------------------------- | ------------------------------- | ------------------------------- | ------------------------------- |
| `generation_id`                 | *Optional[str]*                 | :heavy_minus_sign:              | The unique ID of the generation |
| `version`                       | *Optional[str]*                 | :heavy_minus_sign:              | The unique ID of the prompt     |
| `generation`                    | *Optional[str]*                 | :heavy_minus_sign:              | The generated completion        |
| `stream`                        | *Optional[bool]*                | :heavy_minus_sign:              | Is stream output                |