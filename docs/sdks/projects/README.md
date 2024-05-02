# Projects
(*projects*)

### Available Operations

* [delete_project](#delete_project) - Delete a project
* [get_projects](#get_projects) - Get a list of projects
* [create_project](#create_project) - Create a new project
* [update_project](#update_project) - Update an existing project

## delete_project

Delete a project

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.projects.delete_project(name='<value>')

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `name`             | *str*              | :heavy_check_mark: | N/A                |


### Response

**[operations.DeleteProjectResponse](../../models/operations/deleteprojectresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## get_projects

Get a list of projects

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.projects.get_projects(name='<value>')

if res.projects is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `name`             | *Optional[str]*    | :heavy_minus_sign: | N/A                |


### Response

**[operations.GetProjectsResponse](../../models/operations/getprojectsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## create_project

Create a new project

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.CreateProjectRequest(
    name='<value>',
)

res = s.projects.create_project(req)

if res.project is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `request`                                                                          | [components.CreateProjectRequest](../../models/components/createprojectrequest.md) | :heavy_check_mark:                                                                 | The request object to use for the request.                                         |


### Response

**[operations.CreateProjectResponse](../../models/operations/createprojectresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |

## update_project

Update an existing project

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.Project(
    description='Profit-focused even-keeled encryption',
    name='<value>',
)

res = s.projects.update_project(req)

if res.project is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                | Type                                                     | Required                                                 | Description                                              |
| -------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- |
| `request`                                                | [components.Project](../../models/components/project.md) | :heavy_check_mark:                                       | The request object to use for the request.               |


### Response

**[operations.UpdateProjectResponse](../../models/operations/updateprojectresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4xx-5xx         | */*             |
