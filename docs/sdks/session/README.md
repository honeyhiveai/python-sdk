# Session
(*session*)

## Overview

### Available Operations

* [start_session](#start_session) - Start a new session
* [get_session](#get_session) - Retrieve a session

## start_session

Start a new session

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.session.start_session(request={
    "session": {
        "project": "Simple RAG Project",
        "session_name": "Playground Session",
        "source": "playground",
        "session_id": "caf77ace-3417-4da4-944d-f4a0688f3c23",
        "children_ids": [
            "7f22137a-6911-4ed3-bc36-110f1dde6b66",
        ],
        "inputs": {
            "context": "Hello world",
            "question": "What is in the context?",
            "chat_history": [
                {
                    "role": "system",
                    "content": "Answer the user's question only using provided context.\n" +
                    "\n" +
                    "Context: Hello world",
                },
                {
                    "role": "user",
                    "content": "What is in the context?",
                },
            ],
        },
        "outputs": {
            "role": "assistant",
            "content": "Hello world",
        },
        "error": "<value>",
        "duration": 824.8056,
        "user_properties": {
            "user": "google-oauth2|111840237613341303366",
        },
        "metrics": {

        },
        "feedback": {

        },
        "metadata": {

        },
        "start_time": 1712025501605,
        "end_time": 1712025499832,
    },
})

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                | Type                                                                                     | Required                                                                                 | Description                                                                              |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `request`                                                                                | [operations.StartSessionRequestBody](../../models/operations/startsessionrequestbody.md) | :heavy_check_mark:                                                                       | The request object to use for the request.                                               |
| `retries`                                                                                | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                         | :heavy_minus_sign:                                                                       | Configuration to override the default retry behavior of the client.                      |

### Response

**[operations.StartSessionResponse](../../models/operations/startsessionresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## get_session

Retrieve a session

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.session.get_session(session_id="<id>")

if res.event is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `session_id`                                                        | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[operations.GetSessionResponse](../../models/operations/getsessionresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |