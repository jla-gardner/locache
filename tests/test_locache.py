from pathlib import Path

from locache import persist, verbose


def test_cache_behaviour(tmp_path):
    num_calls = 0

    @persist(root=tmp_path)
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


def test_verbosity(caplog, tmp_path):
    @persist(root=tmp_path)
    def squared(a):
        return a**2

    squared(3)
    assert caplog.text == "", "no logging should happen by default"

    # if the function changes, and we are resetting the cache
    # this should be logged no matter what
    @persist(root=tmp_path)
    def squared(a):
        a += 1
        return a**2

    squared(3)
    assert "Resetting cache" in caplog.text, "resetting cache should be logged"

    # if we set verbose=True, we should see the cache miss...
    verbose(True)
    squared(2)
    assert "Cache miss" in caplog.text, "cache hit should be logged"

    # ...and the cache hit
    squared(3)
    assert "Cache hit" in caplog.text, "cache hit should be logged"

    # turning verbose off again
    verbose(False)
    squared(4)
    assert caplog.text.count("Cache miss"), "logging should be off again"


def test_repr(tmp_path):
    @persist(root=tmp_path)
    def squared(a):
        return a**2

    assert "cache for squared with 0 entries" in repr(squared)

    squared(3)
    assert "cache for squared with 1 entries" in repr(squared)


def test_locations(tmp_path):
    # default location:
    @persist
    def squared(a):
        return a**2

    expected_loc = Path(__file__).with_suffix(".cache") / "squared"
    assert squared.backend.location.resolve() == expected_loc.resolve()

    # custom location:
    @persist(root=tmp_path)
    def cubed(a):
        return a**3

    expected_loc = tmp_path.with_suffix(".cache") / "cubed"
    assert cubed.backend.location.resolve() == expected_loc.resolve()
