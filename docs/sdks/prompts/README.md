# Prompts
(*prompts*)

### Available Operations

* [get_prompts](#get_prompts) - Retrieve a list of prompts based on query parameters.
* [post_prompts](#post_prompts) - Create a new prompt.
* [delete_prompts_id_](#delete_prompts_id_) - Delete an existing prompt.
* [put_prompts_id_](#put_prompts_id_) - Update an existing prompt.

## get_prompts

Retrieve a list of prompts based on query parameters.

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.prompts.get_prompts(task='<value>', name='<value>')

if res.prompts is not None:
    # handle response
    pass
```

### Parameters

| Parameter                         | Type                              | Required                          | Description                       |
| --------------------------------- | --------------------------------- | --------------------------------- | --------------------------------- |
| `task`                            | *str*                             | :heavy_check_mark:                | Task associated with the prompts. |
| `name`                            | *Optional[str]*                   | :heavy_minus_sign:                | Optional name to filter prompts.  |


### Response

**[operations.GetPromptsResponse](../../models/operations/getpromptsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## post_prompts

Create a new prompt.

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.Prompt(
    id='<id>',
    task='<value>',
    version='<value>',
    model='Cruze',
    provider='<value>',
    text='<value>',
)

res = s.prompts.post_prompts(req)

if res.prompt is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                              | Type                                                   | Required                                               | Description                                            |
| ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ |
| `request`                                              | [components.Prompt](../../models/components/prompt.md) | :heavy_check_mark:                                     | The request object to use for the request.             |


### Response

**[operations.PostPromptsResponse](../../models/operations/postpromptsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## delete_prompts_id_

Delete an existing prompt.

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.prompts.delete_prompts_id_(id='<value>')

if res.status_code == 200:
    # handle response
    pass
```

### Parameters

| Parameter                   | Type                        | Required                    | Description                 |
| --------------------------- | --------------------------- | --------------------------- | --------------------------- |
| `id`                        | *str*                       | :heavy_check_mark:          | ID of the prompt to delete. |


### Response

**[operations.DeletePromptsIDResponse](../../models/operations/deletepromptsidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## put_prompts_id_

Update an existing prompt.

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.prompts.put_prompts_id_(id='<value>', prompt=components.Prompt(
    id='<id>',
    task='<value>',
    version='<value>',
    model='V90',
    provider='<value>',
    text='<value>',
))

if res.status_code == 200:
    # handle response
    pass
```

### Parameters

| Parameter                                              | Type                                                   | Required                                               | Description                                            |
| ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ |
| `id`                                                   | *str*                                                  | :heavy_check_mark:                                     | ID of the prompt to update.                            |
| `prompt`                                               | [components.Prompt](../../models/components/prompt.md) | :heavy_check_mark:                                     | N/A                                                    |


### Response

**[operations.PutPromptsIDResponse](../../models/operations/putpromptsidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |
