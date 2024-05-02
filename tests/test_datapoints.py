import honeyhive
import os
from honeyhive.models import components

sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"])


def test_get_datapoints():
    res = sdk.datapoints.get_datapoints(project=os.environ["HH_PROJECT_ID"])
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.datapoints) > 0


def test_create_datapoints():
    req = components.CreateDatapointRequest(
        inputs={},
        ground_truth={"text": "This is part of the Python SDK test suite."},
        project="64d69442f9fa4485aa1cc582",
        type=components.CreateDatapointRequestType.EVALUATION,
    )
    res = sdk.datapoints.create_datapoint(req)
    assert res.status_code == 200
    assert res.object is not None
    assert res.object.result is not None
    assert res.object.result.inserted_id is not None

    inserted_id = res.object.result.inserted_id

    req = components.UpdateDatapointRequest(ground_truth={"text": "I am updating the ground truth in the Python SDK test suite"})
    res = sdk.datapoints.update_datapoint(datapoint_id=inserted_id, update_datapoint_request=req)
    assert res.status_code == 200

    res = sdk.datapoints.get_datapoint(id=inserted_id)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.datapoint) == 1
    assert res.object.datapoint[0].ground_truth.get("text") == "I am updating the ground truth in the Python SDK test suite"

    res = sdk.datapoints.delete_datapoint(id=inserted_id)
    assert res.status_code == 200

    res = sdk.datapoints.get_datapoint(id=inserted_id)
    assert res.status_code == 200
    assert res.object is not None
    assert len(res.object.datapoint) == 0
