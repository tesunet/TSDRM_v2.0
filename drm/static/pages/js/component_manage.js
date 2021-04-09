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
                    $("#component_input_del").hide()
                    $("#component_output_save").hide()
                    $("#component_output_del").hide()
                    $("#component_variable_save").hide()
                    $("#component_variable_del").hide()

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

                    $("#component_input_code").prop("readonly", true);
                    $("#component_input_name").prop("readonly", true);
                    $("#component_input_type").prop("disabled", true);
                    $("#component_input_source").prop("disabled", true);
                    $("#component_input_sort").prop("readonly", true);
                    $("#component_input_remark").prop("readonly", true);
                    $("#component_input_value").prop("readonly", true);

                    $("#component_variable_code").prop("readonly", true);
                    $("#component_variable_name").prop("readonly", true);
                    $("#component_variable_type").prop("disabled", true);

                    $("#component_variable_sort").prop("readonly", true);
                    $("#component_variable_remark").prop("readonly", true);
                    $("#component_variable_value").prop("readonly", true);

                    $("#component_output_code").prop("readonly", true);
                    $("#component_output_name").prop("readonly", true);
                    $("#component_output_type").prop("disabled", true);
                    $("#component_output_sort").prop("readonly", true);
                    $("#component_output_remark").prop("readonly", true);


                    //返回输入参数到页面上
                    $("#component_input").empty()
                    for (var i = 0; i < data.input.length; i++) {
                        $("#component_input").append('<option value="' + data.input[i]["code"]  +"^" + data.input[i]["name"] +"^"+data.input[i]["type"]+ "^" + data.input[i]["source"] + "^"+data.input[i]["remark"]+"^"+ data.input[i]["sort"]+"^"+data.input[i]["value"]+'">' + data.input[i]["name"] + '</option>')
                    }

                    //返回输出参数到页面上
                    $("#component_variable").empty();
                    for (var i = 0; i < data.variable.length; i++) {
                        $("#component_variable").append('<option value="' + data.variable[i]["code"]  +"^" + data.variable[i]["name"] +"^"+data.variable[i]["type"]+ "^" + data.variable[i]["remark"]+"^"+ data.variable[i]["sort"]+"^"+data.variable[i]["value"]+'">' + data.variable[i]["name"] + '</option>')
                    }

                    //返回临时变量到页面上
                    $("#component_output").empty();
                    for (var i = 0; i < data.output.length; i++) {
                        $("#component_output").append('<option value="' + data.output[i]["code"]  +"^" + data.output[i]["name"] +"^"+data.output[i]["type"] + "^"+data.output[i]["remark"]+"^"+ data.output[i]["sort"]+'">' + data.output[i]["name"] + '</option>')
                    }
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
                                        document.getElementById("component_input").options.length = 0;
                                        document.getElementById("component_variable").options.length = 0;
                                        document.getElementById("component_output").options.length = 0;
                                        $('#createtime').val("");
                                        $('#createuser').val("");
                                        $('#updatetime').val("");
                                        $('#updateuser').val("");
                                        $('#shortname').val("");
                                        $('#component_language').val("");
                                        $('#script_code').val("");
                                        $('#icon').val("");
                                        $('#version').val("");
                                        $("#component_language").val("");
                                        $("#script_code").val("");
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

function judgeMember(arr,value){
    for(var i = 0; i < arr.length; i++){
        if(value == arr[i]){
            return "exist";
        }
    }
    return "not exist";
}

getComponentTree();
getComponentTreeSystem();

