# -*- coding:utf-8 -*-

import socket
import os, urllib2
import threading
import httplib
import urlparse
import setting
from utils import log, url_decode

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
ERROR_FILE_SIZE_LARGER_THAN_CONTENT_LENGTH = 2

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
    onupdating_filename = None
    # input: task, filename(without dir) output: None. change task.filename and task.partfilename

    event = threading.Event()

    def __getattr__(self, key):
        try:
            return self.task[key]
        except KeyError, k:
            raise AttributeError, k

    def __init__(self, task):
        self.task = task

    def _filename_from_content_disposition(self, content_disposition):
        # rfc2183
        disposition = content_disposition.split(';')
        for i in xrange(1, len(disposition)):
            disposition_parm = disposition[i].split('=')
            if len(disposition_parm) > 1 and disposition_parm[0].strip() == 'filename':
                filename = url_decode(disposition_parm[1].strip('"'))
                if len(filename) > 0:
                    return filename
                else:
                    break
        return None

    def _mime_type_fron_content_type(self, content_type):
        #rfc2616
        if content_type:
            return content_type.split(';')[0]
        return None

    def download(self):
        # handle errors, and retry
        is_continue_downloading = False
        url = self.task.url
        while self.task.status == STATUS_DOWNLOADING:
            self.retry_count += 1
            f = None
            netfile = None
            try:
                cur_length = 0

                log("download %s, try %d" % (url, self.retry_count))

                if not os.access(self.download_path, os.X_OK):
                    os.makedirs(self.download_path)

                partfilename = None
                if self.task.partfilename:
                    partfilename = os.path.join(self.download_path, self.task.partfilename)
                    if os.access(partfilename, os.W_OK):
                        is_continue_downloading = True

                    #                filename = os.path.join(self.download_path, self.task.filename)
                if is_continue_downloading:
                    if os.path.exists(partfilename):
                        cur_length = os.path.getsize(partfilename)

                request = urllib2.Request(url)

                if cur_length > 0:
                    range = "bytes=%d-" % (cur_length,)
                    request.add_header("Range", range)

                cookie = self.task.cookie
                if cookie is not None and cookie != "":
                    request.add_header("Cookie", cookie)

                referer = self.task.referer
                if referer is not None and referer != "":
                    request.add_header("Referer", referer)

                opener = urllib2.build_opener()
                netfile = opener.open(request, timeout=self.timeout)
                headers = netfile.headers.dict

                should_append = False
                if netfile.code == 200:
                    should_append = False
                elif netfile.code == 206:
                    should_append = True
                elif netfile.code == 301 or netfile.code == 302:
                    url = urlparse.urljoin(url, headers["location"])
                    if setting.DEBUG:
                        log("HTTP 301: " + url)
                    raise httplib.HTTPException(str(netfile.code))
                elif netfile.code == 416:
                    #TODO range错误，重下
                    raise httplib.HTTPException()
                else:
                    #TODO 处理其他情况
                    raise httplib.HTTPException()
                if headers.has_key('content-length'):
                    self.task.total_size = int(headers['content-length']) + self.task.completed_size
                    if self.onupdating_total_size:
                        self.onupdating_total_size(self)
                if not is_continue_downloading:
                    filename = self.task.filename
                    # 处理content-disposition Header，更新文件名
                    content_type = None
                    if headers.has_key('content-disposition'):
                        filename_from_content_disposition = self._filename_from_content_disposition(headers['content-disposition'])
                        if filename_from_content_disposition:
                            filename = filename_from_content_disposition
                    elif headers.has_key('content-type'):
                        # guess extension by content-type only when there is no content-disposition header
                        content_type = headers['content-type']
                    # 检查文件是否已经存在，如果存在，后面添加序号
                    if self.onupdating_filename:
                        self.onupdating_filename(self, filename, self._mime_type_fron_content_type(content_type))
                        partfilename = self.task.partfilename
                    else:
                        partfilename = self.task.filename + ".part"
                        self.task.partfilename = partfilename

                if should_append:
                    self.task.completed_size = cur_length
                    f = open(partfilename, 'ab', BUF_SIZE)
                else:
                    cur_length = self.task.completed_size = 0
                    f = open(partfilename, 'wb', BUF_SIZE)

                if os.name == "posix":
                    os.chmod(partfilename,0666)

                data = netfile.read(CHUNK_SIZE)

                self.task.completed_size = cur_length

                # Download
                while data and self.task.status == STATUS_DOWNLOADING:
                    self.task.completed_size += len(data)
                    f.write(data)
                    data = netfile.read(CHUNK_SIZE)
                f.flush()
                f.close()
                netfile.close()
                complete = True

                # check status

                if self.task.status == STATUS_PAUSED or self.task.status == STATUS_QUEUED or self.task.status == STATUS_DELETED:
                    if self.onstatus_change:
                        self.onstatus_change(self)
                    complete = False
                else:
                    # check file size
                    if self.task.total_size == 0:
                        # file size unknown
                        self.task.total_size = self.task.completed_size
                    elif self.task.total_size < self.task.completed_size:
                        # this is critical error, do NOT retry
                        if self.onerror:
                            self.onerror(self, ERROR_FILE_SIZE_LARGER_THAN_CONTENT_LENGTH)
                        return
                    elif self.task.total_size > self.task.completed_size:
                        # not complete, retry
                        complete = False
                if complete:
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
