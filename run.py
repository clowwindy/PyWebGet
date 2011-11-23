__author__ = 'clowwindy'


import threading
import signal, os
from core.controller import Controller
import core.utils

def sig_handler(signum, frame):
    from core.utils import log
    log("exiting")
    global controller
    controller.stop()
    webui.app.stop()


if os.name == 'posix':
    signal.signal(signal.SIGABRT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
elif os.name == 'nt':
    signal.signal(signal.SIGABRT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

controller = Controller()
controller.init()
controller_thread = threading.Thread(target=controller.run)
controller_thread.start()

import webui.app
webui.app.set_controller(controller)

core.utils.log("started")

webui.app.run()