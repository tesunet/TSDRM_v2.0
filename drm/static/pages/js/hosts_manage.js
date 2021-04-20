function inArray(search, array) {
    for (var i in array) {
        if (JSON.stringify(array[i]) == JSON.stringify(search)) {
            return true;
        }
    }
    return false;
}

function displayAgentParams(agent_type) {
    if (agent_type.indexOf("Oracle") != -1) {
        $('#cv_orcl').show();
        $('#cv_filesystem').hide();
        $('#cv_mssql').hide();
        $('#cv_select_file').hide();
    } else if (agent_type.indexOf("File System") != -1) {
        $('#cv_orcl').hide();
        $('#cv_filesystem').show();
        $('#cv_mssql').hide();
        $('#cv_select_file').show();
    } else if (agent_type.indexOf("SQL Server") != -1) {
        $('#cv_orcl').hide();
        $('#cv_filesystem').hide();
        $('#cv_mssql').show();
        $('#cv_select_file').hide();
    }
}


//主机
function getClientree() {
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: '../get_hosts_tree_by_business/',
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
                            "icon": false
                        }
                    },
                    "contextmenu":$('#is_superuser').val()=="True"?{
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
                                        $('#tabcheck2').attr("style", "color: #cbd5dd");
                                        $("#tabcheck2").parent().attr("style", "pointer-events:none;");
                                        $("#tabcheck1").click();
                                        $("#title").text("新建")
                                        $("#pname").val(obj.data["name"])
                                        $("#id").val("0");
                                        $("#pid").val(obj.id);
                                        $("#my_type").val("CLIENT");
                                        $("#host_ip").val("");
                                        $("#host_name").val("");
                                        $("#host_type").val("");
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
                                        var edit=obj.data.edit
                                        if (!edit) {
                                            alert("该节点无法删除。");
                                            location.reload()
                                        }
                                        else {
                                            if (confirm("确定要删除？删除后不可恢复。")) {
                                                $.ajax({
                                                    type: "POST",
                                                    url: "../hosts_del/",
                                                    data:
                                                        {
                                                            id: obj.id,
                                                        },
                                                    success: function (data) {
                                                        if (data == 1) {
                                                            inst.delete_node(obj);
                                                            $("#form_div").hide();
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
                                }
                            },

                        }
                    }:{"items": {
                            "create": null,
                            "rename": null,
                            "remove": null,
                            "ccp": null,
                        }},
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
                                var edit=data.node.data.edit
                                if (!edit) {
                                    alert("该节点无法移动。");
                                    location.reload()
                                }
                                else {
                                    $.ajax({
                                        type: "POST",
                                        url: "../hosts_move/",
                                        data:
                                            {
                                                id: data.node.id,
                                                parent: data.parent,
                                                old_parent: data.old_parent,
                                                position: data.position,
                                                old_position: data.old_position,
                                            },
                                        success: function (data) {
                                            if (data.ret == 0 ) {
                                                alert(data.info);
                                                location.reload();
                                            }
                                            else{
                                                if (data.data) {
                                                    if (selectid == moveid) {
                                                        var res = data.data.split('^')
                                                        $("#pid").val(res[1])
                                                        $("#pname").val(res[0])
                                                        $("#node_pname").val(res[0])
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
                        }
                    })
                    .bind('select_node.jstree', function (event, data) {
                        $("#form_div").show();
                        var type = data.node.original.type;

                        $("#id").val(data.node.id);
                        $("#pid").val(data.node.parent);
                        $("#my_type").val(type);
                        $("#title").text(data.node.data.name);
                        $('#pname').val(data.node.data.pname);
                        if (type == "CLIENT") {
                            $('#tabcheck2').removeAttr("style", "color: #cbd5dd");
                            $("#tabcheck2").parent().removeAttr("style", "pointer-events:none;");
                            $('#tabcheck3').removeAttr("style", "color: #cbd5dd");
                            $("#tabcheck3").parent().removeAttr("style", "pointer-events:none;");
                            $('#tabcheck4').removeAttr("style", "color: #cbd5dd");
                            $("#tabcheck4").parent().removeAttr("style", "pointer-events:none;");
                            $("#tabcheck1").click();
                            $.ajax({
                                type: "POST",
                                dataType: 'json',
                                url: "../hosts_get_client_detail/",
                                data: {
                                    id: data.node.id,
                                },
                                success: function (data) {
                                    if (data.ret == 1) {
                                        //基础信息
                                        $("#host_ip").val(data.data.host_ip);
                                        $("#host_name").val(data.data.host_name);
                                        $("#host_type").val(data.data.host_type);
                                        $("#username").val(data.data.username);
                                        $("#password").val(data.data.password);
                                        $("#remark").val(data.data.remark);
                                        // 动态参数
                                        $('#param_se').empty();
                                        var variable_param_list = data.data.variable_param_list;
                                        for (var i = 0; i < variable_param_list.length; i++) {
                                            $('#param_se').append('<option value="' + variable_param_list[i].variable_name + '">' + variable_param_list[i].param_name + ':' + variable_param_list[i].variable_name + ':' + variable_param_list[i].param_value + '</option>');
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
                        if (!data.node.data.edit) {
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

//commvault
function get_cv_detail() {
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../get_cv_process/",
        data:
        {
            id: $("#id").val(),
        },
        success: function (data) {
            //流程
            var processtext = ""
            for (var i = 0; i < data["process"].length; i++) {
                processtext += "<div  class='form-group'><button onclick=\"runCVProcess(" + data["process"][i].process_id + ",'1')\"  type='button' class=' btn  green'>流程:" + data["process"][i].process_name + "</button> ";
                processtext += "</div>"
            }
            $("#cv_processdiv").empty();
            $("#cv_processdiv").append(processtext);
        },
        error: function (e) {
            ;
        }
    });

    var table = $('#cv_backup_his').DataTable();
    table.ajax.url("../client_cv_get_backup_his?id=" + $('#cv_id').val()
    ).load();
    // 目标客户端
    var dest_client = $('#cvclient_destination').val();
    if (dest_client == "self") {
        dest_client = $('#cv_id').val();
    }
    var table1 = $('#cv_restore_his').DataTable();
    table1.ajax.url("../client_cv_get_restore_his?id=" + dest_client
    ).load();

    $('#cv_r_sourceClient').val($("#cvclient_source").find("option:selected").text());
    $('#cv_r_destClient').val($('#cvclient_destination').val());

    // Oracle
    $('#cv_r_copy_priority').val($('#cvclient_copy_priority').val());
    $('#cv_r_db_open').val($('#cvclient_db_open').val());
    $('#cv_r_log_restore').val($('#cvclient_log_restore').val());
    $('#cv_r_data_path').val($('#cvclient_data_path').val());

    // SQL Server
    if ($('#cv_isoverwrite').is(':checked')) {
        $('#cv_r_isoverwrite').prop("checked", true);
    } else {
        $('#cv_r_isoverwrite').prop("checked", false);
    }

    // File System
    // cv_overwrite cv_path  cv_mypath cv_fs_se_1
    // cv_r_overwrite cv_r_path cv_r_mypath cv_r_fs_se_1
    var cv_overwrite = $('input[name="cv_overwrite"]:checked').val();
    if (cv_overwrite == "TRUE") {
        $('input[name="cv_r_overwrite"]:last').prop("checked", true);
    } else {
        $('input[name="cv_r_overwrite"]:first').prop("checked", true);
    }
    var cv_path = $('input[name="cv_path"]:checked').val();
    var cv_mypath = $('#cv_mypath').val();
    if (cv_path == 1) {  // 相同文件
        $('input[name="cv_r_path"]:first').prop("checked", true);
    } else {
        $('input[name="cv_r_path"]:last').prop("checked", true);
        $('#cv_r_mypath').val(cv_mypath);
    }
    var cv_fs_se_1 = $('#cv_fs_se_1').html();
    $('#cv_r_fs_se_1').empty().append(cv_fs_se_1);
}

function getCvInstance() {
    $("#cvclient_instance").empty();
    try {
        var clientdata = JSON.parse($("#cvclient_client_info").val());
        var instancelist = [];
        for (var i = 0; i < clientdata.length; i++) {
            if (clientdata[i].clientid == $("#cvclient_source").val() && clientdata[i].agent == $("#cvclient_agentType").val()) {
                if (instancelist.indexOf(clientdata[i].instance) == -1) {
                    instancelist.push(clientdata[i].instance);
                }
            }
        }
        for (var i = 0; i < instancelist.length; i++) {
            $("#cvclient_instance").append('<option value="' + instancelist[i] + '">' + instancelist[i] + '</option>');
        }
    } catch (e){
        console.log(e)
    }

}

function getCvAgenttype() {
    $("#cvclient_agentType").empty();
    try {
        var clientdata = JSON.parse($("#cvclient_client_info").val());
        var agentlist = [];
        for (var i = 0; i < clientdata.length; i++) {
            if (clientdata[i].clientid == $("#cvclient_source").val()) {
                if (agentlist.indexOf(clientdata[i].agent) == -1) {
                    agentlist.push(clientdata[i].agent);
                }
            }
        }
        for (var i = 0; i < agentlist.length; i++) {
            $("#cvclient_agentType").append('<option value="' + agentlist[i] + '">' + agentlist[i] + '</option>');
        }
    } catch (e){
        console.log(e)
    }

    getCvInstance();
}

function getCvClient() {
    $("#cvclient_source").empty();
    var utildata = JSON.parse($("#cvclient_utils_manage_info").val());
    for (var i = 0; i < utildata.length; i++) {
        if (utildata[i].utils_manage == $("#cvclient_utils_manage").val()) {
            var clientlist = [];
            for (var j = 0; j < utildata[i].instance_list.length; j++) {
                var client = { "clientid": utildata[i].instance_list[j].clientid, "clientname": utildata[i].instance_list[j].clientname };
                if (!inArray(client, clientlist)) {
                    clientlist.push(client);
                }
            }
            for (var j = 0; j < clientlist.length; j++) {
                $("#cvclient_source").append('<option value="' + clientlist[j].clientid + '">' + clientlist[j].clientname + '</option>');
            }
            $("#cvclient_client_info").val(JSON.stringify(utildata[i].instance_list))
            break;
        }
    }
    getCvAgenttype();
}

function getCvDestination() {
    $("#cvclient_destination").empty();
    $("#cv_r_destClient").empty();

    var destinationdata = JSON.parse($("#cvclient_u_destination").val());
    for (var i = 0; i < destinationdata.length; i++) {
        if (destinationdata[i].utilid == $("#cvclient_utils_manage").val()) {
            for (var j = 0; j < destinationdata[i].destination_list.length; j++) {
                $("#cvclient_destination").append('<option value="' + destinationdata[i].destination_list[j].id + '">' + destinationdata[i].destination_list[j].name + '</option>');
                $("#cv_r_destClient").append('<option value="' + destinationdata[i].destination_list[j].id + '">' + destinationdata[i].destination_list[j].name + '</option>');
            }
            break;
        }
    }
    $("#cvclient_destination").append('<option value="self">' + "本机" + '</option>');
    $("#cv_r_destClient").append('<option value="self">' + "本机" + '</option>');
}

function getCvinfo() {
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: '../get_cvinfo/',
        success: function (data) {
            for (var i = 0; i < data.u_destination.length; i++) {
                $("#cvclient_utils_manage").append('<option value="' + data.u_destination[i].utilid + '">' + data.u_destination[i].utilname + '</option>');
            }
            $("#cvclient_utils_manage_info").val(JSON.stringify(data.data))
            $("#cvclient_u_destination").val(JSON.stringify(data.u_destination))
            getCvClient();
            getCvDestination();
        }
    });

}

function getFileTree() {
    var setting = {
        async: {
            enable: true,
            url: '../get_file_tree/',
            autoParam: ["id"],
            otherParam: { "cv_id": $('#cv_id').val() },
            dataFilter: filter
        },
        check: {
            enable: true,
            chkStyle: "checkbox",               //多选
            chkboxType: { "Y": "s", "N": "ps" }  //不级联父节点选择
        },
        view: {
            showLine: false
        },

    };

    function filter(treeId, parentNode, childNodes) {
        if (!childNodes) return null;
        for (var i = 0, l = childNodes.length; i < l; i++) {
            childNodes[i].name = childNodes[i].name.replace(/\.n/g, '.');
        }
        return childNodes;
    }

    $.fn.zTree.init($("#cv_fs_tree"), setting);
}
//数据库复制
function get_dbcopy_oracle_detail() {
    var table = $('#dbcopy_his').DataTable();
    table.ajax.url("../client_dbcopy_get_his?id=" + $('#id').val() + "&type=ADG"
    ).load();
    $('#adgstate_div').show();
    $('#mysqlstate_div').hide();
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../get_adg_status/",
        data:
        {
            id: $("#id").val(),
            dbcopy_id: $("#dbcopy_id").val(),
            dbcopy_std: $("#dbcopy_std").val(),
        },
        success: function (data) {
            $(".ldbimg").attr("src", "/static/pages/images/adg/db3.png");
            $(".rdbimg").attr("src", "/static/pages/images/adg/db3.png");
            $(".sync").attr("src", "/static/pages/images/adg/sync_r.png");
            //数据库状态
            l_host_name = data["data"][0].host_name;
            l_db_status = data["data"][0].db_status;
            l_switchover_status = data["data"][0].switchover_status;

            r_host_name = data["data"][1].host_name;
            r_db_status = data["data"][1].db_status;
            r_switchover_status = data["data"][1].switchover_status;
            $(".ldbname").text(l_host_name);
            $(".ldbsta").text(l_db_status);
            $(".rdbname").text(r_host_name);
            $(".rdbsta").text(r_db_status);

            if (l_db_status == "OPEN") {
                $(".ldbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (l_db_status == "READ ONLY WITH APPLY") {
                $(".ldbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (l_db_status == "READ WRITE") {
                $(".ldbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (l_db_status == "READ ONLY") {
                $(".ldbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (l_db_status == "MOUNT") {
                $(".ldbimg").attr("src", "/static/pages/images/adg/db2.png");
            }
            if (r_db_status == "OPEN") {
                $(".rdbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (r_db_status == "READ ONLY WITH APPLY") {
                $(".rdbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (r_db_status == "READ WRITE") {
                $(".rdbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (r_db_status == "MOUNT") {
                $(".rdbimg").attr("src", "/static/pages/images/adg/db2.png");
            }
            if (r_db_status == "READ ONLY") {
                $(".rdbimg").attr("src", "/static/pages/images/adg/db1.png");
            }
            if (l_switchover_status == "PRIMARY") {
                $(".sync").attr("src", "/static/pages/images/adg/sync_r.gif");
            }
            if (r_switchover_status == "PRIMARY") {
                $(".sync").attr("src", "/static/pages/images/adg/sync_l.gif");
            }
            //流程
            var processtext = ""
            for (var i = 0; i < data["process"].length; i++) {
                processtext += "<div  class='form-group'><button onclick=\"runprocess(" + data["process"][i].process_id + ",'1')\"  type='button' class=' btn  green'>流程:" + data["process"][i].process_name + "</button> ";
                if (data["process"][i].back_id != null && data["process"][i].back_id != "") {
                    processtext += "<button onclick=\"runprocess(" + data["process"][i].back_id + ",'2')\" type='button' class='backprocessbtn btn  green'>回切</button>";
                }
                processtext += "</div>"
            }
            $("#processdiv").empty();
            $("#processdiv").append(processtext);
        },
        error: function (e) {
            ;
        }
    });
}
function get_dbcopy_mysql_detail() {
    var table = $('#dbcopy_his').DataTable();
    table.ajax.url("../client_dbcopy_get_his?id=" + $('#id').val() + "&type=MYSQL"
    ).load();
    $('#adgstate_div').hide();
    $('#mysqlstate_div').show();
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../get_mysql_status/",
        data:
        {
            id: $("#id").val(),
            dbcopy_id: $("#dbcopy_id").val(),
            dbcopy_mysql_std: JSON.stringify($("#dbcopy_mysql_std").val()),
        },
        success: function (data) {
            //数据库状态
            $(".mysqlcount").hide();
            $(".mysqlsync").hide();
            $(".mysqlsync").attr("src", "/static/pages/images/adg/sync_r.png");
            $(".mysqlhost").attr("src", "/static/pages/images/adg/db3.png");
            $(".mysqltest").text("")
            var hostcount = data["data"].length;
            $("#mysql_count_" + hostcount.toString()).show();
            if (hostcount > 4) {
                $("#mysql_count_4").show();
            }
            for (var i = 0; i < data["data"].length; i++) {
                num = data["data"][i].num;
                conn_status = data["data"][i].conn_status;
                host_name = data["data"][i].host_name;
                host_ip = data["data"][i].host_ip;
                io_state = data["data"][i].io_state;
                sql_state = data["data"][i].sql_state;
                masternum = data["data"][i].masternum;

                $("#dbhost_" + hostcount.toString() + "_" + num.toString()).text(host_name);
                $("#dbip_" + hostcount.toString() + "_" + num.toString()).text(host_ip);
                if (conn_status == 1) {
                    $("#mysqlimg_" + hostcount.toString() + "_" + num.toString()).attr("src", "/static/pages/images/adg/db1.png");
                }
                $("#sync_" + hostcount.toString() + "_" + masternum.toString() + "_" + num.toString()).show();
                if (io_state == "Yes" && sql_state == "Yes") {
                    $("#sync_" + hostcount.toString() + "_" + masternum.toString() + "_" + num.toString()).attr("src", "/static/pages/images/adg/sync_r.gif");
                }

            }

            //流程
            var processtext = ""
            for (var i = 0; i < data["process"].length; i++) {
                processtext += "<div  class='form-group'><button onclick=\"runprocess(" + data["process"][i].process_id + ",'1')\"  type='button' class=' btn  green'>流程:" + data["process"][i].process_name + "</button> ";
                if (data["process"][i].back_id != null && data["process"][i].back_id != "") {
                    processtext += "<button onclick=\"runprocess(" + data["process"][i].back_id + ",'2')\" type='button' class='backprocessbtn btn  green'>回切</button>";
                }
                processtext += "</div>"
            }
            $("#processdiv").empty();
            $("#processdiv").append(processtext);
        },
        error: function (e) {
            ;
        }
    });
}

function getDbcopyStd() {
    $("#dbcopy_std").empty();

    var stddata = JSON.parse($("#dbcopy_u_std").val());
    for (var i = 0; i < stddata.length; i++) {
        if (stddata[i].type == "1") {
            $("#dbcopy_std").append('<option value="' + stddata[i].id + '">' + stddata[i].name + '</option>');
        }
    }
    $("#dbcopy_std").append('<option value="none">' + "无" + '</option>');
}
function getDbcopyMysqlStd() {
    $("#dbcopy_mysql_std").empty();

    var stddata = JSON.parse($("#dbcopy_u_std").val());
    for (var i = 0; i < stddata.length; i++) {
        if (stddata[i].type == "2") {
            $("#dbcopy_mysql_std").append('<option value="' + stddata[i].id + '">' + stddata[i].name + '</option>');
        }
    }

    $("#dbcopy_mysql_std").select2({
        width: null
    });
}


function getDbcopyinfo() {
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: '../get_dbcopyinfo/',
        success: function (data) {
            $("#dbcopy_u_std").val(JSON.stringify(data.u_std));
            getDbcopyStd();
            getDbcopyMysqlStd();
        }
    });

}
/**
 * 流程模态框
 * @param {*} processid 
 * @param {*} process_type 
 */
function runCVProcess(processid, process_type) {
    /**
     * 自动化恢复流程
     */
    $("#confirmtext").val("");
    $("#static").modal({ backdrop: "static" });
    $('#recovery_time').datetimepicker({
        format: 'yyyy-mm-dd hh:ii:ss',
        pickerPosition: 'top-right'
    });
    // 写入当前时间
    var myDate = new Date();
    $("#run_time").val(myDate.toLocaleString());
    $("#processid").val(processid);
    $("#process_type").val(process_type);

}


function runprocess(processid, process_type) {
    $("#confirmtext").val("");
    $("#static").modal({ backdrop: "static" });
    $('#recovery_time').datetimepicker({
        format: 'yyyy-mm-dd hh:ii:ss',
        pickerPosition: 'top-right'
    });
    // 写入当前时间
    var myDate = new Date();
    $("#run_time").val(myDate.toLocaleString());
    $("#processid").val(processid);
    $("#process_type").val(process_type);
}

//kvm
function kvmFunction() {
    $('#kvm_machine').empty();
    $.ajax({
        type: "POST",
        dataType: 'json',
        url: "../kvm_data/",
        data: {
            utils_kvm_id: $('#kvm_machine_platform').val()
        },
        success: function (data) {
            if (data.ret == 0) {
                alert(data.data)
            } else {
                $("#all_kvm_data").val(JSON.stringify(data.all_kvm_dict));

                var utils_id = $('#kvm_machine_platform').val();
                for (i = 0; i < data.all_kvm_dict[utils_id].length; i++) {
                    $("#kvm_machine").append('<option value="'+ data.all_kvm_dict[utils_id][i].name + '">'+ data.all_kvm_dict[utils_id][i].name + '</option>')
                }

            }
        }
    });
}


function get_kvm_detail(){
    var table1 = $('#kvm_copy').DataTable();
    table1.ajax.url("../kvm_copy_data/?kvmmachine_id=" + $('#kvm_id').val() + "&utils_id=" + $('#kvm_machine_platform').val()
    ).load();
}


$(document).ready(function () {
    //主机
    $(".tabbed>ul>li").click(function () {
        var aa = this.firstElementChild;
        aa.click();
    });

    getClientree();

    $('#node_save').click(function () {
        $.ajax({
            type: "POST",
            dataType: 'json',
            url: "../hosts_node_save/",
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
                            "text": "<i class='jstree-icon jstree-themeicon fa fa-folder icon-state-warning icon-lg jstree-themeicon-custom'></i>" + $("#node_name").val(),
                            "id": data.nodeid,
                            "type": "NODE",
                            "data": { "remark": $("#node_remark").val(), "name": $("#node_name").val(), "pname": $("#pname").val(),"edit":true },
                            "icon": false,
                        }, "last", false, false);
                        $("#id").val(data.nodeid)
                        $('#tree_client').jstree('deselect_all')
                        $('#tree_client').jstree('select_node', $("#id").val(), true)
                    }
                    else {
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace(curnode.data["name"], $("#node_name").val())
                        curnode.text = newtext
                        curnode.data["remark"] = $("#node_remark").val()
                        curnode.data["name"] = $("#node_name").val()
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);
                    }
                    $("#title").text($("#node_name").val())
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
                            "id": data.nodeid,
                            "type": "CLIENT",
                            "data": { "remark": $("#remark").val(), "name": $("#host_name").val(), "pname": $("#pname").val(),"edit":true },
                            "icon": false,
                        }, "last", false, false);
                        $("#id").val(data.nodeid)
                        $('#tree_client').jstree('deselect_all')
                        $('#tree_client').jstree('select_node', $("#id").val(), true)
                        $('#tabcheck2').removeAttr("style", "color: #cbd5dd");
                        $("#tabcheck2").parent().removeAttr("style", "pointer-events:none;");
                        $('#tabcheck3').removeAttr("style", "color: #cbd5dd");
                        $("#tabcheck3").parent().removeAttr("style", "pointer-events:none;");
                        $('#tabcheck4').removeAttr("style", "color: #cbd5dd");
                        $("#tabcheck4").parent().removeAttr("style", "pointer-events:none;");
                    }
                    else {
                        var curnode = $('#tree_client').jstree('get_node', $("#id").val());
                        var newtext = curnode.text.replace(curnode.data["name"], $("#host_name").val())
                        curnode.text = newtext
                        curnode.data["name"] = $("#host_name").val()
                        $('#tree_client').jstree('set_text', $("#id").val(), newtext);
                    }
                    $("#title").text($("#host_name").val())
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
            $('#param_se').append('<option value="' + variable_name + '">' + param_name + ':' + variable_name + ':' + param_value + '</option>');
        }
        if (param_operate == "edit") {
            // 指定value的option修改text
            $('#param_se option[value="' + variable_name + '"]').text(param_name + ':' + variable_name + ':' + param_value);
        }
        $("#static01").modal("hide");
    });



});

