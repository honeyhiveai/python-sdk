# Tools
(*tools*)

### Available Operations

* [delete_tool](#delete_tool) - Delete a tool
* [get_tools](#get_tools) - Retrieve a list of tools
* [create_tool](#create_tool) - Create a new tool
* [update_tool](#update_tool) - Update an existing tool

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
| errors.SDKError | 4xx-5xx         | */*             |

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
| errors.SDKError | 4xx-5xx         | */*             |

## create_tool

Create a new tool

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.Tool(
    name='<value>',
    parameters={
        'key': '<value>',
    },
    task='<value>',
    tool_type=components.ToolType.TOOL,
)

res = s.tools.create_tool(req)

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                          | Type                                               | Required                                           | Description                                        |
| -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- |
| `request`                                          | [components.Tool](../../models/components/tool.md) | :heavy_check_mark:                                 | The request object to use for the request.         |


### Response

**[operations.CreateToolResponse](../../models/operations/createtoolresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## update_tool

Update an existing tool

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.ToolUpdate(
    id='<id>',
)

res = s.tools.update_tool(req)

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                      | Type                                                           | Required                                                       | Description                                                    |
| -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- |
| `request`                                                      | [components.ToolUpdate](../../models/components/toolupdate.md) | :heavy_check_mark:                                             | The request object to use for the request.                     |


### Response

**[operations.UpdateToolResponse](../../models/operations/updatetoolresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |
