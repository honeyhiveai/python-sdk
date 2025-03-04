<!-- Start SDK Example Usage [usage] -->
```python
# Synchronous Example
from honeyhive import HoneyHive

s = HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.session.start_session(request={
    "session": {
        "project": "Simple RAG Project",
        "session_name": "Playground Session",
        "source": "playground",
        "session_id": "caf77ace-3417-4da4-944d-f4a0688f3c23",
        "children_ids": [
            "7f22137a-6911-4ed3-bc36-110f1dde6b66",
        ],
        "inputs": {
            "context": "Hello world",
            "question": "What is in the context?",
            "chat_history": [
                {
                    "role": "system",
                    "content": "Answer the user's question only using provided context.\n" +
                    "\n" +
                    "Context: Hello world",
                },
                {
                    "role": "user",
                    "content": "What is in the context?",
                },
            ],
        },
        "outputs": {
            "role": "assistant",
            "content": "Hello world",
        },
        "error": "<value>",
        "duration": 824.8056,
        "user_properties": {
            "user": "google-oauth2|111840237613341303366",
        },
        "metrics": {

        },
        "feedback": {

        },
        "metadata": {

        },
        "start_time": 1712025501605,
        "end_time": 1712025499832,
    },
})

if res.object is not None:
    # handle response
    pass
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from honeyhive import HoneyHive

async def main():
    s = HoneyHive(
        bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
    )
    res = await s.session.start_session_async(request={
        "session": {
            "project": "Simple RAG Project",
            "session_name": "Playground Session",
            "source": "playground",
            "session_id": "caf77ace-3417-4da4-944d-f4a0688f3c23",
            "children_ids": [
                "7f22137a-6911-4ed3-bc36-110f1dde6b66",
            ],
            "inputs": {
                "context": "Hello world",
                "question": "What is in the context?",
                "chat_history": [
                    {
                        "role": "system",
                        "content": "Answer the user's question only using provided context.\n" +
                        "\n" +
                        "Context: Hello world",
                    },
                    {
                        "role": "user",
                        "content": "What is in the context?",
                    },
                ],
            },
            "outputs": {
                "role": "assistant",
                "content": "Hello world",
            },
            "error": "<value>",
            "duration": 824.8056,
            "user_properties": {
                "user": "google-oauth2|111840237613341303366",
            },
            "metrics": {

            },
            "feedback": {

            },
            "metadata": {

            },
            "start_time": 1712025501605,
            "end_time": 1712025499832,
        },
    })
    if res.object is not None:
        # handle response
        pass

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->