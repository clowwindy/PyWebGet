__author__ = 'clowwindy'

DEBUG = False

import codecs, os
try:
    import json
except ImportError:
    import simplejson as json
from web.utils import Storage
from utils import log

defaults = Storage({
    "port":8090,
    "download_path" : ".",
    "buf_size" : 256 * 1024,
    "thread_limit": 2,
    "retry_limit":100,
    "retry_interval":3,
    "auth_enabled":True,
    "auth_username":"admin",
    "auth_password":"",
    "timeout":30,
})

if os.name == 'posix':
    SETTING_FILE = os.path.expanduser('~/.pywebget/settings.json')
    defaults.download_path = os.path.expanduser('~/Download')
else:
    SETTING_FILE = 'settings.json'

settings_writable = ["download_path", "buf_size", "thread_limit", "retry_limit", "timeout"]

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
        log('settings file is invalid, load default settings')
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

def check_paths():
    if os.name == 'posix':
        if not os.access(os.path.dirname(SETTING_FILE),os.X_OK):
            try:
                os.makedirs(os.path.dirname(SETTING_FILE))
            except Exception:
                log('invalid setting file path')
                import sys
                sys.exit(1)
        import controller
        if not os.access(os.path.dirname(controller.DB_NAME),os.X_OK):
            try:
                os.makedirs(os.path.dirname(controller.DB_NAME))
            except Exception:
                log('invalid database file path')
                import sys
                sys.exit(1)
