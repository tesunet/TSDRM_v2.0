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
                                        $("#remark").val("");

                                        $("#client").hide();
                                        $("#node").show();
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
                                        $("#type").val("");
                                        $("#username").val("");
                                        $("#password").val("");

                                        $("#client").show()
                                        $("#node").hide()
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
                        if (data.node.id == "1" ||data.node.id == "2"||data.node.id == "3" ) {
                            $("#node_save").hide()
                            $("#interface_save").hide()
                        } else {
                            $("#node_save").show()
                            $("#interface_save").show()
                        }
                    });
                }
            }
        });
    }
    getClientree();



});