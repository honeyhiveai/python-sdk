# Session
(*session*)

### Available Operations

* [start_session](#start_session) - Start a new session
* [delete_session](#delete_session) - Delete a session
* [get_session](#get_session) - Retrieve a session
* [process_event_trace](#process_event_trace) - Process an event trace for a given session

## start_session

Start a new session

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = operations.StartSessionRequestBody()

res = s.session.start_session(req)

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                | Type                                                                                     | Required                                                                                 | Description                                                                              |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `request`                                                                                | [operations.StartSessionRequestBody](../../models/operations/startsessionrequestbody.md) | :heavy_check_mark:                                                                       | The request object to use for the request.                                               |


### Response

**[operations.StartSessionResponse](../../models/operations/startsessionresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## delete_session

Delete a session

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.session.delete_session(session_id='<value>')

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `session_id`       | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteSessionResponse](../../models/operations/deletesessionresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## get_session

Retrieve a session

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.session.get_session(session_id='<value>')

if res.event is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `session_id`       | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.GetSessionResponse](../../models/operations/getsessionresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## process_event_trace

Process an event trace for a given session

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.session.process_event_trace(session_id='<value>', request_body=operations.ProcessEventTraceRequestBody())

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                          | Type                                                                                               | Required                                                                                           | Description                                                                                        |
| -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `session_id`                                                                                       | *str*                                                                                              | :heavy_check_mark:                                                                                 | The ID of the session to which this event trace belongs                                            |
| `request_body`                                                                                     | [operations.ProcessEventTraceRequestBody](../../models/operations/processeventtracerequestbody.md) | :heavy_check_mark:                                                                                 | N/A                                                                                                |


### Response

**[operations.ProcessEventTraceResponse](../../models/operations/processeventtraceresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |
