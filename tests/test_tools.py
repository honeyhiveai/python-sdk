import honeyhive
import os
import uuid
from honeyhive.models import components

sdk = honeyhive.HoneyHive(bearer_auth=os.environ["HH_API_KEY"])


def test_get_tools():
    res = sdk.tools.get_tools()
    assert res.status_code == 200
    assert len(res.tools) > 0


def test_create_tools():
    req = components.CreateToolRequest(
        name="Python SDK Test Tool",
        parameters={},
        task=os.environ["HH_PROJECT"],
        type=components.CreateToolRequestType.TOOL,
    )
    res = sdk.tools.create_tool(req)
    assert res.status_code == 200
    assert res.object is not None
    assert res.object.result is not None
    assert res.object.result.inserted_id is not None

    tool_id = res.object.result.inserted_id
    req = components.UpdateToolRequest(
        id=tool_id, name="New Name for Python SDK Test Tool", parameters={}
    )
    res = sdk.tools.update_tool(req)
    assert res.status_code == 200

    res = sdk.tools.get_tools()
    assert res.status_code == 200
    assert len(res.tools) > 0

    found_tool = None
    for t in res.tools:
        if t.id == tool_id:
            found_tool = t
    assert found_tool is not None
    assert found_tool.name == "New Name for Python SDK Test Tool"

    res = sdk.tools.delete_tool(function_id=tool_id)
    assert res.status_code == 200

    res = sdk.tools.get_tools()
    assert res.status_code == 200
    assert len(res.tools) > 0

    found_tool = None
    for t in res.tools:
        if t.id == tool_id:
            found_tool = t
    assert found_tool is None
