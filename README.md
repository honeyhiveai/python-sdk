# HoneyHive

## SDK Installation

```bash
pip install honeyhive
```
<!-- End SDK Installation -->

<!-- Start IDE Support [idesupport] -->
## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

```python
# Synchronous Example
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

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from honeyhive import HoneyHive

async def main():
    s = HoneyHive(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
    )
    res = await s.session.start_session_async(request={
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

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [configurations](docs/sdks/configurations/README.md)

* [get_configurations](docs/sdks/configurations/README.md#get_configurations) - Retrieve a list of configurations
* [create_configuration](docs/sdks/configurations/README.md#create_configuration) - Create a new configuration
* [update_configuration](docs/sdks/configurations/README.md#update_configuration) - Update an existing configuration
* [delete_configuration](docs/sdks/configurations/README.md#delete_configuration) - Delete a configuration

### [datapoints](docs/sdks/datapoints/README.md)

* [get_datapoints](docs/sdks/datapoints/README.md#get_datapoints) - Retrieve a list of datapoints
* [create_datapoint](docs/sdks/datapoints/README.md#create_datapoint) - Create a new datapoint
* [get_datapoint](docs/sdks/datapoints/README.md#get_datapoint) - Retrieve a specific datapoint
* [update_datapoint](docs/sdks/datapoints/README.md#update_datapoint) - Update a specific datapoint
* [delete_datapoint](docs/sdks/datapoints/README.md#delete_datapoint) - Delete a specific datapoint

### [datasets](docs/sdks/datasets/README.md)

* [get_datasets](docs/sdks/datasets/README.md#get_datasets) - Get datasets
* [create_dataset](docs/sdks/datasets/README.md#create_dataset) - Create a dataset
* [update_dataset](docs/sdks/datasets/README.md#update_dataset) - Update a dataset
* [delete_dataset](docs/sdks/datasets/README.md#delete_dataset) - Delete a dataset
* [add_datapoints](docs/sdks/datasets/README.md#add_datapoints) - Add datapoints to a dataset

### [events](docs/sdks/events/README.md)

* [create_event](docs/sdks/events/README.md#create_event) - Create a new event
* [update_event](docs/sdks/events/README.md#update_event) - Update an event
* [get_events](docs/sdks/events/README.md#get_events) - Retrieve events based on filters
* [create_model_event](docs/sdks/events/README.md#create_model_event) - Create a new model event
* [create_event_batch](docs/sdks/events/README.md#create_event_batch) - Create a batch of events
* [create_model_event_batch](docs/sdks/events/README.md#create_model_event_batch) - Create a batch of model events

### [experiments](docs/sdks/experiments/README.md)

* [create_run](docs/sdks/experiments/README.md#create_run) - Create a new evaluation run
* [get_runs](docs/sdks/experiments/README.md#get_runs) - Get a list of evaluation runs
* [get_run](docs/sdks/experiments/README.md#get_run) - Get details of an evaluation run
* [update_run](docs/sdks/experiments/README.md#update_run) - Update an evaluation run
* [delete_run](docs/sdks/experiments/README.md#delete_run) - Delete an evaluation run
* [get_experiment_result](docs/sdks/experiments/README.md#get_experiment_result) - Retrieve experiment result
* [get_experiment_comparison](docs/sdks/experiments/README.md#get_experiment_comparison) - Retrieve experiment comparison


### [metrics](docs/sdks/metrics/README.md)

* [get_metrics](docs/sdks/metrics/README.md#get_metrics) - Get all metrics
* [create_metric](docs/sdks/metrics/README.md#create_metric) - Create a new metric
* [update_metric](docs/sdks/metrics/README.md#update_metric) - Update an existing metric
* [delete_metric](docs/sdks/metrics/README.md#delete_metric) - Delete a metric

### [projects](docs/sdks/projects/README.md)

* [get_projects](docs/sdks/projects/README.md#get_projects) - Get a list of projects
* [create_project](docs/sdks/projects/README.md#create_project) - Create a new project
* [update_project](docs/sdks/projects/README.md#update_project) - Update an existing project
* [delete_project](docs/sdks/projects/README.md#delete_project) - Delete a project

### [session](docs/sdks/session/README.md)

* [start_session](docs/sdks/session/README.md#start_session) - Start a new session
* [get_session](docs/sdks/session/README.md#get_session) - Retrieve a session

### [tools](docs/sdks/tools/README.md)

* [get_tools](docs/sdks/tools/README.md#get_tools) - Retrieve a list of tools
* [create_tool](docs/sdks/tools/README.md#create_tool) - Create a new tool
* [update_tool](docs/sdks/tools/README.md#update_tool) - Update an existing tool
* [delete_tool](docs/sdks/tools/README.md#delete_tool) - Delete a tool

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
from honeyhive import HoneyHive
from honeyhive.utils import BackoffStrategy, RetryConfig

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
},
    RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

if res.object is not None:
    # handle response
    pass

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from honeyhive import HoneyHive
from honeyhive.utils import BackoffStrategy, RetryConfig

s = HoneyHive(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
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
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

Handling errors in this SDK should largely match your expectations. All operations return a response object or raise an exception.

By default, an API error will raise a errors.SDKError exception, which has the following properties:

| Property        | Type             | Description           |
|-----------------|------------------|-----------------------|
| `.status_code`  | *int*            | The HTTP status code  |
| `.message`      | *str*            | The error message     |
| `.raw_response` | *httpx.Response* | The raw HTTP response |
| `.body`         | *str*            | The response content  |

When custom error responses are specified for an operation, the SDK may also raise their associated exceptions. You can refer to respective *Errors* tables in SDK docs for more details on possible exception types for each operation. For example, the `create_event_batch_async` method may raise the following exceptions:

| Error Type                          | Status Code                         | Content Type                        |
| ----------------------------------- | ----------------------------------- | ----------------------------------- |
| errors.CreateEventBatchResponseBody | 500                                 | application/json                    |
| errors.SDKError                     | 4XX, 5XX                            | \*/\*                               |

### Example

```python
from honeyhive import HoneyHive
from honeyhive.models import components, errors

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = None
try:
    res = s.events.create_event_batch(request={
        "events": [
            {
                "project": "Simple RAG",
                "source": "playground",
                "event_name": "Model Completion",
                "event_type": components.CreateEventRequestEventType.MODEL,
                "config": {
                    "model": "gpt-3.5-turbo",
                    "version": "v0.1",
                    "provider": "openai",
                    "hyperparameters": {
                        "temperature": 0,
                        "top_p": 1,
                        "max_tokens": 1000,
                        "presence_penalty": 0,
                        "frequency_penalty": 0,
                        "stop": [
                            "<value>",
                        ],
                        "n": 1,
                    },
                    "template": [
                        {
                            "role": "system",
                            "content": "Answer the user's question only using provided context.\n" +
                            "\n" +
                            "Context: {{ context }}",
                        },
                        {
                            "role": "user",
                            "content": "{{question}}",
                        },
                    ],
                    "type": "chat",
                },
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
                "duration": 999.8056,
                "event_id": "7f22137a-6911-4ed3-bc36-110f1dde6b66",
                "session_id": "caf77ace-3417-4da4-944d-f4a0688f3c23",
                "parent_id": "caf77ace-3417-4da4-944d-f4a0688f3c23",
                "children_ids": [
                    "<value>",
                ],
                "outputs": {
                    "role": "assistant",
                    "content": "Hello world",
                },
                "error": "<value>",
                "start_time": 1714978764301,
                "end_time": 1714978765301,
                "metadata": {
                    "cost": 0.00008,
                    "completion_tokens": 23,
                    "prompt_tokens": 35,
                    "total_tokens": 58,
                },
                "feedback": {

                },
                "metrics": {
                    "Answer Faithfulness": 5,
                    "Answer Faithfulness_explanation": "The AI assistant's answer is a concise and accurate description of Ramp's API. It provides a clear explanation of what the API does and how developers can use it to integrate Ramp's financial services into their own applications. The answer is faithful to the provided context.",
                    "Number of words": 18,
                },
                "user_properties": {
                    "user": "google-oauth2|111840237613341303366",
                },
            },
        ],
        "session_properties": {
            "session_name": "Playground Session",
            "source": "playground",
            "session_id": "caf77ace-3417-4da4-944d-f4a0688f3c23",
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
            "user_properties": {
                "user": "google-oauth2|111840237613341303366",
            },
            "metrics": {

            },
            "feedback": {

            },
            "metadata": {

            },
        },
    })

    if res.object is not None:
        # handle response
        pass

