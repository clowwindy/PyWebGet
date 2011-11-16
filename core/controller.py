__author__ = 'clowwindy'

import web, taskinfo, threading
DB_NAME = 'db.sqlite3.db'
DB_TYPE = 'sqlite'

class Controller(object):
    threads = []
    taskinfos = []
    thread_limit = 2
    lock = threading.Lock()

    def init(self):
        #第一次启动时运行，将所有downloading修改为inqueue
        db = web.database(dbn=DB_TYPE, db=DB_NAME)
        db.update('Task', where="id = %d" % taskinfo.STATUS_DOWNLOADING, value1 = "%d" % taskinfo.STATUS_INQUEUE)

    def update_tasks(self):
        
        #获取所有任务
        db = web.database(dbn=DB_TYPE, db=DB_NAME)
        tasks = db.select('Task')
        task_running = len(self.threads)

        for task in tasks:
            if task.status == taskinfo.STATUS_INQUEUE:
                if task_running >= len(self.threads):
                    break
                threading.Thread(target=self.run_task,args=(task,)).start()

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

    def _onerror(self, task):
        pass
    def _oncomplete(self, task):
        pass