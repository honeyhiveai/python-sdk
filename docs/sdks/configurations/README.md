# Configurations
(*configurations*)

### Available Operations

* [get_configurations](#get_configurations) - Retrieve a list of configurations
* [create_configuration](#create_configuration) - Create a new configuration
* [delete_configuration](#delete_configuration) - Delete a configuration
* [update_configuration](#update_configuration) - Update an existing configuration

## get_configurations

Retrieve a list of configurations

### Example Usage

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

### Parameters

| Parameter                                          | Type                                               | Required                                           | Description                                        |
| -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- |
| `project_name`                                     | *str*                                              | :heavy_check_mark:                                 | Project name for configuration                     |
| `type`                                             | [operations.Type](../../models/operations/type.md) | :heavy_check_mark:                                 | Configuration type - "LLM" or "pipeline"           |


### Response

**[operations.GetConfigurationsResponse](../../models/operations/getconfigurationsresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## create_configuration

Create a new configuration

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.Configuration(
    project='<value>',
    name='<value>',
    provider='<value>',
)

res = s.configurations.create_configuration(req)

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                            | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `request`                                                            | [components.Configuration](../../models/components/configuration.md) | :heavy_check_mark:                                                   | The request object to use for the request.                           |


### Response

**[operations.CreateConfigurationResponse](../../models/operations/createconfigurationresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## delete_configuration

Delete a configuration

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.delete_configuration(id='<value>')

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter          | Type               | Required           | Description        |
| ------------------ | ------------------ | ------------------ | ------------------ |
| `id`               | *str*              | :heavy_check_mark: | Configuration ID   |


### Response

**[operations.DeleteConfigurationResponse](../../models/operations/deleteconfigurationresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## update_configuration

Update an existing configuration

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.update_configuration(id='<value>', configuration=components.Configuration(
    project='<value>',
    name='<value>',
    provider='<value>',
))

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                            | Type                                                                 | Required                                                             | Description                                                          |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| `id`                                                                 | *str*                                                                | :heavy_check_mark:                                                   | Configuration ID                                                     |
| `configuration`                                                      | [components.Configuration](../../models/components/configuration.md) | :heavy_check_mark:                                                   | N/A                                                                  |


### Response

**[operations.UpdateConfigurationResponse](../../models/operations/updateconfigurationresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |
