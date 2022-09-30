import functools
import inspect
from shutil import rmtree as rm_rf

from locache.LocalCache import LocalCache

VERBOSE = False
def verbose(val):
    global VERBOSE
    VERBOSE = val


def info(msg):
    '''Optionally prints a message'''
    if VERBOSE:
        print(">> (locache) " + msg)


def persist(_func=None, *, name=None):
    '''
    decorator that caches the return value of a function to 
    permanent memory for a given set of args and kwargs
    '''

    def persist_decorator(func):
        cache = LocalCache(func, name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _file = cache.file_path(func, args, kwargs)

            if _file.exists():  # cache hit: load from disk
                info(f"Using cached result for {func.__name__}")
                out = LocalCache.load_from_disk(_file)
            
            else: # cache miss: call func and save to disk
                info(f"Caching result for {func.__name__} in {_file}")
                out = func(*args, **kwargs)
                LocalCache.save_to_disk(out, _file)
            
            return out

        return wrapper

    if _func == None:  # called as @persist(name=...)
        return persist_decorator
    else:              # called as @persist
        return persist_decorator(_func)


def reset(func, name=None):

    # remove @persist wrapper
    cache = LocalCache(inspect.unwrap(func), name)
    
    info(f"WARNING: Resetting {func.__name__}'s cache.")
    rm_rf(cache._cache_dir)


