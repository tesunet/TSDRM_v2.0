var selectednode_input = []
function getProcessTree(){
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "../get_workflow_tree/",
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
                    "plugins": ["types", "role"]
                })
                    .bind('select_node.jstree', function (event, data) {
                        var node = data.node;
                        $('#id').val(node.id);
                        $("#title").text(node.text);

                        if (node.type == "LEAF") {
                            selectednode_input = node.data.input
                            $("#tablediv").show();
                            var table = $('#instance_table').DataTable();
                            table.ajax.url("../workflow_instance_data?id=" + $('#id').val()).load();
                        }
                        if (node.type == "NODE") {
                            selectednode_input = []
                            $("#tablediv").hide();
                        }
                    })
            }
        }
    });
}

function getProcessTreeSystem(){
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "../get_workflow_tree/",
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
                        $("#title").text(node.text);
                        if (node.type == "LEAF") {
                            $("#tablediv").show();
                            var table = $('#instance_table').DataTable();
                            table.ajax.url("../workflow_instance_data?id=" + $('#id').val()).load();
                            selectednode_input = node.data.input
                        }
                        if (node.type == "NODE") {
                            $("#tablediv").hide();
                            selectednode_input = []
                        }

                    })
            }
            $('#p_tree_system').hide();
        }
    });
}

getProcessTree();
getProcessTreeSystem();


$('#tabcheck1_2').click(function (data){
    $('#p_tree_system').show();
});

