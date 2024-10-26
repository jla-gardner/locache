import functools
import shutil
from pathlib import Path

import pytest

from locache import persist, reset, verbose

_cache_root = Path(__file__).with_suffix(".cache")


@pytest.fixture(autouse=True)
def reset_env():
    # before each test is run, we need to
    # delete any previously created cache files
    cache_dir = Path(__file__).with_suffix(".cache")
    shutil.rmtree(cache_dir, ignore_errors=True)
    verbose(False)


def test_default_behaviour():
    num_calls = 0

    @persist
    def squared(a):
        nonlocal num_calls
        num_calls += 1
        return a**2

    assert squared(3) == 9, "function not working"
    assert num_calls == 1, "function has been called once"
    assert _cache_root.exists(), "cache root should exist"
    assert (_cache_root / "squared").exists(), "cache file should exist"
    assert (
        len(list((_cache_root / "squared").glob("*.pkl"))) == 1
    ), "should be one entry"

    assert squared(3) == 9, "function not working"
    assert num_calls == 1, "second call should be cached"

    assert squared(4) == 16, "function not working"
    assert num_calls == 2, "function should be called again"
    assert (
        len(list((_cache_root / "squared").glob("*.pkl"))) == 2
    ), "should be two entries"


def test_configured_behaviour(capsys, caplog):
    @persist(max_entries=1)
    def squared(a):
        print(a)
        return a**2

    # caching a single value should work
    squared(1)
    assert "1" in capsys.readouterr().out, "function should be called"
    squared(1)
    assert capsys.readouterr().out == "", "function should be cached"
    assert (
        len(list((_cache_root / "squared").glob("*.pkl"))) == 1
    ), "should be one entry"

    # hit another value: this should evict the first value
    squared(2)
    assert "2" in capsys.readouterr().out, "function should be called"
    _files = list((_cache_root / "squared").glob("*.pkl"))
    assert len(_files) == 1, f"should be one entry, but found {_files}"

    assert "deleting" in caplog.text, "deletion should be logged"
    caplog.clear()

    # cache miss
    squared(1)
    assert "1" in capsys.readouterr().out, "function should be called"
    _files = list((_cache_root / "squared").glob("*.pkl"))
    assert len(_files) == 1, f"should be one entry, but found {_files}"

    # test age limit
    @persist(max_age=0)
    def cubed(a):
        print(a)
        return a**3

    cubed(1)
    assert "1" in capsys.readouterr().out, "function should be called"
    # should already have been removed due to 0 age
    _files = list((_cache_root / "cubed").glob("*.pkl"))
    assert len(_files) == 0, f"should be no entries, but found {_files}"
    assert "deleting" in caplog.text, "deletion should be logged"


def test_code_redefinition(capsys):
    @persist
    def squared(a):  # type: ignore
        print(a)
        return a**2

    squared(3)
    assert "3" in capsys.readouterr().out, "function should be called"

    # redefine the function
    @persist
    def squared(a):  # type: ignore
        print("different")
        return a**2

    squared(3)
    assert "different" in capsys.readouterr().out, "function should be called"

    # redefine the function again back to the original,
    # using **exactly** the same code
    @persist
    def squared(a):  # type: ignore
        print(a)
        return a**2

    squared(3)
    assert capsys.readouterr().out == "", "this should have been cached"


def test_verbosity(caplog):
    @persist
    def squared(a):
        return a**2

    squared(3)
    assert caplog.text == "", "no logging should happen by default"

    # if we set verbose=True, we should see the cache miss...
    verbose(True)
    squared(2)
    assert "cache miss" in caplog.text, "cache hit should be logged"

    # ...and the cache hit
    squared(3)
    assert "cache hit" in caplog.text, "cache hit should be logged"

    # turning verbose off again
    verbose(False)
    squared(4)
    assert caplog.text.count("cache miss") == 1, "logging should be off again"


def test_reset_behaviour():
    num_calls = 0

    @persist
    def squared(a):
        nonlocal num_calls
        num_calls += 1
        return a**2

    squared(3)
    assert num_calls == 1, "function has been called once"

    squared(3)
    assert num_calls == 1, "second call should be cached"

    squared(4)
    assert num_calls == 2, "function should be called again"

    reset(squared)
    squared(3)
    assert num_calls == 3, "function should be called again"


def test_reset_errors(caplog):
    def foo():
        pass

    reset(foo)
    assert (
        "passed a function that is not decorated at all" in caplog.text
    ), "error should be logged"

    def improper_decorator(func):
        # use a wrapper that doesn't propagate the __wrapped__ attribute
        # due to a lack of @functools.wraps
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @improper_decorator
    @persist
    def bar():
        pass

    caplog.clear()
    reset(bar)
    assert (
        "decorator on top of @persist that does not" in caplog.text
    ), "error should be logged"

    def proper_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    @proper_decorator
    @persist
    def baz():
        pass

    caplog.clear()
    reset(baz)
    assert caplog.text == "", "no error should be logged"


def test_normal_location():
    @persist
    def squared(a):
        return a**2

    squared(3)
    location = Path(__file__).with_suffix(".cache") / "squared"
    assert location.exists(), "cache location should exist"


@pytest.fixture
def in_repl(monkeypatch):
    def mock_getfile(func):
        return "<stdin>"

    monkeypatch.setattr("inspect.getfile", mock_getfile)


def test_in_repl(in_repl, caplog):
    @persist
    def squared(a):
        return a**2

    assert (
        "Unable to find the definition of this function." in caplog.text
    ), "REPL should not be supported"

    # test that we can still use the function
    assert squared(3) == 9, "function not working"


@pytest.fixture
def in_notebook(monkeypatch):
    def mock_getfile(func):
        return "ipykernel"

    monkeypatch.setattr("inspect.getfile", mock_getfile)
    monkeypatch.setattr(
        "inspect.getsource", lambda x: "def squared(a):\n    return a**2"
    )


def test_in_notebook(in_notebook):
    @persist
    def squared(a):
        return a**2

    assert squared(3) == 9, "function not working"
