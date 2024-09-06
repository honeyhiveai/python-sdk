# Metrics
(*metrics*)

## Overview

### Available Operations

* [get_metrics](#get_metrics) - Get all metrics
* [create_metric](#create_metric) - Create a new metric
* [update_metric](#update_metric) - Update an existing metric
* [delete_metric](#delete_metric) - Delete a metric

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
| errors.SDKError | 4xx-5xx         | */*             |


## create_metric

Add a new metric

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.metrics.create_metric(request=components.Metric(
    name='<value>',
    task='<value>',
    type=components.MetricType.MODEL,
    description='Fully-configurable neutral framework',
    return_type=components.ReturnType.STRING,
))

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                              | Type                                                   | Required                                               | Description                                            |
| ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------ |
| `request`                                              | [components.Metric](../../models/components/metric.md) | :heavy_check_mark:                                     | The request object to use for the request.             |

### Response

**[operations.CreateMetricResponse](../../models/operations/createmetricresponse.md)**

### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |


## update_metric

Edit a metric

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.metrics.update_metric(request=components.MetricEdit(
    metric_id='<value>',
))

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                      | Type                                                           | Required                                                       | Description                                                    |
| -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- |
| `request`                                                      | [components.MetricEdit](../../models/components/metricedit.md) | :heavy_check_mark:                                             | The request object to use for the request.                     |

### Response

**[operations.UpdateMetricResponse](../../models/operations/updatemetricresponse.md)**

### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |


## delete_metric

Remove a metric

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.metrics.delete_metric(metric_id='<value>')

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `metric_id`        | *str*              | :heavy_check_mark: | N/A                |

### Response

**[operations.DeleteMetricResponse](../../models/operations/deletemetricresponse.md)**

### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |
