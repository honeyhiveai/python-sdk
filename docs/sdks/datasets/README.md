# Datasets
(*datasets*)

### Available Operations

* [delete_dataset](#delete_dataset) - Delete a dataset
* [get_datasets](#get_datasets) - Get datasets
* [create_dataset](#create_dataset) - Create a dataset
* [update_dataset](#update_dataset) - Update a dataset

## delete_dataset

Delete a dataset

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datasets.delete_dataset(dataset_id='<value>')

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                          | Type                                               | Required                                           | Description                                        |
| -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- |
| `dataset_id`                                       | *str*                                              | :heavy_check_mark:                                 | The unique identifier of the dataset to be deleted |


### Response

**[operations.DeleteDatasetResponse](../../models/operations/deletedatasetresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## get_datasets

Get datasets

### Example Usage

```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datasets.get_datasets(project='<value>', type=operations.GetDatasetsQueryParamType.EVALUATION, dataset_id='<value>')

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                              | Type                                                                                                   | Required                                                                                               | Description                                                                                            |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `project`                                                                                              | *str*                                                                                                  | :heavy_check_mark:                                                                                     | Project ID associated with the datasets                                                                |
| `type`                                                                                                 | [Optional[operations.GetDatasetsQueryParamType]](../../models/operations/getdatasetsqueryparamtype.md) | :heavy_minus_sign:                                                                                     | Type of the dataset - "evaluation" or "fine-tuning"                                                    |
| `dataset_id`                                                                                           | *Optional[str]*                                                                                        | :heavy_minus_sign:                                                                                     | Unique dataset ID for filtering specific dataset                                                       |


### Response

**[operations.GetDatasetsResponse](../../models/operations/getdatasetsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## create_dataset

Create a dataset

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.CreateDatasetRequest(
    name='<value>',
    project='<value>',
)

res = s.datasets.create_dataset(req)

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `request`                                                                          | [components.CreateDatasetRequest](../../models/components/createdatasetrequest.md) | :heavy_check_mark:                                                                 | The request object to use for the request.                                         |


### Response

**[operations.CreateDatasetResponse](../../models/operations/createdatasetresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## update_dataset

Update a dataset

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.DatasetUpdate(
    dataset_id='<value>',
)

res = s.datasets.update_dataset(req)

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                            | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `request`                                                            | [components.DatasetUpdate](../../models/components/datasetupdate.md) | :heavy_check_mark:                                                   | The request object to use for the request.                           |


### Response

**[operations.UpdateDatasetResponse](../../models/operations/updatedatasetresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |
