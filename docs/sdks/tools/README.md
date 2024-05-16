# Tools
(*tools*)

### Available Operations

* [get_tools](#get_tools) - Retrieve a list of tools
* [create_tool](#create_tool) - Create a new tool
* [update_tool](#update_tool) - Update an existing tool
* [delete_tool](#delete_tool) - Delete a tool

## get_tools

Retrieve a list of tools

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.tools.get_tools()

if res.tools is not None:
    # handle response
    pass

```


### Response

**[operations.GetToolsResponse](../../models/operations/gettoolsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## create_tool

Create a new tool

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.CreateToolRequest(
    task='<value>',
    name='<value>',
    parameters={
        'key': '<value>',
    },
    type=components.CreateToolRequestType.TOOL,
)

res = s.tools.create_tool(req)

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                    | Type                                                                         | Required                                                                     | Description                                                                  |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `request`                                                                    | [components.CreateToolRequest](../../models/components/createtoolrequest.md) | :heavy_check_mark:                                                           | The request object to use for the request.                                   |


### Response

**[operations.CreateToolResponse](../../models/operations/createtoolresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## update_tool

Update an existing tool

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.UpdateToolRequest(
    id='<id>',
    name='<value>',
    parameters={
        'key': '<value>',
    },
)

res = s.tools.update_tool(req)

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                    | Type                                                                         | Required                                                                     | Description                                                                  |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `request`                                                                    | [components.UpdateToolRequest](../../models/components/updatetoolrequest.md) | :heavy_check_mark:                                                           | The request object to use for the request.                                   |


### Response

**[operations.UpdateToolResponse](../../models/operations/updatetoolresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## delete_tool

Delete a tool

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.tools.delete_tool(function_id='<value>')

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `function_id`      | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteToolResponse](../../models/operations/deletetoolresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |
