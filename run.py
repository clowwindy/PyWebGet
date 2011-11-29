#!/usr/bin/env python
__author__ = 'clowwindy'


import threading
import signal, os, sys
from core.controller import Controller
import core.utils

def sig_handler(signum, frame):
    from core.utils import log
    log("exiting")
    global controller
    controller.stop()
    webui.app.stop()
    log("exited")
    sys.exit(0)


if os.name == 'posix':
    signal.signal(signal.SIGQUIT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGUSR1, sig_handler)
    signal.signal(signal.SIGUSR2, sig_handler)
elif os.name == 'nt':
    signal.signal(signal.SIGABRT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

controller = Controller()
controller.init()
controller_thread = threading.Thread(target=controller.run, name='controller')
controller_thread.setDaemon(True)
controller_thread.start()

import webui.app
webui.app.set_controller(controller)

core.utils.log("started")


try:
    webui.app.run()
finally:
    # stop controller if webui is stopped
#    controller.stop()
    pass