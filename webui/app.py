__author__ = 'clowwindy'
import web
from core import task, version
import time
import utils


def common_setup():
    web.header('Server', "%s/%s" % (version.APP_NAME, version.VERSION))

class index:
    def GET(self):
        common_setup()
        return web.seeother("/static/")

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
    )

    my_app = web.application(urls, globals(),autoreload=False)
    my_app.run()