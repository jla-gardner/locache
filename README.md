# locache
[![PyPI](https://img.shields.io/pypi/v/locache?style=for-the-badge)](https://pypi.org/project/locache/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/locache?color=green&label=Downloads&logo=Python&logoColor=white&style=for-the-badge)](https://pypistats.org/packages/locache)
[![GitHub](https://img.shields.io/github/license/jla-gardner/local-cache?style=for-the-badge)](LICENCE.md)

A small utility library for caching the results of deterministic and pure function calls to disk.
This ability is only intended for use on expensive function calls with simple arguments and keyword arguments.
The cache can optionally invalidate itself if changes to the function's source code are detetcted.

## Installation

`pip3 install locache`

## Examples

When used in normal python scripts, `@persist` is sufficient.

`foo.py`:

```python
from locache import persist

@persist
def my_func(x, num=3):
    print("Hi from foo!")
    return x * num

my_func(1)        # prints "Hi from foo!", returns 3
my_func(2, num=2) # prints "Hi from foo!", returns 4
my_func(1)        # returns 3
my_func(2, num=2) # returns 4
```

Running `foo.py` will lead to the creation of a `foo.cache/my_func/` directory, with files `x=1_num=3` and `x=2_num=2`.

### Notebooks

When using python notebooks, the `name` keyword is also required:

`bar.ipynb`:

```python
from locache import persist

@persist(name="notebook")
def my_func(x, num=3):
    print("Hi from foo!")
    return x * num

my_func(1)        # prints "Hi from foo!", returns 3
my_func(1)        # returns 3
```

Running this cell will lead to the creation of a `notebook.cache/my_func/` directory in the same directory as the notebook.

## Resetting the Cache

By default, the cache is invalidated and reset if source code changes to the function in question are dedicated.
This behaviour can be surpressed: `@persist(auto_invalidate=False)`

Results for specific function calls can be removed from the cache by deleting the appropriate file.

Programmatic resetting of the cache is also possible:

```python
from locache import persist, reset_cache

@persist
def foo(x):
    print("Hi from foo!")
    return x ** 2

foo(1) # prints "Hi from foo!", returns 3
foo(1) # returns 3

reset_cache(foo)

foo(1) # prints "Hi from foo!", returns 3
```

In a notebook setting, the relevant name needs to also be passed:

```python
@persist(name="notebook")
def foo(x):
    return x**2

foo(1)
reset_cache(foo, name="notebook")
```

## Logging

Cache logging can optionally be enabled:

```python
from locache import verbose; verbose(True)
```

## Anti-Examples

Don't pass large data structures to persisted functions:

```python
import numpy as np
from locache import persist

@persist # don't do this!
def foo(x):
    return np.sum(x * x)

arr = np.ones(10) + np.randn(10)
foo(arr)
```
