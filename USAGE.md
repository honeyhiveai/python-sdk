<!-- Start SDK Example Usage [usage] -->
```python
import honeyhive
from honeyhive.models import components

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)

req = components.CreateRunRequest(
    project='<value>',
    name='<value>',
    event_ids=[
        '7ca92550-e86b-4cb5-8288-452bedab53f3',
    ],
)

res = s.post_runs(req)

if res.create_run_response is not None:
    # handle response
    pass

```
<!-- End SDK Example Usage [usage] -->