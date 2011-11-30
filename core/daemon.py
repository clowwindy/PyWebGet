__author__ = 'clowwindy'

DEFAULT_PID_FILE = '/tmp/pywebget.pid'

import os, errno, signal, sys
from core.utils import log

# http://stackoverflow.com/questions/568271/check-if-pid-is-not-in-use-in-python
def pid_exists(pid):
    """Check whether pid exists in the current process table."""
    if pid < 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError, e:
        return e.errno == errno.EPERM
    else:
        return True

def get_pid(pidfile):
    f = None
    try:
        f = open(pidfile, 'r')
        pid = f.read()
        return int(pid)
    except IOError:
#        log("can't read pid file")
        return 0
    finally:
        if f:
            f.close()

def set_pid(pidfile):
    f = None
    try:
        f = open(pidfile, 'w')
        f.write(str(os.getpid()))
        os.chmod(pidfile, 0600)
    except IOError:
        log("can't write pid file")
    finally:
        if f:
            f.close()

def start(pidfile,username=None):
    log("starting daemon")
    if pidfile is None:
        pidfile = DEFAULT_PID_FILE
    pid = get_pid(pidfile)
    if pid != 0 and pid_exists(pid):
        log("daemon pid %d is already running" % pid)
        sys.exit(0)
    pid = os.fork()
    if pid:
        log("daemon pid %d started" % pid)
        sys.exit(0)
    else:
        try:
            sys.stdout = open("/dev/null", "w+")
        except Exception:
            pass
        set_pid(pidfile)
        os.setsid()
        if username:
            import pwd
            try:
                uid = pwd.getpwnam(username)[2]
                os.setuid(uid)
            except KeyError:
                log("can't find user")
                sys.exit(1)


def stop(pidfile, exit=True):
    log("stopping daemon")
    result = True
    if pidfile is None:
        pidfile = DEFAULT_PID_FILE
    pid = get_pid(pidfile)
    if pid != 0:
        try:
            os.kill(pid, signal.SIGINT)
            os.remove(pidfile)
            import time
            for i in xrange(0,10):
                time.sleep(0.5)
                if not pid_exists(pid):
                    break
            if pid_exists(pid):
                log("failed to stop timeout")
            else:
                log("daemon pid %d stopped" % pid)
        except OSError:
            log("failed to stop daemon")
    else:
        log("can't find daemon pid file")
    if exit:
        sys.exit(0)
    else:
        return result

def restart(pidfile,username=None):
    if pidfile is None:
        pidfile = DEFAULT_PID_FILE
    if stop(pidfile, False):
        start(pidfile,username)
