# Events
(*events*)

### Available Operations

* [post_events](#post_events) - Create a new event
* [put_events](#put_events) - Update an event
* [delete_events_event_id_](#delete_events_event_id_) - Delete an event

## post_events

Please refer to our instrumentation guide for detailed information

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

req = operations.PutEventsRequestBody(
    event_id='<value>',
)

res = s.events.put_events(req)

if res is not None:
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

## delete_events_event_id_

Delete an event

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.events.delete_events_event_id_(event_id='<value>', project='<value>')

if res is not None:
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
