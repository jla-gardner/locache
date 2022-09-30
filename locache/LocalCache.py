from pathlib import Path
import inspect
from os import makedirs as make_dir
import pickle

RUNNING_PATH = Path('.').absolute()

class LocalCache:
    def __init__(self, func, name=None) -> None:
        self._func = func
        self._name = name

    @property
    def _cache_dir(self):
        return _get_cache_dir(self._func, self._name)
    
    def file_path(self, func, args, kwargs):
        signature = inspect.signature(func)
        params = signature.bind(*args, **kwargs)
        params.apply_defaults()

        arguments = [*params.arguments.items()]
        _arguments, _kwargs = arguments[:-1], arguments[-1][1]
        _kwargs = {k: _kwargs[k] for k in sorted(_kwargs.keys())}
        arguments = [*_arguments, *_kwargs.items()]

        filename = '_'.join(f'{k}={v}' for k, v in arguments)
        return self._cache_dir / filename

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
        func_file = Path(inspect.getfile(func)).absolute()
        _dir = func_file.with_suffix(".py.cache")
    
    _dir = _dir / func.__name__

    make_dir(_dir, exist_ok=True)
    return _dir


