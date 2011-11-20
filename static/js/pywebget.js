var RELOAD_INTERVAL = 3000;

var STATUS_QUEUED = 0;
var STATUS_DOWNLOADING = 1;
var STATUS_PAUSED = 2;
var STATUS_COMPLETED = 3;

var strings = {
    "Add Task":"Add Task"
};
var _s = strings;
var data = {tasks:[]};
var columns = [
    { "mDataProp": "checkbox" },
    { "mDataProp": "status" },
    { "mDataProp": "filename" },
    { "mDataProp": "dir" },
    { "mDataProp": "total_size" },
    { "mDataProp": "percent" },
    { "mDataProp": "speed" },
    { "mDataProp": "eta" },
    { "mDataProp": "completed_size" },
    { "mDataProp": "date_created" },
    { "mDataProp": "date_completed" }
];

jQuery.fn.dataTableExt.aTypes.push(
    function (sData) {
        return 'html';
    }
);

function str_by_status(status) {
    if (status == STATUS_QUEUED)
        return "Queued";
    else if (status == STATUS_DOWNLOADING)
        return "Downloading";
    else if (status == STATUS_PAUSED)
        return "Paused";
    else if (status == STATUS_COMPLETED)
        return "Completed";
    else
        return "";
}

function init_table() {
    window.oTable = $('#download_list_table').dataTable({
//        "bProcessing": true,
//        "bDestroy": true,
//        "sAjaxSource": "/task_list",
        "sScrollY": 400,
        "bJQueryUI": true,
        "sPaginationType": "full_numbers",
        "bAutoWidth": true,
        "bStateSave": false,
        "oLanguage": {
            "sEmptyTable": "Click Add button to add tasks."
        },
        "aLengthMenu": [
            [25, 50, 100, -1],
            [25, 50, 100, "All"]
        ],
        "aoColumns": columns
    });
}

function reload_data() {
    $.ajax('/task_list', {
        dataType:"json",
        success:function(data) {
            window.old_data = window.data;
            window.data = data;
            reload_table();
        }
    })
}

function callback_on_complement(array1, array2, callback) {
    // find what does array1 have but array2 haven't
    outer:
        for (var i in array1) {
            var id = array1[i].id;
            for (var j in array2) {
                if (id == array2[j].id) {
                    continue outer;
                }
            }
            callback(id, array1[i]);
        }
}

function callback_on_intersection(array1, array2, callback) {
    // find what do array1 and array2 both have
    for (var i in array1) {
        var id = array1[i].id;
        for (var j in array2) {
            if (id == array2[j].id) {
                callback(id, array1[i], array2[j]);
            }
        }
    }
}

function find_table_row_by_id(id) {
    var data = oTable.fnGetData();
    var i = 0;
    for (var row in data) {
        if (+data[row].id == id) {
            return i;
        }
        i++;
    }
    return -1;
}

function render_row(row) {
    // calculate speed
    var speed = 0, speed_str = "", eta = 0;
    if (row.status == STATUS_DOWNLOADING && window.old_data) {
        var cur_date = new Date();
        var interval = RELOAD_INTERVAL;
        if (window['last_check_date']) {
            interval = cur_date - window.last_check_date;
            window.last_check_date = cur_date;
        }
        for (var i in old_data.tasks) {
            var old_row = old_data.tasks[i];
            if (old_row.id == row.id) {
                var dif = row.completed_size - old_row.completed_size;
                speed = Math.max(Math.floor(dif / interval * 1000), 0);
                eta = (row.total_size - row.completed_size) / speed * 1000;
                if (speed > 0 && speed != Infinity) {
                    speed_str = readablize_bytes(speed) + "/s";
                } else {
                    speed_str = "";
                }
                break;
            }
        }
    }
    eta = time_span_str(eta);
    var percent = Math.floor(row.completed_size / row.total_size * 100);
    if (row.completed_size > 0 && percent >= 0 && percent != Infinity) {
        percent += "%";
    } else {
        percent = "";
    }
    return {
        id:row.id,
        checkbox:"<input type='checkbox' class='taskid_checkbox' taskid='" + row.id + "' />",
        status:str_by_status(row.status),
        filename:html_encode(row.filename),
        dir:html_encode(row.dir),
        total_size:readablize_bytes(row.total_size),
        percent:percent,
        completed_size:readablize_bytes(row.completed_size),
        date_created:timestamp_repr(row.date_created),
        date_completed:timestamp_repr(row.date_completed),
        speed:speed_str,
        eta:eta
    };
}

