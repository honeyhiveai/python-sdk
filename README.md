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

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.get_configurations(project='<value>', type='<value>')

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

### [datapoint](docs/sdks/datapoint/README.md)

* [get_datapoints](docs/sdks/datapoint/README.md#get_datapoints) - Retrieve a list of datapoints
* [update_datapoint](docs/sdks/datapoint/README.md#update_datapoint) - Update a specific datapoint
* [create_datapoint](docs/sdks/datapoint/README.md#create_datapoint) - Create a new datapoint
* [delete_datapoint](docs/sdks/datapoint/README.md#delete_datapoint) - Delete a specific datapoint
* [get_datapoint](docs/sdks/datapoint/README.md#get_datapoint) - Retrieve a specific datapoint

### [datasets](docs/sdks/datasets/README.md)

* [get_datasets](docs/sdks/datasets/README.md#get_datasets) - Retrieve a list of datasets
* [create_dataset](docs/sdks/datasets/README.md#create_dataset) - Create a new dataset
* [delete_dataset](docs/sdks/datasets/README.md#delete_dataset) - Delete a dataset
* [update_dataset](docs/sdks/datasets/README.md#update_dataset) - Update a dataset

### [events](docs/sdks/events/README.md)

* [get_events](docs/sdks/events/README.md#get_events) - Retrieve events based on filters
* [post_events](docs/sdks/events/README.md#post_events) - Create a new event
* [put_events](docs/sdks/events/README.md#put_events) - Update an event
* [get_events_chart](docs/sdks/events/README.md#get_events_chart) - Retrieve a chart of events
* [delete_events_event_id_](docs/sdks/events/README.md#delete_events_event_id_) - Delete an event

### [metrics](docs/sdks/metrics/README.md)

* [delete_metrics](docs/sdks/metrics/README.md#delete_metrics) - Delete a metric
* [get_metrics](docs/sdks/metrics/README.md#get_metrics) - Get all metrics
* [post_metrics](docs/sdks/metrics/README.md#post_metrics) - Create a new metric
* [put_metrics](docs/sdks/metrics/README.md#put_metrics) - Update an existing metric
* [post_metrics_compute](docs/sdks/metrics/README.md#post_metrics_compute) - Compute metric

### [prompts](docs/sdks/prompts/README.md)

* [get_prompts](docs/sdks/prompts/README.md#get_prompts) - Retrieve a list of prompts based on query parameters.
* [post_prompts](docs/sdks/prompts/README.md#post_prompts) - Create a new prompt.
* [delete_prompts_id_](docs/sdks/prompts/README.md#delete_prompts_id_) - Delete an existing prompt.
* [put_prompts_id_](docs/sdks/prompts/README.md#put_prompts_id_) - Update an existing prompt.

### [session](docs/sdks/session/README.md)

* [start_session](docs/sdks/session/README.md#start_session) - Start a new session
* [delete_session](docs/sdks/session/README.md#delete_session) - Delete a session
* [get_session](docs/sdks/session/README.md#get_session) - Retrieve a session
* [process_event_trace](docs/sdks/session/README.md#process_event_trace) - Process an event trace for a given session

### [tasks](docs/sdks/tasks/README.md)

* [delete_task](docs/sdks/tasks/README.md#delete_task) - Delete a task
* [get_tasks](docs/sdks/tasks/README.md#get_tasks) - Get a list of tasks
* [create_task](docs/sdks/tasks/README.md#create_task) - Create a new task
* [update_task](docs/sdks/tasks/README.md#update_task) - Update a task

### [testcases](docs/sdks/testcases/README.md)

* [get_testcases](docs/sdks/testcases/README.md#get_testcases) - Get testcases
* [post_testcases](docs/sdks/testcases/README.md#post_testcases) - Create a testcase
* [put_testcases](docs/sdks/testcases/README.md#put_testcases) - Update a testcase

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
from honeyhive.models import errors

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = None
try:
    res = s.configurations.get_configurations(project='<value>', type='<value>')
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

s = honeyhive.HoneyHive(
    server_idx=0,
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.get_configurations(project='<value>', type='<value>')

if res.configurations is not None:
    # handle response
    pass
```


### Override Server URL Per-Client

The default server can also be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
import honeyhive

s = honeyhive.HoneyHive(
    server_url="https://api.honeyhive.ai",
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.get_configurations(project='<value>', type='<value>')

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

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.get_configurations(project='<value>', type='<value>')

if res.configurations is not None:
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
