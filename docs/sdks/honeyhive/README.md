# HoneyHive SDK


## Overview

### Available Operations

* [delete_tasks](#delete_tasks) - Delete a task
* [get_tasks](#get_tasks) - Get all tasks
* [post_tasks](#post_tasks) - Create a task
* [put_tasks](#put_tasks) - Update a task
* [get_generations](#get_generations) - Get all generations
* [post_generations](#post_generations) - Generate a text
* [get_prompts](#get_prompts) - Get all prompts or filter by task and name
* [post_prompts](#post_prompts) - Create a prompt
* [delete_prompts_id_](#delete_prompts_id_) - Delete a prompt by name
* [put_prompts_id_](#put_prompts_id_) - Update a prompt
* [get_fine_tuned_models](#get_fine_tuned_models) - Get all fine-tuned models
* [post_fine_tuned_models](#post_fine_tuned_models) - Create a new fine-tuned model
* [delete_fine_tuned_models_id_](#delete_fine_tuned_models_id_) - Delete a fine-tuned model
* [get_fine_tuned_models_id_](#get_fine_tuned_models_id_) - Get a fine-tuned model
* [delete_datasets](#delete_datasets) - Delete all datasets
* [get_datasets](#get_datasets) - Get datasets
* [post_datasets](#post_datasets) - Create a dataset
* [put_datasets](#put_datasets) - Update a dataset
* [delete_datasets_name_](#delete_datasets_name_) - Delete a dataset
* [delete_metrics](#delete_metrics) - Delete a metric
* [get_metrics](#get_metrics) - Get all metrics
* [post_metrics](#post_metrics) - Create a metric
* [put_metrics](#put_metrics) - Update a metric
* [post_metrics_compute](#post_metrics_compute) - Compute metric
* [post_chat](#post_chat) - Create a chat completion
* [post_generations_log](#post_generations_log) - Log a generation
* [post_feedback](#post_feedback) - Send feedback
* [get_evaluations](#get_evaluations) - Get all evaluations
* [post_evaluations](#post_evaluations) - Log an evaluation
* [delete_evaluations_id_](#delete_evaluations_id_) - Delete an evaluation
* [get_evaluations_id_](#get_evaluations_id_) - Get an evaluation
* [put_evaluations_id_](#put_evaluations_id_) - Update an evaluation
* [post_session_start](#post_session_start) - Start a session
* [post_session_session_id_end](#post_session_session_id_end) - End a session
* [post_session_session_id_event](#post_session_session_id_event) - Log an event
* [post_session_session_id_feedback](#post_session_session_id_feedback) - Log session feedback
* [delete_session_session_id_](#delete_session_session_id_) - Delete a session
* [get_session_session_id_](#get_session_session_id_) - Get a session
* [put_session_session_id_](#put_session_session_id_) - Update a session event
* [get_session_session_id_export](#get_session_session_id_export) - Get a session in Trace Event format
* [get_session](#get_session) - Get all sessions
* [post_session_session_id_traces](#post_session_session_id_traces) - Log a trace

## delete_tasks

Delete a task

### Example Usage

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

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `name`             | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteTasksResponse](../../models/operations/deletetasksresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_tasks

Get all tasks

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_tasks(name='string')

if res.classes is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `name`             | *Optional[str]*    | :heavy_minus_sign: | N/A                |


### Response

**[operations.GetTasksResponse](../../models/operations/gettasksresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_tasks

Create a task

### Example Usage

```python
import dateutil.parser
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.TaskCreationQuery(
    fine_tuned_models=[
        components.FineTunedModelResponse(),
    ],
    prompts=[
        components.PromptResponse(
            input_variables=[
                'string',
            ],
            hyperparameters={
                "key": 'string',
            },
            few_shot_examples=[
                {
                    "key": 'string',
                },
            ],
        ),
    ],
    datasets=[
        components.DatasetResponse(
            file=[
                {
                    "key": 'string',
                },
            ],
        ),
    ],
    metrics=[
        components.MetricResponse(
            threshold={
                "key": 'string',
            },
        ),
    ],
)

res = s.post_tasks(req)

if res.task_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                    | Type                                                                         | Required                                                                     | Description                                                                  |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `request`                                                                    | [components.TaskCreationQuery](../../models/components/taskcreationquery.md) | :heavy_check_mark:                                                           | The request object to use for the request.                                   |


### Response

**[operations.PostTasksResponse](../../models/operations/posttasksresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## put_tasks

Update a task

### Example Usage

```python
import dateutil.parser
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.TaskUpdateQuery(
    fine_tuned_models=[
        components.FineTunedModelResponse(),
    ],
    prompts=[
        components.PromptResponse(
            input_variables=[
                'string',
            ],
            hyperparameters={
                "key": 'string',
            },
            few_shot_examples=[
                {
                    "key": 'string',
                },
            ],
        ),
    ],
    datasets=[
        components.DatasetResponse(
            file=[
                {
                    "key": 'string',
                },
            ],
        ),
    ],
    metrics=[
        components.MetricResponse(
            threshold={
                "key": 'string',
            },
        ),
    ],
)

res = s.put_tasks(req)

if res.task_update_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                | Type                                                                     | Required                                                                 | Description                                                              |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| `request`                                                                | [components.TaskUpdateQuery](../../models/components/taskupdatequery.md) | :heavy_check_mark:                                                       | The request object to use for the request.                               |


### Response

**[operations.PutTasksResponse](../../models/operations/puttasksresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_generations

Get all generations

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_generations(task='string', prompt='string', model_id='string')

if res.classes is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `task`             | *Optional[str]*    | :heavy_minus_sign: | N/A                |
| `prompt`           | *Optional[str]*    | :heavy_minus_sign: | N/A                |
| `model_id`         | *Optional[str]*    | :heavy_minus_sign: | N/A                |


### Response

**[operations.GetGenerationsResponse](../../models/operations/getgenerationsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_generations

Generate a text

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.GenerateQuery(
    input={
        "key": 'string',
    },
    prompts=[
        'string',
    ],
    metadata={
        "key": 'string',
    },
    user_properties={
        "key": 'string',
    },
)

res = s.post_generations(req)

if res.generation_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                            | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `request`                                                            | [components.GenerateQuery](../../models/components/generatequery.md) | :heavy_check_mark:                                                   | The request object to use for the request.                           |


### Response

**[operations.PostGenerationsResponse](../../models/operations/postgenerationsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_prompts

Get all prompts or filter by task and name

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_prompts(task='string', name='string')

if res.classes is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `task`             | *Optional[str]*    | :heavy_minus_sign: | N/A                |
| `name`             | *Optional[str]*    | :heavy_minus_sign: | N/A                |


### Response

**[operations.GetPromptsResponse](../../models/operations/getpromptsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_prompts

Create a prompt

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.PromptCreationQuery(
    hyperparameters={
        "key": 'string',
    },
    few_shot_examples=[
        {
            "key": 'string',
        },
    ],
)

res = s.post_prompts(req)

if res.prompt_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                        | Type                                                                             | Required                                                                         | Description                                                                      |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `request`                                                                        | [components.PromptCreationQuery](../../models/components/promptcreationquery.md) | :heavy_check_mark:                                                               | The request object to use for the request.                                       |


### Response

**[operations.PostPromptsResponse](../../models/operations/postpromptsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## delete_prompts_id_

Delete a prompt by name

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.delete_prompts_id_(id='string')

if res.delete_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `id`               | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeletePromptsIDResponse](../../models/operations/deletepromptsidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## put_prompts_id_

Update a prompt

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.put_prompts_id_(id='string', prompt_update_query=components.PromptUpdateQuery(
    input_variables=[
        'string',
    ],
    hyperparameters={
        "key": 'string',
    },
    few_shot_examples=[
        {
            "key": 'string',
        },
    ],
))

if res.prompt_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                    | Type                                                                         | Required                                                                     | Description                                                                  |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `id`                                                                         | *str*                                                                        | :heavy_check_mark:                                                           | N/A                                                                          |
| `prompt_update_query`                                                        | [components.PromptUpdateQuery](../../models/components/promptupdatequery.md) | :heavy_check_mark:                                                           | N/A                                                                          |


### Response

**[operations.PutPromptsIDResponse](../../models/operations/putpromptsidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_fine_tuned_models

Get all fine-tuned models

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_fine_tuned_models(task='string', model_id='string')

if res.classes is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `task`             | *Optional[str]*    | :heavy_minus_sign: | N/A                |
| `model_id`         | *Optional[str]*    | :heavy_minus_sign: | N/A                |


### Response

**[operations.GetFineTunedModelsResponse](../../models/operations/getfinetunedmodelsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_fine_tuned_models

Create a new fine-tuned model

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = operations.PostFineTunedModelsRequestBody()

res = s.post_fine_tuned_models(req)

if res.object is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                                              | Type                                                                                                   | Required                                                                                               | Description                                                                                            |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `request`                                                                                              | [operations.PostFineTunedModelsRequestBody](../../models/operations/postfinetunedmodelsrequestbody.md) | :heavy_check_mark:                                                                                     | The request object to use for the request.                                                             |


### Response

**[operations.PostFineTunedModelsResponse](../../models/operations/postfinetunedmodelsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## delete_fine_tuned_models_id_

Delete a fine-tuned model

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.delete_fine_tuned_models_id_(id='string')

if res.status_code == 200:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `id`               | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteFineTunedModelsIDResponse](../../models/operations/deletefinetunedmodelsidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_fine_tuned_models_id_

Get a fine-tuned model

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_fine_tuned_models_id_(id='string')

if res.fine_tuned_model_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `id`               | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.GetFineTunedModelsIDResponse](../../models/operations/getfinetunedmodelsidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## delete_datasets

Delete all datasets

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.delete_datasets()

if res.delete_response is not None:
    # handle response
    pass
```


### Response

**[operations.DeleteDatasetsResponse](../../models/operations/deletedatasetsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_datasets

Get datasets

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_datasets(task='string', prompt='string', dataset_id='string', purpose='string')

if res.classes is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `task`             | *Optional[str]*    | :heavy_minus_sign: | N/A                |
| `prompt`           | *Optional[str]*    | :heavy_minus_sign: | N/A                |
| `dataset_id`       | *Optional[str]*    | :heavy_minus_sign: | N/A                |
| `purpose`          | *Optional[str]*    | :heavy_minus_sign: | N/A                |


### Response

**[operations.GetDatasetsResponse](../../models/operations/getdatasetsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_datasets

Create a dataset

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.UploadDataset(
    file=[
        {
            "key": 'string',
        },
    ],
)

res = s.post_datasets(req)

if res.dataset_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                            | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `request`                                                            | [components.UploadDataset](../../models/components/uploaddataset.md) | :heavy_check_mark:                                                   | The request object to use for the request.                           |


### Response

**[operations.PostDatasetsResponse](../../models/operations/postdatasetsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## put_datasets

Update a dataset

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.UploadDataset(
    file=[
        {
            "key": 'string',
        },
    ],
)

res = s.put_datasets(req)

if res.dataset_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                            | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `request`                                                            | [components.UploadDataset](../../models/components/uploaddataset.md) | :heavy_check_mark:                                                   | The request object to use for the request.                           |


### Response

**[operations.PutDatasetsResponse](../../models/operations/putdatasetsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## delete_datasets_name_

Delete a dataset

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.delete_datasets_name_(name='string')

if res.delete_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `name`             | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteDatasetsNameResponse](../../models/operations/deletedatasetsnameresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## delete_metrics

Delete a metric

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.delete_metrics(metric_id='string')

if res.metric_delete_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `metric_id`        | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteMetricsResponse](../../models/operations/deletemetricsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_metrics

Get all metrics

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_metrics(task='string')

if res.classes is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `task`             | *Optional[str]*    | :heavy_minus_sign: | N/A                |


### Response

**[operations.GetMetricsResponse](../../models/operations/getmetricsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_metrics

Create a metric

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.MetricCreateRequest(
    threshold=components.Threshold(),
)

res = s.post_metrics(req)

if res.metric_create_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                        | Type                                                                             | Required                                                                         | Description                                                                      |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `request`                                                                        | [components.MetricCreateRequest](../../models/components/metriccreaterequest.md) | :heavy_check_mark:                                                               | The request object to use for the request.                                       |


### Response

**[operations.PostMetricsResponse](../../models/operations/postmetricsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## put_metrics

Update a metric

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.MetricUpdateRequest(
    threshold=components.MetricUpdateRequestThreshold(),
)

res = s.put_metrics(req)

if res.metric_update_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                        | Type                                                                             | Required                                                                         | Description                                                                      |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `request`                                                                        | [components.MetricUpdateRequest](../../models/components/metricupdaterequest.md) | :heavy_check_mark:                                                               | The request object to use for the request.                                       |


### Response

**[operations.PutMetricsResponse](../../models/operations/putmetricsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_metrics_compute

Compute metric

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.MetricComputeRequest(
    metric=components.Metric(),
)

res = s.post_metrics_compute(req)

if res.metric_compute_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `request`                                                                          | [components.MetricComputeRequest](../../models/components/metriccomputerequest.md) | :heavy_check_mark:                                                                 | The request object to use for the request.                                         |


### Response

**[operations.PostMetricsComputeResponse](../../models/operations/postmetricscomputeresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_chat

Create a chat completion

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.ChatCompletionRequest(
    project='string',
    messages=[
        {
            "key": 'string',
        },
    ],
    model='Golf',
    hyperparameters={
        "key": 'string',
    },
    functions=[
        {
            "key": 'string',
        },
    ],
)

res = s.post_chat(req)

if res.chat_completion_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                            | Type                                                                                 | Required                                                                             | Description                                                                          |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| `request`                                                                            | [components.ChatCompletionRequest](../../models/components/chatcompletionrequest.md) | :heavy_check_mark:                                                                   | The request object to use for the request.                                           |


### Response

**[operations.PostChatResponse](../../models/operations/postchatresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_generations_log

Log a generation

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.GenerationLoggingQuery(
    inputs={
        "key": 'string',
    },
    hyperparameters={
        "key": 'string',
    },
    usage={
        "key": 'string',
    },
    user_properties={
        "key": 'string',
    },
    metadata=components.Metadata(),
    feedback={
        "key": 'string',
    },
)

res = s.post_generations_log(req)

if res.generation_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                              | Type                                                                                   | Required                                                                               | Description                                                                            |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `request`                                                                              | [components.GenerationLoggingQuery](../../models/components/generationloggingquery.md) | :heavy_check_mark:                                                                     | The request object to use for the request.                                             |


### Response

**[operations.PostGenerationsLogResponse](../../models/operations/postgenerationslogresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_feedback

Send feedback

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.FeedbackQuery(
    task='string',
    generation_id='string',
    feedback_json={
        "key": 'string',
    },
)

res = s.post_feedback(req)

if res.feedback_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                            | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `request`                                                            | [components.FeedbackQuery](../../models/components/feedbackquery.md) | :heavy_check_mark:                                                   | The request object to use for the request.                           |


### Response

**[operations.PostFeedbackResponse](../../models/operations/postfeedbackresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_evaluations

Get all evaluations

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_evaluations()

if res.classes is not None:
    # handle response
    pass
```


### Response

**[operations.GetEvaluationsResponse](../../models/operations/getevaluationsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_evaluations

Log an evaluation

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.EvaluationLoggingQuery(
    prompts=[
        {
            "key": 'string',
        },
    ],
    dataset=[
        {
            "key": 'string',
        },
    ],
    metrics=[
        [
            {
                "key": 'string',
            },
        ],
    ],
    metrics_to_compute=[
        'string',
    ],
    results=[
        {
            "key": 'string',
        },
    ],
    summary=[
        {
            "key": 'string',
        },
    ],
    comments=[
        {
            "key": 'string',
        },
    ],
    generations=[
        {
            "key": 'string',
        },
    ],
)

res = s.post_evaluations(req)

if res.success_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                              | Type                                                                                   | Required                                                                               | Description                                                                            |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `request`                                                                              | [components.EvaluationLoggingQuery](../../models/components/evaluationloggingquery.md) | :heavy_check_mark:                                                                     | The request object to use for the request.                                             |


### Response

**[operations.PostEvaluationsResponse](../../models/operations/postevaluationsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## delete_evaluations_id_

Delete an evaluation

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.delete_evaluations_id_(id='string')

if res.delete_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `id`               | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteEvaluationsIDResponse](../../models/operations/deleteevaluationsidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_evaluations_id_

Get an evaluation

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_evaluations_id_(id='string')

if res.evaluation is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `id`               | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.GetEvaluationsIDResponse](../../models/operations/getevaluationsidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## put_evaluations_id_

Update an evaluation

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.put_evaluations_id_(id='string', evaluation_update_request=components.EvaluationUpdateRequest(
    prompts=[
        {
            "key": 'string',
        },
    ],
    dataset=[
        {
            "key": 'string',
        },
    ],
    metrics=[
        [
            {
                "key": 'string',
            },
        ],
    ],
    summary=[
        {
            "key": 'string',
        },
    ],
    generations=[
        {
            "key": 'string',
        },
    ],
    results=[
        {
            "key": 'string',
        },
    ],
    accepted=[
        False,
    ],
    comments=[
        {
            "key": 'string',
        },
    ],
))

if res.update_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                                          | Type                                                                                               | Required                                                                                           | Description                                                                                        |
| -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `id`                                                                                               | *str*                                                                                              | :heavy_check_mark:                                                                                 | N/A                                                                                                |
| `evaluation_update_request`                                                                        | [Optional[components.EvaluationUpdateRequest]](../../models/components/evaluationupdaterequest.md) | :heavy_minus_sign:                                                                                 | N/A                                                                                                |


### Response

**[operations.PutEvaluationsIDResponse](../../models/operations/putevaluationsidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_session_start

Start a session

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="",
)

req = components.SessionStartQuery(
    user_properties={
        "key": 'string',
    },
)

res = s.post_session_start(req)

if res.session_start_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                    | Type                                                                         | Required                                                                     | Description                                                                  |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `request`                                                                    | [components.SessionStartQuery](../../models/components/sessionstartquery.md) | :heavy_check_mark:                                                           | The request object to use for the request.                                   |


### Response

**[operations.PostSessionStartResponse](../../models/operations/postsessionstartresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_session_session_id_end

End a session

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.post_session_session_id_end(session_id='string')

if res.session_end_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `session_id`       | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.PostSessionSessionIDEndResponse](../../models/operations/postsessionsessionidendresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_session_session_id_event

Log an event

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.post_session_session_id_event(session_id='string', session_event_query=components.SessionEventQuery(
    config={
        "key": 'string',
    },
    children=[
        {
            "key": 'string',
        },
    ],
    inputs={
        "key": 'string',
    },
    outputs={
        "key": 'string',
    },
    user_properties={
        "key": 'string',
    },
    metadata={
        "key": 'string',
    },
    metrics={
        "key": 'string',
    },
    feedback={
        "key": 'string',
    },
))

if res.session_event_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                    | Type                                                                         | Required                                                                     | Description                                                                  |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `session_id`                                                                 | *str*                                                                        | :heavy_check_mark:                                                           | N/A                                                                          |
| `session_event_query`                                                        | [components.SessionEventQuery](../../models/components/sessioneventquery.md) | :heavy_check_mark:                                                           | N/A                                                                          |


### Response

**[operations.PostSessionSessionIDEventResponse](../../models/operations/postsessionsessionideventresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_session_session_id_feedback

Log session feedback

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.post_session_session_id_feedback(session_id='string', session_feedback=components.SessionFeedback(
    feedback={
        "key": 'string',
    },
))

if res.success_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                | Type                                                                     | Required                                                                 | Description                                                              |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| `session_id`                                                             | *str*                                                                    | :heavy_check_mark:                                                       | N/A                                                                      |
| `session_feedback`                                                       | [components.SessionFeedback](../../models/components/sessionfeedback.md) | :heavy_check_mark:                                                       | N/A                                                                      |


### Response

**[operations.PostSessionSessionIDFeedbackResponse](../../models/operations/postsessionsessionidfeedbackresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## delete_session_session_id_

Delete a session

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.delete_session_session_id_(session_id='string')

if res.success_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `session_id`       | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteSessionSessionIDResponse](../../models/operations/deletesessionsessionidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_session_session_id_

Get a session

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_session_session_id_(session_id='string')

if res.session_event_query is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `session_id`       | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.GetSessionSessionIDResponse](../../models/operations/getsessionsessionidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## put_session_session_id_

Update a session event

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.put_session_session_id_(session_id='string', session_event_update=components.SessionEventUpdate(
    output=components.Output(),
    error='string',
    inputs=components.Inputs(),
    user_properties=components.UserProperties(),
    feedback=components.Feedback(),
    metadata=components.SessionEventUpdateMetadata(),
))

if res.success_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                                                | Type                                                                                     | Required                                                                                 | Description                                                                              |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `session_id`                                                                             | *str*                                                                                    | :heavy_check_mark:                                                                       | N/A                                                                                      |
| `session_event_update`                                                                   | [Optional[components.SessionEventUpdate]](../../models/components/sessioneventupdate.md) | :heavy_minus_sign:                                                                       | N/A                                                                                      |


### Response

**[operations.PutSessionSessionIDResponse](../../models/operations/putsessionsessionidresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_session_session_id_export

Get a session in Trace Event format

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_session_session_id_export(session_id='string')

if res.trace_event_trace is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `session_id`       | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.GetSessionSessionIDExportResponse](../../models/operations/getsessionsessionidexportresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## get_session

Get all sessions

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.get_session(project='string', query={
    "key": 'string',
}, limit=355376)

if res.classes is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                | Type                                     | Required                                 | Description                              |
| ---------------------------------------- | ---------------------------------------- | ---------------------------------------- | ---------------------------------------- |
| `project`                                | *Optional[str]*                          | :heavy_minus_sign:                       | The project to query sessions for        |
| `query`                                  | Dict[str, *Any*]                         | :heavy_minus_sign:                       | The query for finding sessions           |
| `limit`                                  | *Optional[int]*                          | :heavy_minus_sign:                       | The maximum number of sessions to return |


### Response

**[operations.GetSessionResponse](../../models/operations/getsessionresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |

## post_session_session_id_traces

Log a trace

### Example Usage

```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.post_session_session_id_traces(session_id='string', session_trace=components.SessionTrace(
    logs=[
        components.SessionEventQuery(
            config={
                "key": 'string',
            },
            children=[
                {
                    "key": 'string',
                },
            ],
            inputs={
                "key": 'string',
            },
            outputs={
                "key": 'string',
            },
            user_properties={
                "key": 'string',
            },
            metadata={
                "key": 'string',
            },
            metrics={
                "key": 'string',
            },
            feedback={
                "key": 'string',
            },
        ),
    ],
))

if res.success_trace_response is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                          | Type                                                               | Required                                                           | Description                                                        |
| ------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `session_id`                                                       | *str*                                                              | :heavy_check_mark:                                                 | N/A                                                                |
| `session_trace`                                                    | [components.SessionTrace](../../models/components/sessiontrace.md) | :heavy_check_mark:                                                 | N/A                                                                |


### Response

**[operations.PostSessionSessionIDTracesResponse](../../models/operations/postsessionsessionidtracesresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 400-600         | */*             |
