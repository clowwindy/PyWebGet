# -*- coding:utf-8 -*-
import time
import mimetypes
import urllib
import codecs

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

def detect_encoding(input):
    from thr.chardet import universaldetector
    detector = universaldetector.UniversalDetector()
    detector.reset()
    detector.feed(input)
    detector.close()
    if detector.result and detector.result['confidence'] > 0.5:
        return detector.result['encoding']
    return 'utf-8'

def url_decode(input,encoding=None):
    result = urllib.unquote(input.encode('ascii', 'ignore'))
    if not encoding:
        # detect encoding if encoding is not specified
        encoding = detect_encoding(result)
    return codecs.decode(result, encoding, 'ignore')
