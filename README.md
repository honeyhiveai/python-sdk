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
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.get_configurations(project_name='<value>', type=operations.Type.LLM)

if res.configurations is not None:
    # handle response
    pass

```
<!-- End SDK Example Usage [usage] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

### [configurations](docs/sdks/configurations/README.md)

* [get_configurations](docs/sdks/configurations/README.md#get_configurations) - Retrieve a list of configurations
* [create_configuration](docs/sdks/configurations/README.md#create_configuration) - Create a new configuration
* [delete_configuration](docs/sdks/configurations/README.md#delete_configuration) - Delete a configuration
* [update_configuration](docs/sdks/configurations/README.md#update_configuration) - Update an existing configuration

### [datapoints](docs/sdks/datapoints/README.md)

* [get_datapoints](docs/sdks/datapoints/README.md#get_datapoints) - Retrieve a list of datapoints
* [create_datapoint](docs/sdks/datapoints/README.md#create_datapoint) - Create a new datapoint
* [update_datapoint](docs/sdks/datapoints/README.md#update_datapoint) - Update a specific datapoint
* [delete_datapoint](docs/sdks/datapoints/README.md#delete_datapoint) - Delete a specific datapoint
* [get_datapoint](docs/sdks/datapoints/README.md#get_datapoint) - Retrieve a specific datapoint

### [datasets](docs/sdks/datasets/README.md)

* [delete_datasets](docs/sdks/datasets/README.md#delete_datasets) - Delete a dataset
* [get_datasets](docs/sdks/datasets/README.md#get_datasets) - Get datasets
* [post_datasets](docs/sdks/datasets/README.md#post_datasets) - Create a dataset
* [put_datasets](docs/sdks/datasets/README.md#put_datasets) - Update a dataset

### [events](docs/sdks/events/README.md)

* [post_events](docs/sdks/events/README.md#post_events) - Create a new event
* [put_events](docs/sdks/events/README.md#put_events) - Update an event
* [delete_events_event_id_](docs/sdks/events/README.md#delete_events_event_id_) - Delete an event

### [metrics](docs/sdks/metrics/README.md)

* [delete_metrics](docs/sdks/metrics/README.md#delete_metrics) - Delete a metric
* [get_metrics](docs/sdks/metrics/README.md#get_metrics) - Get all metrics
* [post_metrics](docs/sdks/metrics/README.md#post_metrics) - Create a new metric
* [put_metrics](docs/sdks/metrics/README.md#put_metrics) - Update an existing metric

### [projects](docs/sdks/projects/README.md)

* [delete_project](docs/sdks/projects/README.md#delete_project) - Delete a project
* [get_projects](docs/sdks/projects/README.md#get_projects) - Get a list of projects
* [create_project](docs/sdks/projects/README.md#create_project) - Create a new project
* [update_project](docs/sdks/projects/README.md#update_project) - Update an existing project

### [session](docs/sdks/session/README.md)

* [start_session](docs/sdks/session/README.md#start_session) - Start a new session
* [delete_session](docs/sdks/session/README.md#delete_session) - Delete a session
* [get_session](docs/sdks/session/README.md#get_session) - Retrieve a session
* [process_event_trace](docs/sdks/session/README.md#process_event_trace) - Process an event trace for a given session

### [tools](docs/sdks/tools/README.md)

* [delete_tool](docs/sdks/tools/README.md#delete_tool) - Delete a tool
* [get_tools](docs/sdks/tools/README.md#get_tools) - Retrieve a list of tools
* [create_tool](docs/sdks/tools/README.md#create_tool) - Create a new tool
* [update_tool](docs/sdks/tools/README.md#update_tool) - Update an existing tool
<!-- End Available Resources and Operations [operations] -->

<!-- Start Error Handling [errors] -->
## Error Handling

Handling errors in this SDK should largely match your expectations.  All operations return a response object or raise an error.  If Error objects are specified in your OpenAPI Spec, the SDK will raise the appropriate Error type.

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

### Example

```python
import honeyhive
from honeyhive.models import errors, operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = None
try:
    res = s.configurations.get_configurations(project_name='<value>', type=operations.Type.LLM)
except errors.SDKError as e:
    # handle exception
    raise(e)

if res.configurations is not None:
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
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    server_idx=0,
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.get_configurations(project_name='<value>', type=operations.Type.LLM)

if res.configurations is not None:
    # handle response
    pass

```


### Override Server URL Per-Client

The default server can also be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    server_url="https://api.honeyhive.ai",
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.get_configurations(project_name='<value>', type=operations.Type.LLM)

if res.configurations is not None:
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
s = honeyhive.HoneyHive(client: http_client)
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
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.get_configurations(project_name='<value>', type=operations.Type.LLM)

if res.configurations is not None:
    # handle response
    pass

```

### Per-Operation Security Schemes

Some operations in this SDK require the security scheme to be specified at the request level. For example:
```python
import honeyhive

s = honeyhive.HoneyHive()


res = s.tools.get_tools("<YOUR_BEARER_TOKEN_HERE>")

if res.tools is not None:
    # handle response
    pass

```
<!-- End Authentication [security] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

```bash
pip install git+https://github.com/honeyhiveai/python-sdk.git
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
