__author__ = 'clowwindy'


def timestamp_repr(t):
    import datetime
    try:
        s = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
        return s
    except TypeError:
        return ""