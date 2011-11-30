__author__ = 'clowwindy'

import argparse, os

parser = argparse.ArgumentParser(usage='%(prog)s [options]')
parser.add_argument('-V', '--version', action='version')
parser.add_argument('-c', '--config-file', metavar="FILE", help='specify config file')
parser.add_argument('-d', '--db-file', metavar="FILE", help='specify database file')

if os.name == 'posix':
    parser.add_argument('-b', '--background', action='store_true', help='go to background after startup')
    parser.add_argument('-s', '--stop', action='store_true', help='stop background daemon')
    parser.add_argument('-r', '--restart', action='store_true', help='restart background daemon')
    parser.add_argument('-p', '--pid-file',  metavar="FILE", type=argparse.FileType('rw'), help='specify PID file')

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
    return args
