function readablize_bytes(bytes) {
    var s = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'DB', 'NB'];
    var e = Math.floor(Math.log(bytes)/Math.log(1024));
    return (bytes/Math.pow(1024, Math.floor(e))).toFixed(2)+" "+s[e];
}


function timestamp_repr(t) {
    if(t == 0) {
        return "";
    }
    var d = new Date(t * 1000);
    return d.toString('yyyy-MM-dd HH:mm:ss');
}