# Datasets
(*datasets*)

## Overview

### Available Operations

* [get_datasets](#get_datasets) - Get datasets
* [create_dataset](#create_dataset) - Create a dataset
* [update_dataset](#update_dataset) - Update a dataset
* [delete_dataset](#delete_dataset) - Delete a dataset
* [add_datapoints](#add_datapoints) - Add datapoints to a dataset

## get_datasets

Get datasets

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.datasets.get_datasets(project="<value>")

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                        | Type                                                                             | Required                                                                         | Description                                                                      |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `project`                                                                        | *str*                                                                            | :heavy_check_mark:                                                               | Project Name associated with the datasets like `New Project`                     |
| `type`                                                                           | [Optional[operations.Type]](../../models/operations/type.md)                     | :heavy_minus_sign:                                                               | Type of the dataset - "evaluation" or "fine-tuning"                              |
| `dataset_id`                                                                     | *Optional[str]*                                                                  | :heavy_minus_sign:                                                               | Unique dataset ID for filtering specific dataset like `663876ec4611c47f4970f0c3` |
| `retries`                                                                        | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                 | :heavy_minus_sign:                                                               | Configuration to override the default retry behavior of the client.              |

### Response

**[operations.GetDatasetsResponse](../../models/operations/getdatasetsresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## create_dataset

Create a dataset

### Example Usage

```python
from honeyhive import HoneyHive
from honeyhive.models import components

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.datasets.create_dataset(request={
    "project": "New Project",
    "name": "test-dataset",
    "description": "A test dataset",
    "type": components.CreateDatasetRequestType.EVALUATION,
    "datapoints": [
        "66369748b5773befbdc661e2",
    ],
    "linked_evals": [
        "<value>",
    ],
    "saved": False,
    "pipeline_type": components.CreateDatasetRequestPipelineType.EVENT,
    "metadata": {
        "source": "dev",
    },
})

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `request`                                                                          | [components.CreateDatasetRequest](../../models/components/createdatasetrequest.md) | :heavy_check_mark:                                                                 | The request object to use for the request.                                         |
| `retries`                                                                          | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                   | :heavy_minus_sign:                                                                 | Configuration to override the default retry behavior of the client.                |

### Response

**[operations.CreateDatasetResponse](../../models/operations/createdatasetresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## update_dataset

Update a dataset

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.datasets.update_dataset(request={
    "dataset_id": "663876ec4611c47f4970f0c3",
    "name": "new-dataset-name",
    "description": "An updated dataset description",
    "datapoints": [
        "66369748b5773befbdc661e",
    ],
    "linked_evals": [
        "66369748b5773befbdasdk1",
    ],
    "metadata": {
        "updated": True,
        "source": "prod",
    },
})

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                            | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `request`                                                            | [components.DatasetUpdate](../../models/components/datasetupdate.md) | :heavy_check_mark:                                                   | The request object to use for the request.                           |
| `retries`                                                            | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)     | :heavy_minus_sign:                                                   | Configuration to override the default retry behavior of the client.  |

### Response

**[operations.UpdateDatasetResponse](../../models/operations/updatedatasetresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## delete_dataset

Delete a dataset

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.datasets.delete_dataset(dataset_id="<id>")

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `dataset_id`                                                                       | *str*                                                                              | :heavy_check_mark:                                                                 | The unique identifier of the dataset to be deleted like `663876ec4611c47f4970f0c3` |
| `retries`                                                                          | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                   | :heavy_minus_sign:                                                                 | Configuration to override the default retry behavior of the client.                |

### Response

**[operations.DeleteDatasetResponse](../../models/operations/deletedatasetresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## add_datapoints

Add datapoints to a dataset

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.datasets.add_datapoints(dataset_id="<id>", request_body={
    "project": "<value>",
    "data": [
        {
            "key": "<value>",
            "key1": "<value>",
            "key2": "<value>",
        },
    ],
    "mapping": {
        "inputs": [
            "<value>",
        ],
        "ground_truth": [
            "<value>",
            "<value>",
        ],
        "history": [
            "<value>",
        ],
    },
})

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                  | Type                                                                                       | Required                                                                                   | Description                                                                                |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `dataset_id`                                                                               | *str*                                                                                      | :heavy_check_mark:                                                                         | The unique identifier of the dataset to add datapoints to like  `663876ec4611c47f4970f0c3` |
| `request_body`                                                                             | [operations.AddDatapointsRequestBody](../../models/operations/adddatapointsrequestbody.md) | :heavy_check_mark:                                                                         | N/A                                                                                        |
| `retries`                                                                                  | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                           | :heavy_minus_sign:                                                                         | Configuration to override the default retry behavior of the client.                        |

### Response

**[operations.AddDatapointsResponse](../../models/operations/adddatapointsresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |