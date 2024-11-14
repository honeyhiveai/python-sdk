# NewRun


## Fields

| Field                                                                                                                                    | Type                                                                                                                                     | Required                                                                                                                                 | Description                                                                                                                              |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                                                                                                                     | *Optional[str]*                                                                                                                          | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `run_id`                                                                                                                                 | *Optional[str]*                                                                                                                          | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `project`                                                                                                                                | *Optional[str]*                                                                                                                          | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `tenant`                                                                                                                                 | *Optional[str]*                                                                                                                          | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `created_at`                                                                                                                             | [date](https://docs.python.org/3/library/datetime.html#date-objects)                                                                     | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `event_ids`                                                                                                                              | List[*str*]                                                                                                                              | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `session_ids`                                                                                                                            | List[*str*]                                                                                                                              | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `dataset_id`                                                                                                                             | *Optional[str]*                                                                                                                          | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `datapoint_ids`                                                                                                                          | List[*str*]                                                                                                                              | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `evaluators`                                                                                                                             | List[[components.ExperimentComparisonResponseEvaluators](../../models/components/experimentcomparisonresponseevaluators.md)]             | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `results`                                                                                                                                | [Optional[components.ExperimentComparisonResponseSchemasResults]](../../models/components/experimentcomparisonresponseschemasresults.md) | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `configuration`                                                                                                                          | [Optional[components.ExperimentComparisonResponseConfiguration]](../../models/components/experimentcomparisonresponseconfiguration.md)   | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `metadata`                                                                                                                               | [Optional[components.ExperimentComparisonResponseMetadata]](../../models/components/experimentcomparisonresponsemetadata.md)             | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `passing_ranges`                                                                                                                         | [Optional[components.ExperimentComparisonResponsePassingRanges]](../../models/components/experimentcomparisonresponsepassingranges.md)   | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `status`                                                                                                                                 | *Optional[str]*                                                                                                                          | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |
| `name`                                                                                                                                   | *Optional[str]*                                                                                                                          | :heavy_minus_sign:                                                                                                                       | N/A                                                                                                                                      |