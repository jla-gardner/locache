# `locache` - a local cache for Python

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/locache)](https://pypi.org/project/locache/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/locache?color=green&label=Downloads&logo=Python&logoColor=white)](https://pypistats.org/packages/locache)
[![GitHub](https://img.shields.io/github/license/jla-gardner/local-cache)](LICENCE.md)
[![](https://github.com/jla-gardner/load-atoms/actions/workflows/tests.yaml/badge.svg?branch=main)](https://github.com/jla-gardner/load-atoms/actions/workflows/tests.yaml)
[![codecov](https://codecov.io/gh/jla-gardner/locache/branch/master/graph/badge.svg?token=VGSFM0GWF1)](https://codecov.io/gh/jla-gardner/locache)
</div>


A single-file utility library for caching the results of deterministic and pure function calls to disk, exposed via the [`@persist`](#persist) decorator.

These caches are persistent across runs of the program. If changes to the function's source code are detected, the cache is reset. This can also be manually performed with the `reset` function.

## Installation

`locache` is simple enough that you could have written it yourself. To use it in your project, either:
- copy the [`locache.py`](locache.py) file into your project
- install it with
`pip install locache`

## Usage

`locache` provides 3 importable functions:
- the `@persist` decorator
- `reset`
- `verbose`

### `@persist`

Wrap a pure function with `@persist` to cache its results to disk. The only stipulation is that the function's arguments and return value must be pickle-able.

```python
from locache import persist

@persist
def my_func(x, num=3):
    print("Hi from foo!")
    return x * num

my_func(1)        
# prints "Hi from foo!", returns 3
my_func(2, num=2) 
# prints "Hi from foo!", returns 4
my_func(1)        
# returns 3
```

### `reset(func: Callable)`

Reset the cache for a given function.

```python
from locache import reset

reset(my_func)
my_func(1) # prints "Hi from foo!", returns 3
```


### `verbose(yes: bool = True)`

Turn on verbose logging.

```python
from locache import verbose

reset(my_func)
verbose(yes=True)

my_func(1) 
# prints "cache miss for squared(1)"
# prints "Hi from foo!"
# returns 3

my_func(1)
# prints "cache hit for squared(1)"
# returns 3
```