$(document).ready(function () {
    $('#tabcheck1_-2').click(function (data){
    $('#p_tree_system').show();
});
    $('#node_save, #leaf_save').click(function (data){
        var save_type = $(this).prop("id");
        var inputarray = new Array();
        var variablearray = new Array();
        var outputarray = new Array();
        $("#component_input option").each(function(){
            var val = $(this).val();
            if(val != ""){
                inputarray.push(val);
            }
        })
        $("#component_variable option").each(function(){
            var val = $(this).val();
            if(val != ""){
                variablearray.push(val);
            }
        })
        $("#component_output option").each(function(){
            var val = $(this).val();
            if(val != ""){
                outputarray.push(val);
            }
        })

        var input_arr = inputarray.join("##")
        var variable_arr = variablearray.join("##")
        var output_arr = outputarray.join("##")
        var shortname = $("#shortname").val()
        var component_language = $("#component_language").val()
        var script_code = $("#script_code").val()
        var remark = $("#remark").val()
        var pid = $("#pid").val()
        var id = $("#id").val()
        var my_type = $("#my_type").val()
        var node_name = $("#node_name").val()
        var node_remark = $("#node_remark").val()


        $.ajax({
            type: "POST",
            dataType: "JSON",
            url: "../component_save/",
            data: {
                "pid":pid,
                "id":id,
                "type":my_type,
                "node_name":node_name,
                "node_remark":node_remark,
                "shortname":shortname,
                "input_arr":input_arr,
                "variable_arr":variable_arr,
                "output_arr":output_arr,
                "component_language":component_language,
                "script_code":script_code,
                "remark":remark,
            },
            success: function (data){
                var status = data.status,
                    info = data.info,
                    select_id = data.data,
                    createtime = data.createtime,
                    updatetime = data.updatetime,
                    createuser = data.createuser,
                    updateuser = data.updateuser,
                    component_language = data.component_language,
                    script_code = data.script_code;
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
        if ($('#component_input_type').val() == null) {
            alert("数据类型不能为空。")
            return
        }
        if ($('#component_input_source').val() == null) {
            alert("数据来源不能为空。")
            return
        }
        if ($("#component_input_isnew").val() == "1") {
            var array = new Array();
            $("#component_input option").each(function(){
                var val = $(this).val();
                if(val != ""){
                    array.push(val);
                }
            })
            var code_array = new Array();
            for (var i=0;i<array.length;i++){
                var val_splitarray=array[i].split("^")
                code_array.push(val_splitarray[0])
            }
            var judge_result = judgeMember(code_array,$component_output_save("#component_input_code").val())
            if (judge_result=="exist"){
                alert("已存在参数名")
                return
            }else{
                var code = $("#component_input_code").val();
                var name = $("#component_input_name").val();
                var type = $("#component_input_type").val();
                var source = $("#component_input_source").val();
                var remark = $("#component_input_remark").val();
                var sort = $("#component_input_sort").val();
                var value = $("#component_input_value").val();
                $("#component_input").append('<option value="' + code + "^" + name + "^" + type + "^" + source + "^" + remark + "^" + sort+ "^" + value +'">' + name + '</option>');
                $("#component_input").find("option[value='"+ code + "^" + name + "^" + type + "^" + source + "^" + remark + "^" + sort+ "^" + value +"']").attr("selected", true);
                $("#component_input_code").prop("readonly",value=true)
                $("#component_input_isnew").val("0")
            }
        }else{
            var selectval = $("#component_input option:selected").val();
            var spilt_params = selectval.split("^")
            if ($("#component_input_code").val()==spilt_params[0]){
                var code = $("#component_input_code").val();
                var name = $("#component_input_name").val();
                var type = $("#component_input_type").val();
                var source = $("#component_input_source").val();
                var remark = $("#component_input_remark").val();
                var sort = $("#component_input_sort").val();
                var value = $("#component_input_value").val();
                $("#component_input option:selected").val(code+"^"+name+"^"+type+"^"+source+"^"+remark+"^"+sort+"^"+value)
                $("#component_input option:selected").text(name)
                $("#component_input").val()
            }

        }
        alert("修改成功，点击保存后生效。")
    });
    //点新增后在点确定
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
        if ($('#component_variable_type').val() == null) {
            alert("数据类型不能为空。")
            return
        }
        if ($("#component_variable_isnew").val() == "1") {
            var array = new Array();
            $("#component_variable option").each(function(){
                var val = $(this).val();
                if(val != ""){
                    array.push(val);
                }
            })
            var code_array = new Array();
            for (var i=0;i<array.length;i++){
                var val_splitarray=array[i].split("^")
                code_array.push(val_splitarray[0])
            }
            var judge_result = judgeMember(code_array,$("#component_variable_code").val())
            if (judge_result=="exist"){
                alert("已存在参数名")
                return
            }else{
                var code = $("#component_variable_code").val();
                var name = $("#component_variable_name").val();
                var type = $("#component_variable_type").val();
                var remark = $("#component_variable_remark").val();
                var sort = $("#component_variable_sort").val();
                var value = $("#component_variable_value").val();
                $("#component_variable").append('<option value="' + code + "^" + name + "^" + type + "^" + remark + "^" + sort+ "^" + value +'">' + name + '</option>');
                $("#component_variable").find("option[value='"+ code + "^" + name + "^" + type + "^" + remark + "^" + sort+ "^" + value +"']").attr("selected", true);
                $("#component_variable_code").prop("readonly",value=true)
                $("#component_variable_isnew").val("0")
            }
        }else{
            var selectval = $("#component_variable option:selected").val();
            var spilt_params = selectval.split("^")
            if ($("#component_variable_code").val()==spilt_params[0]){
                var code = $("#component_variable_code").val();
                var name = $("#component_variable_name").val();
                var type = $("#component_variable_type").val();
                var remark = $("#component_variable_remark").val();
                var sort = $("#component_variable_sort").val();
                var value = $("#component_variable_value").val();
                $("#component_variable option:selected").val(code+"^"+name+"^"+type+"^"+remark+"^"+sort+"^"+value)
                $("#component_variable option:selected").text(name)
                $("#component_variable").val()
            }

        }
        alert("修改成功，点击保存后生效。")
});
    //点新增后在点确定
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
        if ($('#component_output_type').val() == null) {
            alert("数据类型不能为空。")
            return
        }
        if ($("#component_output_isnew").val() == "1") {
            var array = new Array();
            $("#component_output option").each(function(){
                var val = $(this).val();
                if(val != ""){
                    array.push(val);
                }
            })
            var code_array = new Array();
            for (var i=0;i<array.length;i++){
                var val_splitarray=array[i].split("^")
                code_array.push(val_splitarray[0])
            }
            var judge_result = judgeMember(code_array,$("#component_output_code").val())
            if (judge_result=="exist"){
                alert("已存在参数名")
                return
            }else{
                var code = $("#component_output_code").val();
                var name = $("#component_output_name").val();
                var type = $("#component_output_type").val();
                var remark = $("#component_output_remark").val();
                var sort = $("#component_output_sort").val();
                $("#component_output").append('<option value="' + code + "^" + name + "^" + type + "^" + remark + "^" + sort+ '">' + name + '</option>');
                $("#component_output").find("option[value='"+ code + "^" + name + "^" + type + "^" + remark + "^" + sort+ "']").attr("selected", true);
                $("#component_output_code").prop("readonly",value=true)
                $("#component_output_isnew").val("0")
            }
        }else{
            var selectval = $("#component_output option:selected").val();
            var spilt_params = selectval.split("^")
            if ($("#component_output_code").val()==spilt_params[0]){
                var code = $("#component_output_code").val();
                var name = $("#component_output_name").val();
                var type = $("#component_output_type").val();
                var remark = $("#component_output_remark").val();
                var sort = $("#component_output_sort").val();
                $("#component_output option:selected").val(code+"^"+name+"^"+type+"^"+remark+"^"+sort)
                $("#component_output option:selected").text(name)
                $("#component_output").val()
            }

        }
        alert("修改成功，点击保存后生效。")
});
    //删除选中的输入参数(删除选中的option)
    $('#component_input_del').click(function () {
        var cof=window.confirm("确认删除该参数?");
        if (cof==true){
            var selectval = $("#component_input option:selected").val();
            $("#component_input").find("option[value='"+ selectval+"']").remove();
            $("#component_input_code").val('')
            $("#component_input_name").val('')
            $("#component_input_source").val('')
            $("#component_input_type").val('')
            $("#component_input_value").val('')
            $("#component_input_sort").val('')
            $("#component_input_remark").val('')
            $("#component_input_code").prop("readonly", true);
            $("#component_input_name").prop("readonly", true);
            $("#component_input_type").prop("disabled", true);
            $("#component_input_source").prop("disabled", true);
            $("#component_input_sort").prop("readonly", true);
            $("#component_input_remark").prop("readonly", true);
            $("#component_input_value").prop("readonly", true);
        }else{
            return
        }
    });
    //删除选中的输入参数(删除选中的option)
    $('#component_variable_del').click(function () {
        var cof=window.confirm("确认删除该参数?");
        if (cof==true){
            var selectval = $("#component_variable option:selected").val();
            $("#component_variable").find("option[value='"+ selectval+"']").remove();
            $("#component_variable_code").val('')
            $("#component_variable_name").val('')
            $("#component_variable_type").val('')
            $("#component_variable_value").val('')
            $("#component_variable_sort").val('')
            $("#component_variable_remark").val('')
            $("#component_variable_code").prop("readonly", true);
            $("#component_variable_name").prop("readonly", true);
            $("#component_variable_type").prop("disabled", true);
            $("#component_variable_sort").prop("readonly", true);
            $("#component_variable_remark").prop("readonly", true);
            $("#component_variable_value").prop("readonly", true);
        }else{
            return
        }
    });
    //删除选中的输入参数(删除选中的option)
    $('#component_output_del').click(function () {
        var cof=window.confirm("确认删除该参数?");
        if (cof==true){
            var selectval = $("#component_output option:selected").val();
            $("#component_output").find("option[value='"+ selectval+"']").remove();
            $("#component_output_code").val('')
            $("#component_output_name").val('')
            $("#component_output_type").val('')
            $("#component_output_sort").val('')
            $("#component_output_remark").val('')
            $("#component_output_code").prop("readonly", true);
            $("#component_output_name").prop("readonly", true);
            $("#component_output_type").prop("disabled", true);
            $("#component_output_sort").prop("readonly", true);
            $("#component_output_remark").prop("readonly", true);
        }else{
            return
        }
    });
    //点新增后在点确定
    $("#component_input_add").click(function () {
        $("#component_input_save").show()
        $("#component_input_del").show()
        //点击确定后取消选中状态
        $('#component_input').find("option:selected").attr("selected", false);
        $("#component_input_isnew").val("1")
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
        });
    //点新增后在点确定
    $("#component_variable_add").click(function () {
        $("#component_variable_save").show()
        $("#component_variable_del").show()
        //点击确定后取消选中状态
        $('#component_variable').find("option:selected").attr("selected", false);
        $("#component_variable_isnew").val("1")
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
    });
    //点新增后在点确定
    $("#component_output_add").click(function () {
        $("#component_output_save").show()
        $("#component_output_del").show()
        //点击确定后取消选中状态
        $('#component_output').find("option:selected").attr("selected", false);
        $("#component_output_isnew").val("1")
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
    });
    //展示输入详细参数信息
    $("#component_input").click(function () {
        var selectval = $("#component_input option:selected").val();
        if(selectval) {
            $("#component_input_del").show();
            $("#component_input_isnew").val() == "0";
            $("#component_input_code").prop("readonly", true);
            $("#component_input_name").prop("readonly", false);
            $("#component_input_type").prop("disabled", false);
            $("#component_input_source").prop("disabled", false);
            $("#component_input_sort").prop("readonly", false);
            $("#component_input_remark").prop("readonly", false);
            $("#component_input_value").prop("readonly", false);
            $("#component_input_add").show()
            $("#component_input_save").show()

            var spilt_params = selectval.split("^")
            if (spilt_params[0] == "null") {
                $("#component_input_code").val("")
            } else {
                $("#component_input_code").val(spilt_params[0])
            }
            if (spilt_params[1] == "null") {
                $("#component_input_name").val("")
            } else {
                $("#component_input_name").val(spilt_params[1])
            }
            if (spilt_params[2] == "null") {
                $("#component_input_type").val("")
            } else {
                $("#component_input_type").val(spilt_params[2])
            }
            if (spilt_params[3] == "null") {
                $("#component_input_source").val("")
            } else {
                $("#component_input_source").val(spilt_params[3])
            }
            if (spilt_params[4] == "null") {
                $("#component_input_remark").val("")
            } else {
                $("#component_input_remark").val(spilt_params[4])
            }
            if (spilt_params[5] == "null") {
                $("#component_input_sort").val("")
            } else {
                $("#component_input_sort").val(spilt_params[5])
            }
            if (spilt_params[6] == "null") {
                $("#component_input_value").val("")
            } else {
                $("#component_input_value").val(spilt_params[6])
            }
        }

    })
    //展示临时变量详细参数信息
    $("#component_variable").click(function () {
        var selectval = $("#component_variable option:selected").val();
        if(selectval) {
            $("#component_variable_del").show();
            $("#component_variable_isnew").val() == "0"
            $("#component_variable_code").prop("readonly", true);
            $("#component_variable_name").prop("readonly", false);
            $("#component_variable_type").prop("disabled", false);
            $("#component_variable_sort").prop("readonly", false);
            $("#component_variable_remark").prop("readonly", false);
            $("#component_variable_value").prop("readonly", false);
            $("#component_variable_add").show()
            $("#component_variable_save").show()

            var spilt_params = selectval.split("^")
            if (spilt_params[0] == "null") {
                $("#component_variable_code").val("")
            } else {
                $("#component_variable_code").val(spilt_params[0])
            }
            if (spilt_params[1] == "null") {
                $("#component_variable_name").val("")
            } else {
                $("#component_variable_name").val(spilt_params[1])
            }
            if (spilt_params[2] == "null") {
                $("#component_variable_type").val("")
            } else {
                $("#component_variable_type").val(spilt_params[2])
            }
            if (spilt_params[3] == "null") {
                $("#component_variable_remark").val("")
            } else {
                $("#component_variable_remark").val(spilt_params[3])
            }
            if (spilt_params[4] == "null") {
                $("#component_variable_sort").val("")
            } else {
                $("#component_variable_sort").val(spilt_params[4])
            }
            if (spilt_params[5] == "null") {
                $("#component_variable_value").val("")
            } else {
                $("#component_variable_value").val(spilt_params[5])
            }
        }

    })
    //展示输出详细信息
    $("#component_output").click(function () {
        var selectval = $("#component_output option:selected").val();
        if(selectval) {
            $("#component_output_del").show();
            $("#component_output_isnew").val() == "0";
            $("#component_output_code").prop("readonly", true);
            $("#component_output_name").prop("readonly", false);
            $("#component_output_type").prop("disabled", false);
            $("#component_output_sort").prop("readonly", false);
            $("#component_output_remark").prop("readonly", false);
            $("#component_output_add").show()
            $("#component_output_save").show()

            var spilt_params = selectval.split("^")
            if (spilt_params[0] == "null") {
                $("#component_output_code").val("")
            } else {
                $("#component_output_code").val(spilt_params[0])
            }
            if (spilt_params[1] == "null") {
                $("#component_output_name").val("")
            } else {
                $("#component_output_name").val(spilt_params[1])
            }
            if (spilt_params[2] == "null") {
                $("#component_output_type").val("")
            } else {
                $("#component_output_type").val(spilt_params[2])
            }
            if (spilt_params[3] == "null") {
                $("#component_output_remark").val("")
            } else {
                $("#component_output_remark").val(spilt_params[3])
            }
            if (spilt_params[4] == "null") {
                $("#component_output_sort").val("")
            } else {
                $("#component_output_sort").val(spilt_params[4])
            }
        }
    })
})
