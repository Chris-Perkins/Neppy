"""
local filestorage-based caching

# Usage:
```py
import cache

cache.set_value("expensive_result") = "Tremendous findings"
...
value = cache.get_value("expensive_result)
```
"""

import os

import neppy_config


def get_value(key: str) -> str | None:
    cache_key_path = _get_cached_file_path(key)
    if not os.path.exists(cache_key_path):
        return None
    with open(cache_key_path, "r") as f:
        cached_value = f.read()
    return cached_value


def set_value(key: str, value: str) -> None:
    cache_key_path = _get_cached_file_path(key)
    with open(cache_key_path, "w") as token:
        token.write(value)


def _get_cached_file_path(key: str) -> str:
    return os.path.join(neppy_config.cache_folder_path, key)
