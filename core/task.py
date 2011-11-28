# -*- coding:utf-8 -*-

import socket
import os, urllib2
import threading
from utils import log

__author__ = 'clowwindy'

BUF_SIZE = 256 * 1024
CHUNK_SIZE = 4096

STATUS_QUEUED = 0
STATUS_DOWNLOADING = 1
STATUS_PAUSED = 2
STATUS_COMPLETED = 3
STATUS_FAILED = 16
STATUS_DELETED = 128

ERROR_UNKNOWN = 0
ERROR_TIMEOUT = 1

def str_by_status(status):
    if status == STATUS_QUEUED:
        return "Queued"
    elif status == STATUS_DOWNLOADING:
        return "Downloading"
    elif status == STATUS_PAUSED:
        return "Paused"
    elif status == STATUS_COMPLETED:
        return "Completed"

class Task(object):
    task_id = -1
    retry_count = 0
    download_path = "."
    task = None
    timeout = 30
    retry_interval = 3

    onerror = None
    oncomplete = None
    onstatus_change = None
    onupdating_total_size = None
    event = threading.Event()

    def __getattr__(self, key):
        try:
            return self.task[key]
        except KeyError, k:
            raise AttributeError, k

    def __init__(self, task):
        self.task = task

    def download(self):
        # handle errors, and retry
        while self.task.status == STATUS_DOWNLOADING:
            self.retry_count += 1
            f = None
            netfile = None
            try:
                cur_length = 0
                url = self.task.url

                log("download %s, try %d" % (url, self.retry_count))

                filename = self.download_path + "/" +self.task.filename
                if os.path.exists(filename):
                    cur_length = os.path.getsize(filename)

                range = "bytes=%d-"%(cur_length,)

                request = urllib2.Request(url)
                request.add_header("Range", range)
                opener = urllib2.build_opener()
                netfile = opener.open(request, timeout = self.timeout)
                headers = netfile.headers.dict

                if netfile.code == 200:
                    cur_length = self.task.completed_size = 0
                    f = open(filename,'wb',BUF_SIZE)
                elif netfile.code == 206:
                    self.task.completed_size = cur_length
                    f = open(filename,'ab',BUF_SIZE)
                else:
                    #TODO 处理301等情况
                    raise
                if headers.has_key('content-length'):
                    self.task.total_size = int(headers['content-length']) + self.task.completed_size
                    if self.onupdating_total_size:
                        self.onupdating_total_size(self)

                data = netfile.read(CHUNK_SIZE)

                self.task.completed_size = cur_length

                # TODO 处理content-disposition Header，更新文件名

                # Download
                while data and self.task.status == STATUS_DOWNLOADING:
                    self.task.completed_size += len(data)
                    f.write(data)
                    data = netfile.read(CHUNK_SIZE)
                f.flush()

                if self.task.status == STATUS_PAUSED or self.task.status == STATUS_QUEUED or self.task.status == STATUS_DELETED:
                    if self.onstatus_change:
                        self.onstatus_change(self)
                else:
                    if self.oncomplete:
                        self.oncomplete(self)
                return
            except socket.timeout:
                import traceback
                traceback.print_exc()

                if self.retry_count > self.retry_limit:
                    if self.onerror:
                        self.onerror(self, ERROR_TIMEOUT)
                    return
            except Exception:
                import traceback
                traceback.print_exc()

                if self.retry_count > self.retry_limit:
                    if self.onerror:
                        self.onerror(self, ERROR_UNKNOWN)
                    return
            finally:
                if f:
                    f.close()
                if netfile:
                    netfile.close()
            if self.status == STATUS_DOWNLOADING:
                log("failed, wait %d seconds for retrying: %s" % (self.retry_interval, self.task.url))
                self.event.clear()
                self.event.wait(self.retry_interval)
            else:
                break
        if self.onstatus_change:
            self.onstatus_change(self)
