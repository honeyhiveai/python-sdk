# Experiments
(*experiments*)

## Overview

### Available Operations

* [create_run](#create_run) - Create a new evaluation run
* [get_runs](#get_runs) - Get a list of evaluation runs
* [get_run](#get_run) - Get details of an evaluation run
* [update_run](#update_run) - Update an evaluation run
* [delete_run](#delete_run) - Delete an evaluation run
* [get_experiment_result](#get_experiment_result) - Retrieve experiment result
* [get_experiment_comparison](#get_experiment_comparison) - Retrieve experiment comparison

## create_run

Create a new evaluation run

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.experiments.create_run(request={
    "project": "<value>",
    "name": "<value>",
    "event_ids": [
        "1504f40b-8865-40f9-b343-513d7da481bd",
    ],
})

if res.create_run_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                  | Type                                                                       | Required                                                                   | Description                                                                |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `request`                                                                  | [components.CreateRunRequest](../../models/components/createrunrequest.md) | :heavy_check_mark:                                                         | The request object to use for the request.                                 |
| `retries`                                                                  | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)           | :heavy_minus_sign:                                                         | Configuration to override the default retry behavior of the client.        |

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
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.experiments.get_runs()

if res.get_runs_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `project`                                                           | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | N/A                                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

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
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.experiments.get_run(run_id="<id>")

if res.get_run_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `run_id`                                                            | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

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
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.experiments.update_run(run_id="<id>", update_run_request={})

if res.update_run_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                  | Type                                                                       | Required                                                                   | Description                                                                |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `run_id`                                                                   | *str*                                                                      | :heavy_check_mark:                                                         | N/A                                                                        |
| `update_run_request`                                                       | [components.UpdateRunRequest](../../models/components/updaterunrequest.md) | :heavy_check_mark:                                                         | N/A                                                                        |
| `retries`                                                                  | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)           | :heavy_minus_sign:                                                         | Configuration to override the default retry behavior of the client.        |

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
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.experiments.delete_run(run_id="<id>")

if res.delete_run_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `run_id`                                                            | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[operations.DeleteRunResponse](../../models/operations/deleterunresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## get_experiment_result

Retrieve experiment result

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.experiments.get_experiment_result(run_id="<id>", project_id="<id>")

if res.experiment_result_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                              | Type                                                                                   | Required                                                                               | Description                                                                            |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `run_id`                                                                               | *str*                                                                                  | :heavy_check_mark:                                                                     | N/A                                                                                    |
| `project_id`                                                                           | *str*                                                                                  | :heavy_check_mark:                                                                     | N/A                                                                                    |
| `aggregate_function`                                                                   | [Optional[operations.AggregateFunction]](../../models/operations/aggregatefunction.md) | :heavy_minus_sign:                                                                     | N/A                                                                                    |
| `retries`                                                                              | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                       | :heavy_minus_sign:                                                                     | Configuration to override the default retry behavior of the client.                    |

### Response

**[operations.GetExperimentResultResponse](../../models/operations/getexperimentresultresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## get_experiment_comparison

Retrieve experiment comparison

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.experiments.get_experiment_comparison(run_id_1="<value>", run_id_2="<value>", project_id="<id>")

if res.experiment_comparison_response is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                                  | Type                                                                                                       | Required                                                                                                   | Description                                                                                                |
| ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `run_id_1`                                                                                                 | *str*                                                                                                      | :heavy_check_mark:                                                                                         | N/A                                                                                                        |
| `run_id_2`                                                                                                 | *str*                                                                                                      | :heavy_check_mark:                                                                                         | N/A                                                                                                        |
| `project_id`                                                                                               | *str*                                                                                                      | :heavy_check_mark:                                                                                         | N/A                                                                                                        |
| `aggregate_function`                                                                                       | [Optional[operations.QueryParamAggregateFunction]](../../models/operations/queryparamaggregatefunction.md) | :heavy_minus_sign:                                                                                         | N/A                                                                                                        |
| `retries`                                                                                                  | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                           | :heavy_minus_sign:                                                                                         | Configuration to override the default retry behavior of the client.                                        |

### Response

**[operations.GetExperimentComparisonResponse](../../models/operations/getexperimentcomparisonresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |