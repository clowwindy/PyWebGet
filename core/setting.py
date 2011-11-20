__author__ = 'clowwindy'

import codecs, json
from web.utils import Storage

SETTING_FILE = "settings.json"

defaults = Storage({
    "download_path" : ".",
    "buf_size" : 256 * 1024,
    "thread_limit": 2,
    "retry_count":10,
    "need_login":True,
    "username":"pywebget",
    "password":"123456",
})


def load_settings():
    f = None
    try:
        f = codecs.open(SETTING_FILE, encoding = 'utf-8' )
        t = f.read()
        setting = json.loads(t)
        setting = dict(list(defaults.items()) + list(setting.items()))
        return Storage(setting)
    except Exception:
        return defaults
    finally:
        if f:
            f.close()

def save_settings(settings):
    f = None
    try:
        f = codecs.open(SETTING_FILE, encoding = 'utf-8', mode = 'wb')
        t = json.dumps(settings)
        f.write(t)
    finally:
        if f:
            f.close()
