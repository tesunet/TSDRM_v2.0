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
            $('#skip').hide();
            $('#div_line').hide();
            $('#div_node').show();
            var stepData = inspectedObject.data
            var modelData = diagram.model.modelData;
            selectedObject= {type:"node",key:stepData['key']};

            //步骤信息
            var stepjob = JSON.parse(stepData['stepjob']);
            $('#step_name').val(stepData['name']);
            $('#step_starttime').val("");
            $('#step_endtime').val("");
            $('#step_rto').val(stepData['rto']);
            $('#step_state').text(stepData['state']);
            $('#step_state').css("background-color",stepData['color']);

            // 步骤参数数据
            $('#bz_finalinput').empty();
            $('#bz_output').empty();
            for (var i = 0; i < stepjob.length; i++) {
                if (stepjob[i]['stepinput']){
                    for (var j = 0; j < stepjob[i]['stepinput'].length; j++) {
                        $('#bz_finalinput').append('参数编码：' + stepjob[i]['stepinput'][j].code + '&#10;');
                        $('#bz_finalinput').append('数据来源：' + stepjob[i]['stepinput'][j].source + '&#10;');
                        $('#bz_finalinput').append('参数数值：' + stepjob[i]['stepinput'][j].value + '&#10;');
                        $('#bz_finalinput').append('&#10;');
                    }
                }
                if (stepjob[i]['stepoutput']){
                    for (var j = 0; j < stepjob[i]['stepoutput'].length; j++) {
                        $('#bz_output').append('参数编码：' + stepjob[i]['stepoutput'][j].code + '&#10;');
                        $('#bz_output').append('参数数值：' + stepjob[i]['stepoutput'][j].value + '&#10;');
                        $('#bz_output').append('&#10;');
                    }
                }
            }

            $("#step_list").empty();
            for (var i = 0; i < stepjob.length; i++) {
                if (i == stepjob.length-1) {
                    $('#step_id').val(stepjob[i]['id']);
                    $('#step_type').val(stepjob[i]['type']);
                    $('#step_guid').val(stepjob[i]['guid']);
                    $('#step_name').val(stepjob[i]['name']);
                    $('#step_starttime').val(stepjob[i]['starttime']);
                    $('#step_endtime').val(stepjob[i]['endtime']);
                    $('#step_rto').val(stepjob[i]['rto']);
                    $('#step_state').text(stepjob[i]['state']);
                    $('#step_state').css("background-color",stepjob[i]['color']);
                    if(stepjob[i]['state_code']=="PAUSE"||stepjob[i]['state_code']=="ERROR"){
                        $('#skip').show();
                    }
                    else{
                        $('#skip').hide();
                    }
                    $("#step_list").append('<option selected value="' + stepjob[i]["id"] + '">' + stepjob[i]["starttime"] + '</option>')
                } else {
                    $("#step_list").append('<option value="' + stepjob[i]["id"] + '">' + stepjob[i]["starttime"] + '</option>')
                }
            }
            // 判断流程中的步骤是否是子流程
            if ($('#step_type').val() == 'WORKFLOW'){
                $('#child_workflow_div').show();
                $('#child_workflow_info').attr("href",'/workflow_monitor/' + $('#step_id').val() +'/?s=true');
                $('#child_workflow_info').text($('#step_name').val());
            }
            else {
                $('#child_workflow_div').hide()
            }

            $('#step_list').unbind("click");

            $('#step_list').click(function () {
                var selectval = $("#step_list option:selected").val();
                for (var i = 0; i < stepjob.length; i++) {
                    if (stepjob[i]["id"] == selectval) {
                        $('#step_name').val(stepjob[i]['name']);
                        $('#step_starttime').val(stepjob[i]['starttime']);
                        $('#step_endtime').val(stepjob[i]['endtime']);
                        $('#step_rto').val(stepjob[i]['rto']);
                        $('#step_state').text(stepjob[i]['state']);
                        $('#step_state').css("background-color",stepjob[i]['color']);
                        if(stepjob[i]['state_code']=="PAUSE"||stepjob[i]['state_code']=="ERROR"){
                            $('#skip').show();
                        }
                        else{
                            $('#skip').hide();
                        }
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
        $('#guid').val(modelData['guid']);
        $('#workflowname').val(modelData['workflowname']);
        $('#instancename').val(modelData['instancename']);
        $('#jobname').val(modelData['jobname']);
        $('#startuser').val(modelData['startuser']);
        $('#reson').val(modelData['reson']);
        $('#starttime').val(modelData['starttime']);
        $('#endtime').val(modelData['endtime']);
        $('#rto').val(modelData['rto']);
        $('#state').text(modelData['state']);
        $('#state').css("background-color",modelData['color']);

        // 流程参数数据
        $('#lc_finalinput').empty();
        $('#lc_output').empty();

        if (modelData['finalinput']){
            for (var i = 0; i < modelData['finalinput'].length; i++) {
                $('#lc_finalinput').append('参数编码：' + modelData['finalinput'][i].code + '&#10;');
                $('#lc_finalinput').append('参数名称：' + modelData['finalinput'][i].name + '&#10;');
                $('#lc_finalinput').append('参数类型：' + modelData['finalinput'][i].type + '&#10;');
                $('#lc_finalinput').append('参数数值：' + modelData['finalinput'][i].value + '&#10;');
                $('#lc_finalinput').append('&#10;');
            }
        }
        if (modelData['output']){
             for (var i = 0; i < modelData['output'].length; i++) {
                $('#lc_output').append('参数编码：' + modelData['output'][i].code + '&#10;');
                $('#lc_output').append('参数名称：' + modelData['output'][i].name + '&#10;');
                $('#lc_output').append('参数类型：' + modelData['output'][i].type + '&#10;');
                $('#lc_output').append('参数数值：' + modelData['output'][i].value + '&#10;');
                $('#lc_output').append('&#10;');
            }
        }
        if(modelData['state_code']=="RUN"||modelData['state_code']=="ERROR"||modelData['state_code']=="PAUSE"||modelData['state_code']==""){
            $('#stop').show();
        }
        else{
            $('#stop').hide();
        }
        if(modelData['state_code']=="RUN"||modelData['state_code']==""){
            $('#pause').show();
        }
        else{
            $('#pause').hide();
        }
        if(modelData['state_code']=="PAUSE"||modelData['state_code']=="ERROR"){
            $('#retry').show();
        }
        else{
            $('#retry').hide();
        }
    }

}
