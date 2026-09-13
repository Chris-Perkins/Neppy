"""Caching utilities for Neppy.

Caches in Neppy are backed by local filestorage, and are
persistent across multiple sessions.

Example: Manual Caching
    ```py
    set_cached_value("item", "Hand of A'dal")
    get_cached_value("item") # returns "Hand of A'dal"
    ```

Example: Automatic Function Caching
    ```py
    @cached
    def expensive_operation(...) -> str:
        time.sleep(1_000)
        return "cat"

    expensive_operation() # Function executes, returns "cat"
    expensive_operation() # Function does not execute, returns "cat" from previous run
    ```
"""

from pathlib import Path
from typing import Callable
import functools
import hashlib

import neppy.config


def cached[**T](fn: Callable[T, str]) -> Callable[T, str]:
    """Decorates an input function so its result is cached in local filestorage.

    If a value has already been cached, the cached value is returned without calling ``fn``.

    Example:
        ```py
        @neppy_cache()
        def expensive_operation(...) -> str:
            ...

        expensive_operation() # executes the function, result is cached
        expensive_operation() # returns the cached result immediately
        ```
    """

    def _get_fn_cache_key(fn: Callable, *args, **kwargs) -> str:
        fn_identifier = f"{fn.__module__}/{fn.__name__}"

        has_self_arg = fn.__code__.co_varnames[:1] == ("self",)
        cacheable_args = args[:1] if has_self_arg else args
        args_str = "_".join(str(x) for x in cacheable_args)
        kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

        parameters_identifier = f"{args_str}_{kwargs_str}"
        # hash parameters to guarantee an OS-safe file name (e.g., no invalid unicode chars)
        parameter_identifier_hash = hashlib.md5(parameters_identifier.encode("utf-8")).hexdigest()
        return f"{fn_identifier}/{parameter_identifier_hash}"

    @functools.wraps(fn)
    def cached_fn(*args, **kwargs) -> str:
        cache_key = _get_fn_cache_key(fn, *args, **kwargs)
        cached_value = get_cached_value(cache_key)
        if cached_value:
            return cached_value

        result = fn(*args, **kwargs)

        set_cached_value(cache_key, result)
        return result

    return cached_fn


def get_cached_value(key: str) -> str | None:
    cache_key_path = _get_cache_key_path(key)
    if not cache_key_path.exists():
        return None
    return cache_key_path.read_text()


def set_cached_value(key: str, value: str) -> None:
    cache_key_path = _get_cache_key_path(key)
    cache_key_path.parent.mkdir(parents=True, exist_ok=True)
    cache_key_path.write_text(value)


def _get_cache_key_path(key: str) -> Path:
    return Path(neppy.config.cache_dir_path).joinpath(key)
