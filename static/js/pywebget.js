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
    var oTable = $('#download_list_table').dataTable({
//        "bProcessing": true,
        "bDestroying": true,
        "sAjaxSource": "/task_list",
        "sScrollX": 1440,
        "sScrollY": 400,
        "bJQueryUI": true,
        "sPaginationType": "full_numbers",
        "bAutoWidth": false,
        "bStateSave": true,
        "aLengthMenu": [
            [25, 50, 100, -1],
            [25, 50, 100, "All"]
        ],
        "aoColumns": [
            { "mDataProp": "id" },
            { "mDataProp": "status" },
            { "mDataProp": "filename" },
            { "mDataProp": "dir" },
            { "mDataProp": "percent" },
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
                    return "<input type='checkbox' id='task_" + oObj.aData["id"] + "' />";
                },
                "aTargets": [ 0 ]
            },
            {
                "fnRender": function (oObj) {
                    return str_by_status(oObj.aData["status"]);
                },
                "aTargets": [ 1 ]
            }
//                        { "bVisible": false,  "aTargets": [ 3 ] },
//                        { "sClass": "center", "aTargets": [ 4 ] }
        ]
    });
}

jQuery.fn.dataTableExt.aTypes.push(
    function (sData) {
        return 'html';
    }
);
$(function() {
    load_data();
    $(".button").button();
    $("a", ".demo").click(function() {
        return false;
    });
    set_table_size();
    $("#add").click(function() {
        $("#add_task").dialog({
            title: _s["Add Task"],
            modal:true,
            minHeight:200,
            minWidth:390,
            buttons: { "Ok": function() {
                $(this).dialog("close");
            },
                "Cancel": function() {
                    $(this).dialog("close");
                } }
        });
    });
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
}

$(window).resize(function() {
    set_table_size();
});

function add_task(){
    var data = JSON.stringify({
        "urls":$("#urls").val(),
        "cookie":$("#cookie").val(),
        "referrer":$("#referrer").val()
    });
    $.ajax("/add_task",{
        data: {data:data},
        type: "POST",
        dataType: "json",
        success: function(d){
            alert(d);
        }
    });
}