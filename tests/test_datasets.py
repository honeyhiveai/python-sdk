import honeyhive
import os
from honeyhive.models import components

sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"])


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
