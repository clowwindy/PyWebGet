# -*- coding:utf-8 -*-
import time
import mimetypes

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

# mimetypes.guess_extension won't return the most commonly used extension; it returns the FIRST extension matches.
_common_mime_types = {
    "application/octet-stream": "",
    "text/plain": ".txt",
    "image/jpeg": ".jpg",
    "video/mpeg": ".mpeg",
    }

def guess_extension_from_mime_type(mime_type):
    if mime_type:
        if _common_mime_types.has_key(mime_type):
            return _common_mime_types[mime_type]
        return mimetypes.guess_extension(mime_type)
    return None
