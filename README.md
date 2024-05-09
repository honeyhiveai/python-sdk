# HoneyHive

## SDK Installation

```bash
pip install honeyhive
```
<!-- End SDK Installation -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example

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
<!-- End SDK Example Usage [usage] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

### [session](docs/sdks/session/README.md)

* [start_session](docs/sdks/session/README.md#start_session) - Start a new session
* [get_session](docs/sdks/session/README.md#get_session) - Retrieve a session
* [process_event_trace](docs/sdks/session/README.md#process_event_trace) - Process an event trace for a given session

### [events](docs/sdks/events/README.md)

* [create_event](docs/sdks/events/README.md#create_event) - Create a new event
* [update_event](docs/sdks/events/README.md#update_event) - Update an event

### [metrics](docs/sdks/metrics/README.md)

* [get_metrics](docs/sdks/metrics/README.md#get_metrics) - Get all metrics
* [create_metric](docs/sdks/metrics/README.md#create_metric) - Create a new metric
* [update_metric](docs/sdks/metrics/README.md#update_metric) - Update an existing metric
* [delete_metric](docs/sdks/metrics/README.md#delete_metric) - Delete a metric

### [tools](docs/sdks/tools/README.md)

* [get_tools](docs/sdks/tools/README.md#get_tools) - Retrieve a list of tools
* [create_tool](docs/sdks/tools/README.md#create_tool) - Create a new tool
* [update_tool](docs/sdks/tools/README.md#update_tool) - Update an existing tool
* [delete_tool](docs/sdks/tools/README.md#delete_tool) - Delete a tool

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

### [projects](docs/sdks/projects/README.md)

* [get_projects](docs/sdks/projects/README.md#get_projects) - Get a list of projects
* [create_project](docs/sdks/projects/README.md#create_project) - Create a new project
* [update_project](docs/sdks/projects/README.md#update_project) - Update an existing project
* [delete_project](docs/sdks/projects/README.md#delete_project) - Delete a project

### [configurations](docs/sdks/configurations/README.md)

* [get_configurations](docs/sdks/configurations/README.md#get_configurations) - Retrieve a list of configurations
* [create_configuration](docs/sdks/configurations/README.md#create_configuration) - Create a new configuration
* [update_configuration](docs/sdks/configurations/README.md#update_configuration) - Update an existing configuration
* [delete_configuration](docs/sdks/configurations/README.md#delete_configuration) - Delete a configuration
<!-- End Available Resources and Operations [operations] -->

<!-- Start Error Handling [errors] -->
## Error Handling

Handling errors in this SDK should largely match your expectations.  All operations return a response object or raise an error.  If Error objects are specified in your OpenAPI Spec, the SDK will raise the appropriate Error type.

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

### Example

```python
import honeyhive
from honeyhive.models import components, errors, operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = None
try:
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
except errors.SDKError as e:
    # handle exception
    raise(e)

if res.object is not None:
    # handle response
    pass

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
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    server_idx=0,
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


### Override Server URL Per-Client

The default server can also be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    server_url="https://api.honeyhive.ai",
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
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [requests](https://pypi.org/project/requests/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with a custom `requests.Session` object.

For example, you could specify a header for every request that this sdk makes as follows:
```python
import honeyhive
import requests

http_client = requests.Session()
http_client.headers.update({'x-custom-header': 'someValue'})
s = honeyhive.HoneyHive(client=http_client)
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
<!-- End Authentication [security] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

```bash
pip install HoneyHive
```
<!-- End SDK Installation [installation] -->

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
