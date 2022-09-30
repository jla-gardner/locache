from locache import persist, reset, verbose

verbose(True)
NUM_CALLS = 0


@persist
def foo(x, pow=1):
    global NUM_CALLS
    NUM_CALLS += 1
    return x ** pow


def test_foo():
    global NUM_CALLS

    reset(foo)

    foo(1)
    # assert NUM_CALLS == 1

    foo(1)
    # assert NUM_CALLS == 1

    foo(2)
    # assert NUM_CALLS == 2

    foo(1, pow=2)
    # assert NUM_CALLS == 3

    foo(1, pow=2)
    # assert NUM_CALLS == 3


if __name__ == '__main__':
    test_foo()
