import inspect
import logging
import pickle
import shutil
from functools import wraps
from hashlib import sha256
from pathlib import Path
from typing import Callable, Optional

__all__ = ["persist", "verbose", "reset"]
__version__ = "3.0.1"


def persist(func: Callable):
    """
    decorator for caching expensive function calls to disk

    Parameters
    ----------
    func : Callable
        the function to cache. In order to be cache-able,
        all arguments and return value must be pickleable.

    Returns
    -------
    Callable
        the decorated function
    """

    location = _prepare_cache_location(func)

    if location is None:
        # if the cache location can't be prepared, we just
        # return the original function
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        cache_path = location / _get_hash(args, kwargs)

        if cache_path.exists():
            log(f"cache hit for {func.__name__} with {args}, {kwargs}")
            with open(cache_path, "rb") as f:
                result = pickle.load(f)

        else:
            log(f"cache miss for {func.__name__} with {args}, {kwargs}")
            result = func(*args, **kwargs)
            with open(cache_path, "wb") as f:
                pickle.dump(result, f)

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
    # unwrap the function if it's wrapped by @persist
    func = getattr(func, "__wrapped__", func)
    _prepare_cache_location(func, reset=True)


def _prepare_cache_location(func, reset=False) -> Optional[Path]:
    """
    Prepare the cache location for a function
    """

    location = _get_cache_location_for(func)
    if location is None:
        log(
            f"locache is not supported for functions defined in the REPL",
            level=logging.WARNING,
        )
        return None

    code_file = location / ".code.py"
    old_code = code_file.read_text() if code_file.exists() else None
    new_code = inspect.getsource(func)

    if location.exists() and old_code is not None:
        if old_code == new_code and not reset:
            # nothing to do
            return location

        if old_code != new_code:
            log(
                f"detected a change in {func.__name__}'s code",
                level=logging.WARNING,
            )
            reset = True

    if reset:
        log(f"resetting the cache for {func.__name__}", level=logging.WARNING)
        shutil.rmtree(location, ignore_errors=True)

    location.mkdir(parents=True, exist_ok=True)
    code_file.write_text(new_code)
    log(f"created cache for {func.__name__}: {location}")

    return location


def _get_cache_location_for(func) -> Optional[Path]:
    """
    get the cache location for a function

    this should work wherever the function is defined,
    i.e. in a file somewhere, in a notebook, or in an
    interactive session

    Parameters
    ----------
    func : Callable
        the function to cache
    """

    file: str = inspect.getfile(func)

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


def _get_hash(args, kwargs) -> str:
    """
    get a hash of the function arguments

    Parameters
    ----------
    args : tuple
        the positional arguments
    kwargs : dict
        the keyword arguments

    Returns
    -------
    str
        the hash of the arguments
    """

    dump = pickle.dumps((args, kwargs))
    return sha256(dump).hexdigest()[:32]


# LOGGING
_logger = logging.getLogger(f"{__name__} : local_cache")
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


def verbose(yes=True):
    """
    set the verbosity of the logging

    Parameters
    ----------
    yes : bool, optional
        whether to log or not, by default True
    """
    _logger.setLevel(logging.DEBUG if yes else logging.INFO)


def log(msg: str, level=logging.DEBUG):
    """
    log a message

    Parameters
    ----------
    msg : str
        the message to log
    """
    _logger.log(level, msg)
