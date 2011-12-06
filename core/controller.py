# -*- coding:utf-8 -*-

__author__ = 'clowwindy'

import web, task, threading, types, time, urllib, os
from utils import log, guess_extension_from_mime_type, url_decode
import setting, wget_parser

if os.name == 'posix':
    DB_NAME = os.path.expanduser('~/.pywebget/db.sqlite')
else:
    DB_NAME = 'db.sqlite'

DB_TYPE = 'sqlite'

EMPTY_DB = "../share/empty.db"

CHECK_INTERVAL = 300

TASK_STOP_TIMEOUT = 5

STATUS_RUNNING = 1
STATUS_STOPPING = 2

class Controller(object):
    controller_thread = None
    threads = []
    tasks = []
    tasklist_lock = threading.Lock()
    filename_lock = threading.Lock()
    update_event = threading.Event()
    status = STATUS_RUNNING

    def __init__(self):
        self.settings = setting.load_settings()

    def init(self):
        #检查db是否存在，如不存在复制一个
        if not os.access(DB_NAME, os.W_OK):
            if setting.DEBUG:
                log('creating new db file')
            src = os.path.join(os.path.dirname(__file__), EMPTY_DB)
            import shutil
            shutil.copy(src, DB_NAME)
            os.chmod(DB_NAME,0660)

        #第一次启动时运行，将所有downloading修改为inqueue
        db = self._db()
        db.update('Task', where="status = %d" % task.STATUS_DOWNLOADING, status = "%d" % task.STATUS_QUEUED)
        self._close_db(db)
 
    def update_tasks(self):
        #获取所有任务
        db = self._db()
        tasks = db.select('Task')
        task_running = len(self.threads)

        for a_task in tasks:
            if a_task.status == task.STATUS_QUEUED:
                if task_running >= self.settings.thread_limit:
                    if setting.DEBUG:
                        log("over limit")
                    break
                a_task.status = task.STATUS_DOWNLOADING
                self._update_task_status(db, task.STATUS_DOWNLOADING, a_task)
                t = threading.Thread(target=self.run_task,args=(a_task,),name='task')
#                t.setDaemon(True)
                self.tasklist_lock.acquire()
                self.threads.append(t)
                self.tasklist_lock.release()
                t.start()
                task_running += 1
        self._close_db(db)

    def run_task(self, a_task):
        if setting.DEBUG:
            log("download thread started")
        thread = threading.currentThread()
        ti = None
        try:
            ti = task.Task(a_task)
            self.tasks.append(ti)
            ti.thread = thread
            ti.retry_limit = self.settings.retry_limit
            ti.download_path = self.settings.download_path
            ti.timeout = self.settings.timeout
            ti.retry_limit = self.settings.retry_limit
            ti.retry_interval = self.settings.retry_interval
            ti.oncomplete = self._oncomplete
            ti.onerror = self._onerror
            ti.onupdating_total_size = self._onupdating_total_size
            ti.onupdating_filename = self._onupdating_filename
            ti.onstatus_change = self._onstatus_change
            ti.download()
        finally:
            self.tasklist_lock.acquire()
            if ti:
                self.tasks.remove(ti)
            self.threads.remove(thread)
            self.tasklist_lock.release()
            if setting.DEBUG:
                log("download thread stopped")

    def run(self):
        self.controller_thread = threading.currentThread()
        self.status = STATUS_RUNNING
        while self.status == STATUS_RUNNING:
            self.update_tasks()
            self.update_event.clear()
            self.update_event.wait(CHECK_INTERVAL)
        if setting.DEBUG:
            log('controller stopped')

    def stop(self):
        if setting.DEBUG:
            log('controller stopping')
        if self.status == STATUS_RUNNING:
            self.status = STATUS_STOPPING
            setting.save_settings(self.settings)
        for a_task in list(self.tasks):
            if setting.DEBUG:
                log('pausing task ' + a_task.url)
            self.pause_task(a_task, dontsave=True)
        self.update_event.set()
        self.controller_thread.join()

    def reload(self):
        #TODO: 更新具体的设置
        self.update_event.set()

    def add_task(self, url, cookie="", referer = "", filename=None, set_update_event = True):
        import re
        if url.startswith('wget'):
            (url, cookie, referer, filename) = wget_parser.parse_args(url)
        if url.startswith('mkdir'):
            return
        if re.match(r"[^:]+://[^/]+/?([^?#]*)",url):
            db = self._db()
            if not filename:
                filename=self._get_filename_by_url(url)
            db.insert('Task', url=url,
                      cookie=cookie,
                      referer=referer,
                      filename=filename,
                      date_created=time.time())
            if set_update_event:
                self.update_event.set()
            self._close_db(db)
            log("add task: "+url)
        else:
            log("add task: URL is not valid:: "+url)
            raise AssertionError("URL is not valid: " + url)

    def pause_task(self, a_task, dontsave=False):
        task_id = a_task
        if not type(a_task) is types.IntType:
            task_id = a_task.id
        db = self._db()
        status = self._get_task_status(db, task_id)
        if status == task.STATUS_DOWNLOADING or status == task.STATUS_QUEUED:
            if not dontsave:
                self._update_task_status(db, task.STATUS_PAUSED, task_id)
            for a_task_1 in self.tasks:
                if task_id == a_task_1.id:
                    a_task_1.task.status = task.STATUS_PAUSED
                    a_task_1.event.set()
                    db.update('Task', where="id = %d" % task_id, completed_size = "%d" % a_task_1.completed_size)
                    a_task_1.thread.join(timeout=TASK_STOP_TIMEOUT)
        self._close_db(db)
                
    def resume_task(self, a_task, set_update_event = True):
        task_id = a_task
        if not type(a_task) is types.IntType:
            task_id = a_task.id
        db = self._db()
        status = self._get_task_status(db, task_id)
        if status == task.STATUS_PAUSED or status == task.STATUS_FAILED:
            self._update_task_status(db, task.STATUS_QUEUED, task_id)
            # 不改变内存中任务的状态，注释掉
