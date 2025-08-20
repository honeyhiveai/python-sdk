import honeyhive
import os
import uuid
from honeyhive.models import components

sdk = honeyhive.HoneyHive(
    bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
)


def test_get_metrics():
    res = sdk.metrics.get_metrics(project_name=os.environ["HH_PROJECT"])
    assert res.status_code == 200
    assert len(res.metrics) > 0


def test_create_metrics():
    random_string = str(uuid.uuid4())
    name = f"Python SDK test metric {random_string}"
    req = components.Metric(
        description="This is in the Python SDK test suite",
        name=name,
        return_type=components.ReturnType.FLOAT,
        task=os.environ["HH_PROJECT"],
        type=components.MetricType.HUMAN,
        criteria="Dummy criteria",
    )
    res = sdk.metrics.create_metric(request=req)
    assert res.status_code == 200

    res = sdk.metrics.get_metrics(project_name=os.environ["HH_PROJECT"])
    assert res.status_code == 200
    assert len(res.metrics) > 0
    found_metric = None
    for metric in res.metrics:
        if metric.name == name:
            found_metric = metric
            break
    assert found_metric is not None

    metric_id = found_metric.id
    assert metric_id is not None
    new_random_string = str(uuid.uuid4())
    new_name = f"Python SDK test metric {new_random_string}"
    req = components.MetricEdit(metric_id=metric_id, name=new_name)
    res = sdk.metrics.update_metric(req)
    assert res.status_code == 200

    res = sdk.metrics.get_metrics(project_name=os.environ["HH_PROJECT"])
    assert res.status_code == 200
    assert len(res.metrics) > 0
    found_metric = None
    for metric in res.metrics:
        if metric.id == metric_id:
            found_metric = metric
            break
    assert found_metric is not None
    assert found_metric.name == new_name

    res = sdk.metrics.delete_metric(metric_id=metric_id)
    assert res.status_code == 200

    res = sdk.metrics.get_metrics(project_name=os.environ["HH_PROJECT"])
    assert res.status_code == 200
    assert len(res.metrics) > 0
    found_metric = None
    for metric in res.metrics:
        if metric.id == metric_id:
            found_metric = metric
            break
    assert found_metric is None
