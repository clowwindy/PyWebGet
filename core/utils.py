# _*_ coding:utf-8 -*-
import time

__author__ = 'clowwindy'

def log(s):
    print "[%s]%s" % (time.asctime(time.localtime()), s)