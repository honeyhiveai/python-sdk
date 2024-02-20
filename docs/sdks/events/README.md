# Events
(*events*)

### Available Operations

* [get_events](#get_events) - Retrieve events based on filters
* [post_events](#post_events) - Create a new event
* [put_events](#put_events) - Update an event
* [get_events_chart](#get_events_chart) - Retrieve a chart of events
* [delete_events_event_id_](#delete_events_event_id_) - Delete an event

## get_events

Retrieve events based on filters

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.events.get_events(project='<value>', filters='<value>')

if res.status_code == 200:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `project`          | *str*              | :heavy_check_mark: | N/A                |
| `filters`          | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.GetEventsResponse](../../models/operations/geteventsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## post_events

Create a new event

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = operations.PostEventsRequestBody()

res = s.events.post_events(req)

if res.object is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                            | Type                                                                                 | Required                                                                             | Description                                                                          |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| `request`                                                                            | [operations.PostEventsRequestBody](../../models/operations/posteventsrequestbody.md) | :heavy_check_mark:                                                                   | The request object to use for the request.                                           |


### Response

**[operations.PostEventsResponse](../../models/operations/posteventsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## put_events

Update an event

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = operations.PutEventsRequestBody()

res = s.events.put_events(req)

if res.status_code == 200:
    # handle response
    pass
```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `request`                                                                          | [operations.PutEventsRequestBody](../../models/operations/puteventsrequestbody.md) | :heavy_check_mark:                                                                 | The request object to use for the request.                                         |


### Response

**[operations.PutEventsResponse](../../models/operations/puteventsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## get_events_chart

Retrieve a chart of events

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.events.get_events_chart(project='<value>', page=726720, limit=838569)

if res.status_code == 200:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `project`          | *str*              | :heavy_check_mark: | N/A                |
| `page`             | *Optional[int]*    | :heavy_minus_sign: | N/A                |
| `limit`            | *Optional[int]*    | :heavy_minus_sign: | N/A                |


### Response

**[operations.GetEventsChartResponse](../../models/operations/geteventschartresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## delete_events_event_id_

Delete an event

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.events.delete_events_event_id_(event_id='<value>', project='<value>')

if res.status_code == 200:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `event_id`         | *str*              | :heavy_check_mark: | N/A                |
| `project`          | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteEventsEventIDResponse](../../models/operations/deleteeventseventidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |
