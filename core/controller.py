# _*_ coding:utf-8 -*-

__author__ = 'clowwindy'

import web, task, threading
from utils import log
DB_NAME = 'db.sqlite3.db'
DB_TYPE = 'sqlite'

CHECK_INTERVAL = 30

STATUS_RUNNING = 1
STATUS_STOPPING = 2

class Controller(object):
    threads = []
    tasks = []
    thread_limit = 2
    lock = threading.Lock()
    update_event = threading.Event()
    status = STATUS_RUNNING

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
        try:
            ti = task.Task(a_task)
            self.tasks.append(a_task)
            ti.oncomplete = self._oncomplete
            ti.onerror = self._onerror
            ti.download()
        finally:
            self.lock.acquire()
            self.tasks.remove(a_task)
            self.threads.remove(thread)
            self.lock.release()

    def run(self):
        self.status = STATUS_RUNNING
        while self.status == STATUS_RUNNING:
            self.update_tasks()
            self.update_event.clear()
            self.update_event.wait(CHECK_INTERVAL)

    def stop(self):
        self.status = STATUS_STOPPING
        self.update_event.set()
        
    def add_task(self, url, cookie="", referrer = ""):
        db = self._db()
        db.insert('Task', url=url, cookie=cookie, referrer=referrer)
        self.update_event.set()

    def pause_task(self, a_task=None, task_id=None):
        if a_task is None and task_id is None:
            raise Exception("task or task_id must be set!")
        if task_id is None:
            task_id = a_task.id
        db = self._db()
        self._update_task_status(db, task.STATUS_PAUSED, task_id=task_id)
        for a_task_1 in self.tasks:
            if task_id == a_task_1.id:
                a_task_1.status = task.STATUS_PAUSED
                
    
    def remove_task(self):
        pass
    
    def task_list(self):
        db = self._db()
        tasks = db.select('Task').list()
        #合并速度和进度信息
        for a_task in tasks:
            found = False
            if a_task.status == task.STATUS_DOWNLOADING:
                for a_task_2 in self.tasks:
                    if a_task.id == a_task_2.id:
                        a_task.completed_size = a_task_2.completed_size
                        a_task.speed = a_task_2.speed
                        found = True
                        break
            if not found:
                a_task.speed = ""
        return tasks
    
    def _db(self):
        return web.database(dbn='sqlite', db=DB_NAME)

    def _update_task_status(self, db, status, a_task=None, task_id=None):
        if a_task is None and task_id is None:
            raise Exception("task or task_id must be set!")
        if task_id is None:
            task_id = a_task.id
        db.update('Task', where="id = %d" % task_id, status = "%d" % status)

    def _onerror(self, a_task):
        #TODO将下载进度等状态保存到数据库
        pass
    def _oncomplete(self, a_task):
        db = self._db()
        self._update_task_status(db, task.STATUS_COMPLETED, a_task)
        import time
        #TODO将下载进度等状态保存到数据库
        db.update('Task', where="id = %d" % a_task.id, date_complete = "%d" % time.time())
        log("complete: "+a_task.url)
        self.update_event.set()
        