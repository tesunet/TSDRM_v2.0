$(document).ready(function () {

    $('#cv_joblist').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "iDisplayLength": 25,
        "bProcessing": true,
        "ajax": "../get_cv_joblist/?util=" + $('#util').val(),
        "columns": [
            {"data": "jobid"},
            {"data": "clientname"},
            {"data": "idataagent"},
            {"data": "instance"},
            {"data": "startdate"},
            {"data": "enddate"},
            {"data": "jobstatus"},
        ],

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

});