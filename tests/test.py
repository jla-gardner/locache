import functools

from locache import persist, reset_cache, verbose
from locache.util import get_source_code_for

verbose(True)
NUM_CALLS = 0


def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@persist
def foo(x, pow=1):
    global NUM_CALLS
    NUM_CALLS += 1
    return x**pow


def test_foo():
    global NUM_CALLS
    reset_cache(foo)

    foo(1)
    assert NUM_CALLS == 1

    foo(1)
    assert NUM_CALLS == 1

    foo(2)
    assert NUM_CALLS == 2

    foo(1, pow=2)
    assert NUM_CALLS == 3

    foo(1, pow=2)
    assert NUM_CALLS == 3


def test_code_inspection():
    @persist
    def foo():
        pass

    code = get_source_code_for(foo)
    assert code == "def foo():\n    pass\n"

    @persist(name="foo")
    def foo():
        pass

    code = get_source_code_for(foo)
    assert code == "def foo():\n    pass\n"

    def get_name():
        return "hi"

    @persist(name=get_name())
    def foo():
        pass

    code = get_source_code_for(foo)
    assert code == "def foo():\n    pass\n"

    @persist
    @decorator
    def foo():
        pass

    code = get_source_code_for(foo)
    assert code == "@decorator\ndef foo():\n    pass\n"

    @decorator
    @persist
    def foo():
        pass

    code = get_source_code_for(foo)
    assert code == "def foo():\n    pass\n"


def test():
    @persist(name="testing")
    def bar(a, b):
        return a + b

    assert bar(1, 2) == 3


if __name__ == "__main__":
    test_foo()
    test_code_inspection()
    test()
