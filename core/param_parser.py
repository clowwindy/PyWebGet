__author__ = 'clowwindy'

import argparse

parser = argparse.ArgumentParser(usage='%(prog)s [options]')
parser.add_argument('-V', '--version', action='version')
parser.add_argument('-c', '--config-file', metavar="FILE", help='specify config file')
parser.add_argument('-d', '--db-file', metavar="FILE", help='specify database file')
parser.add_argument('-b', '--background', action='store_true', help='go to background after startup')
parser.add_argument('-p', '--pid-file',  metavar="FILE", type=argparse.FileType('rw'), help='specify PID file')

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

    print args
