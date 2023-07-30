import shutil
from pathlib import Path

import pytest

from locache import persist, reset, verbose


@pytest.fixture(autouse=True)
def reset_env():
    # before each test is run, we need to
    # delete any previously created cache files
    cache_dir = Path(__file__).with_suffix(".cache")
    shutil.rmtree(cache_dir, ignore_errors=True)
    verbose(False)


def test_cache_behaviour():
    num_calls = 0

    @persist
    def squared(a):
        nonlocal num_calls
        num_calls += 1
        return a**2

    assert squared(3) == 9, "function not working"
    assert num_calls == 1, "function has been called once"

    assert squared(3) == 9, "function not working"
    assert num_calls == 1, "second call should be cached"

    assert squared(4) == 16, "function not working"
    assert num_calls == 2, "function should be called again"


def test_verbosity(caplog):
    @persist
    def squared(a):
        return a**2

    squared(3)
    assert caplog.text == "", "no logging should happen by default"

    # if the function changes, and we are resetting the cache
    # this should be logged no matter what
    @persist
    def squared(a):
        a += 1
        return a**2

    squared(3)
    assert (
        "detected a change" in caplog.text
    ), "resetting cache should be logged"

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


def test_reset():
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


def test_normal_location():
    @persist
    def squared(a):
        return a**2

    squared(3)
    location = Path(__file__).with_suffix(".cache") / "squared"
    assert location.exists(), "cache location should exist"
    assert (location / ".code.py").exists(), "code file should exist"


def test_no_change():
    num_calls = 0

    @persist
    def squared(a):
        nonlocal num_calls
        num_calls += 1
        return a**2

    squared(3)

    @persist
    def squared(a):
        nonlocal num_calls
        num_calls += 1
        return a**2

    squared(3)
    assert num_calls == 1, "function should not be called again"
