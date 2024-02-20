# Testcases
(*testcases*)

### Available Operations

* [get_testcases](#get_testcases) - Get testcases
* [post_testcases](#post_testcases) - Create a testcase
* [put_testcases](#put_testcases) - Update a testcase

## get_testcases

Get testcases

### Example Usage

```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.testcases.get_testcases(project='<value>', type='<value>', testcase_id='<value>')

if res.object is not None:
    # handle response
    pass
```

### Parameters

| Parameter            | Type                 | Required             | Description          |
| -------------------- | -------------------- | -------------------- | -------------------- |
| `project`            | *str*                | :heavy_check_mark:   | Project ID           |
| `type`               | *Optional[str]*      | :heavy_minus_sign:   | Type of the testcase |
| `testcase_id`        | *Optional[str]*      | :heavy_minus_sign:   | N/A                  |


### Response

**[operations.GetTestcasesResponse](../../models/operations/gettestcasesresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## post_testcases

Create a testcase

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.Testcase()

res = s.testcases.post_testcases(req)

if res.object is not None:
    # handle response
    pass
```

### Parameters

| Parameter                                                  | Type                                                       | Required                                                   | Description                                                |
| ---------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------- |
| `request`                                                  | [components.Testcase](../../models/components/testcase.md) | :heavy_check_mark:                                         | The request object to use for the request.                 |


### Response

**[operations.PostTestcasesResponse](../../models/operations/posttestcasesresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |

## put_testcases

Update a testcase

### Example Usage

```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.testcases.put_testcases(testcase_id='<value>', testcase_update=components.TestcaseUpdate())

if res.status_code == 200:
    # handle response
    pass
```

### Parameters

| Parameter                                                              | Type                                                                   | Required                                                               | Description                                                            |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `testcase_id`                                                          | *str*                                                                  | :heavy_check_mark:                                                     | The ID of the testcase to update                                       |
| `testcase_update`                                                      | [components.TestcaseUpdate](../../models/components/testcaseupdate.md) | :heavy_check_mark:                                                     | N/A                                                                    |


### Response

**[operations.PutTestcasesResponse](../../models/operations/puttestcasesresponse.md)**
### Errors

| Error Object    | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| errors.SDKError | 4x-5xx          | */*             |
