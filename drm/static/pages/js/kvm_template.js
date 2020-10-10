$(document).ready(function () {
    $('#kvm_template_dt').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "bProcessing": true,
        "ajax": "../kvm_template_data/",
        "columns": [
            {"data": "id"},
            {"data": "name"},
            {"data": "path"},
            {"data": "type"},
            {"data": "utils_name"},
            {"data": null}
        ],
        "columnDefs": [{
            "targets": -1,
            "data": null,
            "width": "100px",
            "defaultContent": "<button  id='edit' title='编辑' data-toggle='modal'  data-target='#static'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-edit'></i></button>" +
                "<button title='删除'  id='delrow' class='btn btn-xs btn-primary' type='button'><i class='fa fa-trash-o'></i></button>"
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

    $('#kvm_template_dt tbody').on('click', 'button#delrow', function () {
        if (confirm("确定要删除该条数据？")) {
            var table = $('#kvm_template_dt').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.ajax({
                type: "POST",
                // url: "../kvm_template_del/",
                data: {
                    util_manage_id: data.id,
                },
                success: function (data) {
                    if (data.status == 1) {
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

    $('#kvm_template_dt tbody').on('click', 'button#edit', function () {
        var table = $('#kvm_template_dt').DataTable();
        var data = table.row($(this).parents('tr')).data();
    });

    $("#upload").click(function () {
        $("span.fileinput-filename").empty();
        $("#file_status").attr("class", "fileinput fileinput-new");
        $("#id").val(0);
        $("#name").val("");
        $("#code").val("");
        $("#template_file").val("");
        $("#type").val("");
        $("#path").val("");
        $("#utils_id").val("");
    });

    $("#type").change(function () {
        if ($("#type").val() == 'os_image'){
            $("#path").val("/home/images/os-image");
        }
        if ($("#type").val() == 'disk_image'){
            $("#path").val("/home/images/disk-image");
        }
    });

    $("#save").click(function () {
        var table = $('#kvm_template_dt').DataTable();
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_template_save/",
            data:
                {
                    id: $("#id").val(),
                    template_file: $("#template_file").val(),
                    name: $("#name").val(),
                    utils_id: $("#utils_id").val(),
                    type: $("#type").val(),
                    path: $("#path").val(),
                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "保存成功。") {
                    $("#id").val(data["data"]);
                    $('#static').modal('hide');
                    table.ajax.reload();
                }
                alert(myres);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });



});