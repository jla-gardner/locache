VERBOSE = False


def verbose(val):
    global VERBOSE
    VERBOSE = val


def info(msg):
    '''Optionally prints a message'''
    if VERBOSE:
        print(">> (locache) " + msg)
