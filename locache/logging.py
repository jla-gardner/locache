VERBOSE = False


def verbose(val):
    """
    set the verbosity of the locache module logging
    """
    global VERBOSE
    VERBOSE = val


def info(msg):
    """
    Optionally prints a message
    """

    if VERBOSE:
        print(">> (locache) " + msg)
