from locache import persist


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