function get_col_index_by_name(name) {
    for (var i in columns) {
        if (columns[i]["mDataProp"] == name) {
            return i;
        }
    }
    return -1;
}

function reload_table() {
    //和旧数据对比，看看哪些少了，删除
    callback_on_complement(old_data.tasks, data.tasks, function(id) {
        oTable.fnDeleteRow(find_table_row_by_id(id));
    });
    //看看哪些多了，増行
    callback_on_complement(data.tasks, old_data.tasks, function(id, row) {
        oTable.fnAddData(render_row(row));
    });
    //更新相同的数据对应的行里的状态、下载进度、速度信息
    var all_same = true;
    callback_on_intersection(data.tasks, old_data.tasks, function(id, row, row2) {
        // optimize by updating rows changed only
        var same = true;
        for (var i in row) {
            if (row[i] != row2[i]) {
                same = false;
                break;
            }
        }
        if (same && row2.status != STATUS_DOWNLOADING ) return;
        all_same = false;
        var rendered_row = render_row(row);
        var index = find_table_row_by_id(id);
        oTable.fnUpdate(rendered_row.status, index, get_col_index_by_name('status'), false, false);
        oTable.fnUpdate(rendered_row.completed_size, index, get_col_index_by_name('completed_size'), false, false);
        oTable.fnUpdate(rendered_row.total_size, index, get_col_index_by_name('total_size'), false, false);
        oTable.fnUpdate(rendered_row.percent, index, get_col_index_by_name('percent'), false, false);
        oTable.fnUpdate(rendered_row.date_completed, index, get_col_index_by_name('date_completed'), false, false);
        oTable.fnUpdate(rendered_row.speed, index, get_col_index_by_name('speed'), false, false);
        oTable.fnUpdate(rendered_row.eta, index, get_col_index_by_name('eta'), false, false);
    });
    // optimize by redrawing table only once
    if(!all_same) oTable.fnDraw();
}

$(function() {
    init_table();
    reload_data();
    $(".button").button();
    set_table_size();
    $("#add").click(function() {
        $("#add_task").dialog({
            title: _s["Add Task"],
            modal:true,
            minHeight:286,
            minWidth:390,
            buttons: { "Ok": function() {
                add_task();
                $(this).dialog("close");
            },
                "Cancel": function() {
                    $(this).dialog("close");
                }
            }
        });
        $("#add_task").dialog({
            resize: function(event, ui) {
                //TODO: resize textarea
            }
        });
    });
    $("#pause").click(pause_tasks);
    $("#resume").click(resume_tasks);
    $("#remove").click(remove_tasks);
    setInterval(reload_data, RELOAD_INTERVAL);
});

function set_table_size() {
    var table_body_height = window.innerHeight - ($("#toolbar").outerHeight() +
        $($("#download_list_table_wrapper>.ui-toolbar")[0]).outerHeight() +
        $($("#download_list_table_wrapper>.ui-toolbar")[1]).outerHeight() +
        $(".dataTables_scrollHead").outerHeight());
    table_body_height = table_body_height < 0 ? 0 : table_body_height;
    $(".dataTables_scrollBody").css("height",
        table_body_height + "px"
    );
    oTable.fnAdjustColumnSizing();
}

$(window).resize(function() {
    set_table_size();
});

function add_task() {
    var data = JSON.stringify({
        "urls":$("#urls").val(),
        "cookie":$("#cookie").val(),
        "referrer":$("#referrer").val()
    });
    $.ajax("/add_task", {
        data: data,
        type: "POST",
        dataType: "json",
        success: function(d) {
            if (d != 'OK') {
                alert(d);
            } else {
                reload_data();
            }
        }
    });
}
function selected_ids() {
    var ids = [];
    $(".taskid_checkbox:checked").each(function() {
        ids.push(+this.getAttribute('taskid'));
    });
    return ids;
}

function perform_ajax_on_selection(url) {
    var data = JSON.stringify(selected_ids());
    $.ajax(url, {
        data: data,
        type: "POST",
        dataType: "json",
        success: function(d) {
            if (d != 'OK') {
                alert(d);
            } else {
                reload_data();
            }
        }
    });
}

function remove_tasks() {
    perform_ajax_on_selection("/remove_tasks");
}
function resume_tasks() {
    perform_ajax_on_selection("/resume_tasks");
}
function pause_tasks() {
    perform_ajax_on_selection("/pause_tasks");
}