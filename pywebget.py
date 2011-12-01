#!/usr/bin/env python

import threading
import signal, os, sys
from core.controller import Controller
import core.utils
import core.version
import core.param_parser
from core import daemon

print core.version.DESCRIPTION

args = core.param_parser.parse_args()
if args.verbose:
    import core.setting
    core.setting.DEBUG = True

if os.name == 'posix':
    if args.background:
        daemon.start(args.pid_file, args.user)
    if args.stop:
        daemon.stop(args.pid_file)
    if args.restart:
        daemon.restart(args.pid_file, args.user)

core.setting.check_paths()

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