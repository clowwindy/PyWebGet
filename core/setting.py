__author__ = 'clowwindy'

import codecs
try:
    import json
except ImportError:
    import simplejson as json
from web.utils import Storage

SETTING_FILE = "settings.json"

defaults = Storage({
    "download_path" : ".",
    "buf_size" : 256 * 1024,
    "thread_limit": 2,
    "retry_limit":10,
    "auth_enabled":True,
    "auth_username":"admin",
    "auth_password":"",
})

settings_writable = ["download_path", "buf_size", "thread_limit", "retry_limit"]

def hash_password(pwd):
    import hashlib
    s = hashlib.sha256()
    s.update('b94ec72932d881c1f45fcd7789f427482784a61e')
    s.update(pwd)
    return "{%s}" % s.hexdigest()

def load_settings():
    f = None
    setting = None
    try:
        f = codecs.open(SETTING_FILE, encoding = 'utf-8' )
        t = f.read()
        setting = json.loads(t)
        setting = Storage(dict(list(defaults.items()) + list(setting.items())))
    except Exception:
        from utils import log
        log('settings.json is corrupt, load default settings')
        setting = Storage(defaults)
    finally:
        if f:
            f.close()
    if not (len(setting.auth_password) > 0 and setting.auth_password[0] == '{'):
        setting.auth_password = hash_password(setting.auth_password)
    return setting

def save_settings(settings):
    f = None
    try:
        f = codecs.open(SETTING_FILE, encoding = 'utf-8', mode = 'wb')
        t = json.dumps(settings, indent=4,sort_keys=True)
        f.write(t)
    finally:
        if f:
            f.close()
