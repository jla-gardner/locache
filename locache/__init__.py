import functools
import os
from os.path import abspath, exists
import inspect
import pickle
from shutil import rmtree as rm_rf

RUNNING_PATH = abspath('.')
VERBOSE = False


def verbose(val):
    global VERBOSE
    VERBOSE = val


def info(msg):
    if VERBOSE:
        print("(local_cache) " + msg)


def uid(func, args, kwargs):
    parts = [func.__name__]
    if args:
        parts.append("_".join(map(str, args)))
    if kwargs:
        parts.append("_".join(f"{k}={v}" for k, v in kwargs.items()))
    return "__".join(parts)


def get_cache_dir(func, name):
    if name is not None:
        # directory of currently running script + name
        _dir = RUNNING_PATH + f"/{name}.cache"
    else:
        # get the file that func is defined in
        func_file = abspath(inspect.getfile(func))
        _dir = func_file + ".cache"

    os.makedirs(_dir, exist_ok=True)
    return _dir


def persist(_func=None, *, name=None):
    def persist_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _id = uid(func, args, kwargs)
            _dir = get_cache_dir(func, name)
            _file = _dir + "/" + _id

            if exists(_file):
                info(f"Using cached result for {func.__name__}")
                return load_from_disk(_file)

            info(f"Caching result for {func.__name__} in {_file}")
            out = func(*args, **kwargs)
            save_to_disk(out, _file)
            return out

        return wrapper

    if _func == None:  # called as @persist(name=...)
        return persist_decorator

    else:  # called as @persist def foo(): ...
        return persist_decorator(_func)


def reset(func, name=None):
    info(f"WARNING: Resetting {func.__name__}'s cache.")
    _dir = get_cache_dir(func, name)
    rm_rf(_dir)


def load_from_disk(_file):
    with open(_file, "rb") as file:
        return pickle.load(file)


def save_to_disk(obj, _file):
    with open(_file, "wb") as file:
        pickle.dump(obj, file)
