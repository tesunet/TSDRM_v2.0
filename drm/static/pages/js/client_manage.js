$(document).ready(function () {
    $('#tree_client').jstree({
    'core': {
        "themes": {
            "responsive": false
        },
        "check_callback": true,
        'data': treeData
    },

    "types": {
        "NODE": {
            "icon": "fa fa-folder icon-state-warning icon-lg"
        },
        "INTERFACE": {
            "icon": "fa fa-file-code-o icon-state-warning icon-lg"
        }
    },
    "contextmenu": {
        "items": {
            "create": null,
            "rename": null,
            "remove": null,
            "ccp": null,
            "新建节点": {
                "label": "新建节点",
                "action": function (data) {
                    var inst = jQuery.jstree.reference(data.reference),
                        obj = inst.get_node(data.reference);
                    if (obj.type == "INTERFACE") {
                        alert("无法在接口下新建节点。");
                    } else {
                        $("#title").text("新建");
                        $("#id").val("0");
                        $("#pid").val(obj.id);
                        $("#my_type").val("NODE");
                        $("#node_name").val("");
                        $("#node_pname").val(obj.text);
                        $("#remark").val("");

                        $("#interface").hide();
                        $("#node").show();
                        $("#node_save").show();
                    }
                }
            },
            "新建接口": {
                "label": "新建接口",
                "action": function (data) {
                    var inst = jQuery.jstree.reference(data.reference),
                        obj = inst.get_node(data.reference);
                    if (obj.type == "INTERFACE") {
                        alert("无法在接口下新建接口。");
                    } else {
                        $("#title").text("新建")
                        $("#id").val("0")
                        $("#pid").val(obj.id)
                        $("#my_type").val("INTERFACE");
                        $("#pname").val(obj.text)

                        $("#code").val("");
                        $("#name").val("");
                        $("#interface_type").val("");
                        $("#script_text").val("");
                        $("#success_text").val("");
                        $("#remark").val("");

                        $("#interface").show()
                        $("#node").hide()
                        $("#interface_save").show()
                    }
                }
            },
            "删除": {
                "label": "删除",
                "action": function (data) {
                    var inst = jQuery.jstree.reference(data.reference),
                        obj = inst.get_node(data.reference);
                    if (obj.children.length > 0)
                        alert("节点下还有其他节点或者接口，无法删除。");
                    else {
                        if (confirm("确定要删除？删除后不可恢复。")) {
                            $.ajax({
                                type: "POST",
                                url: "../scriptdel/",
                                data:
                                    {
                                        id: obj.id,
                                    },
                                success: function (data) {
                                    if (data == 1) {
                                        inst.delete_node(obj);
                                        alert("删除成功！");
                                    } else
                                        alert("删除失败，请于管理员联系。");
                                },
                                error: function (e) {
                                    alert("删除失败，请于管理员联系。");
                                }
                            });
                        }
                    }
                }
            },

        }
    },
    "plugins": ["contextmenu", "dnd", "types", "role"]
})
    .on('move_node.jstree', function (e, data) {
        var moveid = data.node.id;
        if (data.old_parent == "#") {
            alert("根节点禁止移动。");
            location.reload()
        } else {
            if (data.parent == "#") {
                alert("禁止新建根节点。");
                location.reload()
            } else {
                $.ajax({
                    type: "POST",
                    url: "../script_move/",
                    data:
                        {
                            id: data.node.id,
                            parent: data.parent,
                            old_parent: data.old_parent,
                            position: data.position,
                            old_position: data.old_position,
                        },
                    success: function (data) {
                        if (data == "重名") {
                            alert("目标组织下存在重名。");
                            location.reload()
                        } else {
                            if (data == "接口") {
                                alert("不能移动至接口下。");
                                location.reload()
                            } else {
                                if (data != "0") {
                                    if (selectid == moveid) {
                                        var res = data.split('^')
                                        $("#pid").val(res[1])
                                        $("#pname").val(res[0])
                                        $("#node_pname").val(res[0])
                                    }
                                }
                            }
                        }
                    },
                    error: function (e) {
                        alert("移动失败，请于管理员联系。");
                        location.reload()
                    }
                });


            }
        }
    })
    .bind('select_node.jstree', function (event, data) {
        $("#form_div").show();
        var type = data.node.original.type;

        $("#id").val(data.node.id);
        $("#pid").val(data.node.parent);
        $("#my_type").val(type);
        $("#pname").val(data.node.data.pname);
        $("#title").text(data.node.text);

        if (type == "INTERFACE") {
            // 接口编号 接口名称 接口类型 选择源客户端 类名 选择主机 脚本内容 SUCCESSTEXT 日志地址 接口说明
            $("#code").val(data.node.data.code);
            $("#name").val(data.node.data.name);
            $("#script_text").val(data.node.data.script_text);
            $("#success_text").val(data.node.data.success_text);
            $("#remark").val(data.node.data.remark);
            // Commvault
            $("#interface_type").val(data.node.data.interface_type);

            // 接口参数
            $('#param_se').empty();
            var variable_param_list = data.node.data.variable_param_list;
            for (var i = 0; i < variable_param_list.length; i++) {
                $('#param_se').append('<option value="' + variable_param_list[i].variable_name + '">' + variable_param_list[i].param_name + ': ' + variable_param_list[i].param_value + '</option>');
            }
            insertParams();

            if (data.node.data.interface_type == "Commvault") {
                $("#host_id_div").hide();
                $("#script_text_div").hide();
                $("#success_text_div").hide();
            } else {
                $("#host_id_div").show();
                $("#script_text_div").show();
                $("#success_text_div").show();
            }

            $("#interface").show()
            $("#node").hide()
        }
        if (type == "NODE") {
            $("#node_pname").val(data.node.data.pname)
            $("#node_name").val(data.node.text)
            $("#node_remark").val(data.node.data.remark)
            $("#interface").hide()
            $("#node").show()
        }
        if (data.node.parent == "#") {
            $("#node_save").hide()
            $("#interface_save").hide()
        } else {
            $("#node_save").show()
            $("#interface_save").show()
        }
    });

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