"use strict";
function guid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}

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
    selectedObject= {};

    if (inspectedObject instanceof go.Part) {
        $('#div_workflow').hide();
        var nodeData = inspectedObject.data;

        if (this.inspectedObject instanceof go.Node) {
            $('#div_line').hide();
            $('#div_node').show();
            var stepData = inspectedObject.data
            var modelData = diagram.model.modelData;
            selectedObject= {type:"node",key:stepData['key']};

            //步骤信息
            $('#step_modeltype').val(stepData['modeltype']);
            $('#step_guid').val(stepData['modelguid']);
            $('#step_modelname').val(stepData['modelname']);
            $('#step_stepid').val(stepData['key']);
            $('#step_name').val(stepData['text']);
            $('#step_name').unbind("change");

            $('#step_name').change(function () {
                diagram.startTransaction('修改流程');
                diagram.model.setDataProperty(stepData, "text", $('#step_name').val());
                diagram.commitTransaction('修改流程');
            });

            //步骤输入
            if($('#step_guid').val()=="c2d3f2b6-49a9-11eb-99aa-84fdd1a17907"){
                $('#stepinput_if').show();
                $('#stepinput_others').hide();

                $("#step_criteria").empty();
                var stepinput = JSON.parse(stepData['input']);
                for (var i = 0; i < stepinput.length; i++) {
                    if (stepinput[i]["code"] == "criteria") {
                        var stepcriteria = stepinput[i]["value"];
                        if(stepcriteria) {
                            try {
                                stepcriteria = JSON.parse(stepcriteria);
                            } catch {
                                stepcriteria = []
                            }
                        }
                        else {
                            stepcriteria=[]
                        }
                        for (var j = 0; j < stepcriteria.length; j++) {
                            $("#step_criteria").append('<option value="' + stepcriteria[j]["id"] + '">' + stepcriteria[j]["name"] + '</option>')
                        }
                        break;
                    }
                }
                $('#step_criteria_name').prop("readonly", true);
                $('#step_criteria_logic').prop("disabled", true);
                $('#step_criteria_type').prop("disabled", true);
                $('#step_criteria_source_left').prop("disabled", true);
                $('#step_criteria_value_left').prop("readonly", true);
                $('#step_criteria_char').prop("disabled", true);
                $('#step_criteria_source_right').prop("disabled", true);
                $('#step_criteria_value_right').prop("readonly", true);

                $('#step_criteria_del').hide();
                $('#step_criteria_save').hide();

                $('#step_criteria_isnew').val("1")
                $('#step_criteria_id').val("")
                $('#step_criteria_name').val("")
                $('#step_criteria_logic').val("")
                $('#step_criteria_type').val("")
                $('#step_criteria_source_left').val("")
                $('#step_criteria_value_left').val("")
                $('#step_criteria_char').val("")
                $('#step_criteria_source_right').val("")
                $('#step_criteria_value_right').val("")


                $('#step_criteria_save').unbind("click");
                $('#step_criteria').unbind("click");
                $('#step_criteria_new').unbind("click");
                $('#step_criteria_del').unbind("click");
                $('#step_criteria_value_left').unbind("click");
                $('#step_criteria_value_right').unbind("click");


                $('#step_criteria_value_left').click(function () {
                    var source=$('#step_criteria_source_left').val();
                    if(source == "workfolwInput"){
                        $('#modal_workflowinput').modal('show');
                        var workflowinputdata = JSON.parse(modelData['input']);
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
                                {"data": null},
                            ],
                            "columnDefs": [
                                {
                                    "targets": -2,
                                    "render": function (data, type, full) {
                                        if (data.type == "json") {
                                            return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_workflowinput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                        }
                                    }
                                }, {
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
                            var param_key = ""
                            var param_key_value = $('#table_workflowinput_type_' + table.row($(this).parents('tr')).data().code).val()
                            if (param_key_value!="" && param_key_value!=undefined){
                                param_key = "-->" + param_key_value;
                            }
                            $('#step_criteria_value_left').val(table.row($(this).parents('tr')).data().code + param_key)
                            $('#modal_workflowinput').modal('hide');
                        });


                    }
                    else if(source == "workfolwVariable"){
                        $('#modal_workfolwvariable').modal('show');
                        var workflowvariabledata = JSON.parse(modelData['variable']);
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
                                {"data": null},
                            ],
                            "columnDefs": [
                                {
                                    "targets": -2,
                                    "render": function (data, type, full) {
                                        if (data.type == "json") {
                                            return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_variable_type_" + data.code + "' name='table_variable_type'  type='text'></input>"
                                        }
                                    }
                                }, {
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
                            var param_key = ""
                            var param_key_value = $('#table_workfolwvariable_type_' + table.row($(this).parents('tr')).data().code).val()
                            if (param_key_value!="" && param_key_value!=undefined){
                                param_key = "-->" + param_key_value;
                            }
                            $('#step_criteria_value_left').val(table.row($(this).parents('tr')).data().code+param_key)
                            $('#modal_workfolwvariable').modal('hide');
                        });
                    }
                    else if(source == "stepOutput"){
                        $('#modal_stepoutput').modal('show');
                        var steps = diagram.model.wc;
                        $("#modal_stepoutput_step").empty();
                        for (var i = 0; i < steps.length; i++) {
                            $("#modal_stepoutput_step").append('<option value="' + steps[i]["key"] + '">' + steps[i]["text"] + '</option>')
                        }

                        for (var i = 0; i < steps.length; i++) {
                            if(steps[i]["key"]==$("#modal_stepoutput_step").val()){

                                var stepoutdata = JSON.parse(steps[i]["output"]);
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
                                        {"data": null},
                                    ],
                                    "columnDefs": [
                                        {
                                            "targets": -2,
                                            "render": function (data, type, full) {
                                                if (data.type == "json") {
                                                    return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_stepoutput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                                }
                                            }
                                        },
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
                                    var param_key = ""
                                    var param_key_value = $('#table_stepoutput_type_' + table.row($(this).parents('tr')).data().code).val()
                                    if (param_key_value!="" && param_key_value!=undefined){
                                        param_key = "-->" + param_key_value;
                                    }
                                    $('#step_criteria_value_left').val($("#modal_stepoutput_step").val()+ "^" + table.row($(this).parents('tr')).data().code + param_key)

                                    $('#modal_stepoutput').modal('hide');
                                });
                                break;
                            }
                        }

                        $('#modal_stepoutput_step').unbind("change");
                        $("#modal_stepoutput_step").change(function () {
                            for (var i = 0; i < steps.length; i++) {
                                if(steps[i]["key"]==$("#modal_stepoutput_step").val()){

                                    var stepoutdata = JSON.parse(steps[i]["output"]);
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
                                            {"data": null},
                                        ],
                                        "columnDefs": [
                                            {
                                                "targets": -2,
                                                "render": function (data, type, full) {
                                                    if (data.type == "json") {
                                                        return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_stepoutput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                                    }
                                                }
                                            },{
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
                                        var param_key = ""
                                        var param_key_value = $('#table_stepoutput_type_' + table.row($(this).parents('tr')).data().code).val()
                                        if (param_key_value!="" && param_key_value!=undefined){
                                            param_key = "-->" + param_key_value;
                                        }
                                        $('#step_criteria_value_left').val($("#modal_stepoutput_step").val()+ "^" + table.row($(this).parents('tr')).data().code + param_key)

                                        $('#modal_stepoutput').modal('hide');
                                    });
                                    break;
                                }
                            }
                        });



                    }
                });

                $('#step_criteria_value_right').click(function () {
                    var source=$('#step_criteria_source_right').val();
                    if(source == "workfolwInput"){
                        $('#modal_workflowinput').modal('show');
                        var workflowinputdata = JSON.parse(modelData['input']);
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
                                {"data": null},
                            ],
                            "columnDefs": [
                                {
                                    "targets": -2,
                                    "render": function (data, type, full) {
                                        if (data.type == "json") {
                                            return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_workflowinput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                        }
                                    }
                                }, {
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
                            var param_key = ""
                            var param_key_value = $('#table_workflowinput_type_' + table.row($(this).parents('tr')).data().code).val()
                            if (param_key_value!="" && param_key_value!=undefined){
                                param_key = "-->" + param_key_value;
                            }
                            $('#step_criteria_value_right').val(table.row($(this).parents('tr')).data().code+param_key)
                            $('#modal_workflowinput').modal('hide');
                        });


                    }
                    else if(source == "workfolwVariable"){
                        $('#modal_workfolwvariable').modal('show');
                        var workflowvariabledata = JSON.parse(modelData['variable']);
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
                                {"data": null},
                            ],
                            "columnDefs": [
                                {
                                    "targets": -2,
                                    "render": function (data, type, full) {
                                        if (data.type == "json") {
                                            return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_variable_type_" + data.code + "' name='table_variable_type'  type='text'></input>"
                                        }
                                    }
                                },{
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
                            var param_key = ""
                            var param_key_value = $('#table_workfolwvariable_type_' + table.row($(this).parents('tr')).data().code).val()
                            if (param_key_value!="" && param_key_value!=undefined){
                                param_key = "-->" + param_key_value;
                            }
                            $('#step_criteria_value_right').val(table.row($(this).parents('tr')).data().code+param_key)
                            $('#modal_workfolwvariable').modal('hide');
                        });
                    }
                    else if(source == "stepOutput"){
                        $('#modal_stepoutput').modal('show');
                        var steps = diagram.model.wc;
                        $("#modal_stepoutput_step").empty();
                        for (var i = 0; i < steps.length; i++) {
                            $("#modal_stepoutput_step").append('<option value="' + steps[i]["key"] + '">' + steps[i]["text"] + '</option>')
                        }

                        for (var i = 0; i < steps.length; i++) {
                            if(steps[i]["key"]==$("#modal_stepoutput_step").val()){

                                var stepoutdata = JSON.parse(steps[i]["output"]);
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
                                        {"data": null},
                                    ],
                                    "columnDefs": [
                                        {
                                            "targets": -2,
                                            "render": function (data, type, full) {
                                                if (data.type == "json") {
                                                    return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_stepoutput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                                }
                                            }
                                        },{
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
                                    var param_key = ""
                                    var param_key_value = $('#table_stepoutput_type_' + table.row($(this).parents('tr')).data().code).val()
                                    if (param_key_value!="" && param_key_value!=undefined){
                                        param_key = "-->" + param_key_value;
                                    }
                                    $('#step_criteria_value_right').val($("#modal_stepoutput_step").val()+ "^" + table.row($(this).parents('tr')).data().code + param_key)
                                    $('#modal_stepoutput').modal('hide');
                                });
                                break;
                            }
                        }

                        $('#modal_stepoutput_step').unbind("change");
                        $("#modal_stepoutput_step").change(function () {
                            for (var i = 0; i < steps.length; i++) {
                                if(steps[i]["key"]==$("#modal_stepoutput_step").val()){

                                    var stepoutdata = JSON.parse(steps[i]["output"]);
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
                                            {"data": null},
                                        ],
                                        "columnDefs": [
                                            {
                                                "targets": -2,
                                                "render": function (data, type, full) {
                                                    if (data.type == "json") {
                                                        return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_stepoutput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                                    }
                                                }
                                            },{
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
                                        var param_key = ""
                                        var param_key_value = $('#table_stepoutput_type_' + table.row($(this).parents('tr')).data().code).val()
                                        if (param_key_value!="" && param_key_value!=undefined){
                                            param_key = "-->" + param_key_value;
                                        }
                                        $('#step_criteria_value_right').val($("#modal_stepoutput_step").val()+ "^" + table.row($(this).parents('tr')).data().code + param_key)

                                        $('#modal_stepoutput').modal('hide');
                                    });
                                    break;
                                }
                            }
                        });



                    }
                });

                $('#step_criteria_save').click(function () {
                    if ($('#step_criteria_name').val() == "") {
                        alert("判断名称。")
                        return
                    }
                    if ($('#step_criteria_logic').val() == "") {
                        alert("逻辑符。")
                        return
                    }
                    if ($('#step_criteria_type').val() == "") {
                        alert("数据类型不能为空。")
                        return
                    }
                    if ($('#step_criteria_source_left').val() == "") {
                        alert("左侧来源。")
                        return
                    }
                    if ($('#step_criteria_value_left').val() == "") {
                        alert("左侧值。")
                        return
                    }
                    if ($('#step_criteria_char').val() == "") {
                        alert("操作符。")
                        return
                    }
                    if ($('#step_criteria_source_right').val() == "") {
                        alert("又侧来源。")
                        return
                    }
                    if ($('#step_criteria_value_right').val() == "") {
                        alert("又侧值。")
                        return
                    }
                    var editoptionval = {
                        id: $("#step_criteria_id").val(),
                        name: $("#step_criteria_name").val(),
                        logic: $("#step_criteria_logic").val(),
                        type: $("#step_criteria_type").val(),
                        left_source: $("#step_criteria_source_left").val(),
                        left_value: $("#step_criteria_value_left").val(),
                        char: $("#step_criteria_char").val(),
                        right_source: $("#step_criteria_source_right").val(),
                        right_value: $("#step_criteria_value_right").val(),
                    }

                    var newstepinput = JSON.parse(stepData['input']);
                    var newstepcriteria = []
                    for (var i = 0; i < newstepinput.length; i++) {
                        if (newstepinput[i]["code"] == "criteria") {
                            newstepcriteria = newstepinput[i]["value"];
                            if(newstepcriteria) {
                                try {
                                    newstepcriteria = JSON.parse(newstepcriteria);
                                } catch {
                                    newstepcriteria = []
                                }
                            }
                            else{
                                newstepcriteria = []
                            }
                        }
                    }
                    if ($('#step_criteria_isnew').val() == "1") {
                        var exist = false;

                        for (var i = 0; i < newstepcriteria.length; i++) {
                            if ($('#step_criteria_name').val() == newstepcriteria[i]["name"]) {
                                alert("参数名称已存在")
                                var exist = true;
                                break;
                            }
                        }

                        if (!exist) {
                            var tid = guid();
                            editoptionval["id"] = tid;
                            $("#step_criteria_id").val(tid),
                            newstepcriteria.push(editoptionval)
                            $("#step_criteria").append('<option value="' + tid + '">' + $('#step_criteria_name').val() + '</option>')
                        } else {
                            return
                        }
                    }
                    else {
                        for (var i = 0; i < newstepcriteria.length; i++) {
                            if ($('#step_criteria_id').val() == newstepcriteria[i]["id"]) {
                                newstepcriteria[i] = editoptionval;
                                $("#step_criteria option:selected").text($('#step_criteria_name').val());
                                break;
                            }
                        }

                    }

                    for (var i = 0; i < newstepinput.length; i++) {
                        if (newstepinput[i]["code"] == "criteria") {
                            newstepinput[i]["value"] = JSON.stringify(newstepcriteria);
                            break;

                        }
                    }

                    diagram.model.setDataProperty(stepData, "input", JSON.stringify(newstepinput));


                    $('#step_criteria_isnew').val("0")
                    $('#step_criteria_del').show();
                    $('#step_criteria').val($("#step_criteria_id").val())
                });

                $('#step_criteria').click(function () {
                    var selectval = $("#step_criteria option:selected").val();
                    for (var i = 0; i < stepcriteria.length; i++) {
                        if (stepcriteria[i]["id"] == selectval) {
                            $('#step_criteria_name').prop("readonly", false);
                            $('#step_criteria_logic').prop("disabled", false);
                            $('#step_criteria_type').prop("disabled", false);
                            $('#step_criteria_source_left').prop("disabled", false);
                            $('#step_criteria_value_left').prop("readonly", false);
                            $('#step_criteria_char').prop("disabled", false);
                            $('#step_criteria_source_right').prop("disabled", false);
                            $('#step_criteria_value_right').prop("readonly", false);

                            $('#step_criteria_del').show();
                            $('#step_criteria_save').show();

                            $('#step_criteria_isnew').val("0")
                            $('#step_criteria_id').val(stepcriteria[i]["id"])
                            $('#step_criteria_name').val(stepcriteria[i]["name"])
                            $('#step_criteria_logic').val(stepcriteria[i]["logic"])
                            $('#step_criteria_type').val(stepcriteria[i]["type"])
                            $('#step_criteria_source_left').val(stepcriteria[i]["left_source"])
                            $('#step_criteria_value_left').val(stepcriteria[i]["left_value"])
                            $('#step_criteria_char').val(stepcriteria[i]["char"])
                            $('#step_criteria_source_right').val(stepcriteria[i]["right_source"])
                            $('#step_criteria_value_right').val(stepcriteria[i]["right_value"])
                            break;
                        }
                    }

                });

                $('#step_criteria_new').click(function () {
                    $('#step_criteria_name').prop("readonly", false);
                    $('#step_criteria_logic').prop("disabled", false);
                    $('#step_criteria_type').prop("disabled", false);
                    $('#step_criteria_source_left').prop("disabled", false);
                    $('#step_criteria_value_left').prop("readonly", false);
                    $('#step_criteria_char').prop("disabled", false);
                    $('#step_criteria_source_right').prop("disabled", false);
                    $('#step_criteria_value_right').prop("readonly", false);

                    $('#step_criteria_del').hide();
                    $('#step_criteria_save').show();

                    $('#step_criteria_isnew').val("1")
                    $('#step_criteria_id').val("")
                    $('#step_criteria_name').val("")
                    $('#step_criteria_logic').val("")
                    $('#step_criteria_type').val("")
                    $('#step_criteria_source_left').val("")
                    $('#step_criteria_value_left').val("")
                    $('#step_criteria_char').val("")
                    $('#step_criteria_source_right').val("")
                    $('#step_criteria_value_right').val("")
                });

                $('#step_criteria_del').click(function () {
                    var newstepinput = JSON.parse(stepData['input']);
                    var newstepcriteria = []
                    for (var i = 0; i < newstepinput.length; i++) {
                        if (newstepinput[i]["code"] == "criteria") {
                            newstepcriteria = newstepinput[i]["value"];
                            if(newstepcriteria) {
                                try {
                                        newstepcriteria = JSON.parse(newstepcriteria);
                                } catch {
                                        newstepcriteria = []
                                }
                            }
                            else {
                                newstepcriteria=[]
                            }
                            break;
                        }
                    }
                    var selectval = $("#step_criteria option:selected").val();
                    for (var i = 0; i < newstepcriteria.length; i++) {
                        if ($('#step_criteria_id').val() == newstepcriteria[i]["id"]) {
                            newstepcriteria.splice(i, 1);
                            break;
                        }
                    }
                    for (var i = 0; i < newstepinput.length; i++) {
                        if (newstepinput[i]["code"] == "criteria") {
                            newstepinput[i]["value"] = JSON.stringify(newstepcriteria);

                            diagram.model.setDataProperty(stepData, "input", JSON.stringify(newstepinput));

                            $("#step_criteria option:selected").remove();

                            $('#step_criteria_del').hide();

                            $('#step_criteria_isnew').val("1")
                            $('#step_criteria_id').val("")
                            $('#step_criteria_name').val("")
                            $('#step_criteria_logic').val("")
                            $('#step_criteria_type').val("")
                            $('#step_criteria_source_left').val("")
                            $('#step_criteria_value_left').val("")
                            $('#step_criteria_char').val("")
                            $('#step_criteria_source_right').val("")
                            $('#step_criteria_value_right').val("")
                            break;

                        }
                    }
                });

            }
            else {
                $('#stepinput_if').hide();
                $('#stepinput_others').show();

                $("#step_input").empty();
                var stepinput = JSON.parse(stepData['input']);
                for (var i = 0; i < stepinput.length; i++) {
                    $("#step_input").append('<option value="' + stepinput[i]["code"] + '">' + stepinput[i]["name"] + '</option>')
                }
                $('#step_input_code').val("")
                $('#step_input_name').val("")
                $('#step_input_type').val("")
                $('#step_input_source').val("")
                $('#step_input_value').val("")
                $('#step_input_source').prop("disabled", true);
                $('#step_input_value').prop("readonly", true);

                $('#step_input').unbind("click");
                $('#step_input_source').unbind("change");
                $('#step_input_value').unbind("click");
                $('#step_input_value').unbind("change");

                $('#step_input').click(function () {
                    $('#step_input_source').prop("disabled", true);
                    $('#step_input_value').prop("readonly", true);
                    var selectval = $("#step_input option:selected").val();
                    for (var i = 0; i < stepinput.length; i++) {
                        if (stepinput[i]["code"] == selectval) {
                            $('#step_input_code').val(stepinput[i]["code"])
                            $('#step_input_name').val(stepinput[i]["name"])
                            $('#step_input_type').val(stepinput[i]["type"])
                            $('#step_input_source').val(stepinput[i]["source"])
                            $('#step_input_value').val(stepinput[i]["value"])
                            $('#step_input_source').removeAttr("disabled");
                            $('#step_input_value').removeAttr("readonly");
                            break;
                        }
                    }

                });
                $('#step_input_source').change(function () {
                    if ($('#step_input_source').val() == "function") {
                        $('#step_input_value_lable').text("公式");
                    } else if ($('#step_input_source').val() == "workfolwInput") {
                        $('#step_input_value_lable').text("参数名");
                    } else if ($('#step_input_source').val() == "workfolwVariable") {
                        $('#step_input_value_lable').text("变量名");
                    } else if ($('#step_input_source').val() == "stepOutput") {
                        $('#step_input_value_lable').text("步骤及参数");
                    }else {
                        $('#step_input_value_lable').text("值");
                    }

                    var newstepinput = JSON.parse(stepData['input']);
                    for (var i = 0; i < newstepinput.length; i++) {
                        if ($('#step_input_code').val() == newstepinput[i]["code"]) {
                            newstepinput[i]["source"] = $('#step_input_source').val();
                            break;
                        }
                    }


                    diagram.model.setDataProperty(stepData, "input", JSON.stringify(newstepinput));

                });
                $('#step_input_value').change(function () {
                    var newstepinput = JSON.parse(stepData['input']);
                    for (var i = 0; i < newstepinput.length; i++) {
                        if ($('#step_input_code').val() == newstepinput[i]["code"]) {
                            newstepinput[i]["value"] = $('#step_input_value').val();
                            break;
                        }
                    }


                    diagram.model.setDataProperty(stepData, "input", JSON.stringify(newstepinput));


                });
                $('#step_input_value').click(function () {
                    var source = $('#step_input_source').val();
                    if (source == "workfolwInput") {
                        $('#modal_workflowinput').modal('show');
                        var workflowinputdata = JSON.parse(modelData['input']);
                        var dataSet = workflowinputdata;
                        var oldTable = $('#table_workflowinput').dataTable();
                        oldTable.fnClearTable();
                        oldTable.fnDestroy();
                        $('#table_workflowinput').dataTable({
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
                                {"data": null},
                            ],
                            "columnDefs": [
                                {
                                    "targets": -2,
                                    "render": function (data, type, full) {
                                        if (data.type == "json") {
                                            return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_workflowinput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                        }
                                        else{
                                            return ""
                                        }
                                    }
                                },
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
                        });
                        $('#table_workflowinput tbody').on('click', 'button#select', function () {
                            var table = $('#table_workflowinput').DataTable();
                            var param_key = ""
                            var param_key_value = $('#table_workflowinput_type_' + table.row($(this).parents('tr')).data().code).val()
                            if (param_key_value!="" && param_key_value!=undefined){
                                param_key = "-->" + param_key_value;
                            }
                            $('#step_input_value').val(table.row($(this).parents('tr')).data().code+param_key)
                            $('#step_input_value').change();
                            $('#modal_workflowinput').modal('hide');
                        });


                    } else if (source == "workfolwVariable") {
                        $('#modal_workfolwvariable').modal('show');
                        var workflowvariabledata = JSON.parse(modelData['variable']);
                        var dataSet = workflowvariabledata;
                        var oldTable = $('#table_workfolwvariable').dataTable();
                        oldTable.fnClearTable();
                        oldTable.fnDestroy();
                        $('#table_workfolwvariable').dataTable({
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
                                {"data": null},
                            ],
                            "columnDefs": [
                                {
                                    "targets": -2,
                                    "render": function (data, type, full) {
                                        if (data.type == "json") {
                                            return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_variable_type_" + data.code + "' name='table_variable_type'  type='text'></input>"
                                        }
                                    }
                                },{
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
                        });
                        $('#table_workfolwvariable tbody').on('click', 'button#select', function () {
                            var table = $('#table_workfolwvariable').DataTable();
                            var param_key = ""
                            var param_key_value = $('#table_workfolwvariable_type_' + table.row($(this).parents('tr')).data().code).val()
                            if (param_key_value!="" && param_key_value!=undefined){
                                param_key = "-->" + param_key_value;
                            }
                            $('#step_input_value').val(table.row($(this).parents('tr')).data().code+param_key)
                            $('#step_input_value').change();
                            $('#modal_workfolwvariable').modal('hide');
                        });
                    } else if (source == "stepOutput") {
                        $('#modal_stepoutput').modal('show');
                        var steps = diagram.model.wc;
                        $("#modal_stepoutput_step").empty();
                        for (var i = 0; i < steps.length; i++) {
                            $("#modal_stepoutput_step").append('<option value="' + steps[i]["key"] + '">' + steps[i]["text"] + '</option>')
                        }

                        for (var i = 0; i < steps.length; i++) {
                            if (steps[i]["key"] == $("#modal_stepoutput_step").val()) {

                                var stepoutdata = JSON.parse(steps[i]["output"]);
                                var dataSet = stepoutdata;
                                var oldTable = $('#table_stepoutput').dataTable();
                                oldTable.fnClearTable();
                                oldTable.fnDestroy();
                                $('#table_stepoutput').dataTable({
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
                                        {"data": null},
                                    ],
                                    "columnDefs": [
                                        {
                                            "targets": -2,
                                            "render": function (data, type, full) {
                                                if (data.type == "json") {
                                                    return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_stepoutput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                                }
                                            }
                                        },{
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
                                });
                                $('#table_stepoutput tbody').on('click', 'button#select', function () {
                                    var table = $('#table_stepoutput').DataTable();
                                    var param_key = ""
                                    var param_key_value = $('#table_stepoutput_type_' + table.row($(this).parents('tr')).data().code).val()
                                    if (param_key_value!="" && param_key_value!=undefined){
                                        param_key = "-->" + param_key_value;
                                    }
                                    $('#step_input_value').val($("#modal_stepoutput_step").val()+ "^" + table.row($(this).parents('tr')).data().code + param_key)
                                    $('#step_input_value').change();
                                    $('#modal_stepoutput').modal('hide');
                                });
                                break;
                            }
                        }

                        $('#modal_stepoutput_step').unbind("change");
                        $("#modal_stepoutput_step").change(function () {
                            for (var i = 0; i < steps.length; i++) {
                                if (steps[i]["key"] == $("#modal_stepoutput_step").val()) {

                                    var stepoutdata = JSON.parse(steps[i]["output"]);
                                    var dataSet = stepoutdata;
                                    var oldTable = $('#table_stepoutput').dataTable();
                                    oldTable.fnClearTable();
                                    oldTable.fnDestroy();
                                    $('#table_stepoutput').dataTable({
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
                                            {"data": null},
                                        ],
                                        "columnDefs": [
                                            {
                                                "targets": -2,
                                                "render": function (data, type, full) {
                                                    if (data.type == "json") {
                                                        return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_stepoutput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                                    }
                                                }
                                            },{
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
                                    });
                                    $('#table_stepoutput tbody').on('click', 'button#select', function () {
                                        var table = $('#table_stepoutput').DataTable();
                                        var param_key = ""
                                        var param_key_value = $('#table_stepoutput_type_' + table.row($(this).parents('tr')).data().code).val()
                                        if (param_key_value!="" && param_key_value!=undefined){
                                            param_key = "-->" + param_key_value;
                                        }
                                        $('#step_input_value').val($("#modal_stepoutput_step").val()+ "^" + table.row($(this).parents('tr')).data().code + param_key)

                                        $('#step_input_value').change()
                                        $('#modal_stepoutput').modal('hide');
                                    });
                                    break;
                                }
                            }
                        });


                    }
                });
            }

            //步骤输出
            $("#step_output").empty();
            var stepoutput = JSON.parse(stepData['output']);
            for (var i = 0; i < stepoutput.length; i++) {
                $("#step_output").append('<option value="' + stepoutput[i]["code"] + '">' + stepoutput[i]["name"] + '</option>')
            }
            $("#step_output_to").empty();
            $("#step_output_to").append('<option value="">无</option>')

            var workflowvariable = JSON.parse(modelData['variable']);
            for (var i = 0; i < workflowvariable.length; i++) {
                $("#step_output_to").append('<option value="' + workflowvariable[i]["code"] + '">' + workflowvariable[i]["name"] + '</option>')
            }
            $('#step_output_code').val("")
            $('#step_output_name').val("")
            $('#step_output_type').val("")
            $('#step_output_to').val("")
            $('#step_output_to_type').val("")
            $('#step_output_to').prop("disabled", true);
            $('#step_output_to_type').prop("disabled", true);

            $('#step_output').unbind("click");
            $('#step_output_to').unbind("change");
            $('#step_output_to_type').unbind("change");


            $('#step_output').click(function () {
                $('#step_output_to').prop("disabled", true);
                $('#step_output_to_type').prop("disabled", true);
                var selectval = $("#step_output option:selected").val();
                for (var i = 0; i < stepoutput.length; i++) {
                    if (stepoutput[i]["code"] == selectval) {
                        $('#step_output_code').val(stepoutput[i]["code"])
                        $('#step_output_name').val(stepoutput[i]["name"])
                        $('#step_output_type').val(stepoutput[i]["type"])
                        $('#step_output_to').val(stepoutput[i]["to"])
                        $('#step_output_to_type').val(stepoutput[i]["totype"])
                        $('#step_output_to').removeAttr("disabled");
                        $('#step_output_to_type').removeAttr("disabled");
                        break;
                    }
                }

            });
            $('#step_output_to').change(function () {
                var newstepoutput = JSON.parse(stepData['output']);
                for (var i = 0; i < newstepoutput.length; i++) {
                    if ($('#step_output_code').val() == newstepoutput[i]["code"]) {
                        newstepoutput[i]["to"] = $('#step_output_to').val();
                        break;
                    }
                }

                diagram.model.setDataProperty(stepData, "output", JSON.stringify(newstepoutput));

            });
            $('#step_output_to_type').change(function () {
                var newstepoutput = JSON.parse(stepData['output']);
                for (var i = 0; i < newstepoutput.length; i++) {
                    if ($('#step_output_code').val() == newstepoutput[i]["code"]) {
                        newstepoutput[i]["totype"] = $('#step_output_to_type').val();
                        break;
                    }
                }


                diagram.model.setDataProperty(stepData, "output", JSON.stringify(newstepoutput));

            });
        }
        else if (this.inspectedObject instanceof go.Link) {
            $('#div_line').show();
            $('#div_node').hide();
            var lineData = inspectedObject.data
            var formnode_category = "";
            var formnode_text = "";
            var tonode_text = "";
            $("#line_criteria").empty();
            selectedObject= {type:"link",from:lineData['from'],to:lineData['to']};

            $('#div_criteria').hide();
            var steps = diagram.model.wc;
            for (var i = 0; i < steps.length; i++) {
                if(steps[i]["key"]==lineData['from']){
                    if(steps[i]["category"]=="for" || steps[i]["category"]=="if"){
                        $('#div_criteria').show();
                    }
                    formnode_category=steps[i]["category"]
                    formnode_text=steps[i]["text"]
                }
                if(steps[i]["key"]==lineData['to']){
                    tonode_text=steps[i]["text"]
                }
            }
            if (formnode_category == "for") {
                $("#line_criteria").append('<option value="True">结束</option>')
                $("#line_criteria").append('<option value="False">继续</option>')
            } else if (formnode_category == "if") {
                $("#line_criteria").append('<option value="True">Yes</option>')
                $("#line_criteria").append('<option value="False">No</option>')
            }

            $('#line_from').val(lineData['from']);
            $('#line_to').val(lineData['to']);
            $('#line_from_name').val(formnode_text);
            $('#line_to_name').val(tonode_text);
            $('#line_criteria').val(lineData['criteria']);
            $('#line_criteria').unbind("change");
            $('#line_criteria').change(function () {
                diagram.startTransaction('修改流程');
                diagram.model.setDataProperty(lineData, "criteria", $('#line_criteria').val());
                diagram.model.setDataProperty(lineData, "text", $("#line_criteria option:selected").text());              diagram.commitTransaction('修改流程');

            });
        }
        else {
            ;
        }
        }
    else {
        selectedObject= {type:"base"};
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
        $('#shortname').val(modelData['shortname']);
        $('#icon').val(modelData['icon']);
        $('#version').val(modelData['version']);
        $('#remark').val(modelData['remark']);

        $('#shortname').unbind("change");
        $('#icon').unbind("change");
        $('#version').unbind("change");
        $('#remark').unbind("change");

        $('#shortname').change(function () {

            diagram.startTransaction('修改流程');
            diagram.model.setDataProperty(modelData, "shortname", $('#shortname').val());
            diagram.commitTransaction('修改流程');
        });
        $('#icon').change(function () {

            diagram.startTransaction('修改流程');
            diagram.model.setDataProperty(modelData, "icon", $('#icon').val());
            diagram.commitTransaction('修改流程');
        });
        $('#version').change(function () {

            diagram.startTransaction('修改流程');
            diagram.model.setDataProperty(modelData, "version", $('#version').val());
            diagram.commitTransaction('修改流程');
        });
        $('#remark').change(function () {

            diagram.startTransaction('修改流程');
            diagram.model.setDataProperty(modelData, "remark", $('#remark').val());
            diagram.commitTransaction('修改流程');
        });

        //流程输入
        $("#workflow_input").empty();
        var workflowinput = JSON.parse(modelData['input']);
        for (var i = 0; i < workflowinput.length; i++) {
            $("#workflow_input").append('<option value="' + workflowinput[i]["code"] + '">' + workflowinput[i]["name"] + '</option>')
        }
        $('#workflow_input_code').prop("readonly", true);
        $('#workflow_input_name').prop("readonly", true);
        $('#workflow_input_type').prop("disabled", true);
        $('#workflow_input_source').prop("disabled", true);
        $('#workflow_input_sort').prop("readonly", true);
        $('#workflow_input_remark').prop("readonly", true);
        $('#workflow_input_value').prop("readonly", true);

        $('#workflow_input_save').hide();
        $('#workflow_input_del').hide();

        $('#workflow_input_isnew').val("1")
        $('#workflow_input_code').val("")
        $('#workflow_input_name').val("")
        $('#workflow_input_type').val("")
        $('#workflow_input_source').val("")
        $('#workflow_input_sort').val("")
        $('#workflow_input_remark').val("")
        $('#workflow_input_value').val("")

        $('#workflow_input_save').unbind("click");
        $('#workflow_input').unbind("click");
        $('#workflow_input_new').unbind("click");
        $('#workflow_input_del').unbind("click");

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
            var editoptionval = {
                code: $("#workflow_input_code").val(),
                name: $("#workflow_input_name").val(),
                type: $("#workflow_input_type").val(),
                source: $("#workflow_input_source").val(),
                value: $("#workflow_input_value").val(),
                remark: $("#workflow_input_remark").val(),
                sort: $("#workflow_input_sort").val()
            }
            var newinput = JSON.parse(modelData['input']);
            if ($('#workflow_input_isnew').val() == "1") {
                var exist = false;
                for (var i = 0; i < newinput.length; i++) {
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
                for (var i = 0; i < newinput.length; i++) {
                    if ($('#workflow_input_code').val() == newinput[i]["code"]) {
                        newinput[i] = editoptionval;
                        $("#workflow_input option:selected").text($('#workflow_input_name').val());
                        break;
                    }
                }

            }


            diagram.model.setDataProperty(modelData, "input", JSON.stringify(newinput));

            $('#workflow_input_isnew').val("0")
            $('#workflow_input_code').prop("readonly", true);
            $('#workflow_input_del').show();
            $('#workflow_input').val($("#workflow_input_code").val())
        });

        $('#workflow_input').click(function () {
            var selectval = $("#workflow_input option:selected").val();
            for (var i = 0; i < workflowinput.length; i++) {
                if (workflowinput[i]["code"] == selectval) {
                    $('#workflow_input_name').prop("readonly", false);
                    $('#workflow_input_type').prop("disabled", false);
                    $('#workflow_input_source').prop("disabled", false);
                    $('#workflow_input_sort').prop("readonly", false);
                    $('#workflow_input_remark').prop("readonly", false);
                    $('#workflow_input_value').prop("readonly", false);

                    $('#workflow_input_save').show();
                    $('#workflow_input_del').show();

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
                    break;
                }
            }

        });

        $('#workflow_input_new').click(function () {
            $('#workflow_input_name').prop("readonly", false);
            $('#workflow_input_type').prop("disabled", false);
            $('#workflow_input_source').prop("disabled", false);
            $('#workflow_input_sort').prop("readonly", false);
            $('#workflow_input_remark').prop("readonly", false);
            $('#workflow_input_value').prop("readonly", false);

            $('#workflow_input_save').show();
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
        });

        $('#workflow_input_del').click(function () {
            var selectval = $("#workflow_input option:selected").val();
            for (var i = 0; i < workflowinput.length; i++) {
                if (workflowinput[i]["code"] == selectval) {
                    workflowinput.splice(i, 1);
                    $("#workflow_input option:selected").remove();


                    diagram.model.setDataProperty(modelData, "input", JSON.stringify(workflowinput));


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
        var workflowvariable = JSON.parse(modelData['variable']);
        for (var i = 0; i < workflowvariable.length; i++) {
            $("#workflow_variable").append('<option value="' + workflowvariable[i]["code"] + '">' + workflowvariable[i]["name"] + '</option>')
        }

        $('#workflow_variable_code').prop("readonly", true);
        $('#workflow_variable_name').prop("readonly", true);
        $('#workflow_variable_type').prop("disabled", true);
        $('#workflow_variable_sort').prop("readonly", true);
        $('#workflow_variable_remark').prop("readonly", true);
        $('#workflow_variable_value').prop("readonly", true);

        $('#workflow_variable_save').hide();
        $('#workflow_variable_del').hide();

        $('#workflow_variable_isnew').val("1")
        $('#workflow_variable_code').val("")
        $('#workflow_variable_name').val("")
        $('#workflow_variable_type').val("")
        $('#workflow_variable_sort').val("")
        $('#workflow_variable_remark').val("")
        $('#workflow_variable_value').val("")

        $('#workflow_variable_save').unbind("click");
        $('#workflow_variable').unbind("click");
        $('#workflow_variable_new').unbind("click");
        $('#workflow_variable_del').unbind("click");

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

            var editoptionval = {
                code: $("#workflow_variable_code").val(),
                name: $("#workflow_variable_name").val(),
                type: $("#workflow_variable_type").val(),
                value: $("#workflow_variable_value").val(),
                remark: $("#workflow_variable_remark").val(),
                sort: $("#workflow_variable_sort").val()
            }
            var newvariable = JSON.parse(modelData['variable']);
            if ($('#workflow_variable_isnew').val() == "1") {
                var exist = false;
                for (var i = 0; i < newvariable.length; i++) {
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
                for (var i = 0; i < newvariable.length; i++) {
                    if ($('#workflow_variable_code').val() == newvariable[i]["code"]) {
                        newvariable[i] = editoptionval;
                        $("#workflow_variable option:selected").text($('#workflow_variable_name').val());
                        break;
                    }
                }

            }


            diagram.model.setDataProperty(modelData, "variable", JSON.stringify(newvariable));

            $('#workflow_variable_isnew').val("0")
            $('#workflow_variable_code').prop("readonly", true);
            $('#workflow_variable_del').show();
            $('#workflow_variable').val($("#workflow_variable_code").val())
        });

        $('#workflow_variable').click(function () {
            var selectval = $("#workflow_variable option:selected").val();
            for (var i = 0; i < workflowvariable.length; i++) {
                if (workflowvariable[i]["code"] == selectval) {
                    $('#workflow_variable_name').prop("readonly", false);
                    $('#workflow_variable_type').prop("disabled", false);
                    $('#workflow_variable_sort').prop("readonly", false);
                    $('#workflow_variable_remark').prop("readonly", false);
                    $('#workflow_variable_value').prop("readonly", false);

                    $('#workflow_variable_save').show();
                    $('#workflow_variable_del').show();

                    $('#workflow_variable_isnew').val("0")
                    $('#workflow_variable_code').prop("readonly", true);
                    $('#workflow_variable_del').show();
                    $('#workflow_variable_code').val(workflowvariable[i]["code"])
                    $('#workflow_variable_name').val(workflowvariable[i]["name"])
                    $('#workflow_variable_type').val(workflowvariable[i]["type"])
                    $('#workflow_variable_sort').val(workflowvariable[i]["sort"])
                    $('#workflow_variable_remark').val(workflowvariable[i]["remark"])
                    $('#workflow_variable_value').val(workflowvariable[i]["value"])
                    break;
                }
            }

        });

        $('#workflow_variable_new').click(function () {
            $('#workflow_variable_name').prop("readonly", false);
            $('#workflow_variable_type').prop("disabled", false);
            $('#workflow_variable_sort').prop("readonly", false);
            $('#workflow_variable_remark').prop("readonly", false);
            $('#workflow_variable_value').prop("readonly", false);

            $('#workflow_variable_save').show();
            $('#workflow_variable_del').hide();

            $('#workflow_variable_isnew').val("1")
            $('#workflow_variable_code').prop("readonly", false);
            $('#workflow_variable_code').val("")
            $('#workflow_variable_name').val("")
            $('#workflow_variable_type').val("")
            $('#workflow_variable_sort').val("")
            $('#workflow_variable_remark').val("")
            $('#workflow_variable_value').val("")
        });

        $('#workflow_variable_del').click(function () {
            var selectval = $("#workflow_variable option:selected").val();
            for (var i = 0; i < workflowvariable.length; i++) {
                if (workflowvariable[i]["code"] == selectval) {
                    workflowvariable.splice(i, 1);
                    $("#workflow_variable option:selected").remove();


                    diagram.model.setDataProperty(modelData, "variable", JSON.stringify(workflowvariable));

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
        var workflowoutput = JSON.parse(modelData['output']);
        for (var i = 0; i < workflowoutput.length; i++) {
            $("#workflow_output").append('<option value="' + workflowoutput[i]["code"] + '">' + workflowoutput[i]["name"] + '</option>')
        }

        $('#workflow_output_code').prop("readonly", true);
        $('#workflow_output_name').prop("readonly", true);
        $('#workflow_output_type').prop("disabled", true);
        $('#workflow_output_source').prop("disabled", true);
        $('#workflow_output_sort').prop("readonly", true);
        $('#workflow_output_remark').prop("readonly", true);
        $('#workflow_output_value').prop("readonly", true);

        $('#workflow_output_save').hide();
        $('#workflow_output_del').hide();

        $('#workflow_output_del').hide();
        $('#workflow_output_isnew').val("1")
        $('#workflow_output_code').val("")
        $('#workflow_output_name').val("")
        $('#workflow_output_type').val("")
        $('#workflow_output_source').val("")
        $('#workflow_output_sort').val("")
        $('#workflow_output_remark').val("")
        $('#workflow_output_value').val("")

        $('#workflow_output_value').unbind("click");
        $('#workflow_output_save').unbind("click");
        $('#workflow_output').unbind("click");
        $('#workflow_output_new').unbind("click");
        $('#workflow_output_del').unbind("click");

        $('#workflow_output_value').click(function () {
            var source=$('#workflow_output_source').val();
            if(source == "workfolwInput"){
                $('#modal_workflowinput').modal('show');
                var workflowinputdata = JSON.parse(modelData['input']);
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
                        {"data": null},
                    ],
                    "columnDefs": [
                        {
                            "targets": -2,
                            "render": function (data, type, full) {
                                if (data.type == "json") {
                                    return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_workflowinput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                }
                            }
                        }, {
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
                    var param_key = ""
                    var param_key_value = $('#table_workflowinput_type_' + table.row($(this).parents('tr')).data().code).val()
                    if (param_key_value!="" && param_key_value!=undefined){
                        param_key = "-->" + param_key_value;
                    }
                    $('#workflow_output_value').val(table.row($(this).parents('tr')).data().code+param_key)
                    $('#modal_workflowinput').modal('hide');
                });


            }else if(source == "workfolwVariable"){
                $('#modal_workfolwvariable').modal('show');
                var workflowvariabledata = JSON.parse(modelData['variable']);
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
                        {"data": null},
                    ],
                    "columnDefs": [
                        {
                            "targets": -2,
                            "render": function (data, type, full) {
                                if (data.type == "json") {
                                    return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_variable_type_" + data.code + "' name='table_variable_type'  type='text'></input>"
                                }
                            }
                        },{
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
                    var param_key = ""
                    var param_key_value = $('#table_workfolwvariable_type_' + table.row($(this).parents('tr')).data().code).val()
                    if (param_key_value!="" && param_key_value!=undefined){
                        param_key = "-->" + param_key_value;
                    }
                    $('#workflow_output_value').val(table.row($(this).parents('tr')).data().code+param_key)
                    $('#modal_workfolwvariable').modal('hide');
                });
            }else if(source == "stepOutput"){
                $('#modal_stepoutput').modal('show');
                var steps = diagram.model.wc;
                $("#modal_stepoutput_step").empty();
                for (var i = 0; i < steps.length; i++) {
                    $("#modal_stepoutput_step").append('<option value="' + steps[i]["key"] + '">' + steps[i]["text"] + '</option>')
                }

                for (var i = 0; i < steps.length; i++) {
                    if(steps[i]["key"]==$("#modal_stepoutput_step").val()){

                        var stepoutdata = JSON.parse(steps[i]["output"]);
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
                                {"data": null},
                            ],
                            "columnDefs": [
                                {
                                    "targets": -2,
                                    "render": function (data, type, full) {
                                        if (data.type == "json") {
                                            return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_stepoutput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                        }
                                    }
                                },{
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
                            var param_key = ""
                            var param_key_value = $('#table_stepoutput_type_' + table.row($(this).parents('tr')).data().code).val()
                            if (param_key_value!="" && param_key_value!=undefined){
                                param_key = "-->" + param_key_value;
                            }
                            $('#workflow_output_value').val($("#modal_stepoutput_step").val()+ "^" + table.row($(this).parents('tr')).data().code + param_key)

                            $('#modal_stepoutput').modal('hide');
                        });
                        break;
                    }
                }

                $('#modal_stepoutput_step').unbind("change");
                $("#modal_stepoutput_step").change(function () {
                    for (var i = 0; i < steps.length; i++) {
                        if(steps[i]["key"]==$("#modal_stepoutput_step").val()){

                            var stepoutdata = JSON.parse(steps[i]["output"]);
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
                                    {"data": null},
                                ],
                                "columnDefs": [
                                    {
                                        "targets": -2,
                                        "render": function (data, type, full) {
                                            if (data.type == "json") {
                                                return "<input style='margin-top:-5px;width:134px;height:24px;' id='table_stepoutput_type_" + data.code + "' name='table_workflowinput_type'  type='text'></input>"
                                            }
                                        }
                                    },{
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
                                var param_key = ""
                                var param_key_value = $('#table_stepoutput_type_' + table.row($(this).parents('tr')).data().code).val()
                                if (param_key_value!="" && param_key_value!=undefined){
                                    param_key = "-->" + param_key_value;
                                }
                                $('#workflow_output_value').val($("#modal_stepoutput_step").val()+ "^" + table.row($(this).parents('tr')).data().code + param_key)

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
            var editoptionval = {
                code: $("#workflow_output_code").val(),
                name: $("#workflow_output_name").val(),
                type: $("#workflow_output_type").val(),
                source: $("#workflow_output_source").val(),
                value: $("#workflow_output_value").val(),
                remark: $("#workflow_output_remark").val(),
                sort: $("#workflow_output_sort").val()
            }
            var newoutput = JSON.parse(modelData['output']);
            if ($('#workflow_output_isnew').val() == "1") {
                var exist = false;
                for (var i = 0; i < newoutput.length; i++) {
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
                for (var i = 0; i < newoutput.length; i++) {
                    if ($('#workflow_output_code').val() == newoutput[i]["code"]) {
                        newoutput[i] = editoptionval;
                        $("#workflow_output option:selected").text($('#workflow_output_name').val());
                        break;
                    }
                }

            }


            diagram.model.setDataProperty(modelData, "output", JSON.stringify(newoutput));

            $('#workflow_output_isnew').val("0")
            $('#workflow_output_code').prop("readonly", true);
            $('#workflow_output_del').show();
            $('#workflow_output').val($("#workflow_output_code").val())
        });

        $('#workflow_output').click(function () {
            var selectval = $("#workflow_output option:selected").val();
            for (var i = 0; i < workflowoutput.length; i++) {
                if (workflowoutput[i]["code"] == selectval) {
                    $('#workflow_output_name').prop("readonly", false);
                    $('#workflow_output_type').prop("disabled", false);
                    $('#workflow_output_source').prop("disabled", false);
                    $('#workflow_output_sort').prop("readonly", false);
                    $('#workflow_output_remark').prop("readonly", false);
                    $('#workflow_output_value').prop("readonly", false);

                    $('#workflow_output_save').show();
                    $('#workflow_output_del').show();

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
                    break;
                }
            }

        });

        $('#workflow_output_new').click(function () {
            $('#workflow_output_name').prop("readonly", false);
            $('#workflow_output_type').prop("disabled", false);
            $('#workflow_output_source').prop("disabled", false);
            $('#workflow_output_sort').prop("readonly", false);
            $('#workflow_output_remark').prop("readonly", false);
            $('#workflow_output_value').prop("readonly", false);

            $('#workflow_output_save').show();
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
        });

        $('#workflow_output_del').click(function () {
            var selectval = $("#workflow_output option:selected").val();
            for (var i = 0; i < workflowoutput.length; i++) {
                if (workflowoutput[i]["code"] == selectval) {
                    workflowoutput.splice(i, 1);
                    $("#workflow_output option:selected").remove();


                    diagram.model.setDataProperty(modelData, "output", JSON.stringify(workflowoutput));

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
