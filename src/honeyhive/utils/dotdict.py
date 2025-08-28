"""Dot notation dictionary access utility."""

from typing import Any, Dict, Optional, Union


class dotdict(dict):
    """Dictionary with dot notation access.
    
    Example:
        >>> d = dotdict({'foo': {'bar': 'baz'}})
        >>> d.foo.bar
        'baz'
        >>> d.foo.bar = 'qux'
        >>> d['foo']['bar']
        'qux'
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the dotdict."""
        super().__init__(*args, **kwargs)
        # Convert nested dictionaries to dotdict
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = dotdict(value)
    
    def __getattr__(self, key: str) -> Any:
        """Get attribute using dot notation."""
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")
    
    def __setattr__(self, key: str, value: Any) -> None:
        """Set attribute using dot notation."""
        if isinstance(value, dict):
            value = dotdict(value)
        self[key] = value
    
    def __delattr__(self, key: str) -> None:
        """Delete attribute using dot notation."""
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")
    
    def __getitem__(self, key: str) -> Any:
        """Get item with dot notation support."""
        if '.' in key:
            keys = key.split('.')
            value = self
            for k in keys:
                value = value[k]
            return value
        return super().__getitem__(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set item with dot notation support."""
        if '.' in key:
            keys = key.split('.')
            target = self
            for k in keys[:-1]:
                if k not in target:
                    target[k] = dotdict()
                target = target[k]
            target[keys[-1]] = value
        else:
            if isinstance(value, dict):
                value = dotdict(value)
            super().__setitem__(key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get item with default value, supporting dot notation."""
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default
    
    def setdefault(self, key: str, default: Any = None) -> Any:
        """Set default value for key, supporting dot notation."""
        if '.' in key:
            keys = key.split('.')
            target = self
            for k in keys[:-1]:
                if k not in target:
                    target[k] = dotdict()
                target = target[k]
            if keys[-1] not in target:
                target[keys[-1]] = default
            return target[keys[-1]]
        else:
            return super().setdefault(key, default)
    
    def update(self, other: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Update dictionary with dot notation support."""
        if other is not None:
            for key, value in other.items():
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dotdict back to regular dictionary."""
        result = {}
        for key, value in self.items():
            if isinstance(value, dotdict):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
    
    def copy(self) -> "dotdict":
        """Create a shallow copy."""
        return dotdict(super().copy())
    
    def deepcopy(self) -> "dotdict":
        """Create a deep copy."""
        import copy
        return copy.deepcopy(self)
