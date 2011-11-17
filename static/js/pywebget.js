function timestamp_repr(t){
    var d = new Date(t*1000);
    return d.toString('yyyy-MM-dd HH:mm:ss');
}

function str_by_status(status) {
    var STATUS_QUEUED = 0;
    var STATUS_DOWNLOADING = 1;
    var STATUS_PAUSED = 2;
    var STATUS_COMPLETED = 3;
    if(status == STATUS_QUEUED)
        return "Queued";
    else if(status == STATUS_DOWNLOADING)
        return "Downloading";
    else if(status == STATUS_PAUSED)
        return "Paused";
    else if(status == STATUS_COMPLETED)
        return "Completed";
    else
        return "";
}


jQuery.fn.dataTableExt.aTypes.push(
    function ( sData ) {
        return 'html';
    }
);
$(document).ready(function() {
    var oTable = $('#example').dataTable( {
        "bProcessing": true,
        "sAjaxSource": "/task_list",
        "sScrollX": 1440,
        "bJQueryUI": true,
        "sPaginationType": "full_numbers",
        "bAutoWidth": false,
        "bStateSave": true,
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "aoColumns": [
            { "mDataProp": "checkbox" },
            { "mDataProp": "status" },
            { "mDataProp": "filename" },
            { "mDataProp": "dir" },
            { "mDataProp": "percent" },
            { "mDataProp": "date_created" },
            { "mDataProp": "date_completed" }
        ],
        "aoColumnDefs": [
            {
                "fnRender": function ( oObj ) {
                    console.log(oObj.aData);
                    return timestamp_repr(oObj.aData["date_created"]);
                },
                "aTargets": [ -2 ]
            },
            {
                "fnRender": function ( oObj ) {
                    return timestamp_repr(oObj.aData["date_completed"]);
                },
                "aTargets": [ -1 ]
            },
            {
                "fnRender": function ( oObj ) {
                    return "<input type='checkbox' id='task_" + oObj.aData["id"] + "' />";
                },
                "aTargets": [ 0 ]
            },
            {
                "fnRender": function ( oObj ) {
                    return str_by_status(oObj.aData["status"]);
                },
                "aTargets": [ 1 ]
            }
//                        { "bVisible": false,  "aTargets": [ 3 ] },
//                        { "sClass": "center", "aTargets": [ 4 ] }
        ]
    } );
} );