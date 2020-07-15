$('#tree_2').jstree({
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
                        $("#commv_interface").val("");
                        $("#script_text").val("");
                        $("#success_text").val("");
                        $("#remark").val("");

                        $("#interface").show();
                        $("#node").hide();
                        $("#interface_save").show();

                        $("#param_se").empty();
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
            $("#commv_interface").val(data.node.data.commv_interface);

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
                $("#script_params_div").hide();
                $("#success_text_div").hide();
                $("#commv_interface_div").show();
            } else {
                $("#host_id_div").show();
                $("#script_text_div").show();
                $("#script_params_div").show();
                $("#success_text_div").show();
                $("#commv_interface_div").hide();
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

// interface_type change
$("#interface_type").change(function () {
    var interface_type = $(this).val();
    if (interface_type == "Commvault") {
        $("#host_id_div").hide();
        $("#script_text_div").hide();
        $("#script_params_div").hide();
        $("#success_text_div").hide();
        $("#commv_interface_div").show();
    } else {
        $("#host_id_div").show();
        $("#script_text_div").show();
        $("#script_params_div").show();
        $("#success_text_div").show();
        $("#commv_interface_div").hide();
    }
});

$("#error").click(function () {
    $(this).hide();
});

$('#param_se').contextmenu({
    target: '#context-menu2',
    onItem: function (context, e) {
        if ($(e.target).text() == "新增") {
            $('#param_operate').val('new');

            // 清空所有子节点
            $('#params').empty();

            // 新增节点
            $("#params").append(
                '<div class="form-group">' +
                '<label class="col-md-2 control-label"><span style="color:red; "></span>参数名称</label>' +
                '<div class="col-md-10">' +
                '<input id="param_name" type="text" name="param_name" class="form-control" placeholder="">' +
                '<div class="form-control-focus"></div>' +
                '</div>' +
                '</div>' +
                '<div class="form-group">' +
                '<label class="col-md-2 control-label"><span style="color:red; "></span>变量设置</label>' +
                '<div class="col-md-10">' +
                '<input id="variable_name" type="text" name="variable_name" class="form-control" placeholder="">' +
                '<div class="form-control-focus"></div>' +
                '</div>' +
                '</div>' +
                '<div class="form-group">' +
                '<label class="col-md-2 control-label"><span style="color:red; "></span>参数值</label>' +
                '<div class="col-md-10">' +
                '<input id="param_value" type="text" name="param_value" class="form-control" placeholder="">' +
                '<div class="form-control-focus"></div>' +
                '</div>' +
                '</div>'
            );

            $("button#param_edit").click();
        }
        if ($(e.target).text() == "修改") {
            $('#param_operate').val('edit');
            if ($("#param_se").find('option:selected').length == 0)
                alert("请选择要修改的参数。");
            else {
                if ($("#param_se").find('option:selected').length > 1)
                    alert("修改时请不要选择多条记录。");
                else {
                    var alpha_param = $("#param_se").val();
                    var params_t = $("#param_se").find('option:selected').text();

                    var params_t_list = params_t.split(":");
                    var txt_param = params_t_list[0].trim();
                    var v_param = params_t_list[1].trim();

                    $("#params").empty();
                    $("#params").append(
                        '<div class="form-group">' +
                        '<label class="col-md-2 control-label"><span style="color:red; "></span>参数名称</label>' +
                        '<div class="col-md-10">' +
                        '<input id="param_name" type="text" name="param_name" value="' + txt_param + '" class="form-control" placeholder="">' +
                        '<div class="form-control-focus"></div>' +
                        '</div>' +
                        '</div>' +
                        '<div class="form-group">' +
                        '<label class="col-md-2 control-label"><span style="color:red; "></span>变量设置</label>' +
                        '<div class="col-md-10">' +
                        '<input id="variable_name" type="text" name="variable_name" value="' + alpha_param + '" class="form-control" placeholder="">' +
                        '<div class="form-control-focus"></div>' +
                        '</div>' +
                        '</div>' +
                        '<div class="form-group">' +
                        '<label class="col-md-2 control-label"><span style="color:red; "></span>参数值</label>' +
                        '<div class="col-md-10">' +
                        '<input id="param_value" type="text" name="param_value" value="' + v_param + '" class="form-control" placeholder="">' +
                        '<div class="form-control-focus"></div>' +
                        '</div>' +
                        '</div>'
                    );
                    $("button#param_edit").click();
                }
            }

        }
        if ($(e.target).text() == "删除") {
            $('#param_operate').val('delete');
            if ($("#param_se").find('option:selected').length == 0)
                alert("请选择要删除的参数。");
            else {
                if (confirm("确定要删除该参数吗？")) {
                    $("#param_se").find('option:selected').remove();
                    insertParams();
                }
            }
        }
    }
});



$('#params_save').click(function () {
    var param_operate = $('#param_operate').val();
    var param_name = $('#param_name').val();
    var variable_name = $('#variable_name').val();
    var param_value = $('#param_value').val();


    if (param_operate == "new") {
        $('#param_se').append('<option value="' + variable_name + '">' + param_name + ': ' + param_value + '</option>');
    }
    if (param_operate == "edit") {
        // 指定value的option修改text
        $('#param_se option[value="' + variable_name + '"]').text(param_name + ": " + param_value);
    }
    $("#static01").modal("hide");
    insertParams();
});

function insertParams() {
    // 修改数据 $('#param_se option')都写入$("#params")
    var params_list = [];

    // 构造参数Map>> Array (动态参数)
    $('#param_se option').each(function () {
        // 构造单个参数信息
        var txt_param_list = $(this).text().split(":");
        var val_param = $(this).prop("value");
        var param_dict = {
            "param_name": txt_param_list[0],
            "variable_name": val_param,
            "param_value": txt_param_list[1]
        };
        params_list.push(param_dict)
    });
    $("#insert_params").val(JSON.stringify(params_list));
}
