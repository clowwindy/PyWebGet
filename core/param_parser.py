__author__ = 'clowwindy'

import os
from thr import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-V', '--version', action='version')
parser.add_argument('-c', '--config-file', metavar="FILE", help='specify config file')
parser.add_argument('-d', '--db-file', metavar="FILE", help='specify database file')
parser.add_argument('-l', '--log-file', metavar="FILE", help='specify log file')

if os.name == 'posix':
    daemon_group = parser.add_argument_group('Daemon options')
    daemon_group.add_argument('-b', '--background', action='store_true', help='go to background after startup')
    daemon_group.add_argument('-s', '--stop', action='store_true', help='stop background daemon')
    daemon_group.add_argument('-r', '--restart', action='store_true', help='restart background daemon')
    daemon_group.add_argument('-p', '--pid-file',  metavar="FILE", help='specify PID file')
    daemon_group.add_argument('-u', '--user',  metavar="USERNAME", help='specify username to run as')

parser.add_argument('-v', '--verbose', action='store_true', help='print debug info')

args = None
def parse_args():
    global args
    args = parser.parse_args()

    if args.config_file:
        import setting
        setting.SETTING_FILE = args.config_file
    if args.db_file:
        import controller
        controller.DB_NAME = args.db_file
    if args.log_file:
        import controller
        controller.LOG_FILE = args.log_file

    if os.name == 'posix':
        if [args.background, args.stop, args.restart].count(True) > 1:
            parser.error("argument -b, -s, -r must be used seperately")
            import sys
            sys.exit(1)
    return args
