<!-- Start SDK Example Usage -->
```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="",
)


res = s.delete_tasks(name='string')

if res.delete_response is not None:
    # handle response
    pass
```
<!-- End SDK Example Usage -->