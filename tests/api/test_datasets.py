import honeyhive
import os
from honeyhive.models import components, operations

sdk = honeyhive.HoneyHive(
    bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
)


def test_get_datasets():
    res = sdk.datasets.get_datasets(project=os.environ["HH_PROJECT_ID"])
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.testcases) > 0


def test_create_datasets():
    req = components.CreateDatasetRequest(
        name="Python SDK Test", project=os.environ["HH_PROJECT_ID"]
    )
    res = sdk.datasets.create_dataset(req)
    assert res.status_code == 200
    assert res.object is not None
    assert res.object.result is not None
    assert res.object.result.inserted_id is not None

    dataset_id = res.object.result.inserted_id
    req = components.DatasetUpdate(
        dataset_id=dataset_id, name="New Name for Python SDK Test"
    )
    res = sdk.datasets.update_dataset(req)
    assert res.status_code == 200

    res = sdk.datasets.get_datasets(
        project=os.environ["HH_PROJECT_ID"], dataset_id=dataset_id
    )
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.testcases) == 1
    assert res.object.testcases[0].name == "New Name for Python SDK Test"

    res = sdk.datasets.delete_dataset(dataset_id=dataset_id)
    assert res.status_code == 200

    res = sdk.datasets.get_datasets(
        project=os.environ["HH_PROJECT_ID"], dataset_id=dataset_id
    )
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.testcases) == 0


def test_push_datapoint_to_dataset():
    # dont-delete-dataset below
    dataset_id = "6643b41552d5bf0e7ba34719"

    request_body = operations.AddDatapointsRequestBody(
        project=os.environ["HH_PROJECT"],
        data=[
            {
                "input1": "test",
                "output1": 10,
                "history": [{"role": "system", "content": "test"}],
                "random_field": 1.0
            }
        ],
        mapping=operations.Mapping(
            inputs=["input1"],
            ground_truth=["output1"],
            history=["history"]
        )
    )

    res = sdk.datasets.add_datapoints(dataset_id, request_body)
    assert res.status_code == 200
    assert res.object is not None

    datapoint_ids = res.object.datapoint_ids
    assert len(datapoint_ids) == 1

    res = sdk.datapoints.get_datapoint(datapoint_ids[0])
    assert res.status_code == 200
    assert res.object is not None
    datapoint = res.object.datapoint[0]

    assert datapoint.inputs["input1"] == "test"
    assert datapoint.ground_truth["output1"] == 10
    assert len(datapoint.history) == 1
    assert datapoint.metadata["random_field"] == 1.0
