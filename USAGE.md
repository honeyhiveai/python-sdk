<!-- Start SDK Example Usage [usage] -->
```python
import honeyhive
from honeyhive.models import operations

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.get_configurations(project_name='<value>', type=operations.Type.LLM)

if res.configurations is not None:
    # handle response
    pass

```
<!-- End SDK Example Usage [usage] -->