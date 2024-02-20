# Datasets
(*datasets*)

### Available Operations

* [get_datasets](#get_datasets) - Retrieve a list of datasets
* [create_dataset](#create_dataset) - Create a new dataset
* [delete_dataset](#delete_dataset) - Delete a dataset
* [update_dataset](#update_dataset) - Update a dataset

## get_datasets

Retrieve a list of datasets

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datasets.get_datasets(task='<value>', dataset_id='<value>')

if res.datasets is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `task`             | *str*              | :heavy_check_mark: | N/A                |
| `dataset_id`       | *Optional[str]*    | :heavy_minus_sign: | N/A                |


### Response

**[operations.GetDatasetsResponse](../../models/operations/getdatasetsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## create_dataset

Create a new dataset

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.Dataset(
    name='<value>',
    purpose='<value>',
    file=[
        components.File(),
    ],
    bytes=855366,
    description='Programmable scalable hardware',
    task='<value>',
    prompt='<value>',
)

res = s.datasets.create_dataset(req)

if res.dataset is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                | Type                                                     | Required                                                 | Description                                              |
| -------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- |
| `request`                                                | [components.Dataset](../../models/components/dataset.md) | :heavy_check_mark:                                       | The request object to use for the request.               |


### Response

**[operations.CreateDatasetResponse](../../models/operations/createdatasetresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## delete_dataset

Delete a dataset

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datasets.delete_dataset(id='<value>')

if res.object is not None:
    # handle response
    pass
```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `id`               | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteDatasetResponse](../../models/operations/deletedatasetresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## update_dataset

Update a dataset

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datasets.update_dataset(id='<value>', dataset=components.Dataset(
    name='<value>',
    purpose='<value>',
    file=[
        components.File(),
    ],
    bytes=897277,
    description='Compatible discrete implementation',
    task='<value>',
    prompt='<value>',
))

if res.dataset is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                | Type                                                     | Required                                                 | Description                                              |
| -------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- |
| `id`                                                     | *str*                                                    | :heavy_check_mark:                                       | N/A                                                      |
| `dataset`                                                | [components.Dataset](../../models/components/dataset.md) | :heavy_check_mark:                                       | N/A                                                      |


### Response

**[operations.UpdateDatasetResponse](../../models/operations/updatedatasetresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |
