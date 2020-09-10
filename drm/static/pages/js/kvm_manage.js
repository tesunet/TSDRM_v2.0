$(document).ready(function () {
    $('#kvm_manage_dt').dataTable({
        "bAutoWidth": true,
        "bSort": false,
        "bProcessing": true,
        "ajax": "../kvm_manage_data/?utils_id=" + $('#utils_id').val(),
        "columns": [
            {"data": "kvm_name"},
            {"data": "kvm_cpu"},
            {"data": "kvm_memory"},
            {"data": "kvm_disk"},
            {"data": "kvm_os"},
            {"data": "kvm_state"},
            {"data": null}
        ],
        "columnDefs": [
            {
                "targets": -2,
                "mRender": function (data, type, full) {
                    if (full.kvm_state == '运行中'){
                        return "<span class='fa fa-plug' style='color:green; height:20px;width:14px;'></span>"
                    }
                    if (full.kvm_state == '关闭'){
                        return "<span class='fa fa-plug' style='color:red; height:20px;width:14px;'></span>"
                    }
                    if (full.kvm_state == '暂停'){
                        return "<span class='fa fa-plug' style='color:indianred; height:20px;width:14px;'></span>"
                    }
                }
            },
            {
                "targets": -1,
                "data": null,
                "width": "100px",
                "defaultContent": "<button  id='edit' title='编辑' data-toggle='modal'  data-target='#static01'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-edit'></i></button>" +
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

        },
    });


    $('#kvm_manage_dt tbody').on('click', 'button#edit', function () {
        var table = $('#kvm_manage_dt').DataTable();
        var data = table.row($(this).parents('tr')).data();
        $('#kvm_name').val(data.kvm_name);
        $('#kvm_state').val(data.kvm_state);
        $('#kvm_cpu').val(data.kvm_cpu);
        $('#kvm_memory').val(data.kvm_memory);
        $('#kvm_disk').val(data.kvm_disk);
        $('#kvm_os').val(data.kvm_os);

        if($("#kvm_state").val() == '运行中'){
            $("#kvm_start").hide();
            $("#kvm_shutdown").show();

        }
        if($("#kvm_state").val() == '关闭'){
            $("#kvm_start").show();
            $("#kvm_shutdown").hide();
        }
    });


    $('#kvm_manage_dt tbody').on('click', 'button#delrow', function () {
        if (confirm("确定要删除该虚拟机？")) {
            var table = $('#kvm_manage_dt').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.ajax({
                type: "POST",
                url: "../kvm_delete/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_name: $("#kvm_name").val(),
                        kvm_state: $("#kvm_state").val(),
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "删除成功。") {
                        $('#static01').modal('hide');
                        table.ajax.reload();
                    }
                    alert(myres);
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });
        }
    });


    $('#utils_id').change(function () {
        var table = $('#kvm_manage_dt').DataTable();
        table.ajax.url("../kvm_manage_data/?utils_id=" + $('#utils_id').val()).load();
    });


    $('#kvm_suspend').click(function () {
        if (confirm("确定要暂停该虚拟机？")) {
            var table = $('#kvm_manage_dt').DataTable();
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../kvm_suspend/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_name: $("#kvm_name").val(),
                        kvm_state: $("#kvm_state").val(),
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "暂停成功。") {
                        $('#static01').modal('hide');
                        table.ajax.reload();
                    }
                    alert(myres);
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                }
            });
        }
    });


    $('#kvm_resume').click(function () {
        var table = $('#kvm_manage_dt').DataTable();
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_resume/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                    kvm_state: $("#kvm_state").val(),
                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "运行成功。") {
                    $('#static01').modal('hide');
                    table.ajax.reload();
                }
                alert(myres);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });

    });


    $('#kvm_shutdown').click(function () {
        if (confirm("确定要关闭该虚拟机？")) {
            var table = $('#kvm_manage_dt').DataTable();
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../kvm_shutdown/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_name: $("#kvm_name").val(),
                        kvm_state: $("#kvm_state").val(),
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "关闭成功。") {
                        $('#static01').modal('hide');
                        table.ajax.reload();
                    }
                    alert(myres);
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                }
            });
        }
    });


    $('#kvm_reboot').click(function () {
        var table = $('#kvm_manage_dt').DataTable();
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_reboot/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                    kvm_state: $("#kvm_state").val(),
                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "重启成功。") {
                    $('#static01').modal('hide');
                    table.ajax.reload();
                }
                alert(myres);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });

    });


    $('#kvm_undefine').click(function () {
       if (confirm("确定要删除该虚拟机？")) {
            var table = $('#kvm_manage_dt').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.ajax({
                type: "POST",
                url: "../kvm_delete/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_name: $("#kvm_name").val(),
                        kvm_state: $("#kvm_state").val(),
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "删除成功。") {
                        $('#static01').modal('hide');
                        table.ajax.reload();
                    }
                    alert(myres);
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });
        }

    });


    $('#kvm_clone').click(function () {
        $('#static02').modal('show');
        $('#loading1').hide();
        $('#kvm_clone_div').show();

        $('#kvm_name_old').val($('#kvm_name').val());
        $('#kvm_name_new').val('')
    });


    $('#kvm_clone_save').click(function () {
        $('#kvm_clone_div').hide();
        $('#loading1').show();
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_clone_save/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name_old: $("#kvm_name_old").val(),
                    kvm_name_new: $("#kvm_name_new").val(),
                    kvm_state: $("#kvm_state").val(),
                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "克隆成功。") {
                    $('#loading1').hide();
                    $('#static01').modal('hide');
                    $('#static02').modal('hide');
                    var table = $('#kvm_manage_dt').DataTable();
                    table.ajax.reload();
                }
                alert(myres);
                $('#loading1').hide();
                $('#kvm_clone_div').show();
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
                $('#loading1').hide();
                $('#kvm_clone_div').show();
            }
        });
    });


    $('#kvm_destroy').click(function () {
        if (confirm("确定要断电该虚拟机？")) {
            var table = $('#kvm_manage_dt').DataTable();
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: "../kvm_destroy/",
                data:
                    {
                        utils_id: $("#utils_id").val(),
                        kvm_name: $("#kvm_name").val(),
                        kvm_state: $("#kvm_state").val(),
                    },
                success: function (data) {
                    var myres = data["res"];
                    if (myres == "断电成功。") {
                        $('#static01').modal('hide');
                        table.ajax.reload();
                    }
                    alert(myres);
                },
                error: function (e) {
                    alert("页面出现错误，请于管理员联系。");
                }
            });
        }
    });


    $('#kvm_start').click(function () {
        var table = $('#kvm_manage_dt').DataTable();
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../kvm_start/",
            data:
                {
                    utils_id: $("#utils_id").val(),
                    kvm_name: $("#kvm_name").val(),
                    kvm_state: $("#kvm_state").val(),

                },
            success: function (data) {
                var myres = data["res"];
                if (myres == "开机成功。") {
                    $('#static01').modal('hide');
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