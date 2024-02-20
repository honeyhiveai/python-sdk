<!-- Start SDK Example Usage [usage] -->
```python
import honeyhive

s = honeyhive.HoneyHive(
    bearer_auth="<YOUR_BEARER_TOKEN_HERE>",
)


res = s.configurations.get_configurations(project='<value>', type='<value>')

if res.configurations is not None:
    # handle response
    pass
```
<!-- End SDK Example Usage [usage] -->