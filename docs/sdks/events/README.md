# Events
(*events*)

## Overview

### Available Operations

* [create_event](#create_event) - Create a new event
* [update_event](#update_event) - Update an event
* [get_events](#get_events) - Retrieve events based on filters
* [create_model_event](#create_model_event) - Create a new model event
* [create_event_batch](#create_event_batch) - Create a batch of events
* [create_model_event_batch](#create_model_event_batch) - Create a batch of model events

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
            'hyperparameters': {
                'frequency_penalty': 0,
                'max_tokens': 1000,
                'n': 1,
                'presence_penalty': 0,
                'stop': [
                    '<value>',
                ],
                'temperature': 0,
                'top_p': 1,
            },
            'model': 'gpt-3.5-turbo',
            'provider': 'openai',
            'template': [
                {
                    'role': 'system',
                    'content': 'Answer the user\'s question only using provided context.\n' +
                    '\n' +
                    'Context: {{ context }}',
                },
                {
                    'role': 'user',
                    'content': '{{question}}',
                },
            ],
            'type': 'chat',
            'version': 'v0.1',
        },
        inputs={
            'chat_history': [
                {
                    'role': 'system',
                    'content': 'Answer the user\'s question only using provided context.\n' +
                    '\n' +
                    'Context: Hello world',
                },
                {
                    'role': 'user',
                    'content': 'What is in the context?',
                },
            ],
            'context': 'Hello world',
            'question': 'What is in the context?',
        },
        duration=999.8056,
        event_id='7f22137a-6911-4ed3-bc36-110f1dde6b66',
        session_id='caf77ace-3417-4da4-944d-f4a0688f3c23',
        parent_id='caf77ace-3417-4da4-944d-f4a0688f3c23',
        children_ids=[
            '<value>',
        ],
        outputs={
            'content': 'Hello world',
            'role': 'assistant',
        },
        error='<value>',
        start_time=1714978764301,
        end_time=1714978765301,
        metadata={
            'completion_tokens': 23,
            'cost': 0.00008,
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

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

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
        'completion_tokens': 23,
        'cost': 0.00008,
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
        'content': 'Hello world',
        'role': 'assistant',
    },
    config={
        'template': [
            {
                'role': 'system',
                'content': 'Hello, {{ name }}!',
            },
        ],
    },
    user_properties={
        'user_id': '691b1f94-d38c-4e92-b051-5e03fee9ff86',
    },
    duration=42,
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

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

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

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## create_model_event

Please refer to our instrumentation guide for detailed information

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.events.create_model_event(request=operations.CreateModelEventRequestBody(
    model_event=components.CreateModelEvent(
        project='New Project',
        model='gpt-4o',
        provider='openai',
        messages=[
            {
                'role': 'system',
                'content': 'Hello, world!',
            },
        ],
        response={
            'content': 'Hello, world!',
            'role': 'assistant',
        },
        duration=42,
        usage={
            'completion_tokens': 10,
            'prompt_tokens': 10,
            'total_tokens': 20,
        },
        cost=0.00008,
        error='<value>',
        source='playground',
        event_name='Model Completion',
        hyperparameters={
            'frequency_penalty': 0,
            'max_tokens': 1000,
            'n': 1,
            'presence_penalty': 0,
            'stop': [
                '<value>',
            ],
            'temperature': 0,
            'top_p': 1,
        },
        template=[
            {
                'role': 'system',
                'content': 'Hello, {{ name }}!',
            },
        ],
        template_inputs={
            'name': 'world',
        },
        tools=[
            {
                'type': 'function',
                'function': {
                    'name': 'get_current_weather',
                    'description': 'Get the current weather',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'location': {
                                'type': 'string',
                                'description': 'The city and state, e.g. San Francisco, CA',
                            },
                            'format': {
                                'type': 'string',
                                'enum': [
                                    'celsius',
                                    'fahrenheit',
                                ],
                                'description': 'The temperature unit to use. Infer this from the users location.',
                            },
                        },
                        'required': [
                            'location',
                            'format',
                        ],
                    },
                },
            },
        ],
        tool_choice='none',
        response_format={
            'type': 'text',
        },
    ),
))

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                        | Type                                                                                             | Required                                                                                         | Description                                                                                      |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `request`                                                                                        | [operations.CreateModelEventRequestBody](../../models/operations/createmodeleventrequestbody.md) | :heavy_check_mark:                                                                               | The request object to use for the request.                                                       |

### Response

**[operations.CreateModelEventResponse](../../models/operations/createmodeleventresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## create_event_batch

Please refer to our instrumentation guide for detailed information

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.events.create_event_batch(request=operations.CreateEventBatchRequestBody(
    events=[
        components.CreateEventRequest(
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
                        'content': 'Answer the user\'s question only using provided context.\n' +
                        '\n' +
                        'Context: {{ context }}',
                    },
                    {
                        'role': 'user',
                        'content': '{{question}}',
                    },
                ],
                'type': 'chat',
            },
            inputs={
                'context': 'Hello world',
                'question': 'What is in the context?',
                'chat_history': [
                    {
                        'role': 'system',
                        'content': 'Answer the user\'s question only using provided context.\n' +
                        '\n' +
                        'Context: Hello world',
                    },
                    {
                        'role': 'user',
                        'content': 'What is in the context?',
                    },
                ],
            },
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
            error='<value>',
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
    ],
    session_properties=operations.SessionProperties(
        model_event=components.SessionPropertiesBatch(
            session_name='Playground Session',
            source='playground',
            session_id='caf77ace-3417-4da4-944d-f4a0688f3c23',
            inputs={
                'context': 'Hello world',
                'question': 'What is in the context?',
                'chat_history': [
                    {
                        'role': 'system',
                        'content': 'Answer the user\'s question only using provided context.\n' +
                        '\n' +
                        'Context: Hello world',
                    },
                    {
                        'role': 'user',
                        'content': 'What is in the context?',
                    },
                ],
            },
            outputs={
                'role': 'assistant',
                'content': 'Hello world',
            },
            error='<value>',
            user_properties={
                'user': 'google-oauth2|111840237613341303366',
            },
            metrics={

            },
            feedback={

            },
            metadata={

            },
        ),
    ),
))

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                        | Type                                                                                             | Required                                                                                         | Description                                                                                      |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| `request`                                                                                        | [operations.CreateEventBatchRequestBody](../../models/operations/createeventbatchrequestbody.md) | :heavy_check_mark:                                                                               | The request object to use for the request.                                                       |

### Response

**[operations.CreateEventBatchResponse](../../models/operations/createeventbatchresponse.md)**

### Errors

| Error Type                          | Status Code                         | Content Type                        |
| ----------------------------------- | ----------------------------------- | ----------------------------------- |
| errors.CreateEventBatchResponseBody | 500                                 | application/json                    |
| errors.SDKError                     | 4XX, 5XX                            | \*/\*                               |

## create_model_event_batch

Please refer to our instrumentation guide for detailed information

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.events.create_model_event_batch(request=operations.CreateModelEventBatchRequestBody(
    model_events=[
        components.CreateModelEvent(
            project='New Project',
            model='gpt-4o',
            provider='openai',
            messages=[
                {
                    'role': 'system',
                    'content': 'Hello, world!',
                },
            ],
            response={
                'role': 'assistant',
                'content': 'Hello, world!',
            },
            duration=42,
            usage={
                'prompt_tokens': 10,
                'completion_tokens': 10,
                'total_tokens': 20,
            },
            cost=0.00008,
            error='<value>',
            source='playground',
            event_name='Model Completion',
            hyperparameters={
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
            template=[
                {
                    'role': 'system',
                    'content': 'Hello, {{ name }}!',
                },
            ],
            template_inputs={
                'name': 'world',
            },
            tools=[
                {
                    'type': 'function',
                    'function': {
                        'name': 'get_current_weather',
                        'description': 'Get the current weather',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'location': {
                                    'type': 'string',
                                    'description': 'The city and state, e.g. San Francisco, CA',
                                },
                                'format': {
                                    'type': 'string',
                                    'enum': [
                                        'celsius',
                                        'fahrenheit',
                                    ],
                                    'description': 'The temperature unit to use. Infer this from the users location.',
                                },
                            },
                            'required': [
                                'location',
                                'format',
                            ],
                        },
                    },
                },
            ],
            tool_choice='none',
            response_format={
                'type': 'text',
            },
        ),
    ],
    session_properties=operations.CreateModelEventBatchSessionProperties(
        model_event=components.SessionPropertiesBatch(
            session_name='Playground Session',
            source='playground',
            session_id='caf77ace-3417-4da4-944d-f4a0688f3c23',
            inputs={
                'context': 'Hello world',
                'question': 'What is in the context?',
                'chat_history': [
                    {
                        'role': 'system',
                        'content': 'Answer the user\'s question only using provided context.\n' +
                        '\n' +
                        'Context: Hello world',
                    },
                    {
                        'role': 'user',
                        'content': 'What is in the context?',
                    },
                ],
            },
            outputs={
                'role': 'assistant',
                'content': 'Hello world',
            },
            error='<value>',
            user_properties={
                'user': 'google-oauth2|111840237613341303366',
            },
            metrics={

            },
            feedback={

            },
            metadata={

            },
        ),
    ),
))

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                                  | Type                                                                                                       | Required                                                                                                   | Description                                                                                                |
| ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `request`                                                                                                  | [operations.CreateModelEventBatchRequestBody](../../models/operations/createmodeleventbatchrequestbody.md) | :heavy_check_mark:                                                                                         | The request object to use for the request.                                                                 |

### Response

**[operations.CreateModelEventBatchResponse](../../models/operations/createmodeleventbatchresponse.md)**

### Errors

| Error Type                               | Status Code                              | Content Type                             |
| ---------------------------------------- | ---------------------------------------- | ---------------------------------------- |
| errors.CreateModelEventBatchResponseBody | 500                                      | application/json                         |
| errors.SDKError                          | 4XX, 5XX                                 | \*/\*                                    |