# HoneyHive

## SDK Installation

```bash
pip install honeyhive
```
<!-- End SDK Installation -->

## SDK Example Usage
<!-- Start SDK Example Usage -->
### Example

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.delete_tasks(name='string')

if res.delete_response is not None:
    # handle response
    pass
```
<!-- End SDK Example Usage -->

<!-- Start SDK Available Operations -->
## Available Resources and Operations

### [HoneyHive SDK](docs/sdks/honeyhive/README.md)

* [delete_tasks](docs/sdks/honeyhive/README.md#delete_tasks) - Delete a task
* [get_tasks](docs/sdks/honeyhive/README.md#get_tasks) - Get all tasks
* [post_tasks](docs/sdks/honeyhive/README.md#post_tasks) - Create a task
* [put_tasks](docs/sdks/honeyhive/README.md#put_tasks) - Update a task
* [get_generations](docs/sdks/honeyhive/README.md#get_generations) - Get all generations
* [post_generations](docs/sdks/honeyhive/README.md#post_generations) - Generate a text
* [get_prompts](docs/sdks/honeyhive/README.md#get_prompts) - Get all prompts or filter by task and name
* [post_prompts](docs/sdks/honeyhive/README.md#post_prompts) - Create a prompt
* [delete_prompts_id_](docs/sdks/honeyhive/README.md#delete_prompts_id_) - Delete a prompt by name
* [put_prompts_id_](docs/sdks/honeyhive/README.md#put_prompts_id_) - Update a prompt
* [get_fine_tuned_models](docs/sdks/honeyhive/README.md#get_fine_tuned_models) - Get all fine-tuned models
* [post_fine_tuned_models](docs/sdks/honeyhive/README.md#post_fine_tuned_models) - Create a new fine-tuned model
* [delete_fine_tuned_models_id_](docs/sdks/honeyhive/README.md#delete_fine_tuned_models_id_) - Delete a fine-tuned model
* [get_fine_tuned_models_id_](docs/sdks/honeyhive/README.md#get_fine_tuned_models_id_) - Get a fine-tuned model
* [delete_datasets](docs/sdks/honeyhive/README.md#delete_datasets) - Delete all datasets
* [get_datasets](docs/sdks/honeyhive/README.md#get_datasets) - Get datasets
* [post_datasets](docs/sdks/honeyhive/README.md#post_datasets) - Create a dataset
* [put_datasets](docs/sdks/honeyhive/README.md#put_datasets) - Update a dataset
* [delete_datasets_name_](docs/sdks/honeyhive/README.md#delete_datasets_name_) - Delete a dataset
* [delete_metrics](docs/sdks/honeyhive/README.md#delete_metrics) - Delete a metric
* [get_metrics](docs/sdks/honeyhive/README.md#get_metrics) - Get all metrics
* [post_metrics](docs/sdks/honeyhive/README.md#post_metrics) - Create a metric
* [put_metrics](docs/sdks/honeyhive/README.md#put_metrics) - Update a metric
* [post_metrics_compute](docs/sdks/honeyhive/README.md#post_metrics_compute) - Compute metric
* [post_chat](docs/sdks/honeyhive/README.md#post_chat) - Create a chat completion
* [post_generations_log](docs/sdks/honeyhive/README.md#post_generations_log) - Log a generation
* [post_feedback](docs/sdks/honeyhive/README.md#post_feedback) - Send feedback
* [get_evaluations](docs/sdks/honeyhive/README.md#get_evaluations) - Get all evaluations
* [post_evaluations](docs/sdks/honeyhive/README.md#post_evaluations) - Log an evaluation
* [delete_evaluations_id_](docs/sdks/honeyhive/README.md#delete_evaluations_id_) - Delete an evaluation
* [get_evaluations_id_](docs/sdks/honeyhive/README.md#get_evaluations_id_) - Get an evaluation
* [put_evaluations_id_](docs/sdks/honeyhive/README.md#put_evaluations_id_) - Update an evaluation
* [post_session_start](docs/sdks/honeyhive/README.md#post_session_start) - Start a session
* [post_session_session_id_end](docs/sdks/honeyhive/README.md#post_session_session_id_end) - End a session
* [post_session_session_id_event](docs/sdks/honeyhive/README.md#post_session_session_id_event) - Log an event
* [post_session_session_id_feedback](docs/sdks/honeyhive/README.md#post_session_session_id_feedback) - Log session feedback
* [delete_session_session_id_](docs/sdks/honeyhive/README.md#delete_session_session_id_) - Delete a session
* [get_session_session_id_](docs/sdks/honeyhive/README.md#get_session_session_id_) - Get a session
* [put_session_session_id_](docs/sdks/honeyhive/README.md#put_session_session_id_) - Update a session event
* [get_session_session_id_export](docs/sdks/honeyhive/README.md#get_session_session_id_export) - Get a session in Trace Event format
* [get_session](docs/sdks/honeyhive/README.md#get_session) - Get all sessions
* [post_session_session_id_traces](docs/sdks/honeyhive/README.md#post_session_session_id_traces) - Log a trace
<!-- End SDK Available Operations -->

<!-- Start Error Handling -->
## Error Handling

Handling errors in this SDK should largely match your expectations.  All operations return a response object or raise an error.  If Error objects are specified in your OpenAPI Spec, the SDK will raise the appropriate Error type.

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

### Example

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = None
try:
    res = s.delete_tasks(name='string')

except (errors.SDKError) as e:
    print(e) # handle exception


if res.delete_response is not None:
    # handle response
    pass
```

<!-- End Error Handling -->

<!-- Start Server Selection -->
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
    bearer_auth="",
)


res = s.delete_tasks(name='string')

if res.delete_response is not None:
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
    bearer_auth="",
)


res = s.delete_tasks(name='string')

if res.delete_response is not None:
    # handle response
    pass
```
<!-- End Server Selection -->

<!-- Start Custom HTTP Client -->
## Custom HTTP Client

The Python SDK makes API calls using the (requests)[https://pypi.org/project/requests/] HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with a custom `requests.Session` object.

For example, you could specify a header for every request that this sdk makes as follows:
```python
import honeyhive
import requests

http_client = requests.Session()
http_client.headers.update({'x-custom-header': 'someValue'})
s = honeyhive.HoneyHive(client: http_client)
```
<!-- End Custom HTTP Client -->

<!-- Start Authentication -->

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
    bearer_auth="",
)


res = s.delete_tasks(name='string')

if res.delete_response is not None:
    # handle response
    pass
```
<!-- End Authentication -->

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
