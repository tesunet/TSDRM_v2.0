$(document).ready(function () {
    function getClientree() {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: '../get_client_tree/',
            data: {
                'id': $("#id").val(),
            },
            success: function (data) {
                if (data.ret == 0) {
                    alert(data.data)
                }
                else {
                    $('#tree_client').jstree({
                    'core': {
                        "themes": {
                            "responsive": false
                        },
                        "check_callback": true,
                        'data': data.data
                    },

                    "types": {
                        "NODE": {
                            "icon": false
                        },
                        "CLIENT": {
                            "icon":false
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
                                    if (obj.type == "CLIENT") {
                                        alert("无法在客户端下新建节点。");
                                    } else {
                                        $("#title").text("新建");
                                        $("#id").val("0");
                                        $("#pid").val(obj.id);
                                        $("#my_type").val("NODE");
                                        $("#node_name").val("");
                                        $("#node_pname").val(obj.data["name"]);
                                        $("#node_remark").val("");

                                        $("#client").hide();
                                        $("#node").show();
                                        $("#node_save").show()
                                        $("#client_save").hide()
                                    }
                                }
                            },
                            "新建客户端": {
                                "label": "新建客户端",
                                "action": function (data) {
                                    var inst = jQuery.jstree.reference(data.reference),
                                        obj = inst.get_node(data.reference);
                                    if (obj.type == "CLIENT") {
                                        alert("无法在客户端下新建客户端。");
                                    } else {

                                        $("#title").text("新建")
                                        $("#pname").val(obj.data["name"])
                                        $("#id").val("0");
                                        $("#pid").val(obj.id);
                                        $("#my_type").val("CLIENT");
                                        $("#host_ip").val("");
                                        $("#host_name").val("");
                                        $("#os").val("");
                                        $("#username").val("");
                                        $("#password").val("");
                                        $("#remark").val("");
                                        $('#param_se').empty();

                                        $("#client").show()
                                        $("#node").hide()
                                        $("#node_save").hide()
                                        $("#client_save").show()
                                    }
                                }
                            },
                            "删除": {
                                "label": "删除",
                                "action": function (data) {
                                    var inst = jQuery.jstree.reference(data.reference),
                                        obj = inst.get_node(data.reference);
                                    if (obj.children.length > 0)
                                        alert("节点下还有其他节点或客户端，无法删除。");
                                    else {
                                        if (confirm("确定要删除？删除后不可恢复。")) {
                                            $.ajax({
                                                type: "POST",
                                                url: "../clientdel/",
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
                                    url: "../client_move/",
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
                                            alert("目标节点下存在重名。");
                                            location.reload()
                                        } else {
                                            if (data == "客户端") {
                                                alert("不能移动至客户端下。");
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
                        $("#title").text(data.node.data.name);

                        if (type == "CLIENT") {
                             $.ajax({
                                type: "POST",
                                dataType: 'json',
                                url: "../get_client_detail/",
                                data: {
                                        id: data.node.id,
                                    },
                                success: function (data) {
                                    if (data.ret == 1) {
                                        $("#host_ip").val(data.data.host_ip);
                                        $("#host_name").val(data.data.host_name);
                                        $("#os").val(data.data.os);
                                        $("#username").val(data.data.username);
                                        $("#password").val(data.data.password);
                                        $("#remark").val(data.data.remark);

                                        // 动态参数
                                        $('#param_se').empty();
                                        var variable_param_list = data.data.variable_param_list;
                                        for (var i = 0; i < variable_param_list.length; i++) {
                                            $('#param_se').append('<option value="' + variable_param_list[i].variable_name + '">' + variable_param_list[i].param_name + ':'  + variable_param_list[i].variable_name +  ':' + variable_param_list[i].param_value + '</option>');
                                        }
                                    }
                                    else {
                                        $("#host_id").val("0");
                                        $("#host_ip").val("");
                                        $("#host_name").val("");
                                        $("#os").val("");
                                        $("#username").val("");
                                        $("#password").val("");
                                        $("#remark").val("");
                                        $('#param_se').empty();
                                        alert(data.info);
                                    }
                                },
                                error: function (e) {
                                    alert("页面出现错误，请于管理员联系。");
                                }
                            });
                            $("#client").show()
                            $("#node").hide()
                        }
                        if (type == "NODE") {
                            $("#node_pname").val(data.node.data.pname)
                            $("#node_name").val(data.node.data.name)
                            $("#node_remark").val(data.node.data.remark)
                            $("#client").hide()
                            $("#node").show()
                        }
                        if (data.node.id == "1" ||data.node.id == "2"||data.node.id == "3" ) {
                            $("#node_save").hide()
                            $("#client_save").hide()
                        } else {
                            $("#node_save").show()
                            $("#client_save").show()
                        }
                    });
                }
            }
        });
    }
    getClientree();

    $('#node_save').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../client_node_save/",
            data: {
                id: $("#id").val(),
                pid: $("#pid").val(),
                node_name: $("#node_name").val(),
                node_remark: $("#node_remark").val(),
                            },
            success: function (data) {
                if (data.ret == 1) {
                    if ($("#id").val() == "0") {
                        $('#tree_client').jstree('create_node', $("#pid").val(), {
                            "text": $("#node_name").val(),
                            "id": data.nodeid
                        }, "last", false, false);
                        $("#id").val(data.nodeid)
                    }
                    else{
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace(curnode.data["name"],$("#node_name").val())
                        curnode.text= newtext
                        curnode.data["remark"]=$("#node_remark").val()
                        curnode.data["name"]=$("#node_name").val()
                        $('#tree_client').jstree('set_text', $("#id").val() , newtext);
                    }
                }
                alert(data.info);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
    });
    $('#client_save').click(function () {
        var params_list = [];

        // 构造参数Map>> Array (动态参数)
        $('#param_se option').each(function () {
            // 构造单个参数信息
            var txt_param_list = $(this).text().split(":");
            var val_param = $(this).prop("value");
            var param_dict = {
                "param_name": txt_param_list[0],
                "variable_name": val_param,
                "param_value": txt_param_list[2]
            };
            params_list.push(param_dict)
        });

        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../client_client_save/",
            data: {
                id: $("#id").val(),
                pid: $("#pid").val(),
                host_ip: $("#host_ip").val(),
                host_name: $("#host_name").val(),
                os: $("#os").val(),
                username: $("#username").val(),
                password: $("#password").val(),
                remark: $("#remark").val(),
                config: JSON.stringify(params_list)

                },
            success: function (data) {
                if (data.ret == 1) {
                    if ($("#id").val() == "0") {
                        $('#tree_client').jstree('create_node', $("#pid").val(), {
                            "text": $("#host_name").val(),
                            "id": data.nodeid
                        }, "last", false, false);
                        $("#id").val(data.nodeid)
                    }
                    else{
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace(curnode.data["name"],$("#host_name").val())
                        curnode.text= newtext
                        curnode.data["name"]=$("#host_name").val()
                        $('#tree_client').jstree('set_text', $("#id").val() , newtext);
                    }
                }
                alert(data.info);
            },
            error: function (e) {
                alert("页面出现错误，请于管理员联系。");
            }
        });
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

                        var txt_param = params_t_list[0];
                        var v_param = params_t_list[2];

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
                            '<input id="variable_name" readonly type="text" name="variable_name" value="' + alpha_param + '" class="form-control" placeholder="">' +
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
            $('#param_se').append('<option value="' + variable_name + '">' + param_name + ':'  + variable_name + ':' + param_value + '</option>');
        }
        if (param_operate == "edit") {
            // 指定value的option修改text
            $('#param_se option[value="' + variable_name + '"]').text(param_name+ ':'  + variable_name + ':' + param_value);
        }
        $("#static01").modal("hide");
    });




});