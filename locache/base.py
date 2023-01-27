import pickle
from pathlib import Path
from shutil import rmtree as rm_rf
from typing import Any, Callable

from locache.logging import info
from locache.util import (
    RUNNING_PATH,
    Files,
    get_file_containing,
    get_full_signature,
    get_source_code_for,
    relative_path_to,
)


class LocalCache:
    """
    Class for caching function results to disk.

    Args:
        func:
            the function to cache
        location:
            the location to store the cache on disk
        auto_invalidate:
            if True, the cache will be invalidated if the function code changes

    Example:
        ```
        cache = LocalCache(add, Path("cache"), auto_invalidate=True)
        cache.call(1, 2)
        ```
    """

    def __init__(self, func: Callable, location: Path, auto_invalidate: bool) -> None:
        # setup the cache location on disk, and invalidate if necessary
        _setup(location, func, auto_invalidate)
        self.func = func
        self.location = location

    def call(self, *args, **kwargs):
        """
        hit the cache, or call the function if the cache is empty
        """

        file = self.location / file_name_for(self.func, args, kwargs)
        relative_path = relative_path_to(file)
        name = self.func.__name__

        if file.exists():
            info(f"Using cached result for {name} from {relative_path}")
            out = load_from_disk(file)

        else:
            info(f"Caching result for {name} in {relative_path}")
            out = self.func(*args, **kwargs)
            save_to_disk(out, file)

        return out


def get_cache_location(func: Callable, name: str = None):

    if name is not None:
        prefix = RUNNING_PATH / f"{name}.cache"
    else:
        prefix = get_file_containing(func).with_suffix(".cache")

    return prefix / f"{func.__name__}"


def _setup(cache_location: Path, func: Callable, auto_invalidate: bool):

    # cache_location = cache_location
    cache_location.mkdir(parents=True, exist_ok=True)

    code_file = cache_location / Files.CODE
    function_code = get_source_code_for(func)

    if auto_invalidate:
        # check to see if the code has changed
        if code_file.exists() and code_file.read_text() != function_code:
            info(f"Detecting code has changed for {func.__name__}.")
            reset(cache_location)
            code_file.write_text(function_code)

    # write (or update) the code file
    code_file.write_text(function_code)


def file_name_for(func, args, kwargs):
    signature = get_full_signature(func, args, kwargs)

    SEP = "~"  # an illegal python variable char, and unlikely to be in an arg
    return SEP.join(f"{k}={stringify(v)}" for k, v in signature.items())


def reset(cache_location):
    info(f"Resetting cache at ./{relative_path_to(cache_location)}.")
    rm_rf(cache_location)
    cache_location.mkdir(parents=True, exist_ok=False)


def stringify(thing: Any) -> str:
    # TODO: compress/hash larger objects
    return str(thing)


def load_from_disk(file):
    with open(file, "rb") as file:
        return pickle.load(file)


def save_to_disk(obj, file):
    with open(file, "wb") as file:
        pickle.dump(obj, file)
