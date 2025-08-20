from opentelemetry import context, baggage

class BaggageDict(dict):

    valid_baggage_keys = [
        'session_id', 
        'project',
        'source',
        'run_id',
        'dataset_id',
        'datapoint_id',
        'disable_http_tracing',
    ]
    
    class DefaultGetter:
        @staticmethod
        def get(carrier, key):
            return carrier.get(key)
    
    class DefaultSetter:
        @staticmethod
        def set(carrier, key, value):
            carrier[key] = value

    def update(self, _dict: dict):
        _dict = {
            k: str(v) for k, v in _dict.items() 
            if v is not None and k in self.valid_baggage_keys
        }
        super().update(_dict)
        return self
    
    def __setitem__(self, key: str, value: str | None):
        if value is None:
            return
        super().__setitem__(key, str(value))
    
    def __getitem__(self, key: str):
        if key not in self:
            return None
        value = super().__getitem__(key)
        if value == "True":
            return True
        if value == "False":
            return False
        return value
    
    def get(self, key: str, default=None):
        value = self[key]  # This will use our __getitem__ which already handles missing keys
        return default if value is None else value
    
    def set_all_baggage(self, ctx=None):
        if ctx is None:
            ctx = context.get_current()
        for key in BaggageDict.valid_baggage_keys:
            value = self.get(key)
            if value is not None:
                ctx = baggage.set_baggage(key, value, ctx)
        return ctx

    def get_all_baggage(self, ctx=None):
        if ctx is None:
            ctx = context.get_current()
        bags = {}
        for key in BaggageDict.valid_baggage_keys:
            value = baggage.get_baggage(key, ctx)
            if value is not None:
                bags[key] = value
        return bags