except errors.CreateEventBatchResponseBody as e:
    # handle e.data: errors.CreateEventBatchResponseBodyData
    raise(e)
except errors.SDKError as e:
    # handle exception
    raise(e)
```
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Select Server by Index

You can override the default server globally by passing a server index to the `server_idx: int` optional parameter when initializing the SDK client instance. The selected server will then be used as the default on the operations that use it. This table lists the indexes associated with the available servers:

| # | Server | Variables |
| - | ------ | --------- |
| 0 | `https://api.honeyhive.ai` | None |

#### Example

```python
from honeyhive import HoneyHive

s = HoneyHive(
    server_idx=0,
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


### Override Server URL Per-Client

The default server can also be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from honeyhive import HoneyHive

s = HoneyHive(
    server_url="https://api.honeyhive.ai",
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
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:
```python
from honeyhive import HoneyHive
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = HoneyHive(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from honeyhive import HoneyHive
from honeyhive.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = HoneyHive(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports the following security scheme globally:

| Name          | Type          | Scheme        |
| ------------- | ------------- | ------------- |
| `bearer_auth` | http          | HTTP Bearer   |

To authenticate with the API the `bearer_auth` parameter must be set when initializing the SDK client instance. For example:
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
<!-- End Authentication [security] -->

<!-- Start Summary [summary] -->
## Summary


<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents

* [SDK Installation](#sdk-installation)
* [IDE Support](#ide-support)
* [SDK Example Usage](#sdk-example-usage)
* [Available Resources and Operations](#available-resources-and-operations)
* [Retries](#retries)
* [Error Handling](#error-handling)
* [Server Selection](#server-selection)
* [Custom HTTP Client](#custom-http-client)
* [Authentication](#authentication)
* [Debugging](#debugging)
<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

The SDK can be installed with either *pip* or *poetry* package managers.

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install HoneyHive
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add HoneyHive
```
<!-- End SDK Installation [installation] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `HoneyHive` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from honeyhive import HoneyHive
def main():

    with HoneyHive(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
    ) as honey_hive:
        # Rest of application here...


# Or when using async:
async def amain():

    async with HoneyHive(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
    ) as honey_hive:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from honeyhive import HoneyHive
import logging

logging.basicConfig(level=logging.DEBUG)
s = HoneyHive(debug_logger=logging.getLogger("honeyhive"))
```
<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically.
Feel free to open a PR or a Github issue as a proof of concept and we'll do our best to include it in a future release!

### SDK Created by [Speakeasy](https://docs.speakeasyapi.dev/docs/using-speakeasy/client-sdks)
