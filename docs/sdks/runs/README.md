# Runs
(*runs*)

## Overview

### Available Operations

* [create_run](#create_run) - Create a new evaluation run
* [get_runs](#get_runs) - Get a list of evaluation runs
* [get_run](#get_run) - Get details of an evaluation run
* [update_run](#update_run) - Update an evaluation run
* [delete_run](#delete_run) - Delete an evaluation run

## create_run

Create a new evaluation run

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.runs.create_run(request=components.CreateRunRequest(
    project='<value>',
    name='<value>',
    event_ids=[
        '1504f40b-8865-40f9-b343-513d7da481bd',
    ],
))

if res.create_run_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                  | Type                                                                       | Required                                                                   | Description                                                                |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `request`                                                                  | [components.CreateRunRequest](../../models/components/createrunrequest.md) | :heavy_check_mark:                                                         | The request object to use for the request.                                 |

### Response

**[operations.CreateRunResponse](../../models/operations/createrunresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## get_runs

Get a list of evaluation runs

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.runs.get_runs()

if res.get_runs_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `project`          | *Optional[str]*    | :heavy_minus_sign: | N/A                |

### Response

**[operations.GetRunsResponse](../../models/operations/getrunsresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## get_run

Get details of an evaluation run

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.runs.get_run(run_id='<value>')

if res.get_run_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `run_id`           | *str*              | :heavy_check_mark: | N/A                |

### Response

**[operations.GetRunResponse](../../models/operations/getrunresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## update_run

Update an evaluation run

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.runs.update_run(run_id='<value>', update_run_request=components.UpdateRunRequest())

if res.update_run_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                  | Type                                                                       | Required                                                                   | Description                                                                |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `run_id`                                                                   | *str*                                                                      | :heavy_check_mark:                                                         | N/A                                                                        |
| `update_run_request`                                                       | [components.UpdateRunRequest](../../models/components/updaterunrequest.md) | :heavy_check_mark:                                                         | N/A                                                                        |

### Response

**[operations.UpdateRunResponse](../../models/operations/updaterunresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## delete_run

Delete an evaluation run

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.runs.delete_run(run_id='<value>')

if res.delete_run_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `run_id`           | *str*              | :heavy_check_mark: | N/A                |

### Response

**[operations.DeleteRunResponse](../../models/operations/deleterunresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |