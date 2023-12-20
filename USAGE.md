<!-- Start SDK Example Usage [usage] -->
```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.get_tasks(name='string')

if res.classes is not None:
    # handle response
    pass
```
<!-- End SDK Example Usage [usage] -->