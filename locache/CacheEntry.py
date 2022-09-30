from pathlib import Path
import inspect
from os.path import abspath
from os import makedirs as make_dir
import pickle

RUNNING_PATH = Path(abspath('.'))

class CacheEntry:
    def __init__(self, func, name=None) -> None:
        self._func = func
        self._name = name

    @property
    def _cache_dir(self):
        return _get_cache_dir(self._func, self._name)
    
    def _cache_file(self, func, args, kwargs):
        parts = [func.__name__]
        if args:
            parts.append("_".join(map(str, args)))
        if kwargs:
            parts.append("_".join(f"{k}={v}" for k, v in kwargs.items()))
        return self._cache_dir / "__".join(parts)

    @classmethod
    def load_from_disk(cls, _file):
        with open(_file, "rb") as file:
            return pickle.load(file)

    @classmethod
    def save_to_disk(cls, obj, _file):
        with open(_file, "wb") as file:
            pickle.dump(obj, file)



def _get_cache_dir(func, dirname=None):
    if dirname is not None:
        # directory of currently running script + name
        _dir = RUNNING_PATH / f"{dirname}.cache"
    else:
        # get the file that func is defined in
        func_file = Path(abspath(inspect.getfile(func)))
        _dir = func_file.with_suffix(".py.cache")
    
    _dir = _dir / func.__name__

    make_dir(_dir, exist_ok=True)
    return _dir


