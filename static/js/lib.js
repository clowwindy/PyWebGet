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

$.alert=function(msg, title, callback){
    $("#alert-message").text(msg);
    $("#dialog-alert").dialog({
        title: title,
        modal:true,
        show: dialog_effect,
        hide: dialog_effect,
        resizable: false,
        buttons: { "Ok": function() {
                if(callback)callback();
                $(this).dialog("close");
            }
        }
    });
};

$.confirm=function(msg, title, ok_callback, cancel_callback){
    $("#alert-message").text(msg);
    $("#dialog-alert").dialog({
        title: title,
        modal:true,
        show: dialog_effect,
        hide: dialog_effect,
        resizable: false,
        buttons: { "Ok": function() {
                if(ok_callback)ok_callback();
                $(this).dialog("close");
            },
            "Cancel": function() {
                if(cancel_callback)cancel_callback();
                $(this).dialog("close");
            }
        }
    });
};