import functools
import warnings
from typing import Callable

from locache.base import LocalCache, get_cache_location, reset
from locache.logging import verbose


def persist(function=None, *, name: str = None, auto_invalidate=True):
    """
    decorator for caching function results to disk

    If the function bar is defined in foo.py, then the results
    will be stored in ./foo.cache/bar/, unless a name is specified,
    in which case the results will be stored in ./name.cache/foo/.

    Args:
        function: the function to cache
        name: the name of the cache (if not specified, the function name is used)
        auto_invalidate: if True, the cache will be invalidated if the function code changes

    Returns:
        the decorator

    Example:
        @persist
        def add(a, b):
            return a + b

        @persist(name="addition")
        def add(a, b, c):
            return a + b + c
    """

    def persist_decorator(func):
        location = get_cache_location(func, name)
        cache = LocalCache(func, location, auto_invalidate)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return cache.call(*args, **kwargs)

        return wrapper

    if function == None:  # called as @persist(name=...)
        return persist_decorator
    else:  # called as @persist
        return persist_decorator(function)


def reset_cache(func: Callable = None, name: str = None) -> None:
    """
    reset the cache for a function
    """

    location = get_cache_location(func, name)
    if location.exists():
        reset(location)
    else:
        warnings.warn(f"Attempted to reset cache at {location}, but it does not exist")
