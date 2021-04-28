$(document).ready(function () {
    var default_url = "../syslog_data?type=" + $('#type').val() + "&startdate=" + $('#startdate').val() + "&enddate=" + $('#enddate').val() +  "&user=" + $('#user').val();

    $('#sample_1').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "iDisplayLength": 25,
        "bProcessing": true,
        "ajax": default_url,
        "columns": [
            {"data": "id"},
            {"data": "datatime"},
            {"data": "user"},
            {"data": "type"},
            {"data": "log"},
            {"data": null},
        ],
        "columnDefs": [
            {
                "targets": -1,
                "data": null,
                "width": "40px",
                "defaultContent": "<button  id='edit' title='详情' data-toggle='modal'  data-target='#static'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-edit'></i></button>"
            }
        ],

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

    $('#sample_1 tbody').on('click', 'button#edit', function () {
        var table = $('#sample_1').DataTable();
        var data = table.row($(this).parents('tr')).data();

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
        table.ajax.url("../syslog_data?type=" + $('#type').val() + "&startdate=" + $('#startdate').val() + "&enddate=" + $('#enddate').val() +  "&user=" + $('#user').val()).load();
    })

});