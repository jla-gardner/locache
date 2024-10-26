# `locache` - a local and persistent cache for Python

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/locache)](https://pypi.org/project/locache/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/locache?color=green&label=Downloads&logo=Python&logoColor=white)](https://pypistats.org/packages/locache)
[![GitHub](https://img.shields.io/github/license/jla-gardner/local-cache)](LICENCE.md)
[![](https://github.com/jla-gardner/load-atoms/actions/workflows/tests.yaml/badge.svg?branch=main)](https://github.com/jla-gardner/load-atoms/actions/workflows/tests.yaml)
[![codecov](https://codecov.io/gh/jla-gardner/locache/branch/master/graph/badge.svg?token=VGSFM0GWF1)](https://codecov.io/gh/jla-gardner/locache)
</div>


`locache` is a single-file, 0-dependency utility package for caching the results of deterministic and pure function calls to disk, exposed via the [`@persist`](#persist) decorator.

These caches are:
- **persistent across separate Python sessions**: run the function once to cache the result to disk, and then hit the cache again and again in different runs/notebooks/scripts/sessions
- **aware of the function's source code**: if the function's source code changes, new values will be cached. If you change the source code back, the old values will still be in the cache (useful for using different versions of a function on e.g. different branches)
- **configurable with `max_entries` and `max_age` parameters**: control how many entries to store, and how long to keep them in the cache for.

## Use-case

Have you ever written something like this?

```python
# result = expensive_function(X, y)
result = np.load("cached_result.npy")
```

This is somewhat dangerous: what if you have changed `expensive_function` and forgotten to update the cache? Or accidentally deleted your cache file? Or you have `result = np.load("cached_result-v3-final.npy")`?

`locache.persist` is an easy way to avoid these issues: 
1. wrap `expensive_function` with `@persist`
2. call `expensive_function` as usual
3. `locache` automatically caches the result of `expensive_function` to disk. If the function's source code changes, new values will be cached.


## Installation

`locache` is simple enough that you could have written it yourself. To use it in your project, either:
- copy the [`locache.py`](locache.py) file into your project
- install it with
`pip install locache`

## API

`locache` provides 3 importable functions:
- the `@persist` decorator
- `reset`
- `verbose`

### `@persist` / `@persist(max_entries=-1, max_age=365)`

Wrap a pure function with `@persist` in order to cache its results to disk. The only stipulation is that the function's arguments and return value must be pickle-able.

```python
>>> from locache import persist

>>> @persist
... def my_func(x, num=3):
...     print("Hi from foo!")
...     return x * num

>>> my_func(1) # function behaviour is unchanged       
Hi from foo!
3
>>> my_func(2, num=2) 
Hi from foo!
4
>>> my_func(1)  # cached results are returned
3
```

By default, `@persist` will store up to unlimited entries. Each of these will be removed 365 days after they are last accessed. These parameters can be changed by passing `max_entries` and `max_age` to `@persist`.

### `reset(func: Callable)`

Reset the cache for a given function.

```python
>>> from locache import reset

>>> @persist
... def squared(x):
...     print(f"Squaring {x}")
...     return x * x

>>> squared(2)  # cache miss
Squaring 2
4
>>> squared(2)  # cache hit
4
>>> reset(squared)
>>> squared(2)  # cache miss
Squaring 2
4
```


### `verbose(yes: bool = True)`

Turn on verbose, debug logging.