#            for a_task_1 in self.tasks:
#                if task_id == a_task_1.id:
#                    a_task_1.task.status = task.STATUS_QUEUED
            if set_update_event:
                self.update_event.set()
        self._close_db(db)

    def remove_task(self, a_task):
        task_id = a_task
        if not type(a_task) is types.IntType:
            task_id = a_task.id
        db = self._db()
        status = self._get_task_status(db, task_id)
        self._update_task_status(db, task.STATUS_DELETED, task_id)
        if status == task.STATUS_DOWNLOADING:
            # 如果正在下载，通知下载线程停止下载，并删除
            for a_task_1 in self.tasks:
                if task_id == a_task_1.id:
                    a_task_1.task.status = task.STATUS_DELETED
        else:
            # 直接删除
            db.delete('Task',  where="id = %d" % task_id)
            log("deleted: " + str(task_id))
        self._close_db(db)

    def add_tasks(self, urls,cookie="",referer=""):
        invalid_urls = 0
        try:
            for a_url in urls:
                try:
                    self.add_task(a_url,cookie=cookie,referer=referer,set_update_event=False)
                except AssertionError:
                    invalid_urls += 1
        finally:
            #if an error is raised when one of the urls is valid, set event before leaving
            self.update_event.set()
        if invalid_urls > 0:
            raise AssertionError("%d URLs are invalid" % invalid_urls)

    def pause_tasks(self, tasks):
        for a_task in tasks:
            self.pause_task(a_task)

    def resume_tasks(self, tasks):
        for a_task in tasks:
            self.resume_task(a_task,set_update_event=False)
        self.update_event.set()

    def remove_tasks(self, tasks):
        for a_task in tasks:
            self.remove_task(a_task)
    
    def task_list(self):
        db = self._db()
        tasks = db.select('Task', where="status <> %d" % task.STATUS_DELETED).list()
        self._close_db(db)
        #合并速度和进度信息
        for a_task in tasks:
            found = False
            if a_task.status == task.STATUS_DOWNLOADING:
                for a_task_2 in self.tasks:
                    if a_task.id == a_task_2.id:
                        a_task.completed_size = a_task_2.completed_size
                        a_task.filename = a_task_2.filename
                        found = True
                        break
            if not found:
                a_task.speed = ""
        return tasks
    
    def _db(self):
#        try:
#            if threading.currentThread().__getattribute__('ctl_db'):
#                return threading.currentThread().__getattribute__('ctl_db')
#        except AttributeError:
#            db = web.database(dbn='sqlite', db=DB_NAME)
#            threading.currentThread().__setattr__('ctl_db',db)
#            return db
        return web.database(dbn='sqlite', db=DB_NAME)

    def _close_db(self,db):
