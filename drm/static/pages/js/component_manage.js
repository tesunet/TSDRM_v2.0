function getComponentDetail(id, node_type){
    $.ajax({
        type: "POST",
        dataType: "JSON",
        url: "../get_component_detail/",
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
                if (data.owner == "SYSTEM"){
                $("#component_input_code").prop("readonly", true);
                $("#component_input_name").prop("readonly", true);
                $("#component_input_type").prop("disabled", true);
                $("#component_input_source").prop("disabled", true);
                $("#component_input_value").prop("readonly", true);
                $("#component_input_sort").prop("readonly", true);
                $("#component_input_remark").prop("readonly", true);
                $("#component_language").prop("disabled", true);
                $("#script_code").prop("readonly", true);

                $("#component_variable_code").prop("readonly", true);
                $("#component_variable_name").prop("readonly", true);
                $("#component_variable_type").prop("disabled", true);
                $("#component_variable_source").prop("disabled", true);
                $("#component_variable_value").prop("readonly", true);
                $("#component_variable_sort").prop("readonly", true);
                $("#component_variable_remark").prop("readonly", true);

                $("#component_output_code").prop("readonly", true);
                $("#component_output_name").prop("readonly", true);
                $("#component_output_type").prop("disabled", true);
                $("#component_output_source").prop("disabled", true);
                $("#component_output_sort").prop("readonly", true);
                $("#component_output_remark").prop("readonly", true);

                $("#component_massage_save").hide();
                $("#component_input_save").hide();
                $("#component_variable_save").hide();
                $("#component_output_save").hide();
                $("#component_input_add").hide();
                $("#component_variable_add").hide();
                $("#component_output_add").hide();
                }
                if (data.owner == "USER"){
                $("#component_massage_save").show();
                $("#component_input_save").show();
                $("#component_variable_save").show();
                $("#component_output_save").show()
                }
                if (node_type == "LEAF") {
                    $("#leafdiv").show();
                    $("#nodediv").hide();

                    $('#guid').val(data.guid);
                    $("#pnode").val(data.pname);
                    $('#createtime').val(data.createtime);
                    $('#createuser').val(data.createuser);
                    $('#updatetime').val(data.updatetime);
                    $('#updateuser').val(data.updateuser);
                    $('#shortname').val(data.shortname);
                    $('#component_language').val(data.language);
                    $('#script_code').val(data.code);
                    $('#version').val(data.version);
                    $("#group").val(data.group);
                    $("#group").select2({width: null});
                    $('#remark').val(data.remark);

                    $("#component_input_save").hide()
                    $("#component_output_save").hide()
                    $("#component_variable_save").hide()
                    $("#component_input_code").val('')
                    $("#component_input_name").val('')
                    $("#component_input_source").val('')
                    $("#component_input_type").val('')
                    $("#component_input_value").val('')
                    $("#component_input_sort").val('')
                    $("#component_input_remark").val('')
                    $("#component_output_code").val('')
                    $("#component_output_name").val('')
                    $("#component_output_source").val('')
                    $("#component_output_type").val('')
                    $("#component_output_sort").val('')
                    $("#component_output_remark").val('')
                    $("#component_variable_code").val('')
                    $("#component_variable_name").val('')
                    $("#component_variable_type").val('')
                    $("#component_variable_value").val('')
                    $("#component_variable_sort").val('')
                    //返回输入参数到页面上
                    $("#component_input").empty();
                    for (var i = 0; i < data.input.length; i++) {
                        $("#component_input").append('<option value="' + data.input[i]["code"] + '">' + data.input[i]["name"] + '</option>')
                    }
                    $("#component_input").click(function () {
                        $("#component_input_add").hide()
                        $("#component_input_save").show()
                        var selectval = $("#component_input option:selected").val();
                        for (var i = 0; i < data.input.length; i++) {
                            if (data.input[i]["code"] == selectval) {
                                $("#component_input_code").prop("readonly", true);
                                $("#component_input_name").prop("readonly", false);
                                $("#component_input_type").prop("disabled", false);
                                $("#component_input_source").prop("disabled", false);
                                $("#component_input_sort").prop("readonly", false);
                                $("#component_input_remark").prop("readonly", false);
                                $("#component_input_value").prop("readonly", false);

                                $('#component_input_code').val(data.input[i]["code"]);
                                $('#component_input_name').val(data.input[i]["name"]);
                                $('#component_input_type').val(data.input[i]["type"]);
                                $('#component_input_source').val(data.input[i]["source"]);
                                $('#component_input_sort').val(data.input[i]["sort"]);
                                $('#component_input_remark').val(data.input[i]["remark"]);
                                $('#component_input_value').val(data.input[i]["value"]);
                                break;
                            }
                        }
                    })
                    //返回输出参数到页面上
                    $("#component_output").empty();
                    for (var i = 0; i < data.output.length; i++) {
                        $("#component_output").append('<option value="' + data.output[i]["code"] + '">' + data.output[i]["name"] + '</option>')
                    }
                    $("#component_output").click(function () {
                        $("#component_output_add").hide()
                        $("#component_output_save").show()
                        var selectval = $("#component_output option:selected").val();
                        for (var i = 0; i < data.output.length; i++) {
                            if (data.output[i]["code"] == selectval) {
                                $("#component_output_code").prop("readonly", true);
                                $("#component_output_name").prop("readonly", false);
                                $("#component_output_type").prop("disabled", false);
                                $("#component_output_source").prop("disabled", false);
                                $("#component_output_sort").prop("readonly", false);
                                $("#component_output_remark").prop("readonly", false);

                                $('#component_output_code').val(data.output[i]["code"]);
                                $('#component_output_name').val(data.output[i]["name"]);
                                $('#component_output_type').val(data.output[i]["type"]);
                                $('#component_output_source').val(data.output[i]["source"]);
                                $('#component_output_sort').val(data.output[i]["sort"]);
                                $('#component_output_remark').val(data.output[i]["remark"]);
                                break;
                            }
                        }
                    })
                    //返回临时变量到页面上
                    $("#component_variable").empty();
                    for (var i = 0; i < data.variable.length; i++) {
                        $("#component_variable").append('<option value="' + data.variable[i]["code"] + '">' + data.variable[i]["name"] + '</option>')
                    }
                    $("#component_variable").click(function () {
                        $("#component_variable_add").hide()
                        $("#component_variable_save").show()
                        var selectval = $("#component_variable option:selected").val();
                        for (var i = 0; i < data.variable.length; i++) {
                            if (data.variable[i]["code"] == selectval) {
                                $("#component_variable_code").prop("readonly", true);
                                $("#component_variable_name").prop("readonly", false);
                                $("#component_variable_type").prop("disabled", false);
                                $("#component_variable_source").prop("disabled", false);
                                $("#component_variable_sort").prop("readonly", false);
                                $("#component_variable_remark").prop("readonly", false);
                                $("#component_variable_value").prop("readonly", false);

                                $('#component_variable_code').val(data.variable[i]["code"]);
                                $('#component_variable_name').val(data.variable[i]["name"]);
                                $('#component_variable_type').val(data.variable[i]["type"]);
                                $('#component_variable_source').val(data.variable[i]["source"]);
                                $('#component_variable_sort').val(data.variable[i]["sort"]);
                                $('#component_variable_remark').val(data.variable[i]["remark"]);
                                $('#component_variable_value').val(data.variable[i]["value"]);
                                break;
                            }
                        }
                    })


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

function getComponentTree(){
    $.ajax({
        type: "POST",
        dataType: "JSON",
        url: "../get_component_tree/",
        data: {
            id: $('#id').val(),
            owner:"USER"
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
                                        alert("无法在组件下新建节点。");
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
                            "新建组件": {
                                "label": "新建组件",
                                "action": function (data) {
                                    var inst = jQuery.jstree.reference(data.reference),
                                        obj = inst.get_node(data.reference);
                                    if (obj.type == "LEAF") {
                                            alert("无法在组件下新建组件。");
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
                                        $('#icon').val("");
                                        $('#version').val("");
                                        $("component_language").val("");
                                        $("script_code").val("");
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
                                                url: "../component_del/",
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
                        $("#node_save").show();
                        $("#leaf_save").show();
                        $('#shortname').prop("readonly", false);
                        $('#icon').prop("readonly", false);
                        $('#version').prop("readonly", false);
                        $('#group').prop("disabled", false);
                        $('#remark').prop("readonly", false);
                        $('#node_remark').prop("readonly", false);
                        $('#node_name').prop("readonly", false);

                        var node = data.node;
                        $('#id').val(node.id);
                        $('#pid').val(node.parent);
                        if (node.parent == "#"){
                            $("#form_div").hide();
                            $("#node_save").hide();
                            $("#leaf_save").hide();
                            $("#leaf_link").hide();
                        } else {
                            $("#form_div").show();
                            $("#node_save").show();
                            $("#leaf_save").show();
                            $("#leaf_link").show();
                            getComponentDetail(node.id, node.type);
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
                                    url: "../component_move/",
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
                                            if (data == "组件") {
                                                alert("不能移动到组件，只能移动到节点下。");
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

function getComponentTreeSystem(){
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "../get_component_tree/",
        data: {
            id: $('#id').val(),
            owner:"SYSTEM"
        },
        success: function (data) {
            var status = data.status,
                info = data.info,
                data = data.data;
            if (status == 0){
                alert(info);
            } else {
                $('#p_tree_system').jstree({
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
                    "plugins": ["types", "role"]
                })
                    .bind('select_node.jstree', function (event, data) {
                        var node = data.node;
                        $('#id').val(node.id);
                        $('#pid').val(node.parent);
                        if (node.parent == "#"){
                            $("#form_div").hide();
                            $("#node_save").hide();
                            $("#leaf_save").hide();
                            $("#leaf_link").hide();
                        } else {
                            $("#form_div").show();
                            $("#node_save").show();
                            $("#leaf_save").show();
                            $("#leaf_link").show();
                            getComponentDetail(node.id, node.type);
                        }
                        $("#node_save").hide();
                        $("#leaf_save").hide();
                        $('#shortname').prop("readonly", true);
                        $('#icon').prop("readonly", true);
                        $('#version').prop("readonly", true);
                        $('#group').prop("disabled", true);
                        $('#remark').prop("readonly", true);
                        $('#node_remark').prop("readonly", true);
                        $('#node_name').prop("readonly", true);

                    })
            }
            $('#p_tree_system').hide();
        }
    });
}

getComponentTree();
getComponentTreeSystem();

$('#tabcheck1_-2').click(function (data){
    $('#p_tree_system').show();
});

$('#node_save, #leaf_save').click(function (data){
    var save_type = $(this).prop("id");

    var group = $('#group').val();
    var formdata = $("#p_form").serialize();
    formdata.group=group;

    $.ajax({
        type: "POST",
        dataType: "JSON",
        url: "../component_save/",
        data: formdata,
        success: function (data){
            var status = data.status,
                info = data.info,
                select_id = data.data,
                createtime = data.createtime,
                updatetime = data.updatetime,
                createuser = data.createuser,
                updateuser = data.updateuser,
                component_language = data.language,
                script_code= data.code;
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
                        $("#component_language").val(component_language);
                        $("#script_code").val(script_code);
                        $("#leaf_link").show();
                        $("#leaf_link").attr('href','/component/'+ select_id.toString());
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


$(document).ready(function () {
    $('#component_input_save').click(function () {
        //页面获取组件输入参数
        if ($('#component_input_code').val() == "") {
            alert("参数编码不能为空。")
            return
        }
        if ($('#component_input_name').val() == "") {
            alert("参数名称不能为空。")
            return
        }
        if ($('#component_input_type').val() == "") {
            alert("数据类型不能为空。")
            return
        }
        if ($('#component_input_source').val() == "") {
            alert("数据来源不能为空。")
            return
        }
        if ($("#component_input_isnew").val() == "1") {
            $("#component_input").empty();
            var inputparams = {
                guid: $("#guid").val(),
                isnew: $("#component_input_isnew").val(),
                code: $("#component_input_code").val(),
                name: $("#component_input_name").val(),
                type: $("#component_input_type").val(),
                value: $("#component_input_value").val(),
                source: $("#component_input_source").val(),
                remark: $("#component_input_remark").val(),
                sort: $("#component_input_sort").val(),
            }
            $.ajax({
                url: "../component_form_input/",
                data: JSON.stringify(inputparams),
                type: "POST",
                data_type: "JSON",
                contentType: "application/json",
                headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
                success: function (data) {
                    console.log(inputparams)
                    if (data.status == 1) {
                        alert(data.input)
                        // location.reload()

                    } else if (data.status == 3) {
                        alert(data.input)
                        // location.reload()
                    } else {
                        alert(data.input)
                        // location.reload()
                    }
                },
                error: function (data) {
                    alert("请求错误")
                    location.reload()
                }
            })
        } else if ($("#component_input_isnew").val() == "0") {
            var inputparams = {
                guid: $("#guid").val(),
                isnew: $("#component_input_isnew").val(),
                code: $("#component_input_code").val(),
                name: $("#component_input_name").val(),
                type: $("#component_input_type").val(),
                value: $("#component_input_value").val(),
                source: $("#component_input_source").val(),
                remark: $("#component_input_remark").val(),
                sort: $("#component_input_sort").val(),
            }
            $.ajax({
                url: "../component_form_input/",
                data: JSON.stringify(inputparams),
                type: "POST",
                data_type: "JSON",
                contentType: "application/json",
                headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
                success: function (data) {
                    if (data.status == 2) {
                        alert(data.input)

                    } else {
                        alert(data.input)

                    }

                },
                error: function (data) {
                    alert("请求失败")
                }
            })

        }

    })
    //点新增后在点保存
    $('#component_variable_save').click(function () {
        //页面获取组件输入参数
        if ($('#component_variable_code').val() == "") {
            alert("参数编码不能为空。")
            return
        }
        if ($('#component_variable_name').val() == "") {
            alert("参数名称不能为空。")
            return
        }
        if ($('#component_variable_type').val() == "") {
            alert("数据类型不能为空。")
            return
        }
        if ($('#component_variable_source').val() == "") {
            alert("数据来源不能为空。")
            return
        }
        if ($("#component_variable_isnew").val() == "1") {
            $("#component_variable").empty();
            var variableparams = {
                guid: $("#guid").val(),
                isnew: $("#component_variable_isnew").val(),
                code: $("#component_variable_code").val(),
                name: $("#component_variable_name").val(),
                type: $("#component_variable_type").val(),
                value: $("#component_variable_value").val(),
                remark: $("#component_variable_remark").val(),
                sort: $("#component_variable_sort").val(),
            }
            $.ajax({
                url: "../component_form_variable/",
                data: JSON.stringify(variableparams),
                type: "POST",
                data_type: "JSON",
                contentType: "application/json",
                headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
                success: function (data) {
                    console.log(variableparams)
                    if (data.status == 1) {
                        alert(data.variable)
                    } else if (data.status == 3) {
                        alert(data.variable)
                    } else {
                        alert(data.variable)
                    }
                },
                error: function (data) {
                    alert("请求错误")
                }
            })
        } else if ($("#component_variable_isnew").val() == "0") {
            var variableparams = {
                guid: $("#guid").val(),
                isnew: $("#component_variable_isnew").val(),
                code: $("#component_variable_code").val(),
                name: $("#component_variable_name").val(),
                type: $("#component_variable_type").val(),
                value: $("#component_variable_value").val(),
                remark: $("#component_variable_remark").val(),
                sort: $("#component_variable_sort").val(),
            }
            $.ajax({
                url: "../component_form_variable/",
                data: JSON.stringify(variableparams),
                type: "POST",
                data_type: "JSON",
                contentType: "application/json",
                headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
                success: function (data) {
                    if (data.status == 2) {
                        alert(data.variable)
                    } else {
                        alert(data.variable)
                    }

                },
                error: function (data) {
                    alert("请求失败")
                }
            })

        }

    })
    //点新增后在点保存
    $('#component_output_save').click(function () {
        //页面获取组件输入参数
        if ($('#component_output_code').val() == "") {
            alert("参数编码不能为空。")
            return
        }
        if ($('#component_output_name').val() == "") {
            alert("参数名称不能为空。")
            return
        }
        if ($('#component_output_type').val() == "") {
            alert("数据类型不能为空。")
            return
        }
        if ($("#component_output_isnew").val() == "1") {
            $("#component_output").empty();
            var outputparams = {
                guid: $("#guid").val(),
                isnew: $("#component_output_isnew").val(),
                code: $("#component_output_code").val(),
                name: $("#component_output_name").val(),
                type: $("#component_output_type").val(),
                remark: $("#component_output_remark").val(),
                sort: $("#component_output_sort").val(),
            }
            $.ajax({
                url: "../component_form_output/",
                data: JSON.stringify(outputparams),
                type: "POST",
                data_type: "JSON",
                contentType: "application/json",
                headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
                success: function (data) {
                    console.log(outputparams)
                    if (data.status == 1) {
                        alert(data.output)
                    } else if (data.status == 3) {
                        alert(data.output)
                    } else {
                        alert(data.output)
                    }
                },
                error: function (data) {
                    alert("请求错误")
                }
            })
        } else if ($("#component_output_isnew").val() == "0") {
            var outputparams = {
                guid: $("#guid").val(),
                isnew: $("#component_output_isnew").val(),
                code: $("#component_output_code").val(),
                name: $("#component_output_name").val(),
                type: $("#component_output_type").val(),
                remark: $("#component_output_remark").val(),
                sort: $("#component_output_sort").val(),
            }
            $.ajax({
                url: "../component_form_output/",
                data: JSON.stringify(outputparams),
                type: "POST",
                data_type: "JSON",
                contentType: "application/json",
                headers: {"X-CSRFToken": $('[name="csrfmiddlewaretoken"]').val()},
                success: function (data) {
                    if (data.status == 2) {
                        alert(data.output)
                    } else {
                        alert(data.output)
                    }

                },
                error: function (data) {
                    alert("请求失败")
                }
            })

        }

    })
    //点新增后在点保存
    $("#component_input_add").click(function () {
        $("#component_input_save").show()
        $("#component_input").empty()
        $("#component_input_isnew").val("1")
        $("#component_input").unbind("click")
        $("#component_input_code").val('');
        $("#component_input_name").val('');
        $("#component_input_type").val('');
        $("#component_input_source").val('');
        $("#component_input_value").val('');
        $("#component_input_sort").val('');
        $("#component_input_remark").val('');

        $("#component_input_code").prop("readonly", false);
        $("#component_input_name").prop("readonly", false);
        $("#component_input_type").prop("disabled", false);
        $("#component_input_source").prop("disabled", false);
        $("#component_input_value").prop("readonly", false);
        $("#component_input_sort").prop("readonly", false);
        $("#component_input_remark").prop("readonly", false);
        })
    //点新增后在点保存
    $("#component_variable_add").click(function () {
        $("#component_variable_save").show()
        $("#component_variable").empty()
        $("#component_variable_isnew").val("1")
        $("#component_variable").unbind("click")
        $("#component_variable_code").val('');
        $("#component_variable_name").val('');
        $("#component_variable_type").val('');
        $("#component_variable_source").val('');
        $("#component_variable_value").val('');
        $("#component_variable_sort").val('');
        $("#component_variable_remark").val('');

        $("#component_variable_code").prop("readonly", false);
        $("#component_variable_name").prop("readonly", false);
        $("#component_variable_type").prop("disabled", false);
        $("#component_variable_source").prop("disabled", false);
        $("#component_variable_value").prop("readonly", false);
        $("#component_variable_sort").prop("readonly", false);
        $("#component_variable_remark").prop("readonly", false);
    })
    //点新增后在点保存
    $("#component_output_add").click(function () {
        $("#component_output").empty()
        $("#component_output_save").show()
        $("#component_output_isnew").val("1")
        $("#component_output").unbind("click")
        $("#component_output_code").val('');
        $("#component_output_name").val('');
        $("#component_output_type").val('');
        $("#component_output_sort").val('');
        $("#component_output_remark").val('');

        $("#component_output_code").prop("readonly", false);
        $("#component_output_name").prop("readonly", false);
        $("#component_output_type").prop("disabled", false);
        $("#component_output_sort").prop("readonly", false);
        $("#component_output_remark").prop("readonly", false);
    })

})



