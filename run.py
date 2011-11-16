__author__ = 'clowwindy'


import threading
from core.controller import Controller


#db = web.database(dbn='sqlite', db='db.sqlite3.db')
##db.insert('Task', url="http://mplayerx.googlecode.com/files/MPlayerX_1.0.9.zip")
#
#tasks = db.select('Task',where="id=1")
#taskinfo = TaskInfo(tasks[0])
#taskinfo.download()

controller = Controller()
controller.init()
controller_thread = threading.Thread(target=controller.run)
controller_thread.start()

import webui.app

webui.app.run()