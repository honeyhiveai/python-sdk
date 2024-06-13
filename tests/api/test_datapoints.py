import honeyhive
import os
from honeyhive.models import components

sdk = honeyhive.HoneyHive(
    bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
)

def test_populated_datapoint():
    res = sdk.datapoints.get_datapoints(project=os.environ["HH_PROJECT_ID"], dataset_name="dont-delete-dataset")
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.datapoints[-1].inputs.keys()) > 0
    assert len(res.object.datapoints[-1].ground_truth.keys()) > 0
    assert len(res.object.datapoints[-1].metadata.keys()) > 0
    assert len(res.object.datapoints[-1].history) > 0

def test_create_datapoints():
    req = components.CreateDatapointRequest(
        inputs={},
        ground_truth={"text": "This is part of the Python SDK test suite."},
        project="64d69442f9fa4485aa1cc582",
    )
    res = sdk.datapoints.create_datapoint(req)
    assert res.status_code == 200
    assert res.object is not None
    assert res.object.result is not None
    assert res.object.result.inserted_id is not None

    inserted_id = res.object.result.inserted_id

    req = components.UpdateDatapointRequest(
        ground_truth={
            "text": "I am updating the ground truth in the Python SDK test suite"
        }
    )
    res = sdk.datapoints.update_datapoint(id=inserted_id, update_datapoint_request=req)
    assert res.status_code == 200

    res = sdk.datapoints.get_datapoint(id=inserted_id)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.datapoint) == 1
    assert (
        res.object.datapoint[0].ground_truth.get("text")
        == "I am updating the ground truth in the Python SDK test suite"
    )

    res = sdk.datapoints.delete_datapoint(id=inserted_id)
    assert res.status_code == 200

    res = sdk.datapoints.get_datapoint(id=inserted_id)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.datapoint) == 0
