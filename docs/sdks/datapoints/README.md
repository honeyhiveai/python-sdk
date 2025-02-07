# Datapoints
(*datapoints*)

## Overview

### Available Operations

* [get_datapoints](#get_datapoints) - Retrieve a list of datapoints
* [create_datapoint](#create_datapoint) - Create a new datapoint
* [get_datapoint](#get_datapoint) - Retrieve a specific datapoint
* [update_datapoint](#update_datapoint) - Update a specific datapoint
* [delete_datapoint](#delete_datapoint) - Delete a specific datapoint

## get_datapoints

Retrieve a list of datapoints

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datapoints.get_datapoints(project='<value>')

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                  | Type                                       | Required                                   | Description                                |
| ------------------------------------------ | ------------------------------------------ | ------------------------------------------ | ------------------------------------------ |
| `project`                                  | *str*                                      | :heavy_check_mark:                         | Project name to filter datapoints          |
| `datapoint_ids`                            | List[*str*]                                | :heavy_minus_sign:                         | List of datapoint ids to fetch             |
| `dataset_name`                             | *Optional[str]*                            | :heavy_minus_sign:                         | Name of the dataset to get datapoints from |

### Response

**[operations.GetDatapointsResponse](../../models/operations/getdatapointsresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## create_datapoint

Create a new datapoint

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datapoints.create_datapoint(request=components.CreateDatapointRequest(
    project='New Project',
    inputs={
        'query': 'what\'s the temperature in Iceland?',
    },
    history=[
        {
            'role': 'system',
            'content': 'You are a helpful web assistant that helps users answer questions about the world based on the information provided to you by Google\'s search API. Answer the questions as truthfully as you can. In case you are unsure about the correct answer, please respond with "I apologize but I\'m not sure."',
        },
        {
            'role': 'user',
            'content': 'what\'s the temperature in Iceland?\n\n\n--Google search API results below:---\n\n"snippet":"2 Week Extended Forecast in Reykjavik, Iceland ; Feb 4, 29 / 20 °F · Snow showers early. Broken clouds. ; Feb 5, 27 / 16 °F · Light snow. Decreasing cloudiness.","snippet_highlighted_words":["Feb 4, 29 / 20 °F"]',
        },
    ],
    ground_truth={
        'role': 'assistant',
        'content': 'The temperature in Reykjavik, Iceland is currently around 5F or -15C. Please note that weather conditions can change rapidly, so it\'s best to check a reliable source for the most up-to-date information.',
    },
    linked_event='6bba5182-d4b1-4b29-a64a-f0a8bd964f76',
    linked_datasets=[
        '<value>',
    ],
    metadata={
        'question_type': 'weather',
        'completion_tokens': 47,
        'prompt_tokens': 696,
        'total_tokens': 743,
    },
))

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                              | Type                                                                                   | Required                                                                               | Description                                                                            |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `request`                                                                              | [components.CreateDatapointRequest](../../models/components/createdatapointrequest.md) | :heavy_check_mark:                                                                     | The request object to use for the request.                                             |

### Response

**[operations.CreateDatapointResponse](../../models/operations/createdatapointresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## get_datapoint

Retrieve a specific datapoint

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datapoints.get_datapoint(id='<id>')

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                    | Type                                         | Required                                     | Description                                  |
| -------------------------------------------- | -------------------------------------------- | -------------------------------------------- | -------------------------------------------- |
| `id`                                         | *str*                                        | :heavy_check_mark:                           | Datapoint ID like `65c13dbbd65fb876b7886cdb` |

### Response

**[operations.GetDatapointResponse](../../models/operations/getdatapointresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## update_datapoint

Update a specific datapoint

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datapoints.update_datapoint(id='<id>', update_datapoint_request=components.UpdateDatapointRequest(
    inputs={
        'query': 'what\'s the temperature in Reykjavik?',
    },
    history=[
        {
            'role': 'system',
            'content': 'You are a helpful web assistant that helps users answer questions about the world based on the information provided to you by Google\'s search API. Answer the questions as truthfully as you can. In case you are unsure about the correct answer, please respond with "I apologize but I\'m not sure."',
        },
        {
            'role': 'user',
            'content': 'what\'s the temperature in Reykjavik?\n\n\n--Google search API results below:---\n\n"snippet":"2 Week Extended Forecast in Reykjavik, Iceland ; Feb 4, 29 / 20 °F · Snow showers early. Broken clouds. ; Feb 5, 27 / 16 °F · Light snow. Decreasing cloudiness.","snippet_highlighted_words":["Feb 4, 29 / 20 °F"]',
        },
    ],
    ground_truth={
        'role': 'assistant',
        'content': 'The temperature in Reykjavik, Iceland is currently around 5F or -15C. Please note that weather conditions can change rapidly, so it\'s best to check a reliable source for the most up-to-date information.',
    },
    linked_evals=[
        '<value>',
    ],
    linked_datasets=[
        '<value>',
    ],
    metadata={
        'question_type': 'capital-weather',
        'random_field': 0,
    },
))

if res is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Type                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Required                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Example                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | *str*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | ID of datapoint to update                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `update_datapoint_request`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | [components.UpdateDatapointRequest](../../models/components/updatedatapointrequest.md)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | {<br/>"inputs": {<br/>"query": "what's the temperature in Reykjavik?"<br/>},<br/>"history": [<br/>{<br/>"role": "system",<br/>"content": "You are a helpful web assistant that helps users answer questions about the world based on the information provided to you by Google's search API. Answer the questions as truthfully as you can. In case you are unsure about the correct answer, please respond with \"I apologize but I'm not sure.\""<br/>},<br/>{<br/>"role": "user",<br/>"content": "what's the temperature in Reykjavik?\\n\\n\\n--Google search API results below:---\\n\\n\"snippet\":\"2 Week Extended Forecast in Reykjavik, Iceland ; Feb 4, 29 / 20 °F · Snow showers early. Broken clouds. ; Feb 5, 27 / 16 °F · Light snow. Decreasing cloudiness.\",\"snippet_highlighted_words\":[\"Feb 4, 29 / 20 °F\"]"<br/>}<br/>],<br/>"ground_truth": {<br/>"role": "assistant",<br/>"content": "The temperature in Reykjavik, Iceland is currently around 5F or -15C. Please note that weather conditions can change rapidly, so it's best to check a reliable source for the most up-to-date information."<br/>},<br/>"linked_event": "6bba5182-d4b1-4b29-a64a-f0a8bd964f76",<br/>"linked_evals": [],<br/>"linked_datasets": [],<br/>"metadata": {<br/>"question_type": "capital-weather",<br/>"random_field": 0<br/>}<br/>} |

### Response

**[operations.UpdateDatapointResponse](../../models/operations/updatedatapointresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |

## delete_datapoint

Delete a specific datapoint

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.datapoints.delete_datapoint(id='<id>')

if res.object is not None:
    # handle response
    pass

```

### Parameters

| Parameter                                    | Type                                         | Required                                     | Description                                  |
| -------------------------------------------- | -------------------------------------------- | -------------------------------------------- | -------------------------------------------- |
| `id`                                         | *str*                                        | :heavy_check_mark:                           | Datapoint ID like `65c13dbbd65fb876b7886cdb` |

### Response

**[operations.DeleteDatapointResponse](../../models/operations/deletedatapointresponse.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4XX, 5XX        | \*/\*           |