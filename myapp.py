import web

import threading

urls = (
  '/', 'index'
)

a = {"num":1}

my_lock = threading.Lock()

app = web.application(urls, globals(),autoreload=False)

def my_run():
    import time
    while 1:
        global a, my_lock, app
        time.sleep(1)
        my_lock.acquire()
        a["num"] += 1
        print "a=",a["num"],id(a)
        db = web.database(dbn='sqlite', db='db.sqlite3.db')
        db.insert('users', username="user %d" % a["num"])
        my_lock.release()

#threading.Thread(target=my_run).start()
#threading.Thread(target=my_run).start()
#threading.Thread(target=my_run).start()


class index:
    def GET(self):
        global a, my_lock
        my_lock.acquire()
        a["num"] += 1
        my_lock.release()

#        print "I'm called!"
        db = web.database(dbn='sqlite', db='db.sqlite3.db')
        users = db.select('users')
        r = []
        for user in users:
            r.append(str(user.username))
        print r
        return "a="+str(a["num"])+" "+str(id(a)) + "\n" + ",".join(r)


if __name__ == "__main__": app.run()