$(document).ready(function () {
    $("#std").val("");
    var copy_priority_hidden = $("#copy_priority_hidden").val();
    $("#copy_priority").val(copy_priority_hidden);

    var db_open_hidden = $("#db_open_hidden").val();
    $("#db_open").val(db_open_hidden);

    var log_restore_hidden = $("#log_restore_hidden").val();
    $("#log_restore").val(log_restore_hidden);


    function customProcessDataTable() {
        $('#sample_1').dataTable({
            "destory": true,
            "bAutoWidth": true,
            "bSort": false,
            "bProcessing": true,
            "ajax": "../oracle_restore_data/",
            "fnServerParams": function (aoData) {
                aoData.push({
                    name: "process_id",
                    value: $("#process_id").val()
                })
            },
            "columns": [
                {"data": "processrun_id"},
                {"data": "process_name"},
                {"data": "createuser"},
                {"data": "state"},
                {"data": "run_reason"},
                {"data": "starttime"},
                {"data": "endtime"},
                {"data": "process_id"},
                {"data": "process_url"},
                {"data": null},
            ],
            "columnDefs": [{
                "targets": 1,
                "render": function (data, type, full) {
                    return full.state != "计划" ? "<td><a href='process_url' target='_blank'>data</a></td>".replace("data", full.process_name).replace("process_url", "/processindex/" + full.processrun_id + "?s=true") : "<td>" + full.process_name + "</td>"
                }
            }, {
                "visible": false,
                "targets": -2  // 倒数第一列
            }, {
                "visible": false,
                "targets": -3  // 倒数第一列
            }, {
                "targets": -1,  // 指定最后一列添加按钮；
                "data": null,
                "width": "60px",  // 指定列宽；
                "render": function (data, type, full) {
                    return "<td><a href='/custom_pdf_report/?processrunid&processid'><button class='btn btn-xs btn-primary' type='button'><i class='fa fa-arrow-circle-down' style='color: white'></i></button></a><button title='删除'  id='delrow' class='btn btn-xs btn-primary' type='button'><i class='fa fa-trash-o'></i></button></td>".replace("processrunid", "processrunid=" + full.processrun_id).replace("processid", "processid=" + full.process_id)
                }
            }],

            "oLanguage": {
                "sLengthMenu": "&nbsp;&nbsp;每页显示 _MENU_ 条记录",
                "sZeroRecords": "抱歉， 没有找到",
                "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
                "sInfoEmpty": '',
                "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
                "sSearch": "搜索",
                "oPaginate": {
                    "sFirst": "首页",
                    "sPrevious": "前一页",
                    "sNext": "后一页",
                    "sLast": "尾页"
                },
                "sZeroRecords": "没有检索到数据",

            }
        });

        $('#sample_1 tbody').on('click', 'button#delrow', function () {
            if (confirm("确定要删除该条数据？")) {
                var table = $('#sample_1').DataTable();
                var data = table.row($(this).parents('tr')).data();
                $.ajax({
                    type: "POST",
                    url: "../../delete_current_process_run/",
                    data:
                        {
                            processrun_id: data.processrun_id
                        },
                    success: function (data) {
                        if (data == 1) {
                            table.ajax.reload();
                            alert("删除成功！");
                        } else
                            alert("删除失败，请于管理员联系。");
                    },
                    error: function (e) {
                        alert("删除失败，请于管理员联系。");
                    }
                });

            }
        });
    }

    customProcessDataTable();

    $("#confirm").click(function () {
        var process_id = $("#process_id").val();

        // 非邀请流程启动
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../cv_oracle_run/",
            data:
                {
                    processid: process_id,
                    run_person: $("#run_person").val(),
                    run_time: $("#run_time").val(),
                    run_reason: $("#run_reason").val(),

                    std: $("#std").val(),
                    recovery_time: $("#recovery_time").val(),
                    browseJobId: $("#browseJobId").val(),
                    data_path: $("#data_path").val(),

                    pri: $("#pri").val(),
                    copy_priority: $("#copy_priority").val(),
                    db_open: $("#db_open").val(),
                    log_restore: $("#log_restore").val(),
                },
            success: function (data) {
                if (data["res"] == "新增成功。") {
                    window.location.href = data["data"];
                } else
                    alert(data["res"]);
            },
            error: function (e) {
                alert("流程启动失败，请于管理员联系。");
            }
        });
    });

    $("#run").click(function () {
        $("#static").modal({backdrop: "static"});
        $('#recovery_time').datetimepicker({
            format: 'yyyy-mm-dd hh:ii:ss',
            pickerPosition: 'top-right'
        });
        // 写入当前时间
        var myDate = new Date();
        $("#run_time").val(myDate.toLocaleString());

        $("#std").val("")
    });

    $('#start_date').datetimepicker({
        autoclose: true,
        format: 'yyyy-mm-dd hh:ii',
    });
    $('#end_date').datetimepicker({
        autoclose: true,
        format: 'yyyy-mm-dd hh:ii',
    });

    $("#recovery_time_redio_group").click(function () {
        if ($("input[name='recovery_time_redio']:checked").val() == 2) {
            $("#static02").modal({backdrop: "static"});
            var pri_name = $("#pri_name").val();
            var datatable = $("#backup_point").dataTable();
            datatable.fnClearTable(); //清空数据
            datatable.fnDestroy();
            $('#backup_point').dataTable({
                "bAutoWidth": true,
                "bProcessing": true,
                "bSort": false,
                "ajax": "../../oraclerecoverydata?clientName=" + pri_name,
                "columns": [
                    {"data": "jobId"},
                    {"data": "jobType"},
                    {"data": "Level"},
                    {"data": "StartTime"},
                    {"data": "LastTime"},
                    {"data": null},
                ],
                "columnDefs": [{
                    "targets": -1,
                    "data": null,
                    "defaultContent": "<button  id='select' title='选择'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-check'></i></button>"
                }],

                "oLanguage": {
                    "sLengthMenu": "&nbsp;&nbsp;每页显示 _MENU_ 条记录",
                    "sZeroRecords": "抱歉， 没有找到",
                    "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
                    "sInfoEmpty": '',
                    "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
                    "sSearch": "搜索",
                    "oPaginate": {
                        "sFirst": "首页",
                        "sPrevious": "前一页",
                        "sNext": "后一页",
                        "sLast": "尾页"
                    },
                    "sZeroRecords": "没有检索到数据",

                }
            });
            $('#backup_point tbody').on('click', 'button#select', function () {
                var table = $('#backup_point').DataTable();
                var data = table.row($(this).parents('tr')).data();
                $("#recovery_time").val(data.LastTime);
                $("input[name='recovery_time_redio'][value='1']").prop("checked", false);
                $("input[name='recovery_time_redio'][value='2']").prop("checked", true);
                $("#browseJobId").val(data.jobId);

                $("#static02").modal("hide");

            });
        } else {
            $("#recovery_time").val("");
        }
    });

    // modal.show事件
    $("#static").on("shown.bs.modal", function (event) {
        $("#std").val($("#std_selected").val());
        $("#run_reason").val("");
        $("#recovery_time").val("");

        // 写入当前时间
        var myDate = new Date();
        $("#run_time").val(myDate.toLocaleString());
        $("input[name='recovery_time_redio'][value='1']").prop("checked", true);
        $("input[name='recovery_time_redio'][value='2']").prop("checked", false);
    });
});
