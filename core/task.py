# -*- coding:utf-8 -*-

__author__ = 'clowwindy'

BUF_SIZE = 256 * 1024
CHUNK_SIZE = 4096

STATUS_QUEUED = 0
STATUS_DOWNLOADING = 1
STATUS_PAUSED = 2
STATUS_COMPLETED = 3
STATUS_DELETED = 128

ERROR_UNKNOWN = 0

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
    speed = 0
    retry_count = 0
    download_path = "."
    task = None

    onerror = None
    oncomplete = None
    onstatus_change = None
    onupdating_total_size = None

    def __getattr__(self, key):
        try:
            return self.task[key]
        except KeyError, k:
            raise AttributeError, k

    def __init__(self, task):
        self.task = task

    def download(self):
        f = None
        netfile = None
        try:
            import os, sys, urllib2
            cur_length = 0
            url = self.task.url
                
            filename = self.download_path + "/" +self.task.filename
            if os.path.exists(filename):
                cur_length = os.path.getsize(filename)

            range = "bytes=%d-"%(cur_length,)

            request = urllib2.Request(url)
            request.add_header("Range", range)
            opener = urllib2.build_opener()
            netfile = opener.open(request)
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

        except Exception:
            import traceback
            traceback.print_exc()
            if self.onerror:
                self.onerror(self, ERROR_UNKNOWN)
        finally:
            if f:
                f.close()
            if netfile:
                netfile.close()
