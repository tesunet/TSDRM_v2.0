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

                $('#step_criteria_id').val("")
                $('#step_criteria_name').val("")
                $('#step_criteria_logic').val("")
                $('#step_criteria_type').val("")
                $('#step_criteria_source_left').val("")
                $('#step_criteria_value_left').val("")
                $('#step_criteria_char').val("")
                $('#step_criteria_source_right').val("")
                $('#step_criteria_value_right').val("")


                $('#step_criteria').unbind("click");

                $('#step_criteria').click(function () {
                    var selectval = $("#step_criteria option:selected").val();
                    for (var i = 0; i < stepcriteria.length; i++) {
                        if (stepcriteria[i]["id"] == selectval) {

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

                $('#step_input').unbind("click");

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
                            break;
                        }
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


            $('#step_output').unbind("click");


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
                        break;
                    }
                }

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
                    // if(steps[i]["category"]=="for" || steps[i]["category"]=="if"){
                    //     $('#div_criteria').show();
                    // }
                    $('#div_criteria').show();
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
            }else{
                $("#line_criteria").append('<option value="True">成功</option>')
                $("#line_criteria").append('<option value="False">失败</option>')
                $("#line_criteria").append('<option value="All">全部</option>')
            }

            $('#line_from').val(lineData['from']);
            $('#line_to').val(lineData['to']);
            $('#line_from_name').val(formnode_text);
            $('#line_to_name').val(tonode_text);
            $('#line_criteria').val(lineData['criteria']);
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


        //流程输入
        $("#workflow_input").empty();
        var workflowinput = JSON.parse(modelData['input']);
        for (var i = 0; i < workflowinput.length; i++) {
            $("#workflow_input").append('<option value="' + workflowinput[i]["code"] + '">' + workflowinput[i]["name"] + '</option>')
        }

        $('#workflow_input_isnew').val("1")
        $('#workflow_input_code').val("")
        $('#workflow_input_name').val("")
        $('#workflow_input_type').val("")
        $('#workflow_input_source').val("")
        $('#workflow_input_sort').val("")
        $('#workflow_input_remark').val("")
        $('#workflow_input_value').val("")

        $('#workflow_input').unbind("click");


        $('#workflow_input').click(function () {
            var selectval = $("#workflow_input option:selected").val();
            for (var i = 0; i < workflowinput.length; i++) {
                if (workflowinput[i]["code"] == selectval) {
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



        //临时变量
        $("#workflow_variable").empty();
        var workflowvariable = JSON.parse(modelData['variable']);
        for (var i = 0; i < workflowvariable.length; i++) {
            $("#workflow_variable").append('<option value="' + workflowvariable[i]["code"] + '">' + workflowvariable[i]["name"] + '</option>')
        }


        $('#workflow_variable_isnew').val("1")
        $('#workflow_variable_code').val("")
        $('#workflow_variable_name').val("")
        $('#workflow_variable_type').val("")
        $('#workflow_variable_sort').val("")
        $('#workflow_variable_remark').val("")
        $('#workflow_variable_value').val("")


        $('#workflow_variable').unbind("click");


        $('#workflow_variable').click(function () {
            var selectval = $("#workflow_variable option:selected").val();
            for (var i = 0; i < workflowvariable.length; i++) {
                if (workflowvariable[i]["code"] == selectval) {
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


        //流程输出
        $("#workflow_output").empty();
        var workflowoutput = JSON.parse(modelData['output']);
        for (var i = 0; i < workflowoutput.length; i++) {
            $("#workflow_output").append('<option value="' + workflowoutput[i]["code"] + '">' + workflowoutput[i]["name"] + '</option>')
        }

        $('#workflow_output_code').val("")
        $('#workflow_output_name').val("")
        $('#workflow_output_type').val("")
        $('#workflow_output_source').val("")
        $('#workflow_output_sort').val("")
        $('#workflow_output_remark').val("")
        $('#workflow_output_value').val("")

        $('#workflow_output').unbind("click");


        $('#workflow_output').click(function () {
            var selectval = $("#workflow_output option:selected").val();
            for (var i = 0; i < workflowoutput.length; i++) {
                if (workflowoutput[i]["code"] == selectval) {
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

    }

}
