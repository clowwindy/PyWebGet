(function(){
    var PyWebGet = function(){
        var instance = this;

        var oTable;

        var RELOAD_INTERVAL = 3000;

        var STATUS_QUEUED = 0;
        var STATUS_DOWNLOADING = 1;
        var STATUS_PAUSED = 2;
        var STATUS_COMPLETED = 3;
        var STATUS_FAILED = 16;

        this.strings = {
            "Add Task":"Add Task",
            "Preferences":"Preferences"
        };

        var _s = this.strings;
        this.data = [];
        this.settings = {};
        var columns = [
            { "mDataProp": "checkbox" },
            { "mDataProp": "status" },
            { "mDataProp": "filename" },
            { "mDataProp": "dir" },
            { "mDataProp": "total_size", "sType": "file-size" },
            { "mDataProp": "percent", "sType": "progress" },
            { "mDataProp": "speed", "sType": "numeric" },
            { "mDataProp": "eta" },
            { "mDataProp": "completed_size", "sType": "file-size" },
            { "mDataProp": "date_created" },
            { "mDataProp": "date_completed" }
        ];

        jQuery.fn.dataTableExt.aTypes.push(
            function (sData) {
                return 'html';
            }
        );

        function init_datatable_plugins(){
            jQuery.fn.dataTableExt.oSort['file-size-asc']  = function(a,b) {
                var x = bytes_by_readable(a);
                var y = bytes_by_readable(b);
                return ((x < y) ? -1 : ((x > y) ?  1 : 0));
            };

            jQuery.fn.dataTableExt.oSort['file-size-desc'] = function(a,b) {
                var x = bytes_by_readable(a);
                var y = bytes_by_readable(b);
                return ((x < y) ?  1 : ((x > y) ? -1 : 0));
            };

            jQuery.fn.dataTableExt.oSort['progress-asc'] = function(a,b) {
                var x = progress_by_html(a);
                var y = progress_by_html(b);
                return ((x < y) ? -1 : ((x > y) ?  1 : 0));

            }
            jQuery.fn.dataTableExt.oSort['progress-desc'] = function(a,b) {
                var x = progress_by_html(a);
                var y = progress_by_html(b);
                return ((x < y) ?  1 : ((x > y) ? -1 : 0));

            }
        }

        function str_by_status(status) {
            if (status == STATUS_QUEUED)
                return "<img class='download_tiem_icon' title=Queued src='img/icons/clock.png' />";
            else if (status == STATUS_DOWNLOADING)
                return "<img class='download_tiem_icon' title=Downloading src='img/icons/play.png' />";
            else if (status == STATUS_PAUSED)
                return "<img class='download_tiem_icon' title=Paused src='img/icons/pause.png' />";
            else if (status == STATUS_COMPLETED)
                return "<img class='download_tiem_icon' title=Completed src='img/icons/finish.png' />";
            else if (status == STATUS_FAILED)
                return "<img class='download_tiem_icon' title=Failed src='img/icons/delete.png' />";
            else
                return "";
        }

        function readablize_bytes(bytes) {
            if(bytes == null || bytes == 0) {
                return "";
            }
            var s = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'DB', 'NB'];
            var e = Math.floor(Math.log(bytes)/Math.log(1024));
            return (bytes/Math.pow(1024, Math.floor(e))).toFixed(2)+" "+s[e];
        }

        function bytes_by_readable(readable) {
            var s = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'DB', 'NB'];
            var re=/([\d\.]*)\s*(\w+)/;
            var result = re.exec(readable);
            if(result.length == 0) {
                return 0;
            }
            return parseFloat(result[1]) * Math.pow(1024,s.indexOf(result[2]));
        }

        function progress_by_html(html) {
            var re = /(\d+)*%/;
            var result = re.exec(html);
            if(result.length>1){
                return +result[1];
            }
            return 0;
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

        var dialog_effect = {effect:'drop', direction: "up" };

        $.alert=function(msg, title, callback){
            $("#alert-message").text(msg);
            $("#dialog-alert").dialog({
                title: title,
                modal:true,
                show: dialog_effect,
                hide: dialog_effect,
                resizable: false,
                buttons: { "OK": function() {
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
                buttons: { "OK": function() {
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

        function init_table() {
            oTable = $('#download_list_table').dataTable({
        //        "bProcessing": true,
        //        "bDestroy": true,
        //        "sAjaxSource": "/task_list",
                "sDom":'<"H"<"toolbar"fr>>t<"F"lip>',
                "sScrollY": 400,
                "bJQueryUI": true,
                "sPaginationType": "full_numbers",
                "bAutoWidth": true,
                "bStateSave": false,
                "oLanguage": {
                    "sEmptyTable": "Click Add button to add tasks."
                },
                "aLengthMenu": [
                    [ -1, 10, 50, 100],
                    ["All", 10, 50, 100]
                ],
                "iDisplayLength": -1,
                "aoColumns": columns
            });
            $("div.toolbar").prepend($("#toolbar"));
        }

        function reload_preferences(){
            $.ajax('/preferences', {
                dataType:"json",
                cache:false,
                success:function(data) {
                    instance.settings = data;
                }
            })
        }

        function reload_data() {
            $.ajax('/task_list', {
                dataType:"json",
                cache:false,
                success:function(data) {
                    instance.old_data = instance.data;
                    instance.data = data;
                    reload_table();
                }
            })
        }

        function reload_all() {
            $.ajax('/all_data', {
                dataType:"json",
                cache:false,
                success:function(data) {
                    instance.old_data = instance.data;
                    instance.data = data.tasks;
                    instance.settings = data.preferences;
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
            var progress_html = '<progress value="p_value" max="100" title="p_value%">p_value%</progress>';
            if (row.status == STATUS_DOWNLOADING && instance.old_data) {
                var cur_date = new Date();
                var interval = RELOAD_INTERVAL;
                if (instance['last_check_date']) {
                    interval = cur_date - instance.last_check_date;
                    instance.last_check_date = cur_date;
                }
                for (var i in instance.old_data) {
                    var old_row = instance.old_data[i];
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
                percent = progress_html.replace(/p_value/g, percent.toString());
            } else {
                percent = '<progress></progress>';
            }
            var filename;
            if(row.filename) {
                filename = html_encode(row.filename);
            } else {
                filename = html_encode(row.url);
            }
            return {
                id:row.id,
                checkbox:"<input type='checkbox' class='taskid_checkbox' taskid='" + row.id + "' />",
                status:str_by_status(row.status),
                filename:"<span title='"+html_encode(row.url)+"'>"+filename+"</span>" ,
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

        function save_scroll_pos() {
            this.scroll_pos = $('.dataTables_scrollBody').scrollTop();
        }

        function load_scroll_pos() {
            $('.dataTables_scrollBody')[0].scrollTop=this.scroll_pos;
        }

        function reload_table() {
            save_scroll_pos();
            var all_same = true;
            //和旧数据对比，看看哪些少了，删除
            callback_on_complement(instance.old_data, instance.data, function(id) {
                oTable.fnDeleteRow(find_table_row_by_id(id));
                all_same = false;
            });
            //看看哪些多了，増行
            callback_on_complement(instance.data, instance.old_data, function(id, row) {
                oTable.fnAddData(render_row(row));
                all_same = false;
            });
            //更新相同的数据对应的行里的状态、下载进度、速度信息
            callback_on_intersection(instance.data, instance.old_data, function(id, row, row2) {
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
                oTable.fnUpdate(rendered_row.filename, index, get_col_index_by_name('filename'), false, false);
                oTable.fnUpdate(rendered_row.status, index, get_col_index_by_name('status'), false, false);
                oTable.fnUpdate(rendered_row.completed_size, index, get_col_index_by_name('completed_size'), false, false);
                oTable.fnUpdate(rendered_row.total_size, index, get_col_index_by_name('total_size'), false, false);
                oTable.fnUpdate(rendered_row.percent, index, get_col_index_by_name('percent'), false, false);
                oTable.fnUpdate(rendered_row.date_completed, index, get_col_index_by_name('date_completed'), false, false);
                oTable.fnUpdate(rendered_row.speed, index, get_col_index_by_name('speed'), false, false);
                oTable.fnUpdate(rendered_row.eta, index, get_col_index_by_name('eta'), false, false);
            });
            // optimize by redrawing table only once
            if(!all_same){
                oTable.fnDraw();
                // select checkbox by click rows
                $("#download_list_table tr td").unbind().click(function(e){
                    if(e.target.tagName != 'INPUT'){
                        var checkbox = $(this).parent().find(":checkbox");
                        checkbox.prop('checked', !checkbox[0].checked);
                    }
                    update_button_state();
                });
                $(":checkbox").unbind().change(update_button_state);
                update_button_state();
                // restore scroll position
                load_scroll_pos();
            }
        }

        $(function() {
            init_datatable_plugins();
            init_table();
        //    reload_data();
        //    reload_preferences();
            reload_all();
            $(".button").button();
            set_table_size();
            $("#add").click(function() {
                $("#add_task_dialog").dialog({
                    title: _s["Add Task"],
                    modal:true,
                    minHeight:286,
                    minWidth:390,
                    show: dialog_effect,
                    hide: dialog_effect,
                    buttons: { "OK": function() {
                        add_task();
                        $(this).dialog("close");
                    },
                        "Cancel": function() {
                            $(this).dialog("close");
                        }
                    }
                });
                $("#add_task_dialog").dialog({
                    resize: function(event, ui) {
                        //TODO: resize textarea
                    }
                });
            });
            $("#pause").click(pause_tasks);
            $("#resume").click(resume_tasks);
            $("#remove").click(remove_tasks);
            $("#preferences").click(show_preferences_dialog);
            setInterval((function(){
                var that = instance;
                return function(){
                    reload_data.call(that);
                };
            })(), RELOAD_INTERVAL);
        });

        function update_button_state() {
            if(selected_ids().length > 0){
                $("#pause, #resume, #remove").attr("disabled", null).button("refresh");
            } else {
                $("#pause, #resume, #remove").attr("disabled", true).button("refresh");
            }
        }

        function set_table_size() {
            var table_body_height = window.innerHeight - (
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
                "referer":$("#referer").val()
            });
            $.ajax("/add_task", {
                data: data,
                type: "POST",
                dataType: "json",
                cache:false,
                success: function(d) {
                    if (d != 'OK') {
                        $.alert(d);
                    } else {
                        reload_data();
                    }
                }
            });
        }

        function save_preferences(){
            var data = {};
            var settings = instance.settings;
            if($("#preferences_form").valid()) {
                for(var i in settings) {
                    if(!settings.hasOwnProperty(i))continue;
                    var e = $(document.getElementById(i));
                    if(e.hasClass('number')){
                        data[i] = +e.val();
                    }else{
                        data[i] = e.val();
                    }
                }
                $.ajax('/save_preferences', {
                    data: JSON.stringify(data),
                    type: "POST",
                    dataType: "json",
                    cache:false,
                    success: function(d) {
                        if (d != 'OK') {
                            $.alert(d);
                        } else {
                            reload_preferences();
                        }
                    }
                });
                return true;
            }
            return false;
        }

        function show_preferences_dialog() {
            $("#preferences_dialog").dialog({
                title: _s["Preferences"],
                modal:true,
                minHeight:286,
                minWidth:390,
                show: dialog_effect,
                hide: dialog_effect,
                buttons: { "OK": function() {
                    if(save_preferences()){
                        $(this).dialog("close");
                    }
                },
                    "Cancel": function() {
                        $(this).dialog("close");
                    }
                }
            });
            $("#preferences_dialog").dialog({
                resize: function(event, ui) {
                    //TODO: resize textarea
                }
            });
            var settings = instance.settings;
            for(var i in settings) {
                $(document.getElementById(i)).val(settings[i]);
            }
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
                cache:false,
                success: function(d) {
                    if (d != 'OK') {
                        $.alert(d);
                    } else {
                        reload_data();
                    }
                }
            });
        }

        function remove_tasks() {
            var num = selected_ids().length;
            if(num > 0) {
                $.confirm('Would you like to delete these _num tasks?'.replace("_num", num), "", function(){
                    perform_ajax_on_selection("/remove_tasks");
                },null);
        //        if(confirm()) {
        //            perform_ajax_on_selection("/remove_tasks");
        //        }
            }
        }
        function resume_tasks() {
            perform_ajax_on_selection("/resume_tasks");
        }
        function pause_tasks() {
            perform_ajax_on_selection("/pause_tasks");
        }
    };
    new PyWebGet();

})();