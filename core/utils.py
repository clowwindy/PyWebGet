# -*- coding:utf-8 -*-
import time

__author__ = 'clowwindy'

def log(s):
    print "[%s] %s" % (timestamp_repr(time.time()), s)

def timestamp_repr(t):
    import datetime
    try:
        s = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
        return s
    except TypeError:
        return ""