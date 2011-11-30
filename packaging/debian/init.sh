#! /bin/sh
# pywebget
# clowwindy

### BEGIN INIT INFO
# Provides:          pywebget
# Required-Start:    $remote_fs
# Required-Stop:     $remote_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: A background HTTP download manager with a web interface
# Description:       A background HTTP download manager with a web interface.
### END INIT INFO

BIN=/usr/bin/pywebget
CONFIG_FILE=/etc/pywebget/settings.json
DB_FILE=/var/lib/pywebget/db.sqlite
PIDFILE=/var/run/pywebget/pywebget.pid
USERNAME=debian-pywebget

BASE_DIR=/opt/pywebget

cd $BASE_DIR

# Carry out specific functions when asked to by the system
case "$1" in
  start)
    $BIN -b -c $CONFIG_FILE -d $DB_FILE -p $PIDFILE -u $USERNAME
    ;;
  stop)
    $BIN -s -p $PIDFILE -u $USERNAME
    ;;
  restart)
    $BIN -r -c $CONFIG_FILE -d $DB_FILE -p $PIDFILE -u $USERNAME
    ;;
  *)
    echo "Usage: /etc/init.d/pywebget {start|stop|restart}"
    exit 1
    ;;
esac

exit 0