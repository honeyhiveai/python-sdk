# Metrics
(*metrics*)

### Available Operations

* [delete_metrics](#delete_metrics) - Delete a metric
* [get_metrics](#get_metrics) - Get all metrics
* [post_metrics](#post_metrics) - Create a new metric
* [put_metrics](#put_metrics) - Update an existing metric

## delete_metrics

Remove a metric

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.metrics.delete_metrics(metric_id='<value>')

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `metric_id`        | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteMetricsResponse](../../models/operations/deletemetricsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## get_metrics

Retrieve a list of all metrics

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.metrics.get_metrics(project_name='<value>')

if res.metrics is not None:
    # handle response
    pass

```

### Parameters

| Parameter                            | Type                                 | Required                             | Description                          |
| ------------------------------------ | ------------------------------------ | ------------------------------------ | ------------------------------------ |
| `project_name`                       | *str*                                | :heavy_check_mark:                   | Project name associated with metrics |


### Response

**[operations.GetMetricsResponse](../../models/operations/getmetricsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## post_metrics

Add a new metric

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.Metric(
    description='Enterprise-wide reciprocal standardization',
    name='<value>',
    return_type=components.ReturnType.STRING,
    task='<value>',
    type=components.MetricType.MODEL,
)

res = s.metrics.post_metrics(req)

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                              | Type                                                   | Required                                               | Description                                            |
| ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ |
| `request`                                              | [components.Metric](../../models/components/metric.md) | :heavy_check_mark:                                     | The request object to use for the request.             |


### Response

**[operations.PostMetricsResponse](../../models/operations/postmetricsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## put_metrics

Edit a metric

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.MetricEdit()

res = s.metrics.put_metrics(req)

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                      | Type                                                           | Required                                                       | Description                                                    |
| -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- |
| `request`                                                      | [components.MetricEdit](../../models/components/metricedit.md) | :heavy_check_mark:                                             | The request object to use for the request.                     |


### Response

**[operations.PutMetricsResponse](../../models/operations/putmetricsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |
