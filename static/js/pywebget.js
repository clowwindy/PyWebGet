var strings = {
    "Add Task":"Add Task"
};
var _s = strings;

function timestamp_repr(t) {
    var d = new Date(t * 1000);
    return d.toString('yyyy-MM-dd HH:mm:ss');
}

function str_by_status(status) {
    var STATUS_QUEUED = 0;
    var STATUS_DOWNLOADING = 1;
    var STATUS_PAUSED = 2;
    var STATUS_COMPLETED = 3;
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

function load_data() {
    // to be deprecated
    window.oTable = $('#download_list_table').dataTable({
//        "bProcessing": true,
        "bDestroy": true,
        "sAjaxSource": "/task_list",
        "sScrollY": 400,
        "bJQueryUI": true,
        "sPaginationType": "full_numbers",
        "bAutoWidth": true,
        "bStateSave": true,
        "oLanguage": {
            "sEmptyTable": "Click Add button to add tasks."
        },
        "aLengthMenu": [
            [25, 50, 100, -1],
            [25, 50, 100, "All"]
        ],
        "aoColumns": [
            { "mDataProp": "id" },
            { "mDataProp": "status" },
            { "mDataProp": "filename" },
            { "mDataProp": "dir" },
            { "mDataProp": "total_size" },
            { "mDataProp": "percent" },
            { "mDataProp": "completed_size" },
            { "mDataProp": "date_created" },
            { "mDataProp": "date_completed" }
        ],
        "aoColumnDefs": [
            {
                "fnRender": function (oObj) {
                    return timestamp_repr(oObj.aData["date_created"]);
                },
                "aTargets": [ -2 ]
            },
            {
                "fnRender": function (oObj) {
                    return timestamp_repr(oObj.aData["date_completed"]);
                },
                "aTargets": [ -1 ]
            },
            {
                "fnRender": function (oObj) {
                    return "<input type='checkbox' class='taskid_checkbox' taskid='" + oObj.aData["id"] + "' />";
                },
                "aTargets": [ 0 ]
            },
            {
                "fnRender": function (oObj) {
                    return str_by_status(oObj.aData["status"]);
                },
                "aTargets": [ 1 ]
            },
            {
                "fnRender": function (oObj) {
                    console.log(oObj);
                    return ((oObj.aData["completed_size"] / oObj.aData["total_size"])).toFixed(2);
                },
                "aTargets": [ 5 ]
            },
            {
                "fnRender": function (oObj) {
                    return readablize_bytes(oObj.aData["total_size"]);
                },
                "aTargets": [ 4 ]
            },
            {
                "fnRender": function (oObj) {
                    return readablize_bytes(oObj.aData["completed_size"]);
                },
                "aTargets": [ 6 ]
            }
//                        { "bVisible": false,  "aTargets": [ 3 ] },
//                        { "sClass": "center", "aTargets": [ 4 ] }
        ]
    });
}

function reload_data(){
    load_data();
    // 检查删除的行，将其删除
}

jQuery.fn.dataTableExt.aTypes.push(
    function (sData) {
        return 'html';
    }
);
$(function() {
    load_data();
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