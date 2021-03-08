$(document).ready(function () {
    var default_url = "../workflow_job_data?runstate=" + $('#runstate').val() + "&startdate=" + $('#startdate').val() + "&enddate=" + $('#enddate').val() +  "&runperson=" + $('#runperson').val()

    $('#sample_1').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "bProcessing": true,
        "ajax": default_url,
        "columns": [
            {"data": "id"},
            {"data": "name"},
            {"data": "startuser"},
            {"data": "state"},
            {"data": "reson"},
            {"data": "createtime"},
            {"data": "starttime"},
            {"data": "endtime"},
            {"data": null},
        ],
        "columnDefs": [{
            "targets": 1,
            "render": function (data, type, full) {
                return "<td><a href='process_url' target='_blank'>data</a></td>".replace("data", full.name).replace("process_url", "/workflow_monitor/" + full.id + "?s=true")
            }
        }, {
            "targets": -1,  // 指定最后一列添加按钮；
            "data": null,
            "width": "60px",  // 指定列宽；
            "render": function (data, type, full) {
                return "<td><button title='删除'  id='delrow' class='btn btn-xs btn-primary' type='button'><i class='fa fa-trash-o'></i></button></td>"
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
                url: "../workflow_job_del/",
                data:
                    {
                        id: data.id
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

    $('#startdate').datetimepicker({
        autoclose: true,
        minView: "month",
        format: 'yyyy-mm-dd',
    });
    $('#enddate').datetimepicker({
        autoclose: true,
        minView: "month",
        format: 'yyyy-mm-dd',
    });
    $('#cx').click(function () {
        var table = $('#sample_1').DataTable();
        table.ajax.url("../workflow_job_data?runstate=" + $('#runstate').val() + "&startdate=" + $('#startdate').val() + "&enddate=" + $('#enddate').val() +  "&runperson=" + $('#runperson').val()).load();
    })

});