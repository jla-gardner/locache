import functools
import inspect
import os

from locache.LocalCache import LocalCache, RUNNING_PATH
from locache.logging import info, verbose


def persist(_func=None, *, name=None, auto_invalidate=True):
    '''
    decorator that caches the return value of a function to 
    permanent memory for a given set of args and kwargs
    '''

    def persist_decorator(func):
        cache = LocalCache(func, name, auto_invalidate)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _file = cache.file_path(args, kwargs)
            _relative_path = os.path.relpath(_file, RUNNING_PATH)

            if _file.exists():  # cache hit: load from disk
                info(
                    f"Using cached result for {func.__name__} "
                    f"from {_relative_path}"
                )
                out = LocalCache.load_from_disk(_file)

            else:  # cache miss: call func and save to disk
                info(
                    f"Caching result for {func.__name__} "
                    f"in {_relative_path}"
                )
                out = func(*args, **kwargs)
                LocalCache.save_to_disk(out, _file)

            return out

        return wrapper

    if _func == None:  # called as @persist(name=...)
        return persist_decorator
    else:              # called as @persist
        return persist_decorator(_func)


def reset_cache(func, name=None):
    cache = LocalCache(inspect.unwrap(func), name)
    cache.reset()
