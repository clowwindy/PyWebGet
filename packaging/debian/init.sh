#! /bin/sh
# pywebget
# clowwindy

### BEGIN INIT INFO
# Provides:          pywebget
# Required-Start:    $local_fs $remote_fs $network
# Required-Stop:     $local_fs $remote_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: A background HTTP download manager with a web interface
### END INIT INFO

Name=pywebget
BIN=/usr/bin/pywebget
CONFIG_FILE=/etc/pywebget/settings.json
DB_FILE=/var/lib/pywebget/db.sqlite
LOG_FILE=/var/log/pywebget.log
PIDFILE=/var/run/pywebget.pid
USERNAME=debian-pywebget
OPTIONS="-c $CONFIG_FILE -d $DB_FILE"

BASE_DIR=/opt/pywebget

cd $BASE_DIR

[ -x $DAEMON ] || exit 0

. /lib/lsb/init-functions

case "$1" in
    start)
        log_daemon_msg "Starting pywebget daemon" "$NAME"
	$BIN -b -c $CONFIG_FILE -d $DB_FILE -p $PIDFILE -l $LOG_FILE -u $USERNAME >/dev/null
        log_end_msg $?
        ;;
    stop)
        log_daemon_msg "Stopping pywebget daemon" "$NAME"
        $BIN -s -p $PIDFILE -l $LOG_FILE -u $USERNAME >/dev/null
        log_end_msg $?
        ;;
    restart)
        log_daemon_msg "Restarting pywebget daemon" "$NAME"
	$BIN -r -c $CONFIG_FILE -d $DB_FILE -p $PIDFILE -l $LOG_FILE -u $USERNAME >/dev/null
        log_end_msg $?
        ;;
    *)
        echo "Usage: /etc/init.d/$NAME {start|stop|restart}"
        exit 2
        ;;
esac

exit 0

