$(document).ready(function () {
    $('#client_dt').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "bProcessing": true,
        "ajax": "../client_manage_data/",
        "columns": [
            {"data": "client_manage_id"},
            {"data": "client_name"},
            {"data": "client_id"},
            {"data": "client_os"},
            {"data": "install_time"},
            {"data": null}
        ],

        "columnDefs": [{
            "targets": -1,
            "data": null,
            "width": "100px",
            "defaultContent": "<button  id='edit' title='编辑' data-toggle='modal'  data-target='#static'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-edit'></i></button><button title='删除'  id='delrow' class='btn btn-xs btn-primary' type='button'><i class='fa fa-trash-o'></i></button>"
        }],
        "oLanguage": {
            "sLengthMenu": "每页显示 _MENU_ 条记录",
            "sZeroRecords": "抱歉， 没有找到",
            "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
            "sInfoEmpty": "没有数据",
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
    // 行按钮
    $('#client_dt tbody').on('click', 'button#delrow', function () {
        if (confirm("确定要删除该条数据？")) {
            var table = $('#client_dt').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.ajax({
                type: "POST",
                url: "../hosts_manage_del/",
                data: {
                    host_id: data.host_id,
                },
                success: function (data) {
                    if (data.ret == 1) {
                        table.ajax.reload();
                    }
                    alert(data.info);
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });

        }
    });
    $('#client_dt tbody').on('click', 'button#edit', function () {
        var table = $('#client_dt').DataTable();
        var data = table.row($(this).parents('tr')).data();

        $("#client_manage_id").val(data.client_manage_id);
        $("#client_name").val(data.client_name);
        $("#client_id").val(data.client_id);
        $("#client_os").val(data.client_os);
        $("#install_time").val(data.install_time);
    });

    // select client
    $("#client_name").change(function () {
        var client_info = $("#client_info").val();
        client_info = JSON.parse(client_info);

        var cur_client = $("#client_name").val();
        for (var i = 0; i < client_info.length; i++) {
            if (client_info[i].client_name == cur_client) {
                $("#client_id").val(client_info[i].client_id);
                $("#client_os").val(client_info[i].client_os);
                $("#install_time").val(client_info[i].install_time);
                break
            }
        }
    });

    $("#new").click(function () {
        $("#client_manage_id").val(0);
        $("#client_name").val("");
        $("#client_id").val("");
        $("#client_os").val("");
        $("#install_time").val("");
    });

    $('#save').click(function () {
        var table = $('#client_dt').DataTable();

        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../client_save/",
            data: {
                client_manage_id: $("#client_manage_id").val(),
                client_id: $("#client_id").val(),
                client_name: $("#client_name").val(),
                client_os: $("#client_os").val(),
                install_time: $("#install_time").val()
            },
            success: function (data) {
                if (data.ret == 1) {
                    $('#static').modal('hide');
                    table.ajax.reload();
                }
                alert(data.info);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    })

    $('#error').click(function () {
        $(this).hide()
    })
});