function getProcessDetail(id, node_type){
    $.ajax({
        type: "POST",
        dataType: "JSON",
        url: "../get_workflow_detail/",
        data: {
            id: id,
        },
        success: function (data) {
            var status = data.status,
                info = data.info,
                data = data.data;
            if (status == 0){
                alert(info);
            } else {
                $("#title").text(data.shortname);
                $("#my_type").val(node_type);
                if (node_type == "LEAF") {
                    $("#leafdiv").show();
                    $("#nodediv").hide();

                    $('#guid').val(data.guid);
                    $("#pname").val(data.pname);
                    $('#createtime').val(data.createtime);
                    $('#createuser').val(data.createuser);
                    $('#updatetime').val(data.updatetime);
                    $('#updateuser').val(data.updateuser);
                    $('#shortname').val(data.shortname);
                    $('#owner').val(data.owner);
                    $('#icon').val(data.icon);
                    $('#version').val(data.version);
                    $("#group").val(data.group);
                    $("#group").select2({width: null});
                    $('#remark').val(data.remark);

                    $("#leaf_link").attr('href','/workflow/'+ id.toString());
                }
                if (node_type == "NODE") {
                    $("#leafdiv").hide();
                    $("#nodediv").show();

                    $("#node_pname").val(data.pname);
                    $("#node_name").val(data.shortname);
                    $("#node_remark").val(data.remark);

                }
            }
        }
    });
}

function getProcessTree(){
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "../get_workflow_tree/",
        data: {
            id: $('#id').val(),
        },
        success: function (data) {
            var status = data.status,
                info = data.info,
                data = data.data;
            if (status == 0){
                alert(info);
            } else {
                $('#p_tree').jstree({
                    'core': {
                        "themes": {
                            "responsive": false
                        },
                        "check_callback": true,
                        'data': data
                    },
                    "types": {
                        "NODE": {
                            "icon": "fa fa-folder icon-state-warning icon-lg"
                        },
                        "LEAF": {
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
                                    if (obj.type == "LEAF") {
                                        alert("无法在流程下新建节点。");
                                    } else {
                                        $("#form_div").show();
                                        $("#leafdiv").hide();
                                        $("#nodediv").show();
                                        $("#node_save").show();

                                        $("#title").text("新建");
                                        $("#id").val("0");
                                        $("#pid").val(obj.id);
                                        $("#my_type").val("NODE");

                                        $("#node_name").val("");
                                        $("#node_pname").val(obj.text);
                                        $("#node_remark").val("");

                                    }
                                }
                            },
                            "新建流程": {
                                "label": "新建流程",
                                "action": function (data) {
                                    var inst = jQuery.jstree.reference(data.reference),
                                        obj = inst.get_node(data.reference);
                                    if (obj.type == "LEAF") {
                                            alert("无法在流程下新建流程。");
                                    } else {
                                        $("#form_div").show();
                                        $("#leafdiv").show();
                                        $("#nodediv").hide();
                                        $("#leaf_save").show();
                                        $("#leaf_link").hide();

                                        $("#title").text("新建");
                                        $("#my_type").val("LEAF");
                                        $("#id").val("0");
                                        $("#pid").val(obj.id);
                                        $("#pname").val(obj.text);

                                        $('#guid').val("");
                                        $('#createtime').val("");
                                        $('#createuser').val("");
                                        $('#updatetime').val("");
                                        $('#updateuser').val("");
                                        $('#shortname').val("");
                                        $('#owner').val("USER");
                                        $('#icon').val("");
                                        $('#version').val("");
                                        $("#group").val("");
                                        $("#group").select2({width: null});
                                        $('#remark').val("");
                                    }
                                }
                            },
                            "删除": {
                                "label": "删除",
                                "action": function (data) {
                                    var inst = jQuery.jstree.reference(data.reference),
                                        obj = inst.get_node(data.reference);
                                    if (obj.children.length > 0)
                                        alert("当前节点包含子节点，无法删除。");
                                    else {
                                        if (confirm("确定要删除？删除后不可恢复。")) {
                                            $.ajax({
                                                type: "POST",
                                                url: "../workflow_del/",
                                                data:
                                                    {
                                                        id: obj.id,
                                                    },
                                                success: function (data) {
                                                    if (data == 1) {
                                                        inst.delete_node(obj);
                                                        alert("删除成功！");
                                                        $("#form_div").hide();
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
                    .bind('select_node.jstree', function (event, data) {
                        var node = data.node;
                        $('#id').val(node.id);
                        $('#pid').val(node.parent);
                        if (node.parent == "#"){
                            $("#form_div").hide();
                            $("#node_save").hide();
                            $("#lead_save").hide();
                            $("#leaf_link").hide();
                        } else {
                            $("#form_div").show();
                            $("#node_save").show();
                            $("#lead_save").show();
                            $("#leaf_link").show();
                            getProcessDetail(node.id, node.type);
                        }
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
                                    url: "../workflow_move/",
                                    data: {
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
                                            if (data == "流程") {
                                                alert("不能移动到流程，只能移动到节点下。");
                                                location.reload()
                                            } else {
                                                if (data != "0") {
                                                    var selectid = $("#id").val();
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
                    });
            }
        }
    });
}

getProcessTree();


$('#node_save, #leaf_save').click(function (data){
    var save_type = $(this).prop("id");

    var group = $('#group').val();
    var formdata = $("#p_form").serialize();
    formdata.group=group;

    $.ajax({
        type: "POST",
        dataType: "JSON",
        url: "../workflow_save/",
        data: formdata,
        success: function (data){
            var status = data.status,
                info = data.info,
                select_id = data.data,
                createtime = data.createtime,
                updatetime = data.updatetime,
                createuser = data.createuser,
                updateuser = data.updateuser;
            if (status == 1){
                if ($("#id").val() == "0") {
                    if (save_type == "node_save"){

                        $('#p_tree').jstree('create_node', $("#pid").val(), {
                            "text": $("#node_name").val(),
                            "id": select_id,
                            "type": "NODE",
                        }, "last", false, false);
                    } else {
                        $('#createtime').val(createtime);
                        $('#updatetime').val(updatetime);
                        $('#createuser').val(createuser);
                        $('#updateuser').val(updateuser);
                        $("#leaf_link").show();
                        $("#leaf_link").attr('href','/workflow/'+ select_id.toString());
                        $('#p_tree').jstree('create_node', $("#pid").val(), {
                            "text": $("#shortname").val(),
                            "id": select_id,
                            "type": "LEAF",
                        }, "last", false, false);
                    }

                    $("#id").val(select_id);
                    $('#title').text($("#shortname").val());
                    $('#p_tree').jstree('deselect_all');
                    $('#p_tree').jstree('select_node', $("#id").val(), true);
                } else {
                    var curnode = $('#p_tree').jstree('get_node', $("#id").val());
                    var name = "";
                    if (save_type == "node_save"){

                        name = $("#node_name").val();
                    } else {
                        $('#updatetime').val(updatetime);
                        $('#updateuser').val(updateuser);
                        name = $('#shortname').val();
                    }
                    var newtext = curnode.text.replace(curnode.text, name);
                    curnode.text = newtext;
                    $('#p_tree').jstree('set_text', $("#id").val(), newtext);
                    $('#title').text(newtext);

                }
            }   
            alert(info);
        }
    });
});
