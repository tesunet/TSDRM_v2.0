"use strict";

function Inspector(diagram) {
    this._diagram = diagram;
    this._inspectedProperties = {};
    this._multipleProperties = {};

    // Either a GoJS Part or a simple data object, such as Model.modelData
    this.inspectedObject = null;

    // Inspector options defaults:
    this.includesOwnProperties = true;
    this.declaredProperties = {};
    this.inspectsSelection = true;
    this.propertyModified = null;
    this.showAllProperties = false;
    this.showSize = 0;

    var self = this;
    diagram.addModelChangedListener(function (e) {
        if (e.isTransactionFinished) self.inspectObject();
    });
    if (this.inspectsSelection) {
        diagram.addDiagramListener("ChangedSelection", function (e) {
            self.inspectObject();
        });
    }
}

// Some static predicates to use with the "show" property.
Inspector.showIfNode = function (part) {
    return part instanceof go.Node
};
Inspector.showIfLink = function (part) {
    return part instanceof go.Link
};
Inspector.showIfGroup = function (part) {
    return part instanceof go.Group
};

// Only show the property if its present. Useful for "key" which will be shown on Nodes and Groups, but normally not on Links
Inspector.showIfPresent = function (data, propname) {
    if (data instanceof go.Part) data = data.data;
    return typeof data === "object" && data[propname] !== undefined;
};

/**
 * Update the HTML state of this Inspector given the properties of the {@link #inspectedObject}.
 * @param {Object} object is an optional argument, used when {@link #inspectSelection} is false to
 *                        set {@link #inspectedObject} and show and edit that object's properties.
 */
