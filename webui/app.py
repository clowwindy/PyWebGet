__author__ = 'clowwindy'
import web

class index:
    def GET(self):
        return web.seeother("/static/")

class task_list:
    def GET(self):
        global controller
        import json
        return json.dumps({"aaData":controller.tasks})

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