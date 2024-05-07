<!-- Start SDK Example Usage [usage] -->
```python
import honeyhive
from honeyhive.models import components, operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

res = s.session.start_session(request=operations.StartSessionRequestBody(
    session=components.SessionStartRequest(
        project='Simple RAG Project',
        session_name='Playground Session',
        source='playground',
        session_id='caf77ace-3417-4da4-944d-f4a0688f3c23',
        children_ids=[
            '7f22137a-6911-4ed3-bc36-110f1dde6b66',
        ],
        inputs={
            'context': 'Hello world',
            'question': 'What is in the context?',
            'chat_history': '<value>',
        },
        outputs={
            'role': 'assistant',
            'content': 'Hello world',
        },
        error=None,
        duration=824.8056,
        user_properties={
            'user': 'google-oauth2|111840237613341303366',
        },
        metrics={

        },
        feedback={

        },
        metadata={

        },
        start_time=1712025501605,
        end_time=1712025499832,
    ),
))

if res.object is not None:
    # handle response
    pass

```
<!-- End SDK Example Usage [usage] -->