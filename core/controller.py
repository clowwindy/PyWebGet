# -*- coding:utf-8 -*-

__author__ = 'clowwindy'

import web, task, threading, types, time, urllib
from utils import log
import setting
DB_NAME = 'db.sqlite3.db'
DB_TYPE = 'sqlite'

CHECK_INTERVAL = 300

STATUS_RUNNING = 1
STATUS_STOPPING = 2

class Controller(object):
    threads = []
    tasks = []
    thread_limit = 2
    lock = threading.Lock()
    update_event = threading.Event()
    status = STATUS_RUNNING

    def __init__(self):
        self.settings = setting.load_settings()
        self.thread_limit = self.settings.thread_limit

    def init(self):
        #第一次启动时运行，将所有downloading修改为inqueue
        db = self._db()
        db.update('Task', where="status = %d" % task.STATUS_DOWNLOADING, status = "%d" % task.STATUS_QUEUED)
 
    def update_tasks(self):
        #获取所有任务
        db = self._db()
        tasks = db.select('Task')
        task_running = len(self.threads)

        for a_task in tasks:
            if a_task.status == task.STATUS_QUEUED:
                if task_running >= self.thread_limit:
                    log("over limit")
                    break
                a_task.status = task.STATUS_DOWNLOADING
                self._update_task_status(db, task.STATUS_DOWNLOADING, a_task)
                t = threading.Thread(target=self.run_task,args=(a_task,))
                self.lock.acquire()
                self.threads.append(t)
                self.lock.release()
                t.start()
                task_running += 1

    def run_task(self, a_task):
        thread = threading.currentThread()
        ti = None
        try:
            ti = task.Task(a_task)
            self.tasks.append(ti)
            ti.retry_limit = self.settings.retry_limit
            ti.download_path = self.settings.download_path
            ti.oncomplete = self._oncomplete
            ti.onerror = self._onerror
            ti.onupdating_total_size = self._onupdating_total_size
            ti.onstatus_change = self._onstatus_change
            ti.download()
        finally:
            self.lock.acquire()
            if ti:
                self.tasks.remove(ti)
            self.threads.remove(thread)
            self.lock.release()

    def run(self):
        self.status = STATUS_RUNNING
        while self.status == STATUS_RUNNING:
            self.update_tasks()
            self.update_event.clear()
            self.update_event.wait(CHECK_INTERVAL)

    def stop(self):
        if self.status == STATUS_RUNNING:
            self.status = STATUS_STOPPING
            setting.save_settings(self.settings)
        self.update_event.set()

    def reload(self):
        #TODO: 更新具体的设置
        self.update_event.set()

    def add_task(self, url, cookie="", referrer = ""):
        import re
        if re.match(r"[^:]+://[^/]+/?([^?#]*)",url):
            db = self._db()
            db.insert('Task', url=url,
                      cookie=cookie,
                      referrer=referrer,
                      filename=self._get_filename_by_url(url),
                      date_created=time.time())
            self.update_event.set()
            log("add task: "+url)
        else:
            log("add task: URL is not valid:: "+url)
            raise AssertionError("URL is not valid: " + url)

    def pause_task(self, a_task):
        task_id = a_task
        if not type(a_task) is types.IntType:
            task_id = a_task.id
        db = self._db()
        status = self._get_task_status(db, task_id)
        if status == task.STATUS_DOWNLOADING or status == task.STATUS_QUEUED:
            self._update_task_status(db, task.STATUS_PAUSED, task_id)
            for a_task_1 in self.tasks:
                if task_id == a_task_1.id:
                    a_task_1.task.status = task.STATUS_PAUSED
                    db.update('Task', where="id = %d" % task_id, completed_size = "%d" % a_task_1.completed_size)
                
    def resume_task(self, a_task, set_update_event = True):
        task_id = a_task
        if not type(a_task) is types.IntType:
            task_id = a_task.id
        db = self._db()
        status = self._get_task_status(db, task_id)
        if status == task.STATUS_PAUSED:
            self._update_task_status(db, task.STATUS_QUEUED, task_id)
            # 不改变内存中任务的状态，注释掉
#            for a_task_1 in self.tasks:
#                if task_id == a_task_1.id:
#                    a_task_1.task.status = task.STATUS_QUEUED
            if set_update_event:
                self.update_event.set()

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
        #合并速度和进度信息
        for a_task in tasks:
            found = False
            if a_task.status == task.STATUS_DOWNLOADING:
                for a_task_2 in self.tasks:
                    if a_task.id == a_task_2.id:
                        a_task.completed_size = a_task_2.completed_size
                        a_task.speed = a_task_2.speed
                        a_task.filename = a_task_2.filename
                        found = True
                        break
            if not found:
                a_task.speed = ""
        return tasks
    
    def _db(self):
        return web.database(dbn='sqlite', db=DB_NAME)

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
        db.update('Task', where="id = %d" % a_task.id, completed_size = "%d" % a_task.completed_size, filename=a_task.filename)
        log("error %s: %s" % (error_code, a_task.url))

    def _onstatus_change(self, a_task):
        if a_task.status == task.STATUS_DELETED:
            db = self._db()
            db.delete('Task',  where="id = %d" % a_task.id)
        else:
            db = self._db()
            db.update('Task', where="id = %d" % a_task.id, completed_size = "%d" % a_task.completed_size, filename=a_task.filename)


    def _onupdating_total_size(self, a_task):
        db = self._db()
        db.update('Task', where="id = %d" % a_task.id, total_size = "%d" % a_task.total_size, filename=a_task.filename)

        
    def _oncomplete(self, a_task):
        db = self._db()
        self._update_task_status(db, task.STATUS_COMPLETED, a_task)
        db.update('Task', where="id = %d" % a_task.id, date_completed = "%d" % time.time(),completed_size = "%d" % a_task.completed_size, filename=a_task.filename)
        log("complete: "+a_task.url)
        self.update_event.set()


    def _get_filename_by_url(self, url):
        try:
            import re
            result = re.match(r"[^:]+://[^/]+/?([^?#]*)",url).groups()[0]
            result = result.split('/')[-1]
            if result:
                return urllib.unquote(result)
            else:
                return "download"
        except Exception:
            return "download"