# -*- coding:utf-8 -*-
import time
import mimetypes
import urllib
import codecs

LOG_FORMAT = '%(asctime)-15s %(levelname)s %(message)s'

import logging, controller

def init_log(username=None):
    filename = controller.LOG_FILE
    logging.basicConfig(filename=filename, level=logging.INFO, format=LOG_FORMAT)
    import os
    if not os.access(filename, os.W_OK):
        try:
            open(filename, 'w').close()
            if username:
                import pwd
                uid = pwd.getpwnam(username)[2]
                os.chown(filename, uid, -1)
        except (IOError, OSError):
            import sys
            print >> sys.stderr, 'Warning: Could not create log file %s' % filename


def close_log():
    logging.shutdown()

def log(msg, level=logging.INFO):
    logging.log(level, msg)
#    print "[%s] %s" % (timestamp_repr(time.time()), s)


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
    if input.find('%') >= 0:
        result = urllib.unquote(input.encode('ascii', 'ignore'))
    else:
        result = input
    if not encoding:
        # detect encoding if encoding is not specified
        encoding = detect_encoding(result)
    return codecs.decode(result, encoding, 'ignore')
