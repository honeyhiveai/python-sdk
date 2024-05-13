import honeyhive
import os
import uuid
from honeyhive.models import components

sdk = honeyhive.HoneyHive(
    bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
)


def test_get_projects():
    res = sdk.projects.get_projects()
    assert res.status_code == 200
    assert len(res.projects) > 0


def test_create_projects():
    req = components.CreateProjectRequest(
        name="Python SDK Test",
        description="A project created in the Python SDK test suite",
    )
    res = sdk.projects.create_project(req)
    assert res.status_code == 200
    assert res.project is not None
    assert res.project.id is not None

    project = res.project
    req = components.UpdateProjectRequest(
        project_id=project.id, description="A new description"
    )
    res = sdk.projects.update_project(req)
    assert res.status_code == 200

    res = sdk.projects.get_projects()
    assert res.status_code == 200
    assert len(res.projects) > 0

    found_project = None
    for p in res.projects:
        if p.id == project.id:
            found_project = p
    assert found_project is not None
    assert found_project.description == "A new description"

    res = sdk.projects.delete_project(name=project.name)
    assert res.status_code == 200

    res = sdk.projects.get_projects()
    assert res.status_code == 200
    assert len(res.projects) > 0

    found_project = None
    for p in res.projects:
        if p.id == project.id:
            found_project = p
    assert found_project is None
