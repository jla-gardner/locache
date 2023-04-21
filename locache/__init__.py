import inspect
import logging
import pickle
import shutil
from functools import partial
from hashlib import sha256
from pathlib import Path
from typing import Callable, Union

__all__ = ["persist", "verbose"]
__version__ = "3.0.0"


class LocalCache:
    def __init__(self, func, location, auto_invalidate=False):
        self.func = func
        self.backend = Backend(func, location, auto_invalidate)
        self.__doc__ = func.__doc__

    def __call__(self, *args, **kwargs):
        cache_path = self.backend.get_cache_path(*args, **kwargs)
        _logger.debug(
            f"Querying cache at {self.backend.location} for {args}, {kwargs}"
        )

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

    def number_of_entries(self):
        return len(list(self.backend.location.glob("*.pkl")))

    def __repr__(self):
        n = self.number_of_entries()
        return f"<cache for {self.func.__name__} with {n} entries>"


class Backend:
    """
    A class for managing the cache directory

    Args:
        func: the function to cache
        location: the directory where the cache is stored
        auto_invalidate: if True, the cache will be invalidated
                            if the function code changes
    """

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
            _logger.warning(
                f"Detected code change for {func.__name__}. Resetting cache."
            )
            shutil.rmtree(location)
            self.location.mkdir(parents=True)
            code_file.write_text(new_code)

    def get_cache_path(self, *args, **kwargs):
        dump = pickle.dumps((args, kwargs))
        signature = sha256(dump).hexdigest()[:32]
        return self.location / f"{signature}.pkl"


def get_directory_for_(func: Callable, root: Union[Path, str] = None):
    """
    get the directory where the cache for a function is stored
    """

    # if root isn't passed, we store the cache in
    # <path-to-function's-file>.cache/<function-name>
    # e.g. /home/user/src/foo.cache/bar/
    path = Path(inspect.getfile(func))

    # unless we're in a notebook, in which case we store the cache in
    # <cwd>/notebook.cache/<function-name>
    # e.g. /home/user/notebook.cache/bar/
    if "ipykernel" in str(path):
        path = Path.cwd() / "notebook.cache"

    # if root is passed, we store the cache in
    # <root>.cache/<function-name>
    # e.g. /home/user/special_name.cache/bar/
    if root is not None:
        path = Path(root)

    return path.with_suffix(".cache") / func.__name__


def persist(
    func: Callable = None,
    *,
    root: Union[Path, str] = None,
    auto_invalidate: bool = True,
):
    """
    A decorator for caching function results to disk

    If the function bar is defined in foo.py, then the results
    will be stored in foo.cache/bar/. For notebooks, the results
    will be stored in notebook.cache/bar/.

    Args:
        function: the function to cache
        auto_invalidate: if True, the cache will be invalidated if the function code changes

    Returns:
        the LocalCache wrapper object

    Example:
        @persist
        def add(a, b):
            return a + b

        @persist(auto_invalidate=False)
        def add(a, b, c):
            return a + b + c
    """

    if func is None:
        # decorator called using (**kwargs), so return a partial
        return partial(persist, root=root, auto_invalidate=auto_invalidate)

    location = get_directory_for_(func, root)
    cache = LocalCache(func, location, auto_invalidate)
    return cache


# LOGGING
_logger = logging.getLogger(f"{__name__} : local_cache")
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())


def verbose(val: bool):
    if val:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.INFO)
