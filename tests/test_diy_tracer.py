import os
from honeyhive.utils.tracer import HoneyHiveTracer
from openai import OpenAI

openai_client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ["OPENAI_API_KEY"],
)


def test_thing():
    tracer = HoneyHiveTracer(
        project=os.environ["HH_PROJECT"],
        name="DIY Test",
        source="diy_test",
        api_key=os.environ["HH_API_KEY"],
    )
    input = "Hello there"
    with tracer.model(
        event_name="DIY Test",
        description="DIY testing",
        input=input,
        config={"provider": "openai"},
    ) as model_call:
        resp = openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": input}]
        )
    assert model_call.event_id is not None


def test_streaming_thing():
    tracer = HoneyHiveTracer(
        project=os.environ["HH_PROJECT"],
        name="DIY Stream Test",
        source="diy_stream_test",
        api_key=os.environ["HH_API_KEY"],
    )
    input = "Hello there, stream"
    with tracer.model(
        event_name="DIY Stream Test",
        description="DIY stream testing",
        input=input,
        config={"provider": "openai", "endpoint": "streaming"},
    ) as model_call:
        resp = openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": input}], stream=True
        )
    assert model_call.event_id is not None
