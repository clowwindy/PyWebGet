# -*- coding:utf-8 -*-

__author__ = 'clowwindy'
import web
from core import task, version
try:
    import json
except ImportError:
    import simplejson as json
import re
import base64
from core.setting import hash_password, settings_writable

def common_setup():
    web.header('Server', "%s/%s" % (version.APP_NAME, version.VERSION))
    # for quick shutdown
    web.header('Connection', "Close")
    global controller
    if controller.settings.auth_enabled:
        auth = web.ctx.env.get('HTTP_AUTHORIZATION')
        authreq = False
        if auth is None:
            authreq = True
        else:
            auth = re.sub('^Basic ', '', auth)
            username, password = base64.decodestring(auth).split(':')
            if username == controller.settings.auth_username and hash_password(password) == controller.settings.auth_password:
                return
            else:
                authreq = True
        if authreq:
            web.header('WWW-Authenticate', 'Basic realm="PyWebGet"')
            web.ctx.status = '401 Unauthorized'
            raise web.Unauthorized()

class index:
    def GET(self):
        common_setup()
        return web.seeother("/static/")


class add_task:
    def POST(self):
        global controller
        common_setup()
        web.header('Content-Type', 'application/json')
        try:
            data = json.loads(web.data())
            #TODO: 支持多个URL
            controller.add_task(data['urls'], data['cookie'], data['referrer'])
            return '"OK"'
        except Exception, e:
            return json.dumps(unicode(e))


class pause_tasks:
    def POST(self):
        global controller
        common_setup()
        web.header('Content-Type', 'application/json')
        try:
            data = json.loads(web.data())
            controller.pause_tasks(data)
            return '"OK"'
        except Exception, e:
            return json.dumps(unicode(e))


class resume_tasks:
    def POST(self):
        global controller
        common_setup()
        web.header('Content-Type', 'application/json')
        try:
            data = json.loads(web.data())
            controller.resume_tasks(data)
            return '"OK"'
        except Exception, e:
            return json.dumps(unicode(e))


class remove_tasks:
    def POST(self):
        global controller
        common_setup()
        web.header('Content-Type', 'application/json')
        try:
            data = json.loads(web.data())
            controller.remove_tasks(data)
            return '"OK"'
        except Exception, e:
            return json.dumps(unicode(e))

def _get_task_list():
    global controller
    tasks = controller.task_list()
    return tasks

class task_list:
    def GET(self):
#        for a_task in tasks:
        #            a_task.status = task.str_by_status(a_task.status)
        #            a_task.checkbox = "<input type='checkbox' id='task_%d' />" % a_task.id
        #            a_task.date_completed = utils.timestamp_repr(a_task.date_completed)
        #            a_task.date_created = utils.timestamp_repr(a_task.date_created)

        web.header('Content-Type', 'application/json')
        common_setup()
        return json.dumps( _get_task_list())

class stop_server:
    def GET(self):
        common_setup()
        global application
        application.stop()
        return "stopped"

def _get_preferences():
    global controller
    result = {}
    for s in settings_writable:
        result[s] = controller.settings[s]
    return result

class preferences:
    def GET(self):
        common_setup()
        web.header('Content-Type', 'application/json')
        return json.dumps(_get_preferences())

class save_preferences:
    def POST(self):
        global controller
        common_setup()
        web.header('Content-Type', 'application/json')
        try:
            data = json.loads(web.data())
            for s in settings_writable:
                controller.settings[s] = data[s]
            controller.reload()
            return '"OK"'
        except Exception, e:
            return json.dumps(unicode(e))

class all_data:
    def GET(self):
        common_setup()
        web.header('Content-Type', 'application/json')
        return json.dumps({'tasks':_get_task_list(),
                           'preferences':_get_preferences()})

controller = None
application = None

def set_controller(c):
    global controller
    controller = c


def run():
    urls = (
        '/', 'index',
        '/task_list', 'task_list',
        '/add_task', 'add_task',
        '/pause_tasks', 'pause_tasks',
        '/resume_tasks', 'resume_tasks',
        '/remove_tasks', 'remove_tasks',
        '/stop_server', 'stop_server',
        '/preferences', 'preferences',
        '/save_preferences', 'save_preferences',
        '/all_data', 'all_data',
        )
    global application
    application = web.application(urls, globals(), autoreload=False)
    application.run()

def stop():
    global application
    application.stop()