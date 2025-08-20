import copy
import jinja2

from typing import Any

class TemplateString(str):
    def render(self, **kwargs):
        return jinja2.Template(self).render(**kwargs)

class dotdict(dict):
    def __init__(self, d=None):
        # TODO: handle YAMLs that are not dictionaries
        try:
            super().__init__({} if d is None else d)
        except Exception as e:
            raise ValueError(f"Error initializing dotdict. Ensure that the YAML is a valid dictionary.")

    @staticmethod
    def _is_dict(value):
        return isinstance(value, dict) and not isinstance(value, dotdict)
    
    def __getattr__(self, key) -> jinja2.Template | dict | list | Any:
        if key.startswith('__') and key.endswith('__'):
            return super().__getattr__(key)
        try:
            if key in self:
                value = self[key]
                if dotdict._is_dict(value):
                    value = dotdict(value)
                    self[key] = value
                elif isinstance(value, list):
                    value = [
                        dotdict(item) if dotdict._is_dict(item) else item
                        for item in value
                    ]
                    self[key] = value
                
                # make string renderable
                if isinstance(value, str):
                    try:
                        value = TemplateString(value)
                    except Exception as e:
                        pass

                return value
            return super().__getattr__(key)
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute or key '{key}'")

    def __setattr__(self, key, value):
        if key.startswith('__') and key.endswith('__'):
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if dotdict._is_dict(value):
            value = dotdict(value)
            self[key] = value
        return value

    def __setitem__(self, key, value):
        # Convert nested dictionaries in lists
        if isinstance(value, list):
            value = [
                dotdict(item) if isinstance(item, dict) and not isinstance(item, dotdict)
                else item
                for item in value
            ]
        # Convert direct dictionary values
        elif isinstance(value, dict) and not isinstance(value, dotdict):
            value = dotdict(value)
        super().__setitem__(key, value)

    def __delattr__(self, key):
        if key.startswith('__') and key.endswith('__'):
            super().__delattr__(key)
        else:
            del self[key]

    def __eq__(self, other):
        if isinstance(other, (dict, dotdict)):
            return dict(self) == dict(other)
        elif isinstance(other, list):
            # If we're comparing with a list, get the value from self
            # and compare it with the list
            for key, value in self.items():
                if value == other:
                    return True
            return False
        return other == self

    def __deepcopy__(self, memo):
        return dotdict(copy.deepcopy(dict(self), memo))