#        try:
#            if threading.currentThread().__getattribute__('ctl_db'):
#                threading.currentThread().__getattribute__('ctl_db').ctx.get('db').close()
#                threading.currentThread().__delattr__('ctl_db')
#        except AttributeError:
#            pass
        db.ctx.get('db').close()

    def _update_task_status(self, db, status, a_task):
        task_id = a_task
        if not type(a_task) is types.IntType:
            task_id = a_task.id
        db.update('Task', where="id = %d" % task_id, status = "%d" % status)

    def _get_task_status(self, db, a_task):
        task_id = a_task
        if not type(a_task) is types.IntType:
            task_id = a_task.id
        return db.select('Task', where="id = %d" % task_id)[0].status

    def _onerror(self, a_task, error_code):
        db = self._db()
        self._update_task_status(db, task.STATUS_FAILED, a_task)
        db.update('Task', where="id = %d" % a_task.id, completed_size = "%d" % a_task.completed_size, filename=a_task.filename)
        self._close_db(db)
        log("error %s: %s" % (error_code, a_task.url))

    def _onstatus_change(self, a_task):
        if a_task.status == task.STATUS_DELETED:
            log("deleted: "+a_task.url)
            db = self._db()
            db.delete('Task',  where="id = %d" % a_task.id)
            self._close_db(db)
        else:
            if setting.DEBUG:
                log("status changed: "+a_task.url + " " + str(a_task.status))
            db = self._db()
            db.update('Task', where="id = %d" % a_task.id, completed_size = "%d" % a_task.completed_size, filename=a_task.filename)
            self._close_db(db)


    def _onupdating_total_size(self, a_task):
        db = self._db()
        db.update('Task', where="id = %d" % a_task.id, total_size = "%d" % a_task.total_size, filename=a_task.filename)
        self._close_db(db)
#        db.ctx.get('db').close()

    def _onupdating_filename(self, a_task, filename, mime_type=None):
        self.filename_lock.acquire()
        download_path = self.settings.download_path
        # guess content-type if there is no content-disposition and there is no extension in the filename
        if mime_type:
            fileext = os.path.splitext(filename)
            if not fileext[1]:
                ext = guess_extension_from_mime_type(mime_type)
                if ext:
                    filename += ext
        try:
            i = -1
            while True:
                # check if file exists. if exists, append (n) to filename
                i += 1
                if i > 0:
                    fileext = os.path.splitext(filename)
                    filename_to_test = "%s (%d)%s" % (fileext[0], i, fileext[1])
                else:
                    filename_to_test = filename
                # filename not in download path
                if os.path.exists(os.path.join(download_path, filename_to_test)):
                    continue
                # partfilename not in download path
                partfilename_to_test = os.path.join(download_path, filename_to_test + ".part")
                if os.path.exists(partfilename_to_test):
                    continue
                # filename or partfilenaem not in database
                db = self._db()
                results = db.query("SELECT count(*) as count FROM Task WHERE id <> $id and (filename=$filename or partfilename=$partfilename) and status <> $completed and status <> $deleted",
                    vars={'id':a_task.id, 'filename':filename_to_test, 'partfilename':partfilename_to_test, 'completed':task.STATUS_COMPLETED,'deleted':task.STATUS_DELETED})
                if int(results[0]['count']) > 0:
                    self._close_db(db)
                    continue
                a_task.task.filename = filename_to_test
                a_task.task.partfilename = partfilename_to_test
                db.update('Task', where="id=%d" % a_task.id, filename = filename_to_test, partfilename = partfilename_to_test)
                self._close_db(db)
                break
        finally:
            self.filename_lock.release()
        
    def _oncomplete(self, a_task):
        db = self._db()
        self._update_task_status(db, task.STATUS_COMPLETED, a_task)
        db.update('Task', where="id = %d" % a_task.id, date_completed = "%d" % time.time(),completed_size = "%d" % a_task.completed_size, total_size = "%d" % a_task.total_size, filename=a_task.filename)
        log("complete: "+a_task.url)
        self._close_db(db)
        # rename filename
        self.filename_lock.acquire()
        try:
            os.rename(a_task.partfilename, os.path.join(self.settings.download_path, a_task.filename))
        finally:
            self.filename_lock.release()
        self.update_event.set()

    def _get_filename_by_url(self, url):
        try:
            import re
            result = re.match(r"[^:]+://[^/]+/?([^?#]*)",url).groups()[0]
            result = result.split('/')[-1]
            if result:
                return url_decode(result)
            else:
                return "download"
        except Exception:
            return "download"