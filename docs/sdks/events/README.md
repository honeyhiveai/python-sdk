# Events
(*events*)

### Available Operations

* [create_event](#create_event) - Create a new event
* [update_event](#update_event) - Update an event
* [get_events](#get_events) - Retrieve events based on filters

## create_event

Please refer to our instrumentation guide for detailed information

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.events.create_event(request=operations.CreateEventRequestBody(
    event=components.CreateEventRequest(
        project='Simple RAG',
        source='playground',
        event_name='Model Completion',
        event_type=components.CreateEventRequestEventType.MODEL,
        config={
            'model': 'gpt-3.5-turbo',
            'version': 'v0.1',
            'provider': 'openai',
            'hyperparameters': {
                'temperature': 0,
                'top_p': 1,
                'max_tokens': 1000,
                'presence_penalty': 0,
                'frequency_penalty': 0,
                'stop': [
                    '<value>',
                ],
                'n': 1,
            },
            'template': [
                {
                    'role': 'system',
                    'content': 'Answer the user\'s question only using provided context.

                    Context: {{ context }}',
                },
                {
                    'role': 'user',
                    'content': '{{question}}',
                },
            ],
            'type': 'chat',
        },
        inputs=components.CreateEventRequestInputs(
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
            additional_properties={
                'context': 'Hello world',
                'question': 'What is in the context?',
            },
        ),
        duration=999.8056,
        event_id='7f22137a-6911-4ed3-bc36-110f1dde6b66',
        session_id='caf77ace-3417-4da4-944d-f4a0688f3c23',
        parent_id='caf77ace-3417-4da4-944d-f4a0688f3c23',
        children_ids=[
            '<value>',
        ],
        outputs={
            'role': 'assistant',
            'content': 'Hello world',
        },
        error=None,
        start_time=1714978764301,
        end_time=1714978765301,
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
))

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                              | Type                                                                                   | Required                                                                               | Description                                                                            |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `request`                                                                              | [operations.CreateEventRequestBody](../../models/operations/createeventrequestbody.md) | :heavy_check_mark:                                                                     | The request object to use for the request.                                             |


### Response

**[operations.CreateEventResponse](../../models/operations/createeventresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## update_event

Update an event

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.events.update_event(request=operations.UpdateEventRequestBody(
    event_id='7f22137a-6911-4ed3-bc36-110f1dde6b66',
    metadata={
        'cost': 0.00008,
        'completion_tokens': 23,
        'prompt_tokens': 35,
        'total_tokens': 58,
    },
    feedback={
        'rating': 5,
    },
    metrics={
        'num_words': 2,
    },
    outputs={
        'role': 'assistant',
        'content': 'Hello world',
    },
))

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                              | Type                                                                                   | Required                                                                               | Description                                                                            |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `request`                                                                              | [operations.UpdateEventRequestBody](../../models/operations/updateeventrequestbody.md) | :heavy_check_mark:                                                                     | The request object to use for the request.                                             |


### Response

**[operations.UpdateEventResponse](../../models/operations/updateeventresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## get_events

Retrieve events based on filters

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.events.get_events(request=operations.GetEventsRequestBody(
    project='<value>',
    filters=[
        components.EventFilter(
            field='event_type',
            value='model',
            operator=components.Operator.IS,
            type=components.Type.STRING,
        ),
    ],
))

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `request`                                                                          | [operations.GetEventsRequestBody](../../models/operations/geteventsrequestbody.md) | :heavy_check_mark:                                                                 | The request object to use for the request.                                         |


### Response

**[operations.GetEventsResponse](../../models/operations/geteventsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |
