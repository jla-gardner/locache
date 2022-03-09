from locache import persist

NUM_CALLS = 0


@persist
def foo(x, pow=1):
    NUM_CALLS += 1
    return x ** pow


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
