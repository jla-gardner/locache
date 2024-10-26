from __future__ import annotations

import functools
import inspect
import logging
import pickle
import shutil
import time
from hashlib import sha256
from pathlib import Path
from typing import Callable

__all__ = ["persist", "verbose", "reset"]
__version__ = "3.0.1"


_logger = logging.getLogger(f"{__name__} : local_cache")
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


_IS_BASE_FUNC = "__is_base_func"


def persist(func: Callable):
    """
    decorator for caching expensive function calls to disk

    Parameters
    ----------
    func
        the function to cache. In order to be cache-able,
        all arguments and return value must be pickleable.

    Returns
    -------
    Callable
        the decorated function
    """

    # we cache the results of this function call to files
    # in a directory directly associated with the function
    location = _get_cache_location_for(func)
    if location is None:
        _logger.warning(
            "Unable to find the definition of this function. "
            "Perhaps you defined it in the REPL? (This is not "
            "supported.) No caching will happen. Please "
            "raise an issue, if you think this should be "
            "working, at https://github.com/jla-gardner/locache/issues",
        )
        return func

    # mark this as the base function for caching:
    # this lets us unwrap any decorators that are applied
    # on top of @persist in a reliable fashion (see reset)
    setattr(func, _IS_BASE_FUNC, True)

    MAX_CACHE_SIZE = 100
    OLD_AGE = 365  # days

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _logger.debug(f"caching {func.__name__} to {location}")

        location.mkdir(parents=True, exist_ok=True)

        # within this directory, we use a hash of the function's
        # source code and arguments as a unique identifier for this
        # particular function call
        source_code = inspect.getsource(func)
        dump = pickle.dumps((source_code, args, kwargs))
        hash = sha256(dump).hexdigest()[:32]

        # we save the result of this function call to a file
        # with this unique identifier as the filename
        file_path = location / f"{hash}.pkl"

        if file_path.exists():
            _logger.debug(f"cache hit for {func.__name__} with {args}, {kwargs}")
            with open(file_path, "rb") as f:
                result = pickle.load(f)

        else:
            _logger.debug(f"cache miss for {func.__name__} with {args}, {kwargs}")
            result = func(*args, **kwargs)
            with open(file_path, "wb") as f:
                pickle.dump(result, f)

        # before returning the result, we clean up the cache:

        # some OS settings disable routine writing to st_atime
        # (i.e. the file's last access time) so instead we update
        # the file's last modified time
        file_path.touch()

        # list files in order of last touched ascending
        all_files = sorted(location.glob("*.pkl"), key=lambda f: f.stat().st_mtime)

        # remove files if we're over the size limit
        to_delete = len(all_files) - MAX_CACHE_SIZE
        for file in all_files[:to_delete]:
            file.unlink()
        all_files = all_files[to_delete:]

        # delete all old files
        now = time.time()
        ages_days = [(now - f.stat().st_mtime) / (60 * 60 * 24) for f in all_files]
        for age, file in zip(ages_days, all_files):
            if age > OLD_AGE:
                file.unlink()

        return result

    return wrapper


def reset(func):
    """
    reset the cache for a function

    Parameters
    ----------
    func : Callable
        the function to reset the cache for
    """

    # unwrap the function (optionally multiply decorated) func
    # until we get to the function that would have been passed
    # to @persist

    og_func = func
    removed = False
    while not removed:
        new_func = getattr(func, "__wrapped__", None)
        removed = getattr(func, _IS_BASE_FUNC, False)
        if removed:
            func = new_func
            break

        if new_func is None:
            _logger.warning(
                f"While attempting to unwrap {og_func.__name__}, "
                "we found that the __wrapped__ attribute was not "
                f"properly propagated through {func.__name__}. This suggests "
                "that:\n (a) you are using a decorator on top of @persist that does not "
                "set the __wrapped__ attribute, using e.g. functools.wraps\n (b) you "
                "have passed a function that is not decorated at all.\n"
                "We can't access the actual function that is being cached, "
                "and therefore no cache will be reset. "
            )
            return

        func = new_func

    # func is now the actual function that would have been
    # passed to @persist
    location = _get_cache_location_for(func)
    if location is not None:
        shutil.rmtree(location, ignore_errors=True)


def _get_cache_location_for(func) -> Path | None:
    """
    get the cache location for a function

    this should work wherever the function is defined,
    i.e. in a file somewhere, in a notebook, or in an
    interactive session

    Parameters
    ----------
    func : Callable
        the function to cache


    Returns
    -------
    Path | None
        the cache location, or None if the function is defined
        in the REPL / can't be found
    """

    file = inspect.getfile(func)

    # filter out if in a REPL
    if file == "<stdin>":
        return None

    # default case: func is defined in a file:
    # location = <path-to-function's-file>.cache/<function-name>
    path = Path(file).with_suffix(".cache")

    # if we're in a notebook, we store the cache in
    # <cwd>/notebook.cache/<function-name>
    if "ipykernel" in file:
        path = Path.cwd() / "notebook.cache"

    return path / func.__name__


def verbose(yes=True):
    """
    set the verbosity of the logging

    Parameters
    ----------
    yes : bool, optional
        whether to log or not, by default True
    """
    _logger.setLevel(logging.DEBUG if yes else logging.INFO)
