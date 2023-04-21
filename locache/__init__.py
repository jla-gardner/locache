import inspect
import logging
import pickle
from functools import partial
from hashlib import sha256
from pathlib import Path

__all__ = ["persist", "verbose"]
__version__ = "2.1.1"


def persist(func=None, *, auto_invalidate=True):
    """
    decorator for caching function results to disk

    If the function bar is defined in foo.py, then the results
    will be stored in ./foo.cache/bar/

    Args:
        function: the function to cache
        auto_invalidate: if True, the cache will be invalidated if the function code changes

    Returns:
        the decorator

    Example:
        @persist
        def add(a, b):
            return a + b

        @persist(auto_invalidate=False)
        def add(a, b, c):
            return a + b + c
    """
    if func is None:
        return partial(persist, auto_invalidate=auto_invalidate)

    location = get_filename_containing_(func)
    cache = LocalCache(func, location, auto_invalidate)
    return cache


_logger = logging.getLogger(f"{__name__} : local_cache")
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


def verbose(val: bool):
    if val:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.INFO)


class LocalCache:
    def __init__(self, func, location, auto_invalidate=False):
        self.func = func
        self.backend = Backend(func, location, auto_invalidate)
        self.__doc__ = func.__doc__

    def __call__(self, *args, **kwargs):
        cache_path = self.backend.get_cache_path(*args, **kwargs)
        _logger.debug(f"Querying cache at {self.backend.location} for {args}, {kwargs}")

        if cache_path.exists():
            _logger.debug("Cache hit")
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        else:
            _logger.debug("Cache miss")
            result = self.func(*args, **kwargs)
            with open(cache_path, "wb") as f:
                pickle.dump(result, f)
            return result

    def __repr__(self):
        n = len(list(self.backend.location.glob("*.pkl")))
        return f"<cache for {self.func.__name__} with {n} entries>"


class Backend:
    def __init__(self, func, location, auto_invalidate):
        self.location = location
        code_file = location / ".code.py"
        new_code = inspect.getsource(func)

        if not location.exists() or not code_file.exists():
            location.mkdir(parents=True, exist_ok=True)
            code_file.write_text(new_code)
            return

        old_code = code_file.read_text()
        if auto_invalidate and new_code != old_code:
            _logger.info(f"Detected code change for {func.__name__}. Deleting cache.")
            self.location.rmdir()
            self.location.mkdir(parents=True)
            code_file.write_text(new_code)

    def get_cache_path(self, *args, **kwargs):
        dump = pickle.dumps((args, kwargs))
        signature = sha256(dump).hexdigest()[:32]
        return self.location / f"{signature}.pkl"


def get_filename_containing_(func):
    path = Path(inspect.getfile(func))
    if "ipykernel" in str(path):
        path = Path.cwd() / "notebook.py"
    return path.with_suffix(".cache") / func.__name__
