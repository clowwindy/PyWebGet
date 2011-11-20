function readablize_bytes(bytes) {
    if(bytes == null || bytes == 0) {
        return "";
    }
    var s = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'DB', 'NB'];
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

function html_encode(value) {
    if(value == null){
        value="";
    }
    return $('<div/>').text(value).html();
}

function time_span_str(milliseconds) {
    if(milliseconds > 0 && milliseconds < Infinity) {
        var ts = new TimeSpan(milliseconds);
        var result = "";
        var start = false;
        var attrs = ['days','hours','minutes','seconds'];
        var display_names = ['d','h','min','s'];
        for(var a in attrs){
            if(ts[attrs[a]] > 0 || start) {
                start = true;
                result += " " + ts[attrs[a]] + display_names[a];
            }
        }
        return result;
    }
    return "";
}