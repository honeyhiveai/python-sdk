# Datapoints
(*datapoints*)

### Available Operations

* [get_datapoints](#get_datapoints) - Retrieve a list of datapoints
* [create_datapoint](#create_datapoint) - Create a new datapoint
* [update_datapoint](#update_datapoint) - Update a specific datapoint
* [delete_datapoint](#delete_datapoint) - Delete a specific datapoint
* [get_datapoint](#get_datapoint) - Retrieve a specific datapoint

## get_datapoints

Retrieve a list of datapoints

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datapoints.get_datapoints(project='<value>', type=operations.QueryParamType.EVALUATION, datapoint_ids=[
    '<value>',
])

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                        | Type                                                                             | Required                                                                         | Description                                                                      |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `project`                                                                        | *str*                                                                            | :heavy_check_mark:                                                               | Project ID to filter datapoints                                                  |
| `type`                                                                           | [Optional[operations.QueryParamType]](../../models/operations/queryparamtype.md) | :heavy_minus_sign:                                                               | Type of data - "evaluation" or "event"                                           |
| `datapoint_ids`                                                                  | List[*str*]                                                                      | :heavy_minus_sign:                                                               | List of datapoint ids to fetch                                                   |


### Response

**[operations.GetDatapointsResponse](../../models/operations/getdatapointsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## create_datapoint

Create a new datapoint

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.CreateDatapointRequest(
    inputs={
        'key': '<value>',
    },
    project='<value>',
    type=components.CreateDatapointRequestType.EVALUATION,
)

res = s.datapoints.create_datapoint(req)

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                              | Type                                                                                   | Required                                                                               | Description                                                                            |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `request`                                                                              | [components.CreateDatapointRequest](../../models/components/createdatapointrequest.md) | :heavy_check_mark:                                                                     | The request object to use for the request.                                             |


### Response

**[operations.CreateDatapointResponse](../../models/operations/createdatapointresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## update_datapoint

Update a specific datapoint

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datapoints.update_datapoint(datapoint_id='<value>', update_datapoint_request=components.UpdateDatapointRequest())

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                              | Type                                                                                   | Required                                                                               | Description                                                                            |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `datapoint_id`                                                                         | *str*                                                                                  | :heavy_check_mark:                                                                     | ID of datapoint to update                                                              |
| `update_datapoint_request`                                                             | [components.UpdateDatapointRequest](../../models/components/updatedatapointrequest.md) | :heavy_check_mark:                                                                     | N/A                                                                                    |


### Response

**[operations.UpdateDatapointResponse](../../models/operations/updatedatapointresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## delete_datapoint

Delete a specific datapoint

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datapoints.delete_datapoint(id='<value>')

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `id`               | *str*              | :heavy_check_mark: | Datapoint ID       |


### Response

**[operations.DeleteDatapointResponse](../../models/operations/deletedatapointresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## get_datapoint

Retrieve a specific datapoint

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datapoints.get_datapoint(id='<value>')

if res.datapoint is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `id`               | *str*              | :heavy_check_mark: | Datapoint ID       |


### Response

**[operations.GetDatapointResponse](../../models/operations/getdatapointresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |
