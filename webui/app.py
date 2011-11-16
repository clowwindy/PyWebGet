__author__ = 'clowwindy'
import web

class index:
    def GET(self):
        return web.seeother("/static/")

def run():
    urls = (
      '/', 'index'
    )

    my_app = web.application(urls, globals(),autoreload=False)
    my_app.run()