$('#instance_table').dataTable({
    "bAutoWidth": true,
    "bSort": false,
    "bProcessing": true,
    //"ajax": "../oracle_restore_data/",
    "fnServerParams": function (aoData) {
        aoData.push({
            name: "process_id",
            value: $("#process_id").val()
        })
    },
    "columns": [
        { "data": "id" },
        { "data": "name" },
        { "data": "instancetype_text" },
        { "data": "monitorable_text" },
        { "data": "loglevel" },
        { "data": null },
    ],
    "columnDefs":
        [{
            "targets": -1,
            "data": null,
            "width": "50px",
            "render": function (data, type, full) {
                return "<button  id='edit' title='编辑' data-toggle='modal' data-target='#static' class='btn btn-xs btn-primary' type='button'><i class='fa fa-edit'></i></button>" +
                    "<button title='删除'  id='delrow' class='btn btn-xs btn-primary' type='button'><i class='fa fa-trash-o'></i></button>";
            },
        }],

    "oLanguage": {
        "sLengthMenu": "&nbsp;&nbsp;每页显示 _MENU_ 条记录",
        "sZeroRecords": "抱歉， 没有找到",
        "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
        "sInfoEmpty": '',
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
$('#instance_table tbody').on('click', 'button#delrow', function () {
        if (confirm("确定要删除该条数据？")) {
            var table = $('#instance_table').DataTable();
            var data = table.row($(this).parents('tr')).data();
            $.ajax({
                type: "POST",
                url: "../workflow_instance_del/",
                data:
                {
                    id: data.id
                },
                success: function (data) {
                    if (data == 1) {
                        table.ajax.reload();
                        alert("删除成功！");
                    } else
                        alert("删除失败，请于管理员联系。");
                },
                error: function (e) {
                    alert("删除失败，请于管理员联系。");
                }
            });

        }
    });
$('#instance_table tbody').on('click', 'button#edit', function () {
        var table = $('#instance_table').DataTable();
        var data = table.row($(this).parents('tr')).data();
        $('#instance_id').val(data.id);
        $('#guid').val(data.guid);
        $('#createtime').val(data.createtime);
        $('#createuser').val(data.createuser);
        $('#updatetime').val(data.updatetime);
        $('#updateuser').val(data.updateuser);
        $('#workflowname').val($("#title").text());

        $('#name').val(data.name);
        $('#instancetype').val(data.instancetype);
        var monitorable = data.monitorable;
        if (monitorable == "False") {
            $('#monitorable').prop("checked", false);
        } else {
            $('#monitorable').prop("checked", true);
        }
        $('#loglevel').val(data.loglevel);
        $('#remark').val(data.remark);

        /**
         * 加载流程参数
         */
        $('#pro_param_ribbon').empty();

        var input = data.input

        if (input.length > 0) {
            $('#process_div').show();

            var process_param_list = input
            var pro_param_html = '';
            for (var k = 0; k < process_param_list.length; k++) {
                var param = process_param_list[k];
                var pre_group_div = '',
                    aft_group_div = '';
                pre_group_div = '<div class="form-group">';
                aft_group_div = '</div>';
                var valuetext='    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><input   id="process_param_value_' +param.code + '" type="text" class="form-control" name="process_param_' +param.code + '"  value="' + param.value+ '"></div></div>';
                if (param.type == "password") {
                    valuetext = '    <div class="col-md-5"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><input  id="process_param_value_' + param.code + '" type="password" class="form-control" name="process_param_' + param.code + '"  value="' + param.value + '"></div></div>';
                }else if(param.type=="int" || param.type=="decimal" )
                {
                    valuetext='    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><input  id="process_param_value_' +param.code + '" type="number" class="form-control" name="process_param_' +param.code + '"  value="' + param.value+ '"></div></div>';
                }else if(param.type=="bool")
                {
                    if (param.value == "True") {
                        valuetext = '    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><select  name="instancetype" id="process_param_value_' + param.code + '" class="form-control"><option selected value="True">True</option><option value="False">False</option></select></div></div>';
                    }
                    else{
                        valuetext = '    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><select  name="instancetype" id="process_param_value_' + param.code + '" class="form-control"><option  value="True">True</option><option selected value="False">False</option></select></div></div>';
                    }                }
                else if(param.type=="datetime")
                {
                    valuetext='    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><input  id="process_param_value_' +param.code + '" value="' + param.value+ '" autoComplete="off" name="process_param_' +param.code + '" type="datetime"  class="form-control datetime"></div></div>';
                }
                else if(param.type=="password")
                {
                    valuetext='    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><input  id="process_param_value_' +param.code + '" type="password" class="form-control" name="process_param_' +param.code + '"  value="' + param.value+ '"></div></div>';
                }

                var variablevalue=''
                if(param.variable=="True"){
                    variablevalue="checked"
                }

                pro_param_html += pre_group_div +
                    '    <div class="col-md-offset-1 col-md-2"><label class="control-label" for="form_control_1">名称：</label><label class="control-label" style="padding-left: 0;">' + param.name + '</label></div>' +
                    '    <div class="col-md-2"><label class="control-label" for="form_control_1">编码：</label><label class="control-label" style="padding-left: 0;">' + param.code + '</label></div>' +
                    '    <div class="col-md-2"><label class="control-label" for="form_control_1">类型：</label><label class="control-label" style="padding-left: 0;">' + param.type + '</label></div>' +
                     valuetext +
                    '    <div class="col-md-2"><label class="col-md-7 control-label" for="form_control_1">可变：</label><div class="col-md-5"><input   id="process_param_variable_' +param.code + '"  type="checkbox" class="form-control" name="process_param_variable_' +param.code + '" ' + variablevalue + ' style="width: 20px; height: 20px;margin-top: 5px;margin-left: -20px"/></div></div>' +
                    aft_group_div;
            }
            $('#pro_param_ribbon').append(pro_param_html);
        } else {
            $('#process_div').hide();
        }

        layui.use('laydate', function () {
                var laydate = layui.laydate;

                $('.datetime').each(function () {
                    var d_ele = $(this).prop("id");
                    laydate.render({
                        elem: '#' + d_ele,
                        type: 'datetime',
                        theme: '#428bca'
                    });
                });
            });
    });

$('#instance_save').click(function () {
    var process_params = [];
    $('#process_param_div').find('input').each(function (index, el) {
        if($(el).prop('id').indexOf("process_param_value_") != -1 )
        {
            var param_code = $(el).prop('id').replace('process_param_value_', '');
            var param_value = $(el).val();
            var param_variable = "False";
            if ($('#' + $(el).prop('id').replace('process_param_value_', 'process_param_variable_')).is(':checked')) {
                param_variable = "True"
            }
            process_params.push({
                'code': param_code,
                'value': param_value,
                'variable': param_variable,
            })
        }
    });
    $('#process_param_div').find('select').each(function (index, el) {
        if($(el).prop('id').indexOf("process_param_value_") != -1 ) {
            var param_code = $(el).prop('id').replace('process_param_value_', '');
            var param_value = $(el).val();
            var param_variable = "False";
            if ($('#' + $(el).prop('id').replace('process_param_value_', 'process_param_variable_')).is(':checked')) {
                param_variable = "True"
            }
            process_params.push({
                'code': param_code,
                'value': param_value,
                'variable': param_variable,
            })
        }
    });

    try {
        process_params = JSON.stringify(process_params);
    } catch (e) {
        process_params = ''
    }
    var monitorable= "False"
    if ($('#monitorable').is(':checked')) {
            monitorable = "True"
    }

    var table = $('#instance_table').DataTable();

    $.ajax({
        type: "POST",
        dataType: "json",
        url: "../workflow_instance_save/",
        data: {
            pid:$('#id').val(),
            id: $('#instance_id').val(),  // 实例ID
            name: $('#name').val(),
            instancetype: $('#instancetype').val(),
            monitorable: monitorable,
            loglevel: $('#loglevel').val(),
            remark: $('#remark').val(),
            params: process_params,
        },
        success: function (data) {
            var status = data.status,
                info = data.info,
                id = data.id;
                createtime = data.createtime;
                updatetime = data.updatetime;
                createuser = data.createuser;
                updateuser = data.updateuser;
                guid = data.guid;
            if (status == 1) {
                $('#instance_id').val(id);
                $('#createtime').val(createtime);
                $('#updatetime').val(updatetime);
                $('#createuser').val(createuser);
                $('#updateuser').val(updateuser);
                $('#guid').val(guid);

                table.ajax.reload();
            }
            alert(info);
        }
    });
});

$('#instance_new').click(function () {
        $('#instance_id').val("0");
        $('#guid').val("");
        $('#createtime').val("");
        $('#createuser').val("");
        $('#updatetime').val("");
        $('#updateuser').val("");
        $('#workflowname').val($("#title").text());
        $('#name').val("");
        $('#loglevel').val("");
        $('#remark').val("");

        /**
         * 加载流程参数
         */
        $('#pro_param_ribbon').empty();


        var input = selectednode_input

        if (input.length > 0) {
            $('#process_div').show();

            var process_param_list = input
            var pro_param_html = '';
            for (var k = 0; k < process_param_list.length; k++) {
                var param = process_param_list[k];
                var pre_group_div = '',
                    aft_group_div = '';
                pre_group_div = '<div class="form-group">';
                aft_group_div = '</div>';
                var valuetext='    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><input   id="process_param_value_' +param.code + '" type="text" class="form-control" name="process_param_' +param.code + '"  value=""></div></div>';
                if (param.type == "password") {
                    valuetext = '    <div class="col-md-5"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><input  id="process_param_value_' + param.code + '" type="password" class="form-control" name="process_param_' + param.code + '"  value="' + param.value + '"></div></div>';
                }else if(param.type=="int" || param.type=="decimal" )
                {
                    valuetext='    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><input  id="process_param_value_' +param.code + '" type="number" class="form-control" name="process_param_' +param.code + '"  value=""></div></div>';
                }else if(param.type=="bool") {
                    valuetext = '    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><select  name="instancetype" id="process_param_value_' + param.code + '" class="form-control"><option selected value="True">True</option><option value="False">False</option></select></div></div>';
                }
                else if(param.type=="datetime")
                {
                    valuetext='    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><input  id="process_param_value_' +param.code + '" value="" autoComplete="off" name="process_param_' +param.code + '" type="datetime"  class="form-control datetime"></div></div>';
                }
                else if(param.type=="password")
                {
                    valuetext='    <div class="col-md-3"><label class="col-md-2 control-label" for="form_control_1">值：</label><div class="col-md-10"><input  id="process_param_value_' +param.code + '" type="password" class="form-control" name="process_param_' +param.code + '"  value="' + param.value+ '"></div></div>';
                }

                pro_param_html += pre_group_div +
                    '    <div class="col-md-offset-1 col-md-2"><label class="control-label" for="form_control_1">名称：</label><label class="control-label" style="padding-left: 0;">' + param.name + '</label></div>' +
                    '    <div class="col-md-2"><label class="control-label" for="form_control_1">编码：</label><label class="control-label" style="padding-left: 0;">' + param.code + '</label></div>' +
                    '    <div class="col-md-2"><label class="control-label" for="form_control_1">类型：</label><label class="control-label" style="padding-left: 0;">' + param.type + '</label></div>' +
                     valuetext +
                    '    <div class="col-md-2"><label class="col-md-7 control-label" for="form_control_1">可变：</label><div class="col-md-5"><input   id="process_param_variable_' +param.code + '"  type="checkbox" class="form-control" name="process_param_variable_' +param.code + '" checked  style="width: 20px; height: 20px;margin-top: 5px;margin-left: -20px"/></div></div>' +
                    aft_group_div;
            }
            $('#pro_param_ribbon').append(pro_param_html);
        } else {
            $('#process_div').hide();
        }

        layui.use('laydate', function () {
                var laydate = layui.laydate;

                $('.datetime').each(function () {
                    var d_ele = $(this).prop("id");
                    laydate.render({
                        elem: '#' + d_ele,
                        type: 'datetime',
                        theme: '#428bca'
                    });
                });
            });
    });

