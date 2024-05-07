# Session
(*session*)

### Available Operations

* [start_session](#start_session) - Start a new session
* [get_session](#get_session) - Retrieve a session
* [process_event_trace](#process_event_trace) - Process an event trace for a given session

## start_session

Start a new session

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.session.start_session(request=operations.StartSessionRequestBody(
    session=components.SessionStartRequest(
        project='Simple RAG Project',
        session_name='Playground Session',
        source='playground',
        session_id='caf77ace-3417-4da4-944d-f4a0688f3c23',
        children_ids=[
            '7f22137a-6911-4ed3-bc36-110f1dde6b66',
        ],
        inputs={
            'context': 'Hello world',
            'question': 'What is in the context?',
            'chat_history': '<value>',
        },
        outputs={
            'role': 'assistant',
            'content': 'Hello world',
        },
        error=None,
        duration=824.8056,
        user_properties={
            'user': 'google-oauth2|111840237613341303366',
        },
        metrics={

        },
        feedback={

        },
        metadata={

        },
        start_time=1712025501605,
        end_time=1712025499832,
    ),
))

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
| errors.SDKError | 4xx-5xx         | */*             |

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
| errors.SDKError | 4xx-5xx         | */*             |

## process_event_trace

Process an event trace for a given session

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.session.process_event_trace(session_id='<value>', request_body=operations.ProcessEventTraceRequestBody(
    logs=[
        components.Event(
            project_id='65e0fc2d6a2eb95f55a92cbc',
            source='playground',
            event_name='Model Completion',
            event_type=components.EventType.MODEL,
            event_id='7f22137a-6911-4ed3-bc36-110f1dde6b66',
            session_id='caf77ace-3417-4da4-944d-f4a0688f3c23',
            parent_id='caf77ace-3417-4da4-944d-f4a0688f3c23',
            children_ids=[
                '<value>',
            ],
            config={
                'model': 'gpt-3.5-turbo',
                'version': 'v0.1 - Fork',
                'provider': 'openai',
                'hyperparameters': '<value>',
                'template': '<value>',
                'type': 'chat',
            },
            inputs=components.Inputs(
                chat_history=[
                    {
                        'role': 'system',
                        'content': 'Answer the user\'s question only using provided context.

                        Context: Hello world',
                    },
                    {
                        'role': 'user',
                        'content': 'What is in the context?',
                    },
                ],
            ),
            outputs={
                'role': 'assistant',
                'content': 'Hello world',
            },
            error=None,
            start_time=2024-04-01 22:38:19,
            end_time=2024-04-01 22:38:19,
            duration=824.8056,
            metadata={
                'cost': 0.00008,
                'completion_tokens': 23,
                'prompt_tokens': 35,
                'total_tokens': 58,
            },
            feedback={

            },
            metrics={
                'Answer Faithfulness': 5,
                'Answer Faithfulness_explanation': 'The AI assistant\'s answer is a concise and accurate description of Ramp\'s API. It provides a clear explanation of what the API does and how developers can use it to integrate Ramp\'s financial services into their own applications. The answer is faithful to the provided context.',
                'Number of words': 18,
            },
            user_properties={
                'user': 'google-oauth2|111840237613341303366',
            },
        ),
    ],
))

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
| errors.SDKError | 4xx-5xx         | */*             |
