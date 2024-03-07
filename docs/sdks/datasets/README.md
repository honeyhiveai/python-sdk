# Datasets
(*datasets*)

### Available Operations

* [delete_datasets](#delete_datasets) - Delete a dataset
* [get_datasets](#get_datasets) - Get datasets
* [post_datasets](#post_datasets) - Create a dataset
* [put_datasets](#put_datasets) - Update a dataset

## delete_datasets

Delete a dataset

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datasets.delete_datasets(dataset_id='<value>')

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                          | Type                                               | Required                                           | Description                                        |
| -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- |
| `dataset_id`                                       | *str*                                              | :heavy_check_mark:                                 | The unique identifier of the dataset to be deleted |


### Response

**[operations.DeleteDatasetsResponse](../../models/operations/deletedatasetsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

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
| errors.SDKError | 4x-5xx          | */*             |

## post_datasets

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

res = s.datasets.post_datasets(req)

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `request`                                                                          | [components.CreateDatasetRequest](../../models/components/createdatasetrequest.md) | :heavy_check_mark:                                                                 | The request object to use for the request.                                         |


### Response

**[operations.PostDatasetsResponse](../../models/operations/postdatasetsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## put_datasets

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

res = s.datasets.put_datasets(req)

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                            | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `request`                                                            | [components.DatasetUpdate](../../models/components/datasetupdate.md) | :heavy_check_mark:                                                   | The request object to use for the request.                           |


### Response

**[operations.PutDatasetsResponse](../../models/operations/putdatasetsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |
