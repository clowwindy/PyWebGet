# _*_ coding:utf-8 -*-

__author__ = 'clowwindy'
import web
from core import task, version
import time
import utils
import json

def common_setup():
    web.header('Server', "%s/%s" % (version.APP_NAME, version.VERSION))

class index:
    def GET(self):
        common_setup()
        return web.seeother("/static/")
    
class add_task:
    def POST(self):
        global controller
        common_setup()
        try:
            data = json.loads(web.input()['data'])
            #TODO: 支持多个URL
            controller.add_task(data['urls'], data['cookie'], data['referrer'])
            return "'OK'"
        except Exception, e:
            return json.dumps(unicode(e))

class task_list:
    def GET(self):
        global controller
        tasks = controller.task_list()
        for a_task in tasks:
#            a_task.status = task.str_by_status(a_task.status)
#            a_task.checkbox = "<input type='checkbox' id='task_%d' />" % a_task.id
            a_task.percent = "100%"
            a_task.percent = "100%"
#            a_task.date_completed = utils.timestamp_repr(a_task.date_completed)
#            a_task.date_created = utils.timestamp_repr(a_task.date_created)
        import json
        web.header('Content-Type', 'application/x-javascript')
        common_setup()
        return json.dumps({"aaData":tasks})

controller = None

def set_controller(c):
    global controller
    controller = c

def run():
    urls = (
      '/', 'index',
      '/task_list', 'task_list',
      '/add_task', 'add_task',
    )

    my_app = web.application(urls, globals(),autoreload=False)
    my_app.run()