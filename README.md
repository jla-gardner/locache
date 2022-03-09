# locache

A small util library for caching the results of function calls to disk.

Only intended for expensive function calls with simple arguments and keyword arguments.

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

Running `foo.py` will lead to the creation of a `foo.py.cache/` directory, with files `my_func__1__num=3` and `my_func__2__num=2`.

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

Running this cell will lead to the creation of a `notebook.cache/` directory in the same directory as the notebook.

### Resetting the Cache

Resetting the cache can be achieved in two ways:

-   manually deleting the relevant cache files / directories.
-   using `locache.reset`

```python
from locache import persist, reset

@persist
def foo(x):
    print("hello from foo")
    return x ** 2

foo(1) # prints "Hi from foo!", returns 3
foo(1) # returns 3

reset(foo)

foo(1) # prints "Hi from foo!", returns 3
```

In a notebook setting, the relevant name needs to also be passed:

```python
@persist(name="notebook")
def foo(x):
    return x**2

foo(1)
reset(foo, name="notebook")
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
