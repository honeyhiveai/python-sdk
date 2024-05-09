import honeyhive
import os
import uuid
from honeyhive.models import components, operations

sdk = honeyhive.HoneyHive(
    bearer_auth=os.environ["HH_API_KEY"], server_url=os.environ["HH_API_URL"]
)


def test_get_configurations():
    res = sdk.configurations.get_configurations(project_name=os.environ["HH_PROJECT"])
    assert res.status_code == 200
    assert len(res.configurations) > 0


def test_post_configurations():
    random_string = str(uuid.uuid4())
    config_name = f"python-sdk-test-{random_string}"
    configuration = components.PostConfigurationRequest(
        project=os.environ["HH_PROJECT_ID"],
        name=config_name,
        provider="test-provider",
        parameters=components.PostConfigurationRequestParameters(
            call_type=components.PostConfigurationRequestCallType.CHAT,
            model="Test Model",
        ),
    )
    res = sdk.configurations.create_configuration(configuration)
    assert res.status_code == 200

    res = sdk.configurations.get_configurations(
        project_name=os.environ["HH_PROJECT"], name=config_name
    )
    assert res.status_code == 200
    assert len(res.configurations) == 1
    assert res.configurations[0].id is not None

    inserted_id = res.configurations[0].id
    res = sdk.configurations.update_configuration(
        id=inserted_id,
        put_configuration_request=components.PutConfigurationRequest(
            project=configuration.project,
            name=configuration.name,
            provider=configuration.provider,
            parameters=configuration.parameters,
            type=components.PutConfigurationRequestType.PIPELINE,
        ),
    )
    assert res.status_code == 200

    res = sdk.configurations.get_configurations(
        project_name=os.environ["HH_PROJECT"],
        name=config_name,
        type_=operations.GetConfigurationsQueryParamType.PIPELINE,
    )
    assert res.status_code == 200
    assert len(res.configurations) == 1
    assert (
        res.configurations[0].type
        == operations.GetConfigurationsQueryParamType.PIPELINE
    )

    res = sdk.configurations.delete_configuration(id=inserted_id)
    assert res.status_code == 200

    res = sdk.configurations.get_configurations(
        project_name=os.environ["HH_PROJECT"],
        name=config_name,
        type_=operations.GetConfigurationsQueryParamType.PIPELINE,
    )
    assert res.status_code == 200
    assert len(res.configurations) == 0