Inspector.prototype.inspectObject = function (object) {
    var inspectedObject = null;
    var inspectedObjects = null;
    var diagram = this._diagram;
    if (object === null) return;
    if (object === undefined) {
        if (this.inspectsSelection) {
            inspectedObject = this._diagram.selection.first();
        } else { // if there is a single inspected object
            inspectedObject = this.inspectedObject;
        }
    } else { // if object was passed in as a parameter
        inspectedObject = object;
    }

    if (inspectedObject === null) {
        inspectedObject = diagram.model.modelData;
    }
    this.inspectedObject = inspectedObject;

    if (inspectedObject instanceof go.Part) {
        $('#div_workflow').hide();
        var nodeData = inspectedObject.data;

        if (this.inspectedObject instanceof go.Node) {
            ;
        } else if (this.inspectedObject instanceof go.Link) {
            ;
        } else {
            ;
        }
    } else {
        $('#div_workflow').show();
        $('#div_node').hide();
        $('#div_line').hide();
        var modelData = inspectedObject

        //流程信息
        $('#id').val(modelData['id']);
        $('#guid').val(modelData['guid']);
        $('#pnode').val(modelData['pnode']);
        $('#createtime').val(modelData['createtime']);
        $('#createuser').val(modelData['createuser']);
        $('#updatetime').val(modelData['updatetime']);
        $('#updateuser').val(modelData['updateuser']);
        $('#longname').val(modelData['longname']);
        $('#shortname').val(modelData['shortname']);
        $('#owner').val(modelData['owner']);
        $('#icon').val(modelData['icon']);
        $('#version').val(modelData['version']);
        $("#group").val(modelData['group']).trigger("change");
        $('#remark').val(modelData['remark']);

        $('#longname').change(function () {
            diagram.model.setDataProperty(modelData, "longname", $('#longname').val());
        });
        $('#shortname').change(function () {
            diagram.model.setDataProperty(modelData, "shortname", $('#shortname').val());
        });
        $('#owner').change(function () {
            diagram.model.setDataProperty(modelData, "owner", $('#owner').val());
        });
        $('#icon').change(function () {
            diagram.model.setDataProperty(modelData, "icon", $('#icon').val());
        });
        $('#version').change(function () {
            diagram.model.setDataProperty(modelData, "version", $('#version').val());
        });
        $('#group').change(function () {
            diagram.model.setDataProperty(modelData, "group", $('#group').val());
        });
        $('#remark').change(function () {
            diagram.model.setDataProperty(modelData, "remark", $('#remark').val());
        });

        //流程输入
        $("#workflow_input").empty();
        var workflowinput = modelData['input'];
        for (i = 0; i < workflowinput.length; i++) {
            $("#workflow_input").append('<option value="' + workflowinput[i]["code"] + '">' + workflowinput[i]["name"] + '</option>')
        }
        $('#workflow_input_del').hide();
        $('#workflow_input_isnew').val("1")
        $('#workflow_input_code').prop("readonly", false);
        $('#workflow_input_code').val("")
        $('#workflow_input_name').val("")
        $('#workflow_input_type').val("")
        $('#workflow_input_source').val("")
        $('#workflow_input_sort').val("")
        $('#workflow_input_remark').val("")
        $('#workflow_input_value').val("")


        $('#workflow_input_save').click(function () {
            if ($('#workflow_input_code').val() == "") {
                alert("参数编码不能为空。")
                return
            }
            if ($('#workflow_input_name').val() == "") {
                alert("参数名称不能为空。")
                return
            }
            if ($('#workflow_input_type').val() == "") {
                alert("数据类型不能为空。")
                return
            }
            if ($('#workflow_input_source').val() == "") {
                alert("数据来源不能为空。")
                return
            }
            if ($('#workflow_input_sort').val() == "") {
                alert("序号不能为空。")
                return
            }
            var editoptionval = {
                code: $("#workflow_input_code").val(),
                name: $("#workflow_input_name").val(),
                type: $("#workflow_input_type").val(),
                source: $("#workflow_input_source").val(),
                value: $("#workflow_input_value").val(),
                remark: $("#workflow_input_remark").val(),
                sort: $("#workflow_input_sort").val()
            }
            var newinput = modelData['input'];
            if ($('#workflow_input_isnew').val() == "1") {
                var exist = false;
                for (i = 0; i < newinput.length; i++) {
                    if ($('#workflow_input_code').val() == newinput[i]["code"]) {
                        alert("参数编码已存在")
                        var exist = true;
                        break;
                    } else if ($('#workflow_input_name').val() == newinput[i]["name"]) {
                        alert("参数名称已存在")
                        var exist = true;
                        break;
                    }
                }

                if (!exist) {
                    newinput.push(editoptionval)
                    $("#workflow_input").append('<option value="' + $("#workflow_input_code").val() + '">' + $('#workflow_input_name').val() + '</option>')
                } else {
                    return
                }
            }
            else {
                for (i = 0; i < newinput.length; i++) {
                    if ($('#workflow_input_code').val() == newinput[i]["code"]) {
                        newinput[i] = editoptionval;
                        $("#workflow_input option:selected").text($('#workflow_input_name').val());
                        break;
                    }
                }

            }
            diagram.model.setDataProperty(modelData, "input", newinput);
            $('#workflow_input_isnew').val("0")
            $('#workflow_input_code').prop("readonly", true);
            $('#workflow_input_del').show();
        });

        $('#workflow_input').click(function () {
            var selectval = $("#workflow_input option:selected").val();
            for (i = 0; i < workflowinput.length; i++) {
                if (workflowinput[i]["code"] == selectval) {
                    $('#workflow_input_isnew').val("0")
                    $('#workflow_input_code').prop("readonly", true);
                    $('#workflow_input_del').show();
                    $('#workflow_input_code').val(workflowinput[i]["code"])
                    $('#workflow_input_name').val(workflowinput[i]["name"])
                    $('#workflow_input_type').val(workflowinput[i]["type"])
                    $('#workflow_input_source').val(workflowinput[i]["source"])
                    $('#workflow_input_sort').val(workflowinput[i]["sort"])
                    $('#workflow_input_remark').val(workflowinput[i]["remark"])
                    $('#workflow_input_value').val(workflowinput[i]["value"])
                }
            }

        });

        $('#workflow_input_new').click(function () {
            $('#workflow_input_isnew').val("1")
            $('#workflow_input_code').prop("readonly", false);
            $('#workflow_input_code').val("")
            $('#workflow_input_name').val("")
            $('#workflow_input_type').val("")
            $('#workflow_input_source').val("")
            $('#workflow_input_sort').val("")
            $('#workflow_input_remark').val("")
            $('#workflow_input_value').val("")
            $('#workflow_input_del').hide();
        });

        $('#workflow_input_del').click(function () {
            var selectval = $("#workflow_input option:selected").val();
            for (i = 0; i < workflowinput.length; i++) {
                if (workflowinput[i]["code"] == selectval) {
                    workflowinput.splice(i, 1);
                    $("#workflow_input option:selected").remove();
                    diagram.model.setDataProperty(modelData, "input", workflowinput);
                    $('#workflow_input_isnew').val("1")
                    $('#workflow_input_code').prop("readonly", false);
                    $('#workflow_input_code').val("")
                    $('#workflow_input_name').val("")
                    $('#workflow_input_type').val("")
                    $('#workflow_input_source').val("")
                    $('#workflow_input_sort').val("")
                    $('#workflow_input_remark').val("")
                    $('#workflow_input_value').val("")
                    $('#workflow_input_del').hide();
                }
            }

        });


        //临时变量
        $("#workflow_variable").empty();
        var workflowvariable = modelData['variable'];
        for (i = 0; i < workflowvariable.length; i++) {
            $("#workflow_variable").append('<option value="' + workflowvariable[i]["code"] + '">' + workflowvariable[i]["name"] + '</option>')
        }
        $('#workflow_variable_del').hide();
        $('#workflow_variable_isnew').val("1")
        $('#workflow_variable_code').prop("readonly", false);
        $('#workflow_variable_code').val("")
        $('#workflow_variable_name').val("")
        $('#workflow_variable_type').val("")
        $('#workflow_variable_sort').val("")
        $('#workflow_variable_remark').val("")
        $('#workflow_variable_value').val("")

        $('#workflow_variable_save').click(function () {
            if ($('#workflow_variable_code').val() == "") {
                alert("参数编码不能为空。")
                return
            }
            if ($('#workflow_variable_name').val() == "") {
                alert("参数名称不能为空。")
                return
            }
            if ($('#workflow_variable_type').val() == "") {
                alert("数据类型不能为空。")
                return
            }

            if ($('#workflow_variable_sort').val() == "") {
                alert("序号不能为空。")
                return
            }
            var editoptionval = {
                code: $("#workflow_variable_code").val(),
                name: $("#workflow_variable_name").val(),
                type: $("#workflow_variable_type").val(),
                value: $("#workflow_variable_value").val(),
                remark: $("#workflow_variable_remark").val(),
                sort: $("#workflow_variable_sort").val()
            }
            var newvariable = modelData['variable'];
            if ($('#workflow_variable_isnew').val() == "1") {
                var exist = false;
                for (i = 0; i < newvariable.length; i++) {
                    if ($('#workflow_variable_code').val() == newvariable[i]["code"]) {
                        alert("参数编码已存在")
                        var exist = true;
                        break;
                    } else if ($('#workflow_variable_name').val() == newvariable[i]["name"]) {
                        alert("参数名称已存在")
                        var exist = true;
                        break;
                    }
                }

                if (!exist) {
                    newvariable.push(editoptionval)
                    $("#workflow_variable").append('<option value="' + $("#workflow_variable_code").val() + '">' + $('#workflow_variable_name').val() + '</option>')
                } else {
                    return
                }
            }
            else {
                for (i = 0; i < newvariable.length; i++) {
                    if ($('#workflow_variable_code').val() == newvariable[i]["code"]) {
                        newvariable[i] = editoptionval;
                        $("#workflow_variable option:selected").text($('#workflow_variable_name').val());
                        break;
                    }
                }

            }
            diagram.model.setDataProperty(modelData, "variable", newvariable);
            $('#workflow_variable_isnew').val("0")
            $('#workflow_variable_code').prop("readonly", true);
            $('#workflow_variable_del').show();
        });

        $('#workflow_variable').click(function () {
            var selectval = $("#workflow_variable option:selected").val();
            for (i = 0; i < workflowvariable.length; i++) {
                if (workflowvariable[i]["code"] == selectval) {
                    $('#workflow_variable_isnew').val("0")
                    $('#workflow_variable_code').prop("readonly", true);
                    $('#workflow_variable_del').show();
                    $('#workflow_variable_code').val(workflowvariable[i]["code"])
                    $('#workflow_variable_name').val(workflowvariable[i]["name"])
                    $('#workflow_variable_type').val(workflowvariable[i]["type"])
                    $('#workflow_variable_sort').val(workflowvariable[i]["sort"])
                    $('#workflow_variable_remark').val(workflowvariable[i]["remark"])
                    $('#workflow_variable_value').val(workflowvariable[i]["value"])
                }
            }

        });

        $('#workflow_variable_new').click(function () {
            $('#workflow_variable_isnew').val("1")
            $('#workflow_variable_code').prop("readonly", false);
            $('#workflow_variable_code').val("")
            $('#workflow_variable_name').val("")
            $('#workflow_variable_type').val("")
            $('#workflow_variable_sort').val("")
            $('#workflow_variable_remark').val("")
            $('#workflow_variable_value').val("")
            $('#workflow_variable_del').hide();
        });

        $('#workflow_variable_del').click(function () {
            var selectval = $("#workflow_variable option:selected").val();
            for (i = 0; i < workflowvariable.length; i++) {
                if (workflowvariable[i]["code"] == selectval) {
                    workflowvariable.splice(i, 1);
                    $("#workflow_variable option:selected").remove();
                    diagram.model.setDataProperty(modelData, "variable", workflowvariable);
                    $('#workflow_variable_isnew').val("1")
                    $('#workflow_variable_code').prop("readonly", false);
                    $('#workflow_variable_code').val("")
                    $('#workflow_variable_name').val("")
                    $('#workflow_variable_type').val("")
                    $('#workflow_variable_sort').val("")
                    $('#workflow_variable_remark').val("")
                    $('#workflow_variable_value').val("")
                    $('#workflow_variable_del').hide();
                }
            }

        });

        //流程输出
        $("#workflow_output").empty();
        var workflowoutput = modelData['output'];
        for (i = 0; i < workflowoutput.length; i++) {
            $("#workflow_output").append('<option value="' + workflowoutput[i]["code"] + '">' + workflowoutput[i]["name"] + '</option>')
        }
        $('#workflow_output_del').hide();
        $('#workflow_output_isnew').val("1")
        $('#workflow_output_code').prop("readonly", false);
        $('#workflow_output_code').val("")
        $('#workflow_output_name').val("")
        $('#workflow_output_type').val("")
        $('#workflow_output_source').val("")
        $('#workflow_output_sort').val("")
        $('#workflow_output_remark').val("")
        $('#workflow_output_value').val("")

        $('#workflow_output_value').click(function () {
            var source=$('#workflow_output_source').val();
            if(source == "workfolwInput"){
                $('#modal_workflowinput').modal('show');
                var workflowinputdata = modelData['input'];
                var dataSet = workflowinputdata;
                var oldTable = $('#table_workflowinput').dataTable();
                oldTable.fnClearTable();
                oldTable.fnDestroy();
                $('#table_workflowinput').dataTable( {
                    "bAutoWidth": true,
                    "bPaginate": false,
                    "bSort": false,
                    "bFilter": false,
                    "bProcessing": true,
                    "data": dataSet,
                    "columns": [
                        {"data": "code"},
                        {"data": "name"},
                        {"data": "type"},
                        {"data": "remark"},
                        {"data": null},
                    ],
                    "columnDefs": [
                        {
                            "targets": -1,
                            "data": null,
                            "defaultContent": "<button  id='select' title='选择'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-check'></i></button>"
                        }

                    ],
                    "oLanguage": {
                        "sLengthMenu": "每页显示 _MENU_ 条记录",
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
                        "sZeroRecords": "没有检索到数据"
                    },
            } );
                $('#table_workflowinput tbody').on('click', 'button#select', function () {
                    var table = $('#table_workflowinput').DataTable();
                    $('#workflow_output_value').val(table.row($(this).parents('tr')).data().code)
                    $('#modal_workflowinput').modal('hide');
                });


            }else if(source == "workfolwVariable"){
                $('#modal_workfolwvariable').modal('show');
                var workflowvariabledata = modelData['variable'];
                var dataSet = workflowvariabledata;
                var oldTable = $('#table_workfolwvariable').dataTable();
                oldTable.fnClearTable();
                oldTable.fnDestroy();
                $('#table_workfolwvariable').dataTable( {
                    "bAutoWidth": true,
                    "bPaginate": false,
                    "bSort": false,
                    "bFilter": false,
                    "bProcessing": true,
                    "data": dataSet,
                    "columns": [
                        {"data": "code"},
                        {"data": "name"},
                        {"data": "type"},
                        {"data": "remark"},
                        {"data": null},
                    ],
                    "columnDefs": [
                        {
                            "targets": -1,
                            "data": null,
                            "defaultContent": "<button  id='select' title='选择'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-check'></i></button>"
                        }

                    ],
                    "oLanguage": {
                        "sLengthMenu": "每页显示 _MENU_ 条记录",
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
                        "sZeroRecords": "没有检索到数据"
                    },
            } );
                $('#table_workfolwvariable tbody').on('click', 'button#select', function () {
                    var table = $('#table_workfolwvariable').DataTable();
                    $('#workflow_output_value').val(table.row($(this).parents('tr')).data().code)
                    $('#modal_workfolwvariable').modal('hide');
                });
            }else if(source == "stepOutput"){
                $('#modal_stepoutput').modal('show');
                var steps = diagram.model.wc;
                $("#modal_stepoutput_step").empty();
                for (i = 0; i < steps.length; i++) {
                    $("#modal_stepoutput_step").append('<option value="' + steps[i]["key"] + '">' + steps[i]["text"] + '</option>')
                }

                for (i = 0; i < steps.length; i++) {
                    if(steps[i]["key"]==$("#modal_stepoutput_step").val()){

                        var stepoutdata = steps[i]["output"];
                        var dataSet = stepoutdata;
                        var oldTable = $('#table_stepoutput').dataTable();
                        oldTable.fnClearTable();
                        oldTable.fnDestroy();
                        $('#table_stepoutput').dataTable( {
                            "bAutoWidth": true,
                            "bPaginate": false,
                            "bSort": false,
                            "bFilter": false,
                            "bProcessing": true,
                            "data": dataSet,
                            "columns": [
                                {"data": "code"},
                                {"data": "name"},
                                {"data": "type"},
                                {"data": "remark"},
                                {"data": null},
                            ],
                            "columnDefs": [
                                {
                                    "targets": -1,
                                    "data": null,
                                    "defaultContent": "<button  id='select' title='选择'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-check'></i></button>"
                                }

                            ],
                            "oLanguage": {
                                "sLengthMenu": "每页显示 _MENU_ 条记录",
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
                                "sZeroRecords": "没有检索到数据"
                            },
                    } );
                        $('#table_stepoutput tbody').on('click', 'button#select', function () {
                            var table = $('#table_stepoutput').DataTable();
                            $('#workflow_output_value').val(table.row($(this).parents('tr')).data().code)
                            $('#modal_stepoutput').modal('hide');
                        });
                        break;
                    }
                }

                $("#modal_stepoutput_step").change(function () {
                    for (i = 0; i < steps.length; i++) {
                        if(steps[i]["key"]==$("#modal_stepoutput_step").val()){

                            var stepoutdata = steps[i]["output"];
                            var dataSet = stepoutdata;
                            var oldTable = $('#table_stepoutput').dataTable();
                            oldTable.fnClearTable();
                            oldTable.fnDestroy();
                            $('#table_stepoutput').dataTable( {
                                "bAutoWidth": true,
                                "bPaginate": false,
                                "bSort": false,
                                "bFilter": false,
                                "bProcessing": true,
                                "data": dataSet,
                                "columns": [
                                    {"data": "code"},
                                    {"data": "name"},
                                    {"data": "type"},
                                    {"data": "remark"},
                                    {"data": null},
                                ],
                                "columnDefs": [
                                    {
                                        "targets": -1,
                                        "data": null,
                                        "defaultContent": "<button  id='select' title='选择'  class='btn btn-xs btn-primary' type='button'><i class='fa fa-check'></i></button>"
                                    }

                                ],
                                "oLanguage": {
                                    "sLengthMenu": "每页显示 _MENU_ 条记录",
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
                                    "sZeroRecords": "没有检索到数据"
                                },
                        } );
                            $('#table_stepoutput tbody').on('click', 'button#select', function () {
                                var table = $('#table_stepoutput').DataTable();
                                $('#workflow_output_value').val($("#modal_stepoutput_step").val()+ "^" + table.row($(this).parents('tr')).data().code)
                                $('#modal_stepoutput').modal('hide');
                            });
                            break;
                        }
                    }
                });



            }


        });

        $('#workflow_output_save').click(function () {
            if ($('#workflow_output_code').val() == "") {
                alert("参数编码不能为空。")
                return
            }
            if ($('#workflow_output_name').val() == "") {
                alert("参数名称不能为空。")
                return
            }
            if ($('#workflow_output_type').val() == "") {
                alert("数据类型不能为空。")
                return
            }
            if ($('#workflow_output_source').val() == "") {
                alert("数据来源不能为空。")
                return
            }
            if ($('#workflow_output_sort').val() == "") {
                alert("序号不能为空。")
                return
            }
            var editoptionval = {
                code: $("#workflow_output_code").val(),
                name: $("#workflow_output_name").val(),
                type: $("#workflow_output_type").val(),
                source: $("#workflow_output_source").val(),
                value: $("#workflow_output_value").val(),
                remark: $("#workflow_output_remark").val(),
                sort: $("#workflow_output_sort").val()
            }
            var newoutput = modelData['output'];
            if ($('#workflow_output_isnew').val() == "1") {
                var exist = false;
                for (i = 0; i < newoutput.length; i++) {
                    if ($('#workflow_output_code').val() == newoutput[i]["code"]) {
                        alert("参数编码已存在")
                        var exist = true;
                        break;
                    } else if ($('#workflow_output_name').val() == newoutput[i]["name"]) {
                        alert("参数名称已存在")
                        var exist = true;
                        break;
                    }
                }

                if (!exist) {
                    newoutput.push(editoptionval)
                    $("#workflow_output").append('<option value="' + $("#workflow_output_code").val() + '">' + $('#workflow_output_name').val() + '</option>')
                } else {
                    return
                }
            }
            else {
                for (i = 0; i < newoutput.length; i++) {
                    if ($('#workflow_output_code').val() == newoutput[i]["code"]) {
                        newoutput[i] = editoptionval;
                        $("#workflow_output option:selected").text($('#workflow_output_name').val());
                        break;
                    }
                }

            }
            diagram.model.setDataProperty(modelData, "output", newoutput);
            $('#workflow_output_isnew').val("0")
            $('#workflow_output_code').prop("readonly", true);
            $('#workflow_output_del').show();
        });

        $('#workflow_output').click(function () {
            var selectval = $("#workflow_output option:selected").val();
            for (i = 0; i < workflowoutput.length; i++) {
                if (workflowoutput[i]["code"] == selectval) {
                    $('#workflow_output_isnew').val("0")
                    $('#workflow_output_code').prop("readonly", true);
                    $('#workflow_output_del').show();
                    $('#workflow_output_code').val(workflowoutput[i]["code"])
                    $('#workflow_output_name').val(workflowoutput[i]["name"])
                    $('#workflow_output_type').val(workflowoutput[i]["type"])
                    $('#workflow_output_source').val(workflowoutput[i]["source"])
                    $('#workflow_output_sort').val(workflowoutput[i]["sort"])
                    $('#workflow_output_remark').val(workflowoutput[i]["remark"])
                    $('#workflow_output_value').val(workflowoutput[i]["value"])
                }
            }

        });

        $('#workflow_output_new').click(function () {
            $('#workflow_output_isnew').val("1")
            $('#workflow_output_code').prop("readonly", false);
            $('#workflow_output_code').val("")
            $('#workflow_output_name').val("")
            $('#workflow_output_type').val("")
            $('#workflow_output_source').val("")
            $('#workflow_output_sort').val("")
            $('#workflow_output_remark').val("")
            $('#workflow_output_value').val("")
            $('#workflow_output_del').hide();
        });

        $('#workflow_output_del').click(function () {
            var selectval = $("#workflow_output option:selected").val();
            for (i = 0; i < workflowoutput.length; i++) {
                if (workflowoutput[i]["code"] == selectval) {
                    workflowoutput.splice(i, 1);
                    $("#workflow_output option:selected").remove();
                    diagram.model.setDataProperty(modelData, "output", workflowoutput);
                    $('#workflow_output_isnew').val("1")
                    $('#workflow_output_code').prop("readonly", false);
                    $('#workflow_output_code').val("")
                    $('#workflow_output_name').val("")
                    $('#workflow_output_type').val("")
                    $('#workflow_output_source').val("")
                    $('#workflow_output_sort').val("")
                    $('#workflow_output_remark').val("")
                    $('#workflow_output_value').val("")
                    $('#workflow_output_del').hide();
                }
            }

        });

    }

}
;

