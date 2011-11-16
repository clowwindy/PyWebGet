# _*_ coding:utf-8 -*-

__author__ = 'clowwindy'

import web, taskinfo, threading
DB_NAME = 'db.sqlite3.db'
DB_TYPE = 'sqlite'

CHECK_INTERVAL = 30

STATUS_RUNNING = 1
STATUS_QUITTING = 2

class Controller(object):
    threads = []
    taskinfos = []
    thread_limit = 2
    lock = threading.Lock()
    update_event = threading.Event()
    status = STATUS_RUNNING

    def init(self):
        #第一次启动时运行，将所有downloading修改为inqueue
        db = web.database(dbn=DB_TYPE, db=DB_NAME)
        db.update('Task', where="status = %d" % taskinfo.STATUS_DOWNLOADING, status = "%d" % taskinfo.STATUS_INQUEUE)

    def update_tasks(self):
        
        #获取所有任务
        db = web.database(dbn=DB_TYPE, db=DB_NAME)
        tasks = db.select('Task')
        task_running = len(self.threads)

        for task in tasks:
            if task.status == taskinfo.STATUS_INQUEUE:
                if task_running >= self.thread_limit:
                    break
                self._update_task_status(task,taskinfo.STATUS_DOWNLOADING)
                t = threading.Thread(target=self.run_task,args=(task,))
                self.lock.acquire()
                self.threads.append(t)
                self.lock.release()
                t.start()
                task_running += 1

    def run_task(self, task):
        thread = threading.currentThread()
        self.threads.append(thread)
        try:
            ti = taskinfo.TaskInfo(task)
            ti.oncomplete = self._oncomplete
            ti.onerror = self._onerror
            ti.download()
        finally:
            self.lock.acquire()
            self.threads.remove(thread)
            self.lock.release()

    def run(self):
        while self.status == STATUS_RUNNING:
            self.update_tasks()
            self.update_event.clear()
            self.update_event.wait(CHECK_INTERVAL)

    def stop(self):
        pass
    def add_task(self):
        pass
    def pause_task(self):
        pass
    def remove_task(self):
        pass
    def task_list(self):
        db = web.database(dbn='sqlite', db=DB_NAME)
        tasks = db.select('Task')
        return tasks
        #TODO: 转换成json

    def _update_task_status(self,task,status):
        db = web.database(dbn=DB_TYPE, db=DB_NAME)
        db.update('Task', where="id = %d" % task.id, status = "%d" % status)

    def _onerror(self, task):
        pass
    def _oncomplete(self, task):
        self._update_task_status(task,taskinfo.STATUS_COMPLETED)
        print "complete: "+task.url
        self.update_event.set()
        