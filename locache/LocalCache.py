import inspect
import pickle
from os import makedirs as make_dir
from pathlib import Path
from shutil import rmtree as rm_rf

from locache.logging import info

RUNNING_PATH = Path('.').absolute()


class LocalCache:
    def __init__(self, func, dirname=None, auto_invalidate=True) -> None:
        self._func = func
        self._dirname = dirname

        if not self.code_file.exists():
            # function has not been cached before
            self._setup()

        elif self._is_stale and not auto_invalidate:
            # cached calls are no longer valid
            self.reset()

    @property
    def code_file(self):
        return self._cache_dir / 'code.py'

    @property
    def code_i_am_caching(self):
        return inspect.getsource(self._func)

    def _setup(self):
        dir = self._cache_dir
        assert not dir.exists()
        make_dir(dir)

        self.code_file.write_text(self.code_i_am_caching)

    @property
    def _is_stale(self):
        old_code = self.code_file.read_text()
        new_code = self.code_i_am_caching
        return old_code != new_code

    @property
    def _cache_dir(self):
        if self._dirname is not None:
            # directory of currently running script + name
            _dir = RUNNING_PATH / f"{self._dirname}.cache"
        else:
            # get the file that func is defined in
            func_file = Path(inspect.getsourcefile(self._func)).absolute()
            _dir = func_file.with_suffix(".cache")

        return _dir / self._func.__name__

    def reset(self):
        info(f"WARNING: Resetting {self._func.__name__}'s cache.")
        rm_rf(self._cache_dir)
        self._setup()

    def file_path(self, args, kwargs):
        signature = inspect.signature(self._func)
        params = signature.bind(*args, **kwargs)
        params.apply_defaults()

        filename = '_'.join(
            f'{k}={v}' for k, v in params.arguments.items()
        )
        return self._cache_dir / filename

    @classmethod
    def load_from_disk(cls, _file):
        with open(_file, "rb") as file:
            return pickle.load(file)

    @classmethod
    def save_to_disk(cls, obj, _file):
        with open(_file, "wb") as file:
            pickle.dump(obj, file)
