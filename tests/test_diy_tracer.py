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
        input={"input": input, "chat_history": [{"role": "user", "content": input}]},
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
        input={"input": input, "chat_history": [{"role": "user", "content": input}]},
        config={"provider": "openai", "endpoint": "streaming"},
    ) as model_call:
        resp = openai_client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": input}], stream=True
        )
    assert model_call.event_id is not None

def test_function_call_streaming():
    tracer = HoneyHiveTracer(
        project=os.environ["HH_PROJECT"],
        name="DIY Function Call Stream Test",
        source="diy_function_stream_test",
        api_key=os.environ["HH_API_KEY"],
    )
    input = "Hello, what's the weather in Beijing in celsius?"
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use. Infer this from the users location.",
                        },
                    },
                    "required": ["location", "format"],
                },
            }
        },
    ]

    with tracer.model(
        event_name="DIY Stream Test",
        description="DIY stream testing",
        input={"input": input, "chat_history": [{"role": "user", "content": input}]},
        config={"provider": "openai", "endpoint": "streaming"},
    ) as model_call:
        resp = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": input}],
            tools=tools,
            stream=True
        )
    assert model_call.event_id is not None