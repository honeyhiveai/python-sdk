# Configurations
(*configurations*)

## Overview

### Available Operations

* [get_configurations](#get_configurations) - Retrieve a list of configurations
* [create_configuration](#create_configuration) - Create a new configuration
* [update_configuration](#update_configuration) - Update an existing configuration
* [delete_configuration](#delete_configuration) - Delete a configuration

## get_configurations

Retrieve a list of configurations

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.configurations.get_configurations(project="<value>")

if res.configurations is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `project`                                                           | *str*                                                               | :heavy_check_mark:                                                  | Project name for configuration like `Example Project`               |
| `env`                                                               | [Optional[operations.Env]](../../models/operations/env.md)          | :heavy_minus_sign:                                                  | Environment - "dev", "staging" or "prod"                            |
| `name`                                                              | *Optional[str]*                                                     | :heavy_minus_sign:                                                  | The name of the configuration like `v0`                             |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[operations.GetConfigurationsResponse](../../models/operations/getconfigurationsresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## create_configuration

Create a new configuration

### Example Usage

```python
from honeyhive import HoneyHive
from honeyhive.models import components

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.configurations.create_configuration(request={
    "project": "660d7ba7995cacccce4d299e",
    "name": "function-v0",
    "provider": "openai",
    "parameters": components.PostConfigurationRequestParameters(
        call_type=components.PostConfigurationRequestCallType.CHAT,
        model="gpt-4-turbo-preview",
        hyperparameters={
            "temperature": 0,
            "max_tokens": 1000,
            "top_p": 1,
            "top_k": -1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop_sequences": [
                "<value>",
            ],
        },
        selected_functions=[
            {
                "id": "64e3ba90e81f9b3a3808c27f",
                "name": "get_google_information",
                "description": "Get information from Google when you do not have that information in your context",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query asked by the user",
                        },
                    },
                    "required": [
                        "query",
                    ],
                },
            },
        ],
        function_call_params=components.PostConfigurationRequestFunctionCallParams.AUTO,
        force_function={

        },
        **{
            "template": [
                {
                    "role": "system",
                    "content": "You are a web search assistant.",
                },
                {
                    "role": "user",
                    "content": "{{ query }}",
                },
            ],
        },
    ),
    "env": [
        components.PostConfigurationRequestEnv.STAGING,
    ],
    "user_properties": {
        "user_id": "google-oauth2|108897808434934946583",
        "user_name": "Dhruv Singh",
        "user_picture": "https://lh3.googleusercontent.com/a/ACg8ocLyQilNtK9RIv4M0p-0FBSbxljBP0p5JabnStku1AQKtFSK=s96-c",
        "user_email": "dhruv@honeyhive.ai",
    },
})

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                  | Type                                                                                       | Required                                                                                   | Description                                                                                |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| `request`                                                                                  | [components.PostConfigurationRequest](../../models/components/postconfigurationrequest.md) | :heavy_check_mark:                                                                         | The request object to use for the request.                                                 |
| `retries`                                                                                  | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                           | :heavy_minus_sign:                                                                         | Configuration to override the default retry behavior of the client.                        |

### Response

**[operations.CreateConfigurationResponse](../../models/operations/createconfigurationresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## update_configuration

Update an existing configuration

### Example Usage

```python
from honeyhive import HoneyHive
from honeyhive.models import components

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.configurations.update_configuration(id="<id>", put_configuration_request={
    "project": "New Project",
    "name": "function-v0",
    "provider": "openai",
    "parameters": components.PutConfigurationRequestParameters(
        call_type=components.PutConfigurationRequestCallType.CHAT,
        model="gpt-4-turbo-preview",
        hyperparameters={
            "temperature": 0,
            "max_tokens": 1000,
            "top_p": 1,
            "top_k": -1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop_sequences": [
                "<value>",
            ],
        },
        selected_functions=[
            {
                "id": "64e3ba90e81f9b3a3808c27f",
                "name": "get_google_information",
                "description": "Get information from Google when you do not have that information in your context",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query asked by the user",
                        },
                    },
                    "required": [
                        "query",
                    ],
                },
            },
        ],
        function_call_params=components.PutConfigurationRequestFunctionCallParams.AUTO,
        force_function={

        },
        **{
            "template": [
                {
                    "role": "system",
                    "content": "You are a web search assistant.",
                },
                {
                    "role": "user",
                    "content": "{{ query }}",
                },
            ],
        },
    ),
    "env": [
        components.PutConfigurationRequestEnv.STAGING,
    ],
    "type": components.PutConfigurationRequestType.LLM,
    "user_properties": {
        "user_id": "google-oauth2|108897808434934946583",
        "user_name": "Dhruv Singh",
        "user_picture": "https://lh3.googleusercontent.com/a/ACg8ocLyQilNtK9RIv4M0p-0FBSbxljBP0p5JabnStku1AQKtFSK=s96-c",
        "user_email": "dhruv@honeyhive.ai",
    },
})

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Type                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Required                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Example                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | *str*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Configuration ID like `6638187d505c6812e4043f24`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `put_configuration_request`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | [components.PutConfigurationRequest](../../models/components/putconfigurationrequest.md)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | {<br/>"project": "New Project",<br/>"name": "function-v0",<br/>"provider": "openai",<br/>"parameters": {<br/>"call_type": "chat",<br/>"model": "gpt-4-turbo-preview",<br/>"hyperparameters": {<br/>"temperature": 0,<br/>"max_tokens": 1000,<br/>"top_p": 1,<br/>"top_k": -1,<br/>"frequency_penalty": 0,<br/>"presence_penalty": 0,<br/>"stop_sequences": []<br/>},<br/>"responseFormat": {<br/>"type": "text"<br/>},<br/>"selectedFunctions": [<br/>{<br/>"id": "64e3ba90e81f9b3a3808c27f",<br/>"name": "get_google_information",<br/>"description": "Get information from Google when you do not have that information in your context",<br/>"parameters": {<br/>"type": "object",<br/>"properties": {<br/>"query": {<br/>"type": "string",<br/>"description": "The query asked by the user"<br/>}<br/>},<br/>"required": [<br/>"query"<br/>]<br/>}<br/>}<br/>],<br/>"functionCallParams": "auto",<br/>"forceFunction": {},<br/>"template": [<br/>{<br/>"role": "system",<br/>"content": "You are a web search assistant."<br/>},<br/>{<br/>"role": "user",<br/>"content": "{{ query }}"<br/>}<br/>]<br/>},<br/>"env": [<br/>"staging"<br/>],<br/>"type": "LLM",<br/>"tags": [],<br/>"user_properties": {<br/>"user_id": "google-oauth2\|108897808434934946583",<br/>"user_name": "Dhruv Singh",<br/>"user_picture": "https://lh3.googleusercontent.com/a/ACg8ocLyQilNtK9RIv4M0p-0FBSbxljBP0p5JabnStku1AQKtFSK=s96-c",<br/>"user_email": "dhruv@honeyhive.ai"<br/>}<br/>} |
| `retries`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Configuration to override the default retry behavior of the client.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

### Response

**[operations.UpdateConfigurationResponse](../../models/operations/updateconfigurationresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## delete_configuration

Delete a configuration

### Example Usage

```python
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.configurations.delete_configuration(id="<id>")

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `id`                                                                | *str*                                                               | :heavy_check_mark:                                                  | Configuration ID like `6638187d505c6812e4043f24`                    |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[operations.DeleteConfigurationResponse](../../models/operations/deleteconfigurationresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |