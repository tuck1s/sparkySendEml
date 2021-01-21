import sys, os

def eprint(*args, **kwargs):
    """
    Print to stderr - see https://stackoverflow.com/a/14981125/8545455
    """
    print(*args, file=sys.stderr, **kwargs)


def strip_end(h, s):
    """
    If string h ends with s, strip it off; return the result
    """
    if h.endswith(s):
        h = h[:-len(s)]
    return h


def strip_start(h, s):
    """
    If string h starts with s, strip it off; return the result
    """
    if h.startswith(s):
        h = h[len(s):]
    return h


def host_cleanup(host):
    """
    Condense URL into a standard form
    """
    if not host.startswith('https://'):
        host = 'https://' + host  # Add schema
    host = strip_end(host, '/')
    host = strip_end(host, '/api/v1')
    host = strip_end(host, '/')
    return host


def getenv_check(e):
    """
    Check environment variable is defined, and return the result
    """
    res = os.getenv(e)
    if res == None:
        print(e, 'environment variable not set - stopping.')
        exit(1)
    else:
        return res


def getenv(*args, **kwargs):
    """
    Get environment variable
    """
    return os.getenv(*args, **kwargs)


def xstr(s):
    """
    Return s as a string, mapping None value to an empty string
    """
    return str(s) if s else ''